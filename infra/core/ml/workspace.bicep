@description('Specifies the location for all resources.')
param location string

@description('Specifies the name of the workspace.')
param workspace_name string

@description('Resource ID of the application insights resource')
param applicationInsightsId string

@description('Resource ID of the container registry resource')
param containerRegistryId string

@description('Resource ID of the key vault resource')
param keyVaultId string

@description('Resource ID of the storage account resource')
param storageAccountId string

@description('Create Workspace ref: https://learn.microsoft.com/en-us/azure/templates/microsoft.machinelearningservices/2022-10-01/workspaces?pivots=deployment-language-bicep#workspaces or https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.machinelearningservices/machine-learning-end-to-end-secure/modules/machinelearning.bicep')
resource workspace 'Microsoft.MachineLearningServices/workspaces@2022-10-01' = {
  name: workspace_name
  location: location
  sku: {
    family: 'A'
    name: 'standard'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    allowPublicAccessWhenBehindVnet: true
    applicationInsights: applicationInsightsId
    containerRegistry: containerRegistryId
    keyVault: keyVaultId
    storageAccount: storageAccountId
    publicNetworkAccess: 'Enabled'
    description: '<this is description here>'
    friendlyName: workspace_name
    v1LegacyMode: false
  }
}

output machineLearningId string = workspace.id
output machineLearningName string = workspace.name
