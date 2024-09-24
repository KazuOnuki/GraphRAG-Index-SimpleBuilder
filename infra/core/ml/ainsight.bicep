@description('Specifies the location for all resources.')
param location string

@description('Specifies the name of the Application Insights.')
param ai_name string

@description('Create LogAnalytics Workspace ref:https://learn.microsoft.com/en-us/azure/templates/microsoft.operationalinsights/workspaces?pivots=deployment-language-bicep or https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.machinelearningservices/machine-learning-end-to-end-secure/modules/applicationinsights.bicep' )
resource LogAnaWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${ai_name}loganaws'
  location: location
  properties: {
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Disabled'
    retentionInDays: 30
    sku: {
      name: 'PerGB2018'
    }
  }
}

@description('Create Application Insights ref:https://learn.microsoft.com/en-us/azure/templates/microsoft.insights/components?pivots=deployment-language-bicep')
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: ai_name
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: LogAnaWorkspace.id
    Flow_Type: 'Bluefield'
  }
}

output applicationInsightsId string = applicationInsights.id
