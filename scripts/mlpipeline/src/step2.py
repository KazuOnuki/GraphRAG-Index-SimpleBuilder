"""
Summary:
This script processes Markdown (.md) files from a specified input folder, splits the content into sections with a token limit,
and extracts summaries from the Markdown files. The processed sections are saved as individual files, and summaries are extracted and saved into a CSV file.

The script is controlled by command-line arguments that specify the input and output directories.

Key functionalities:
- Splitting Markdown files into sections, ensuring each section has no more than 512 tokens.
- Saving each section as a separate file in the output directory.
- Extracting summaries and saving them in a CSV file, including file path information.

Command-line Arguments:
- --step2_input: The input folder containing Markdown files.
- --step2_output: The output folder to save processed files and summaries.
"""

import argparse
import csv
import os
import re

import tiktoken

parser = argparse.ArgumentParser()
parser.add_argument("--step2_input", type=str)
parser.add_argument("--step2_output", type=str)
print("Hello...\nI'm step2 :-)")

args = parser.parse_args()
arr = os.listdir(args.step2_input)
print(f"files in input path: {arr}")


def count_tokens(text):
    """
    Function to count the number of tokens in a text.
    Uses the tiktoken library to count tokens.

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
    Function to split a section by a specified delimiter.

    Args:
    section (str): The section to split.
    delimiter (str): The delimiter (e.g., '#', '##', '###').

    Returns:
    list: A list of split sections.
    """
    return re.split(rf"(?m)^{delimiter} ", section)


def process_sections(sections, max_tokens=512):
    """
    Function to split sections so that each section contains no more than 512 tokens.

    Args:
    sections (list): A list of split sections.
    max_tokens (int): The maximum number of tokens.

    Returns:
    list: A list of sections that meet the token count requirement.
    """
    processed_sections = []
    for section in sections:
        if count_tokens(section) <= max_tokens:
            # If the section is within 512 tokens, add it directly
            processed_sections.append(section)
        else:
            # First try to split by `##`
            sub_sections = split_section(section, "##")
            if all(count_tokens(sub) <= max_tokens for sub in sub_sections):
                processed_sections.extend(sub_sections)
            else:
                # If still not within limit, try splitting by `###`
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
                            # If still not within limit, add it as is
                            sub_sub_sections.append(sub_section)
                processed_sections.extend(sub_sub_sections)
    return processed_sections


def split_markdown_file(file_path, max_tokens=512):
    """
    Function to read a Markdown file, split it into sections, and ensure each section has no more than 512 tokens.

    Args:
    file_path (str): The path to the Markdown file to read.
    max_tokens (int): The maximum number of tokens.

    Returns:
    list: A list of split sections.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split by the top-level header
    sections = split_section(content, "#")

    # Add the delimiter back to each section
    sections = ["# " + section for section in sections]

    # Process each section to meet the token count requirement
    processed_sections = process_sections(sections, max_tokens)

    return processed_sections


def save_sections(sections, output_dir, base_filename):
    """
    Function to save each section as an individual Markdown file.

    Args:
    sections (list): A list of sections to save.
    output_dir (str): The directory to save the sections.
    base_filename (str): The base filename for the sections.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for idx, section in enumerate(sections):
        section_filename = f"{base_filename}_part_{idx+1}.md"
        section_path = os.path.join(output_dir, section_filename)
        with open(section_path, "w", encoding="utf-8") as section_file:
            section_file.write(section)


def extract_summaries(output_dir, csv_filename):
    """
    Function to extract SUMMARIZE statements from split Markdown files and save them to a CSV.

    Args:
    output_dir (str): The directory where the split Markdown files are saved.
    csv_filename (str): The name of the CSV file to save the summaries.
    """
    summaries = []

    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Extract PATH information
                    path_match = re.search(
                        r"^# PATH: (.*)$", content, re.MULTILINE
                    )
                    path_info = (
                        path_match.group(1).strip()
                        if path_match
                        else "No PATH info"
                    )

                    # Extract SUMMARIZE statement
                    summary_match = re.search(
                        r"^SUMMARIZE: (.*)$", content, re.MULTILINE
                    )
                    if summary_match:
                        summary = summary_match.group(1).strip()
                        base_filename = re.sub(r"_part_\d+\.md$", "", file)
                        summaries.append([base_filename, path_info, summary])

    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename", "PATH", "Summary"])
        writer.writerows(summaries)


def process_markdown_folder(
    src_folder, dst_folder, csv_filename, max_tokens=512
):
    """
    Function to process each Markdown file in the source folder, split and save them, and extract SUMMARIZE statements to a CSV.

    Args:
    src_folder (str): The path to the source folder containing Markdown files.
    dst_folder (str): The path to the destination folder to save split files.
    csv_filename (str): The name of the CSV file to save the summaries.
    max_tokens (int): The maximum number of tokens.
    """
    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                sections = split_markdown_file(file_path, max_tokens)
                base_filename = os.path.splitext(file)[0]
                save_sections(sections, dst_folder, base_filename)

    extract_summaries(dst_folder, csv_filename)


if __name__ == "__main__":
    src_folder = args.step2_input
    dst_folder = args.step2_output
    analysis_output_folder = f"{dst_folder}/analysis_output"

    os.makedirs(dst_folder, exist_ok=True)
    os.makedirs(analysis_output_folder, exist_ok=True)

    csv_filename = f"{analysis_output_folder}/summaries.csv"  # the CSV file to save summaries
    process_markdown_folder(src_folder, dst_folder, csv_filename)
    print("Markdown files have been split and summaries have been extracted.")
