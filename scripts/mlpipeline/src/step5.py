"""
Summary:
This script processes Markdown (.md) files by splitting them into smaller chunks based on token count and generating new summaries for each chunk using Azure OpenAI's GPT model.
The script reads Markdown files from a specified folder, splits them if they exceed a token threshold, and resummarizes them using existing summaries stored in a CSV file.
The new summaries are appended to the original content, and the processed files are saved in a designated output folder.
A temporary folder is used to handle split files, which is deleted after processing.

Key functionalities:
- **Text Splitting**: If a Markdown file exceeds a token limit (1000 tokens), it is split into smaller chunks based on tokens, preserving code blocks and list items.
- **Integration with Azure OpenAI**: Similar to `step4.py`, this script uses Azure OpenAI to generate summaries for the Markdown files.
- **Temporary Directory Management**: Temporary files are created for split Markdown files and deleted after processing.
- **CSV Handling**: The script reads summaries and paths from a CSV file and associates them with the corresponding Markdown files.
- **New File Generation**: The resummarized content is appended to the original Markdown and saved in a new directory. Temporary files are deleted afterward.

Differences from `step4.py`:
1. **Token Counting and Splitting**: `step5.py` includes functionality to count tokens in the Markdown content and splits the files into smaller parts if they exceed 1000 tokens. This is handled using the `tiktoken` library, which is absent in `step4.py`.
2. **Temporary File Handling**: `step5.py` creates and uses a temporary directory (`temp_output_path`) for storing split Markdown files, which is removed after processing. This mechanism is not present in `step4.py`.
3. **Larger File Processing**: `step5.py` processes larger files that may require splitting, whereas `step4.py` assumes that all files fit within a single API request and handles them as whole documents.
4. **Cleanup Process**: After processing, `step5.py` deletes temporary files, adding a cleanup step that `step4.py` does not include.
"""

import argparse
import csv
import glob
import os
import shutil

import tiktoken
from openai import AzureOpenAI

parser = argparse.ArgumentParser()
parser.add_argument("--aoai_resource", type=str)
parser.add_argument("--aoai_apikey", type=str)
parser.add_argument("--aoai_model", type=str)
parser.add_argument("--step2_output", type=str)
parser.add_argument("--step5_input", type=str)
parser.add_argument("--step5_output", type=str)
print("Hello...\nI'm step5 :-)")

args = parser.parse_args()
arr = os.listdir(args.step5_input)
print(f"files in input path: {arr}")


def count_tokens(text, encoding_name="cl100k_base"):
    """Function to count tokens."""
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text, disallowed_special=())
    return len(tokens), tokens


def split_text_by_tokens(text, max_tokens=512, encoding_name="cl100k_base"):
    """Function to split text based on token count."""
    encoding = tiktoken.get_encoding(encoding_name)

    # Split by paragraphs considering code blocks and list items
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    current_chunk_tokens = 0

    for paragraph in paragraphs:
        paragraph_tokens = len(
            encoding.encode(paragraph, disallowed_special=())
        )
        # Treat code blocks and list items as one chunk
        if paragraph.startswith("```") or paragraph.lstrip().startswith(
            (
                "-",
                "*",
                "+",
                "1.",
                "2.",
                "3.",
                "4.",
                "5.",
                "6.",
                "7.",
                "8.",
                "9.",
                "0.",
            )
        ):
            if (
                current_chunk_tokens
                + paragraph_tokens
                + len(encoding.encode("\n\n", disallowed_special=()))
                > max_tokens
            ):
                chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
                current_chunk_tokens = paragraph_tokens + len(
                    encoding.encode("\n\n", disallowed_special=())
                )
            else:
                current_chunk += paragraph + "\n\n"
                current_chunk_tokens += paragraph_tokens + len(
                    encoding.encode("\n\n", disallowed_special=())
                )
        else:
            sentences = paragraph.split(". ")
            for sentence in sentences:
                sentence_tokens = len(
                    encoding.encode(sentence, disallowed_special=())
                )
                if current_chunk_tokens + sentence_tokens > max_tokens:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                    current_chunk_tokens = sentence_tokens
                else:
                    current_chunk += sentence
                    current_chunk_tokens += sentence_tokens

            current_chunk += "\n\n"  # Add newline at the end of paragraph
            current_chunk_tokens += len(
                encoding.encode("\n\n", disallowed_special=())
            )

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def summarize_content(
    system_prompt_msg: str, md_content: str, summary: str
) -> str:
    """
    Function to summarize Markdown content using Azure OpenAI.

    Args:
    system_prompt_msg (str): System prompt message.
    md_content (str): Markdown content.
    summary (str): Original summary of md_content.

    Returns:
    str: Summarized content.
    """
    try:
        client = AzureOpenAI(
            azure_endpoint=f"https://{args.aoai_resource}.openai.azure.com/",
            api_key=args.aoai_apikey,
            api_version="2024-02-01",
        )

        user_msg = f"""
        // Original Summary: {summary}

        // Provided Markdown Content: {md_content}
        """

        response = client.chat.completions.create(
            model=args.aoai_model,
            messages=[
                {"role": "system", "content": system_prompt_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0,
            max_tokens=100,
        )
        return response.choices[0].message.content
    except Exception as e:
        return summary


def process_markdown_files(
    summaries: dict, folder_path, temp_output_path, resummarize_output_path
):
    """Function to process Markdown files in a folder and split if necessary."""
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                token_count, _ = count_tokens(content)

                if token_count > 1000:
                    chunks = split_text_by_tokens(content)
                    base_name, ext = os.path.splitext(filename)

                    for i, chunk in enumerate(chunks):
                        new_file_path = os.path.join(
                            temp_output_path, f"{base_name}_part{i+1}{ext}"
                        )
                        with open(
                            new_file_path, "w", encoding="utf-8"
                        ) as new_file:
                            new_file.write(chunk)
                else:
                    pass
                    # print(f"{filename} does not need splitting.")

    for filename, summary in summaries.items():
        # List up md file names in the reading source folder
        for file_name in os.listdir(temp_output_path):
            # If each Summary's content is included in the file name,
            if (file_name.endswith(".md")) and (filename in file_name):
                print(f"processing <{file_name}> ・・・")

                file_path = os.path.join(temp_output_path, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    md_content = f.read()

                # Set system prompt message
                system_prompt_msg = """
                Summarize the content of the provided Markdown file.
                Based on the Original Summary, explain in English what the provided Markdown is describing.
                Ensure that the Response is concise and contains only one sentence!
                """

                # Summarize
                summarized_content = summarize_content(
                    system_prompt_msg, md_content, summary[1]
                )

                # Save as a new Markdown file
                new_file_path = os.path.join(
                    resummarize_output_path,
                    os.path.splitext(file_name)[0] + "_summarized.md",
                )
                with open(new_file_path, "w", encoding="utf-8") as f:
                    print("# PATH:" in md_content)
                    if "# PATH:" in md_content:
                        f.write(md_content)
                    else:
                        f.write(
                            summarized_content
                            + "\n\n"
                            + f"# PATH: {summary[0]}"
                            + "\n\n"
                            + md_content
                        )
    # 処理完了後に temp_output_path を削除
    if os.path.exists(temp_output_path):
        shutil.rmtree(temp_output_path)
        print(f"Temporary directory {temp_output_path} has been removed.")


def read_summaries_csv(csv_file: str) -> dict:
    """
    Function to read summaries and filenames from a CSV file.

    Args:
    csv_file (str): Path of the CSV file to read.

    Returns:
    dict: Dictionary with filename as key and summary as value.
    """
    summaries = {}
    with open(csv_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filename = row["Filename"]
            summary = row["Summary"]
            path = row["PATH"]
            summaries[filename] = [path, summary]

    print(f"summaries: {summaries}")
    return summaries


if __name__ == "__main__":
    src_folder = args.step5_input
    start_path = args.step2_output
    target_file = "summaries.csv"
    dst_folder = args.step5_output
    temp_output_path = f"{dst_folder}/temp_5th_processed"

    os.makedirs(temp_output_path, exist_ok=True)
    os.makedirs(dst_folder, exist_ok=True)

    def find_file(start_path, target_file):
        """Function to search targeted file in specified path"""
        search_pattern = os.path.join(start_path, "**", target_file)
        file_list = glob.glob(search_pattern, recursive=True)
        print(search_pattern)
        print(file_list)
        if file_list:
            return file_list[0]
        return None

    csv_file = find_file(start_path, target_file)
    msg: str = (
        f"found summaries.csv in {start_path}: {csv_file}"
        if csv_file
        else f"Couldn't find summaries.csv in {start_path}"
    )
    print(msg)

    # Read summaries and filenames from the CSV file
    summaries = read_summaries_csv(csv_file)
    process_markdown_files(summaries, src_folder, temp_output_path, dst_folder)
