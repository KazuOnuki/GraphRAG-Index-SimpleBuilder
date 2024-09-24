"""
Summary:

This script processes Markdown (.md) files from a specified input folder.
It first extracts the list of Markdown files, summarizes their content using an AI model from Azure OpenAI,
and then copies the files to an output folder. During this process, it adds the file name and a summary
to the top of each file and removes specific text from the content.

The script is controlled by command-line arguments to define resources such as the AI model and file paths.

Key functionalities:
- Summarizing Markdown files using an AI model.
- Copying files to a new folder with additional information (file name, summary).
- Removing specific text from the file content during copying.
"""

import argparse
import os
import time

from openai import AzureOpenAI

parser = argparse.ArgumentParser()
parser.add_argument("--aoai_resource", type=str)
parser.add_argument("--aoai_apikey", type=str)
parser.add_argument("--aoai_model", type=str)
parser.add_argument("--step1_input", type=str)
parser.add_argument("--step1_output", type=str)
print("Hello...\nI'm step1 :-)")

args = parser.parse_args()
arr = os.listdir(args.step1_input)
print(f"files in input path: {arr}")


def summarize_content(system_prompt_msg: str, md_content: str) -> str:
    try:
        client = AzureOpenAI(
            azure_endpoint=f"https://{args.aoai_resource}.openai.azure.com/",
            api_key=args.aoai_apikey,
            api_version="2024-02-01",
        )
        response = client.chat.completions.create(
            model=args.aoai_model,
            messages=[
                {"role": "system", "content": system_prompt_msg},
                {
                    "role": "user",
                    "content": f"Summarize the following Markdown data: {md_content}",
                },
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return ""


def extract_md_files(src_folder: str) -> list:
    """
    function to extract md file path list from specified src_folder

    Parameters
    -----
    - folder_path: str
        - folder path including md file
    """
    md_files = list()
    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))
    return md_files


def remove_text(content: str, text_to_remove: str) -> str:
    """
    function to delete specified text from content string

    Parameters
    -----
    - content: str
        - targeted process string
    - text_to_remove: str
        - string to delete
    """
    return content.replace(text_to_remove, "")


def replace_special_tokens(text):
    """Function to replace special token with empty String"""
    special_tokens = {
        "<|endofprompt|>",
        "<|endoftext|>",
        "<|fim_prefix|>",
        "<|fim_suffix|>",
        "<|fim_middle|>",
    }
    for token in special_tokens:
        text = text.replace(token, "")  # 特殊トークンを空文字列に置き換える
    return text


def copy_md_files_with_info(
    md_files: list,
    dst_folder: str,
    text_to_remove: str,
    system_prompt_msg: str,
):
    """
    function to delete specified string and add folder/file name info at header of md file, after copying md_files to dst_folder

    Parameters
    -----
    - md_files: list
        - targeted md files list
    - dst_folder: str
    - text_to_remove: str
        - string to delete
    """
    for file in md_files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"==========summarizing {file}============")
        path_info = f"PATH: {os.path.basename(file)}\n"
        summarize_info = (
            f"SUMMARIZE: {summarize_content(system_prompt_msg, content)}\n"
        )
        new_content = path_info + summarize_info + content
        new_content = remove_text(new_content, text_to_remove)

        # !delete special tokens
        new_content = replace_special_tokens(new_content)

        new_file_path = os.path.join(dst_folder, os.path.basename(file))
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(new_content)


if __name__ == "__main__":
    start = time.perf_counter()
    src_folder = args.step1_input
    dst_folder = args.step1_output
    os.makedirs(dst_folder, exist_ok=True)

    # extract parent directory name
    text_to_remove = os.path.dirname(args.step1_input)

    # Set system prompt message
    system_prompt_msg = """
    You are an AI assistant designed to summarize the content of Markdown files.
    Your task is to provide a concise summary of the provided Markdown file content in a way that is understandable to beginners, within 300 characters.
    Extract the key points and ensure that the overall summary conveys the main idea.

    ### Instructions:
    1. Clearly state the subject and purpose of the file.
    2. Concisely explain the main features or functionalities.
    3. Include troubleshooting points and important considerations for the user.
    4. Mention important links or references if necessary.
    """

    md_files = extract_md_files(src_folder)
    copy_md_files_with_info(
        md_files, dst_folder, text_to_remove, system_prompt_msg
    )
    print(
        "Markdown files copied, folder/file info added, and specified text removed successfully."
    )
    end = time.perf_counter()
    print(f"End: {end - start:.3f} s.")
