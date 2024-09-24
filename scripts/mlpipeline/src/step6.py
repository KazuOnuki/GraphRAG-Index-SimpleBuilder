"""
Summary:
This script processes Markdown (.md) files, deletes those with more than 1000 tokens or less than 40 tokens, and uploads the remaining files to an Azure Blob Storage container.
The script reads files from two input directories (`step6_input` and `step4_output`), processes them, and saves the results in an output directory (`step6_output`).
After processing, the script uploads the valid files to a specified Azure Blob Storage container.

Key functionalities:
1. **File Processing**:
- The script copies Markdown files from two input directories (`step6_input` and `step4_output`).
- Files with more than 1000 tokens or fewer than 40 tokens are deleted.

2. **Azure Blob Storage Integration**:
- The script connects to an Azure Blob Storage account using the provided connection string and uploads the remaining Markdown files to a specified container.
- The container is created if it doesn’t exist.

3. **Token Counting**:
- The script counts the tokens in each Markdown file using the `tiktoken` library to determine if a file should be kept or deleted.
- Files with more than 1000 tokens are assumed to be too large and are deleted.
- Files with fewer than 40 tokens are considered noise and also deleted.

4. **Folder and File Management**:
- The script handles file operations such as copying and removing files from the input directories to the output directory,
ensuring that only files that meet the token criteria are uploaded to Azure Blob Storage.
"""

import argparse
import os
import shutil

import tiktoken
from azure.storage.blob import BlobServiceClient

parser = argparse.ArgumentParser()
parser.add_argument("--target_storage_account_input", type=str)
parser.add_argument("--target_storage_api_key_input", type=str)
parser.add_argument("--target_storage_container_input", type=str)
parser.add_argument("--step6_input", type=str)
parser.add_argument("--step4_output", type=str)
parser.add_argument("--step6_output", type=str)
print("Hello...\nI'm step6 :-)")

args = parser.parse_args()
arr = os.listdir(args.step6_input)
print(f"files in input path: {arr}")


def count_tokens(text, encoding_name="cl100k_base"):
    """Function to count tokens."""
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text, disallowed_special=())
    return len(tokens)


def copy_files(source_folder, dest_folder):
    """Function to copy Markdown files from source to destination folder."""
    for filename in os.listdir(source_folder):
        if filename.endswith(".md"):
            source_file_path = os.path.join(source_folder, filename)
            dest_file_path = os.path.join(dest_folder, filename)
            shutil.copyfile(source_file_path, dest_file_path)


def process_markdown_files(past_folder, temp_output_path, dst_folder):
    """Function to process Markdown files, delete files with more than 1000 tokens, and copy files from temp_output_path."""
    # Copy files from temp_output_path after deleting files with more than 1000 tokens
    copy_files(temp_output_path, dst_folder)
    copy_files(past_folder, dst_folder)

    for filename in os.listdir(dst_folder):
        if filename.endswith(".md"):
            file_path = os.path.join(dst_folder, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                token_count = count_tokens(content)

            if token_count > 1000:
                os.remove(file_path)  # Delete files with more than 1000 tokens
                print(f"Deleted {filename}.")

            # Delete files with token count less than 40 as they are likely noise
            if token_count < 40:
                print(
                    f"{filename} has less than 40 tokens. Deleting the file."
                )
                os.remove(file_path)

    # # Copy files from temp_output_path after deleting files with more than 1000 tokens
    # copy_files(temp_output_path, past_folder)
    # copy_files(past_folder, dst_folder)


def upload_files_to_blob(storage_account_name, container_name, folder_path):
    """Function to upload files from a folder to a specific Azure Blob container."""
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )
    container_client = blob_service_client.get_container_client(container_name)

    # Create the container if it doesn't exist
    try:
        container_client.create_container()
    except Exception as e:
        print(f"Container already exists or couldn't be created: {e}")

    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            blob_client = container_client.get_blob_client(filename)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            print(f"Uploaded {filename} to Azure Blob Storage.")


if __name__ == "__main__":
    src_folder = args.step6_input
    past_folder = args.step4_output
    dst_folder = args.step6_output
    # NOTE: final result should be in the step4 output dst older
    process_markdown_files(past_folder, src_folder, dst_folder)

    # Upload the files to Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING = f"DefaultEndpointsProtocol=https;AccountName={args.target_storage_account_input};AccountKey={args.target_storage_api_key_input}"
    CONTAINER_NAME = f"{args.target_storage_container_input}"
    upload_files_to_blob(
        AZURE_STORAGE_CONNECTION_STRING, CONTAINER_NAME, dst_folder
    )
