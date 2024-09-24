"""
Summary:
This script processes Markdown (.md) files from a specified input folder by splitting them into sections with a token limit.
The content of each file is divided based on heading levels (`#`, `##`, `###`), and any sections exceeding the maximum token count (512 tokens) are further split.
During processing, the script removes lines containing "SUMMARIZE" and "# PATH:" before saving the sections as individual Markdown files in an output folder.

Key functionalities:
- Splitting Markdown files into sections and ensuring each section has no more than 512 tokens.
- Removing specific metadata lines ("SUMMARIZE" and "# PATH:") from the content.
- Saving each section as a separate file in the output directory.

Differences from Step2:
1. **No CSV Output**: Unlike `step2`, this script does not extract summaries or path information into a CSV file.
2. **Removal of Metadata**: This script removes "SUMMARIZE" and "# PATH:" lines from the Markdown files, which was not performed in `step2`.
3. **Simplified Output**: `step2` focuses on extracting and saving summaries, while this script purely processes the file content by splitting it into sections and removing metadata lines.
4. **No Analysis Output**: Unlike `step2`, which generates an analysis folder for summaries, this script only focuses on splitting and saving Markdown files.

Command-line Arguments:
- --step3_input: The input folder containing Markdown files.
- --step3_output: The output folder to save the processed files.
"""

import argparse
import os
import re

import tiktoken

parser = argparse.ArgumentParser()
parser.add_argument("--step3_input", type=str)
parser.add_argument("--step3_output", type=str)
print("Hello...\nI'm step3 :-)")

args = parser.parse_args()
arr = os.listdir(args.step3_input)
print(f"files in input path: {arr}")


def count_tokens(text):
    """
    Function to count the number of tokens in a text.
    Uses the tiktoken library to count the tokens.

    Args:
    text (str): The text to count tokens in.

    Returns:
    int: The number of tokens.
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text, disallowed_special=())
    return len(tokens)


def split_section(section, delimiter):
    """
    Function to split a section by the specified delimiter.

    Args:
    section (str): The section to split.
    delimiter (str): The delimiter (e.g., '#', '##', '###').

    Returns:
    list: A list of split sections.
    """
    return re.split(rf"(?m)^{delimiter} ", section)


def process_sections(sections, max_tokens=512):
    """
    Function to split sections to fit within 512 tokens.

    Args:
    sections (list): A list of split sections.
    max_tokens (int): The maximum number of tokens.

    Returns:
    list: A list of sections that meet the token count requirement.
    """
    processed_sections = []
    for section in sections:
        if count_tokens(section) <= max_tokens:
            processed_sections.append(section)
        else:
            sub_sections = split_section(section, "##")
            if all(count_tokens(sub) <= max_tokens for sub in sub_sections):
                processed_sections.extend(sub_sections)
            else:
                sub_sub_sections = []
                for sub_section in sub_sections:
                    if count_tokens(sub_section) <= max_tokens:
                        sub_sub_sections.append(sub_section)
                    else:
                        deeper_sub_sections = split_section(sub_section, "###")
                        if all(
                            count_tokens(deep) <= max_tokens
                            for deep in deeper_sub_sections
                        ):
                            sub_sub_sections.extend(deeper_sub_sections)
                        else:
                            sub_sub_sections.append(sub_section)
                processed_sections.extend(sub_sub_sections)
    return processed_sections


def remove_summaries_and_paths(content):
    """
    Function to remove SUMMARIZE and # PATH: lines from a Markdown file.

    Args:
    content (str): The content of the Markdown file.

    Returns:
    str: The content with SUMMARIZE and # PATH: lines removed.
    """
    content = re.sub(r"^SUMMARIZE: .*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"^# PATH: .*$", "", content, flags=re.MULTILINE)
    # print(content)
    return content


def split_markdown_file(file_path, max_tokens=512):
    """
    Function to read a Markdown file, split it into sections, and fit each section within 512 tokens.

    Args:
    file_path (str): The path of the Markdown file to read.
    max_tokens (int): The maximum number of tokens.

    Returns:
    list: A list of split sections.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    content = remove_summaries_and_paths(content)
    sections = split_section(content, "#")
    sections = ["# " + section for section in sections]
    processed_sections = process_sections(sections, max_tokens)
    return processed_sections


def save_sections(sections, output_dir, base_filename):
    """
    Function to save each section as an individual Markdown file.

    Args:
    sections (list): A list of sections to save.
    output_dir (str): The directory to save the sections in.
    base_filename (str): The base filename to use.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for idx, section in enumerate(sections):
        section_filename = f"{base_filename}_part_{idx+1}.md"
        section_path = os.path.join(output_dir, section_filename)
        with open(section_path, "w", encoding="utf-8") as section_file:
            section_file.write(section)


def process_markdown_folder(src_folder, dst_folder, max_tokens=512):
    """
    Function to process each Markdown file in a source folder, split and save them, and extract SUMMARIZE and # PATH: lines to CSV.

    Args:
    src_folder (str): The path of the source folder.
    dst_folder (str): The path of the destination folder.
    max_tokens (int): The maximum number of tokens.
    """
    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                sections = split_markdown_file(file_path, max_tokens)
                base_filename = os.path.splitext(file)[0]
                save_sections(sections, dst_folder, base_filename)


if __name__ == "__main__":
    # Example usage
    src_folder = args.step3_input
    dst_folder = args.step3_output
    process_markdown_folder(src_folder, dst_folder)
    print(
        "Markdown files have been split, and SUMMARIZE and # PATH: lines have been removed."
    )
