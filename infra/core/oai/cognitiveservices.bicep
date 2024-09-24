// AOAI account name
param name string
param location string = ''
param tags object = {}
param customSubDomainName string = name
param deployments array = []
param kind string = 'OpenAI'
param publicNetworkAccess string = 'Enabled'
param sku object = {
  name: 'S0' // default is S0
}
// Create AOAI Resource
resource account 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: replace(name, '/', '') // Resource Name
  location: location // Resource Location
  tags: tags // Tag
  kind: kind // Service Kind
  properties: {
    customSubDomainName: customSubDomainName // Custom Sub Domain Name
    publicNetworkAccess: publicNetworkAccess // Settings of public network access
  }
  sku: sku // SKU Info
}

// Model Deployment Resource Info
@batchSize(1)
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [for deployment in deployments: {
  parent: account // Model Deployment Parent AOAI Resource Account
  name: deployment.name // Each Deployment Name
  properties: {
    model: deployment.model // Model Deploymen Name
    raiPolicyName: deployment.?raiPolicyName ?? null
  }
  sku: {
    name: 'Standard' // Deployment Sku
    capacity: deployment.capacity // Deployment Capacity (TPM)
  }
}]

// Output Parameter
output endpoint string = account.properties.endpoint  // Created AOAI Endpoint
output id string = account.id                         // Account ID
output name string = account.name                     // AOAI Resource Name
output skuName string = account.sku.name              // AOAI Resource SKU
output oaiKey string = account.listKeys().key1        // AOAI API Key

// output Deployment Name at index
output gptModelName string = deployment[0].name
output embeddingModelName string = deployment[1].name
