// Creates compute resources in the specified machine learning workspace
@description('Azure region of the deployment')
param location string
@description('Name for the workspace resource name')
param workspaceName string
@description('Name for the compute resource name')
param compute_name string

resource machineLearningComputeInstance 'Microsoft.MachineLearningServices/workspaces/computes@2022-10-01' = {
  name:'${workspaceName}/${compute_name}'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    computeType: 'ComputeInstance'
    computeLocation: location
    description: 'Machine Learning compute instance'
    disableLocalAuth: true
    properties: {
      applicationSharingPolicy: 'Personal'
      computeInstanceAuthorizationType: 'personal'
      sshSettings: {
        sshPublicAccess: 'Disabled'
      }
      vmSize: 'Standard_DS11_v2'
    }
  }
}
