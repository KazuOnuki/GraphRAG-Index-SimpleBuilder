"""
Summary:
This script downloads all `.md` (Markdown) files from an Azure Blob Storage container and renames them to `.txt` files.
The script connects to the specified Azure Blob Storage account using the provided credentials, retrieves the list of blobs in the specified container,
and downloads files with the `.md` extension. After downloading, it renames these files to `.txt` format, preparing them for further processing,
such as indexing by tools like GraphRAG.

Key functionalities:
1. **Azure Blob Storage Connection**:
    - The script connects to Azure Blob Storage using the provided account name and API key.
2. **File Download**:
    - It lists all blobs in the specified container and downloads those that have the `.md` extension into a local directory.
3. **File Renaming**:
    - Once downloaded, the script renames all `.md` files to `.txt` format, which is suitable for applications like GraphRAG that may require `.txt` inputs.

### Steps:
1. **Connection to Blob Storage**:
    - The script first establishes a connection to the Azure Blob Storage using `BlobServiceClient` and the provided account information.
2. **Listing and Downloading `.md` Files**:
    - It iterates over all blobs in the specified container, downloading any file that ends with `.md` into a local directory (`./test`). The directory is created if it doesn't already exist.
3. **Renaming Files**:
    - After downloading, the script renames each `.md` file to a `.txt` file by changing the file extension. This is typically done to support other processing tools that might require `.txt` files instead of `.md`.

### Usage:
- The script requires three command-line arguments:
    - `--storage_account_name`: Name of the Azure storage account.
    - `--storage_apikey`: The API key for accessing the storage account.
    - `--storage_container_name`: The name of the container from which the `.md` files are to be downloaded.

- After execution, all `.md` files from the specified container will be downloaded and renamed to `.txt`.

### Difference from step7.py and step6.py:
- **Focus on File Download and Conversion**:
   - Unlike **step6.py** and **step7.py**, this script focuses on **downloading** `.md` files from Azure Blob Storage and **renaming** them to `.txt`.
   - Step6.py processes files by filtering based on token count, and step7.py performs token analysis and visualization. This script handles **file retrieval** from Azure Blob Storage and prepares them for further use.
"""

import argparse
import os

from azure.storage.blob import BlobServiceClient

parser = argparse.ArgumentParser()
parser.add_argument("--storage_account_name", type=str)
parser.add_argument("--storage_apikey", type=str)
parser.add_argument("--storage_container_name", type=str)
print("Hello...\nI'm step8 :-)")
args = parser.parse_args()

# storage acccount info
storage_account_connection_string = f"DefaultEndpointsProtocol=https;AccountName={args.storage_account_name};AccountKey={args.storage_apikey};EndpointSuffix=core.windows.net"
container_name = f"{args.storage_container_name}"
local_download_path = "./test"

# create BlobServiceClient instance
blob_service_client = BlobServiceClient.from_connection_string(
    storage_account_connection_string
)
# get container client
container_client = blob_service_client.get_container_client(container_name)
# list all blobs in specified containers
blobs_list = container_client.list_blobs()
# download blob
for blob in blobs_list:
    if blob.name.endswith(".md"):
        blob_client = container_client.get_blob_client(blob)
        download_file_path = os.path.join(local_download_path, blob.name)
        # create new dir if no dir
        os.makedirs(os.path.dirname(download_file_path), exist_ok=True)
        print(f"Downloading {blob.name} to {download_file_path}...")
        # download file and save it to local
        with open(download_file_path, "wb") as download_file:
            download_data = blob_client.download_blob()
            download_file.write(download_data.readall())
        print(f"Downloaded {blob.name} to {download_file_path}.")
print("All .md files have been downloaded.")

# search files in local dirs
for root, dirs, files in os.walk(local_download_path):
    for file in files:
        if file.endswith(".md"):
            md_file_path = os.path.join(root, file)
            txt_file_path = os.path.join(
                root, file[:-3] + ".txt"
            )  # change .md to .txt for supporting graphrag index
            os.rename(md_file_path, txt_file_path)
            print(f"Renamed {md_file_path} to {txt_file_path}")
print("All .md files have been renamed to .txt.")
