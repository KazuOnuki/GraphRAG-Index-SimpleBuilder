"""
Summary:
This script processes Markdown (.md) files by generating new summaries for them using Azure OpenAI's GPT model.
It takes as input a CSV file containing existing summaries and paths to original documents, reads Markdown files from a specified folder, and uses the Azure OpenAI API to re-summarize the content. The new summaries are appended to the original Markdown content, and the files are saved in a designated output folder.

Key functionalities:
- **Integration with Azure OpenAI**: It connects to an Azure OpenAI resource to generate new summaries for Markdown content.
- **CSV Handling**: The script reads summaries and paths from a CSV file and uses them to associate with the corresponding Markdown files.
- **Markdown File Processing**: It reads each Markdown file, uses the existing summary as a prompt, generates a new summary, and saves it along with the original content.
- **New File Generation**: The re-summarized content is appended to the original Markdown file and saved as a new file in the output directory.

Command-line Arguments:
- --aoai_resource: The Azure OpenAI resource name.
- --aoai_apikey: The API key for accessing Azure OpenAI.
- --aoai_model: The name of the Azure OpenAI model to use for summarization.
- --step2_output: The output folder from Step 2, containing the CSV file with summaries.
- --step4_input: The input folder containing Markdown files to process.
- --step4_output: The folder where processed Markdown files will be saved.

Azure OpenAI API is used to ensure that each file receives a concise, single-sentence summary in English.
"""

import argparse
import csv
import glob
import os

from openai import AzureOpenAI

parser = argparse.ArgumentParser()
parser.add_argument("--aoai_resource", type=str)
parser.add_argument("--aoai_apikey", type=str)
parser.add_argument("--aoai_model", type=str)
parser.add_argument("--step2_output", type=str)
parser.add_argument("--step4_input", type=str)
parser.add_argument("--step4_output", type=str)
print("Hello...\nI'm step4 :-)")

args = parser.parse_args()
arr = os.listdir(args.step4_input)
print(f"files in input path: {arr}")


def summarize_content(
    system_prompt_msg: str, md_content: str, summary: str
) -> str:
    """
    Function to re-summarize the content of a Markdown file using Azure OpenAI.

    Args:
    system_prompt_msg (str): System prompt message.
    md_content (str): Content of the Markdown file.
    summary (str): Summary of the original document from which md_content was extracted.

    Returns:
    str: The re-summarized content.
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


def read_summaries_csv(csv_file: str) -> dict:
    """
    Function to read summaries and filenames from a CSV file.

    Args:
    csv_file (str): The path of the CSV file to read.

    Returns:
    dict: A dictionary where filenames are keys and summaries are values.
    """
    summaries = {}
    with open(csv_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filename = row["Filename"]
            summary = row["Summary"]
            path = row["PATH"]
            summaries[filename] = [path, summary]
    return summaries


def process_md_files_with_summaries(
    src_folder: str, summaries: dict, dst_folder: str, system_prompt_msg: str
):
    """
    Function to process Markdown files with summaries and save them as new Markdown files.

    Args:
    src_folder (str): The path of the folder containing original Markdown files.
    summaries (dict): A dictionary where filenames are keys and summaries are values.
    dst_folder (str): The path of the folder to save the new Markdown files.
    system_prompt_msg (str): System prompt message.
    """
    for filename, summary in summaries.items():
        for file_name in os.listdir(src_folder):
            if (file_name.endswith(".md")) and (filename in file_name):
                print(f"processing <{file_name}> ・・・")

                file_path = os.path.join(src_folder, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    md_content = f.read()

                summarized_content = summarize_content(
                    system_prompt_msg, md_content, summary[1]
                )

                new_file_path = os.path.join(
                    dst_folder,
                    os.path.splitext(file_name)[0] + "_summarized.md",
                )
                with open(new_file_path, "w", encoding="utf-8") as f:
                    if "# PATH:" in md_content:
                        f.write(summarized_content + "\n\n" + md_content)
                    else:
                        f.write(
                            summarized_content
                            + "\n\n"
                            + f"# PATH: {summary[0]}"
                            + "\n\n"
                            + md_content
                        )


if __name__ == "__main__":
    src_folder = args.step4_input
    start_path = args.step2_output
    target_file = "summaries.csv"

    def find_file(start_path, target_file):
        """Function to search targeted file in specified paths"""
        search_pattern = os.path.join(start_path, "**", target_file)
        file_list = glob.glob(search_pattern, recursive=True)
        print(search_pattern)
        print(file_list)
        if file_list:
            return file_list[0]  # return file path found first
        return None

    csv_file = find_file(start_path, target_file)
    msg: str = (
        f"found summaries.csv in {start_path}: {csv_file}"
        if csv_file
        else f"Couldn't find summaries.csv in {start_path}"
    )
    print(msg)

    dst_folder = args.step4_output
    os.makedirs(dst_folder, exist_ok=True)

    system_prompt_msg = """
    Summarize the content of the provided Markdown file.
    Based on the Original Summary, explain in English what the provided Markdown is describing.
    Ensure that the Response is concise and contains only one sentence!
    """

    summaries = read_summaries_csv(csv_file)
    process_md_files_with_summaries(
        src_folder, summaries, dst_folder, system_prompt_msg
    )
    print("New Markdown files have been generated.")
