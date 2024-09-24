<#
Summary:
This PowerShell script automates the setup of an Azure Machine Learning (ML) environment, including necessary configurations, 
installation of required tools, and submission of an ML pipeline job using the Azure CLI. 
Here's a breakdown of the script's key tasks:

1. **Environment Variable Retrieval**:
  - The script retrieves various environment variables using the Azure Developer CLI (`azd env get-value`) command, such as:
    - Git repository URL and folder for sparse checkout.
    - Azure OpenAI Key, model names (GPT and embedding), and resource name.
    - Target storage account and container details.
    - Resource group, workspace, and compute instance/cluster names.

2. **Azure CLI Version Management**:
  - Ensures that the Azure CLI version is 2.59.0 and installs the Azure Machine Learning extension (`ml`) version 2.26.1 if not already installed. 
    The script removes any existing ML extension to avoid version conflicts.

3. **Python Virtual Environment Setup**:
  - A Python virtual environment is created using `python -m venv`, and required packages are installed (e.g., `setuptools`, `pydash`, `azure-ai-ml`, `azure-cli`)
    to ensure compatibility with Azure Machine Learning operations.

4. **ML Pipeline Job Creation**:
  - An Azure Machine Learning pipeline job is created using the Azure CLI command `az ml job create`. 
    This pipeline job takes several inputs, such as the Git URL, OpenAI API key, model names, and storage account details, 
      and it sets the default compute instance/cluster to be used in the job.
  - Inputs are passed dynamically using the `--set` flag for flexible configuration.

### Usage:
  - This script is ideal for setting up and submitting an Azure Machine Learning pipeline job with predefined configurations. 
    It can be used to automate the deployment of machine learning workflows that require interaction with various Azure resources.

### Requirements:
  - The script assumes that the Azure CLI is installed and configured with the correct version, along with necessary permissions to create 
      and manage ML jobs and interact with other Azure resources (storage, compute).

### Assumptions:
  - Environment variables are pre-set using Azure Developer CLI (`azd`) to ensure smooth execution.
#>


# get azd env
$gitURL = azd env get-value gitURL
$gitSparceCheckOutFolder = azd env get-value gitSparceCheckOutFolder

$oaiKey = azd env get-value oaiKey
$gptModelName = azd env get-value gptModelName
$embeddingModelName = azd env get-value embeddingModelName
$oaiName = azd env get-value oaiName
$targetStorageName = azd env get-value targetStorageName
$targetStorageContainer = azd env get-value targetStorageContainer
$targetStorageApiKey = azd env get-value targetStorageApiKey
$rgName = azd env get-value rgName
$workspaceName = azd env get-value workspaceName
$ciName = azd env get-value ciName
$ccName = azd env get-value ccName

$graphragStorageName = azd env get-value graphragStorageName
$graphragStorageApiKey = azd env get-value graphragStorageApiKey
$graphragStorageContainer = azd env get-value graphragStorageContainer

# azure cli version should be 2.59.0
# ML extention install
######################
# {
#   "azure-cli": "2.59.0",
#   "azure-cli-core": "2.59.0",
#   "azure-cli-telemetry": "1.1.0",
#   "extensions": {
#     "ml": "2.26.1"
#   }
# }
az extension remove -n azure-cli-ml
az extension add -n ml --version 2.26.1
######################


python -m venv .venv
.\.venv\Scripts\activate
######################
# if you don't have it, please install it.
pip install setuptools
pip install pydash
pip install azure-ai-ml==1.19.0
pip install azure-cli==2.59
######################

# create ML Pipeline Job
az ml job create --file './scripts/mlpipeline/pipeline.yaml' `
  --set inputs.pipeline_input_git_url=$gitURL `
  --set inputs.pipeline_input_sparse_checkout_folder=$gitSparceCheckOutFolder `
  --set inputs.pipeline_input_aoai_apikey=$oaiKey `
  --set inputs.pipeline_input_aoai_model=$gptModelName `
  --set inputs.pipeline_input_aoai_embedding_model=$embeddingModelName `
  --set inputs.pipeline_input_aoai_resource=$oaiName `
  --set inputs.pipeline_input_target_storage_account_name=$targetStorageName `
  --set inputs.pipeline_input_target_storage_container_name=$targetStorageContainer `
  --set inputs.pipeline_input_apikey=$targetStorageApiKey `
  --set inputs.pipeline_input_graphrag_storage_account_name=$graphragStorageName `
  --set inputs.pipeline_input_graphrag_storage_container_name=$graphragStorageContainer `
  --set inputs.pipeline_input_graphrag_apikey=$graphragStorageApiKey `
  --set settings.default_compute="azureml:$ccName" `
  --resource-group=$rgName `
  --workspace-name=$workspaceName