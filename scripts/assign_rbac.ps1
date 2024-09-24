<#
Summary:
This PowerShell script manages role assignments for Azure Managed Identities related to Azure Machine Learning (ML) workspaces and their associated storage accounts. 
The script performs the following key tasks:

1. **Retrieve Workspace and Storage Account Information**:
    - It fetches the workspace name from the Azure Developer CLI environment.
    - It retrieves the Managed Identity IDs associated with the compute resources of the specified ML workspace.
    - It gets the Resource IDs for both the source and target storage accounts specified in the Azure Developer CLI environment.

2. **Check and Assign Role Permissions**:
    - The script checks whether the "Storage Blob Data Owner" role is assigned to each Managed Identity for both the source and target storage accounts.
    - If a Managed Identity does not have the role assigned for either storage account, the script assigns the "Storage Blob Data Owner" role to that Managed Identity.

3. **Role Assignment Logic**:
    - The role assignment is verified using Azure CLI commands, and if an assignment does not exist, it creates one. 
        The script outputs messages indicating whether a role assignment was created or already exists for each Managed Identity.

### Usage:
- The script is useful for ensuring that Managed Identities associated with an Azure ML workspace have the appropriate access permissions to Azure Storage accounts.
    This is critical for enabling seamless data access for machine learning operations.

### Requirements:
    - The script relies on Azure CLI (az) commands to retrieve and assign role information. 
        Ensure that you have the Azure CLI installed and configured with appropriate permissions to run these commands.

### Assumptions:
- The script assumes that the required environment variables (like `workspaceName`, `srcStorageName`, `targetStorageName`, and `rgName`) 
    are properly set in the Azure Developer CLI environment before execution.
#>


$workspaceName = azd env get-value workspaceName
# get specified MLWorkspace Compute Managed ID
$managed_identity_ids = az ad sp list --all --filter "servicePrincipalType eq 'ManagedIdentity'" --query "[?contains(displayName, '$workspaceName/computes')].id" -o tsv
# get specified MLWorkspace associated Storage Account Resource ID
$src_storage_account_name = azd env get-value srcStorageName
$src_resource_group_name = azd env get-value rgName
$src_storage_account_id = az storage account show --name $src_storage_account_name --resource-group $src_resource_group_name --query "id" -o tsv

# get targeted Storage Account Resource.
$target_storage_account_name = azd env get-value targetStorageName
$target_resource_group_name = azd env get-value rgName
$target_storage_account_id = az storage account show --name $target_storage_account_name --resource-group $target_resource_group_name --query "id" -o tsv

# Check "Storage Blob Data Owner" Assignment on targeted managed identity. if no assignment, assign it to MLWorkspace ComputeInstance/Cluster ManagedID.
foreach ($id in $managed_identity_ids -split "`n") {
    $role_assignment_src = az role assignment list --assignee $id --role "Storage Blob Data Owner" --scope $src_storage_account_id
    if ($role_assignment_src -eq "[]") {
        Write-Output "No existing role assignment for $id in source storage, creating role assignment..."
        az role assignment create --assignee $id --role "Storage Blob Data Owner" --scope $src_storage_account_id
    } else {
        Write-Output "Role assignment already exists for $id in source storage."
    }

    $role_assignment_target = az role assignment list --assignee $id --role "Storage Blob Data Owner" --scope $target_storage_account_id
    if ($role_assignment_target -eq "[]") {
        Write-Output "No existing role assignment for $id in target storage, creating role assignment..."
        az role assignment create --assignee $id --role "Storage Blob Data Owner" --scope $target_storage_account_id
    } else {
        Write-Output "Role assignment already exists for $id in target storage."
    }
}
