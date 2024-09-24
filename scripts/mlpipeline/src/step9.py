"""
Summary:
This Python script automates the process of uploading files from a local directory to an Azure Blob Storage container.
It uses Azure Storage Blob SDK and takes several command-line arguments for configuring the target storage account and the input/output paths.
Here's a breakdown of the script's key functionality:

1. **Command-Line Argument Parsing**:
    - The script uses `argparse` to accept the following inputs from the user:
    - `target_storage_account_name`: Name of the Azure storage account.
    - `target_storage_api_key`: API key for authenticating the storage account.
    - `target_storage_container_name`: The container within the storage account where files will be uploaded.
    - `step9_input`: Local directory containing files to be uploaded.
    - `step9_output`: Not explicitly used in the script but is accepted as an argument.

2. **File Listing and Preparation**:
    - The script lists and displays all files in the specified input directory, showing which files are going to be uploaded to the Azure Blob Storage container.

3. **Azure Blob Storage Interaction**:
    - The script constructs the connection string for the Azure Blob Storage service using the provided storage account name and API key.
    - It attempts to create the specified container if it doesn’t already exist.
    - Files are uploaded to the Azure Blob Storage container while preserving their relative paths. Each file’s progress is logged as it is successfully uploaded.

4. **Error Handling**:
    - In case the container already exists or cannot be created, an exception is handled gracefully with an informative message.

### Usage:
    - This script is designed to automate the file upload process to Azure Blob Storage. It is especially useful for scenarios where a large number of files or
        directories need to be transferred to the cloud in a structured way.

### Requirements:
    - The script requires the Azure Storage Blob Python SDK (`azure-storage-blob`) and assumes that the user has appropriate permissions to upload files
        to the Azure storage account and create containers if needed.

### Assumptions:
    - The target Azure Blob Storage container may not already exist, but the script will attempt to create it.
    - Input folder (`step9_input`) contains files ready for upload, and appropriate API keys and storage account names are provided.
"""

import argparse
import os

from azure.storage.blob import BlobServiceClient

parser = argparse.ArgumentParser()
parser.add_argument("--target_storage_account_name", type=str)
parser.add_argument("--target_storage_api_key", type=str)
parser.add_argument("--target_storage_container_name", type=str)
parser.add_argument("--step9_input", type=str)
parser.add_argument("--step9_output", type=str)
print("Hello...\nI'm step9 :-)")

args = parser.parse_args()
arr = os.listdir(args.step9_input)
print(f"files in input path: {arr}")

print(
    f"export targeted storage account name: {args.target_storage_account_name}"
)
print(
    f"export targeted storage container name: {args.target_storage_container_name}"
)


def upload_files_to_blob(storage_account_name, container_name, folder_path):
    """Function to upload files from a folder to a specific Azure Blob container."""
    blob_service_client = BlobServiceClient.from_connection_string(
        storage_account_name
    )
    container_client = blob_service_client.get_container_client(container_name)

    # Create the container if it doesn't exist
    try:
        container_client.create_container()
    except Exception as e:
        print(f"Container already exists or couldn't be created: {e}")

    # Walk through all files in the directory
    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            print(file_path)
            # Create a relative path for the blob
            relative_path = os.path.relpath(file_path, folder_path).replace(
                "\\", "/"
            )
            # Create a blob client
            blob_client = container_client.get_blob_client(relative_path)
            # Upload the file
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            print(f"Uploaded {relative_path} to Azure Blob Storage.")


if __name__ == "__main__":
    src_folder = args.step9_input
    # Upload the files to Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING = f"DefaultEndpointsProtocol=https;AccountName={args.target_storage_account_name};AccountKey={args.target_storage_api_key}"
    CONTAINER_NAME = f"{args.target_storage_container_name}"
    print(f"connection_string: {AZURE_STORAGE_CONNECTION_STRING}")
    print(f"container_name: {CONTAINER_NAME}")
    upload_files_to_blob(
        AZURE_STORAGE_CONNECTION_STRING, CONTAINER_NAME, src_folder
    )
