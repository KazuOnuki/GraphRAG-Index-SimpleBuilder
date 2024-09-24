@description('Specifies the location for all resources.')
param location string

@description('Specifies the name of the container registry.')
param cr_name string

@description('Create Container Registry ref:https://learn.microsoft.com/en-us/azure/templates/microsoft.containerregistry/2022-12-01/registries?pivots=deployment-language-bicep or https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.machinelearningservices/machine-learning-end-to-end-secure/modules/containerregistry.bicep')
resource containerregistry 'Microsoft.ContainerRegistry/registries@2022-12-01' = {
  name: cr_name
  location: location
  sku: {
    name: 'Premium'
  }
  properties: {
    adminUserEnabled: true
    policies: {
      quarantinePolicy: {
        status: 'disabled'
      }
      retentionPolicy: {
        days: 7
        status: 'disabled'
      }
      trustPolicy: {
        status: 'disabled'
        type: 'Notary'
      }
    }
    publicNetworkAccess: 'Enabled'
  }
}

output containerRegistryId string = containerregistry.id
