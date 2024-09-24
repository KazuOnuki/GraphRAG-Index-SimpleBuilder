targetScope = 'subscription'
// Load abbreviations from JSON file
var abbrs = loadJsonContent('abbreviations.json')
// UtcNow datetime > use it for generate Suffix
param baseTime string = utcNow('u')

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string


@allowed([
  'https://github.com/MicrosoftDocs/azure-ai-docs.git'
])
@description('Select PullTarget Git Repo URL')
param gitURL string

// gitSparseCheckoutFolder
@allowed([
  'articles/ai-services/openai'
  'articles/machine-learning'
])
@description('Select git Sparse Checkout Folder')
param gitSparseCheckoutFolder string


// Tags that should be applied to all resources.
// Note that 'azd-service-name' tags should be applied separately to service host resources.
// Example usage:
//   tags: union(tags, { 'azd-service-name': <service name in azure.yaml> })
var tags = {
  'azd-env-name': environmentName
}

resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}


// ====================================================================================================
// Ref: https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.machinelearningservices/machine-learning-end-to-end-secure/main.bicep
// AZURE MACHINE LEARENING RELATED RESOURCES
// ====================================================================================================
// Variables
var name = toLower('${environmentName}')
// Create a short, unique suffix, that will be unique to each resource group
var uniqueSuffix = substring(uniqueString(rg.id, environmentName, baseTime), 0, 5)

// Dependent resources for the Azure Machine Learning workspace
module keyvault 'core/ml/kv.bicep' = {
  scope: rg
  name: 'kv-${name}-${uniqueSuffix}'
  params: {
    location: location
    kv_name: 'kv-${name}-${uniqueSuffix}'
  }
}

module storage 'core/ml/storage.bicep' = {
  scope: rg
  name: 'st${name}${uniqueSuffix}'
  params: {
    location: location
    storage_name: 'st${name}${uniqueSuffix}'
  }
}

module containerRegistry 'core/ml/cr.bicep' = {
  scope: rg
  name: 'cr${name}${uniqueSuffix}'
  params: {
    location: location
    cr_name: 'cr${name}${uniqueSuffix}'
  }
}

module applicationInsights 'core/ml/ainsight.bicep' = {
  scope: rg
  name: 'ainsight-${name}-${uniqueSuffix}'
  params: {
    location: location
    ai_name: 'appi-${name}-${uniqueSuffix}'
  }
}

module azuremlWorkspace 'core/ml/workspace.bicep' = {
  scope: rg
  name: 'mlw-${name}-${uniqueSuffix}'
  params: {
    // workspace organization
    workspace_name: 'mlw-${name}-${uniqueSuffix}'
    location: location
    // dependent resources
    applicationInsightsId: applicationInsights.outputs.applicationInsightsId
    containerRegistryId: containerRegistry.outputs.containerRegistryId
    keyVaultId: keyvault.outputs.keyvaultId
    storageAccountId: storage.outputs.storageId
  }
  dependsOn: [
    keyvault
    containerRegistry
    applicationInsights
    storage
  ]
}

module computeInstance 'core/ml/computeinstance.bicep' = {
  scope: rg
  name: 'ci-${name}-${uniqueSuffix}'
  params: {
    // compute organization
    compute_name: 'ci-${name}-${uniqueSuffix}'
    location: location
    // dependent resources
    workspaceName: azuremlWorkspace.outputs.machineLearningName
  }
  dependsOn: [
    azuremlWorkspace
  ]
}

module computeCluster 'core/ml/computecluster.bicep' = {
  scope: rg
  name: 'cc-${name}-${uniqueSuffix}'
  params: {
    // compute organization
    compute_name: 'cc-${name}-${uniqueSuffix}'
    location: location
    // dependent resources
    workspaceName: azuremlWorkspace.outputs.machineLearningName
  }
  dependsOn: [
    azuremlWorkspace
  ]
}


// ====================================================================================================
// AZURE AI Search and Storage
// ====================================================================================================
// Parameters for Storage Account
param storageAccountName string = ''
// Parameters for Azure AI Search Service configuration
// param searchServiceName string = ''
// param searchServiceResourceGroupLocation string = location
// param searchServiceSkuName string = ''

// Configure Azure Cognitive Search service
// module searchService 'core/search/search.bicep' = {
//   name: 'search-${name}-${uniqueSuffix}'
//   scope: rg
//   params: {
//     name: !empty(searchServiceName) ? searchServiceName : 'search-${name}-${uniqueSuffix}'
//     location: searchServiceResourceGroupLocation
//     tags: tags
//     authOptions: {
//       aadOrApiKey: {
//         aadAuthFailureMode: 'http401WithBearerChallenge'
//       }
//     }
//     sku: {
//       name: !empty(searchServiceSkuName) ? searchServiceSkuName : 'standard'
//     }
//     semanticSearch: 'free'
//   }
// }

// Storage Account
module searchStorage 'core/search/searchstorage.bicep' = {
  name: 'searchsto${name}${uniqueSuffix}'
  scope: rg
  params: {
    name: !empty(storageAccountName) ? storageAccountName : 'searchsto${name}${uniqueSuffix}'
    location: location
    tags: tags
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowCrossTenantReplication: true
    allowSharedKeyAccess: true
    defaultToOAuthAuthentication: false
    deleteRetentionPolicy: {}
    dnsEndpointType: 'Standard'
    kind: 'StorageV2'
    minimumTlsVersion: 'TLS1_2'
    publicNetworkAccess: 'Enabled'
    sku: {
      name: 'Standard_LRS'
    }
    containers: [
      {
        name: 'data'
        publicAccess: 'None'
      }
    ]
  }
}

// ====================================================================================================
// AZURE Open AI
// ====================================================================================================
// Parameters for Azure OpenAI Service configuration
param openAiResourceName string = 'oai-dev-test'
param openAiResourceLocation string = 'eastus2'
param openAiSkuName string = 'S0'
param openAIModel string = 'gpt-4o'
param openAIModelName string = 'gpt-4o'
param openAIModelVersion string = '2024-08-06'
param embeddingDeploymentName string = 'text-embedding-3-large'
param embeddingModelName string = 'text-embedding-3-large'
param embeddingModelVersion string = '1'


// Configure OpenAI service
//// ${uniqueSuffix}'
module openAi 'core/oai/cognitiveservices.bicep' = {
  name: 'openai'
  scope: rg
  params: {
    name: !empty(openAiResourceName) ? openAiResourceName : replace('oai-${name}-${uniqueSuffix}', '/', '')
    location: !empty(openAiResourceLocation) ? openAiResourceLocation : 'eastus2'
    tags: tags
    sku: {
      name: !empty(openAiSkuName) ? openAiSkuName : 'S0'
    }
    deployments: [
      {
        name: !empty(openAIModel) ? openAIModel : 'gpt-4o'
        model: {
          format: 'OpenAI'
          name: !empty(openAIModelName) ? openAIModelName : 'gpt-4o'
          version: !empty(openAIModelVersion) ? openAIModelVersion : '2024-08-06'
        }
        capacity: 150
      }
      {
        name: !empty(embeddingDeploymentName) ? embeddingDeploymentName : 'text-embedding-3-large'
        model: {
          format: 'OpenAI'
          name: !empty(embeddingModelName) ? embeddingModelName : 'text-embedding-3-large'
          version: !empty(embeddingModelVersion) ? embeddingModelVersion : '1'
        }
        capacity: 240
      }
    ]
  }
}


// ====================================================================================================
// GRAPHRAG Storage
// ====================================================================================================
// Parameters for Storage Account
param graphragstorageAccountName string = ''

// Storage Account
module graphragStorage 'core/graphrag/graphragstorage.bicep' = {
  name: 'graphragsto${name}${uniqueSuffix}'
  scope: rg
  params: {
    name: !empty(graphragstorageAccountName) ? graphragstorageAccountName : 'graphragsto${name}${uniqueSuffix}'
    location: location
    tags: tags
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowCrossTenantReplication: true
    allowSharedKeyAccess: true
    defaultToOAuthAuthentication: false
    deleteRetentionPolicy: {}
    dnsEndpointType: 'Standard'
    kind: 'StorageV2'
    minimumTlsVersion: 'TLS1_2'
    publicNetworkAccess: 'Enabled'
    sku: {
      name: 'Standard_LRS'
    }
    containers: [
      {
        name: 'data'
        publicAccess: 'None'
      }
    ]
  }
}


// PullTarget Git URL
output gitURL string = gitURL
output gitSparceCheckOutFolder string = gitSparseCheckoutFolder


output workspaceName string = azuremlWorkspace.name
output ciName string = computeInstance.name
output ccName string = computeCluster.name
output rgName string = rg.name
output srcStorageName string = storage.name
output targetStorageName string = searchStorage.name
output targetStorageApiKey string = searchStorage.outputs.storageApiKey
output targetStorageContainer string = 'data'
// output searchServiceName string = searchService.name
// output searchServiceApiKey string = searchService.outputs.adminKey
output searchServiceIndexName string = 'idx-${name}-${uniqueSuffix}'
output oaiName string = openAi.outputs.name
output oaiKey string = openAi.outputs.oaiKey
output gptModelName string = openAi.outputs.gptModelName
output embeddingModelName string = openAi.outputs.embeddingModelName

output graphragStorageName string = graphragStorage.name
output graphragStorageApiKey string = graphragStorage.outputs.storageApiKey
output graphragStorageContainer string = 'graphdata'
