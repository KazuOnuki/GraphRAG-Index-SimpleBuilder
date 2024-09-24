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
    computeType: 'AmlCompute'
    computeLocation: location
    description: 'Machine Learning compute cluster'
    properties: {
      scaleSettings: {
        maxNodeCount: 5
        minNodeCount: 1
        nodeIdleTimeBeforeScaleDown: 'PT120S'
      }
      vmSize: 'Standard_D13_v2'
    }
  }
}
