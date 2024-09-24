@description('Specifies the location for all resources.')
param location string

@description('Specifies the name of the Key Vault.')
param kv_name string

@description('Create Key Vault ref:https://learn.microsoft.com/en-us/azure/templates/microsoft.keyvault/2022-07-01/vaults?pivots=deployment-language-bice or https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.machinelearningservices/machine-learning-end-to-end-secure/modules/keyvault.bicep' )
resource keyvault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: kv_name
  location: location
  properties: {
    createMode: 'default'
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
    enableSoftDelete: true
    enableRbacAuthorization: true
    enablePurgeProtection: true
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Deny'
    }
    sku: {
      family: 'A'
      name: 'standard'
    }
    softDeleteRetentionInDays: 7
    tenantId: subscription().tenantId
  }
}

output keyvaultId string = keyvault.id
