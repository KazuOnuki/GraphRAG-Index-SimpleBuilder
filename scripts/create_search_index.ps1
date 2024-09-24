<#
This Script IS NOT USED for this project
#>

$access_token = (az account get-access-token --scope "https://search.azure.com/.default" --query accessToken -o tsv)
$api_key = azd env get-value searchServiceApiKey
$search_service_name = azd env get-value searchServiceName
$api_version = "2024-05-01-Preview"
$index_name = azd env get-value searchServiceIndexName
$datasource_name = "${index_name}-datasource"
$semantic_configuration_name = "${index_name}-semantic-configuration"
$algorithm_name = "${index_name}-algorithm"
$profile_name = "${index_name}-azureOpenAi-text-profile"
$vectorizer_name = "${index_name}-azureOpenAi-text-vectorizer"
$skillset_name = "${index_name}-skillset"
$indexer_name = "${index_name}-indexer"
$storage_account_name = azd env get-value targetStorageName
$storage_account_key = azd env get-value targetStorageApiKey
$container_name = azd env get-value targetStorageContainer
$azure_openai_resource_uri = "https://$(azd env get-value oaiName).openai.azure.com/"
$deployment_id = azd env get-value EMBEDDING_DEPLOYMENT_NAME
$azure_openai_api_key = azd env get-value oaiKey
$model_name = azd env get-value EMBEDDING_MODEL_NAME

# create Data Source
Invoke-RestMethod -Uri "https://${search_service_name}.search.windows.net/datasources?api-version=${api_version}" `
  -Method Post `
  -Headers @{
    "api-key" = $api_key
    "authorization" = "Bearer $access_token"
    "content-type" = "application/json"
  } `
  -Body (@{
    "name" = $datasource_name
    "type" = "azureblob"
    "credentials" = @{
      "connectionString" = "DefaultEndpointsProtocol=https;AccountName=${storage_account_name};AccountKey=${storage_account_key};EndpointSuffix=core.windows.net"
    }
    "container" = @{
      "name" = $container_name
    }
  } | ConvertTo-Json -Depth 10)

# Create Index
Invoke-RestMethod -Uri "https://${search_service_name}.search.windows.net/indexes?api-version=${api_version}" `
  -Method Post `
  -Headers @{
    "api-key" = $api_key
    "authorization" = "Bearer $access_token"
    "content-type" = "application/json"
  } `
  -Body (@{
    "name" = $index_name
    "fields" = @(
      @{ "name" = "chunk_id"; "type" = "Edm.String"; "key" = $true; "filterable" = $true; "sortable" = $true; "facetable" = $true; "analyzer" = "keyword" }
      @{ "name" = "parent_id"; "type" = "Edm.String"; "filterable" = $true; "sortable" = $true; "facetable" = $true }
      @{ "name" = "chunk"; "type" = "Edm.String"; "filterable" = $false; "sortable" = $false; "facetable" = $false }
      @{ "name" = "title"; "type" = "Edm.String"; "filterable" = $true; "sortable" = $false; "facetable" = $false }
      @{ "name" = "text_vector"; "type" = "Collection(Edm.Single)"; "retrievable" = $true; "stored" = $true; "searchable" = $true; "dimensions" = 1536; "vectorSearchProfile" = $profile_name }
    )
    "semantic" = @{
      "defaultConfiguration" = $semantic_configuration_name
      "configurations" = @(
        @{
          "name" = $semantic_configuration_name
          "prioritizedFields" = @{
            "titleField" = @{ "fieldName" = "title" }
            "prioritizedContentFields" = @(@{ "fieldName" = "chunk" })
          }
        }
      )
    }
    "vectorSearch" = @{
      "algorithms" = @(@{ "name" = $algorithm_name; "kind" = "hnsw" })
      "profiles" = @(
        @{
          "name" = $profile_name
          "algorithm" = $algorithm_name
          "vectorizer" = $vectorizer_name
        }
      )
      "vectorizers" = @(
        @{
          "name" = $vectorizer_name
          "kind" = "azureOpenAI"
          "azureOpenAIParameters" = @{
            "resourceUri" = $azure_openai_resource_uri
            "deploymentId" = $deployment_id
            "apiKey" = $azure_openai_api_key
            "modelName" = $model_name
          }
        }
      )
    }
  } |  ConvertTo-Json -Depth 10)

# Create SKillset
Invoke-RestMethod -Uri "https://${search_service_name}.search.windows.net/skillsets?api-version=${api_version}" `
  -Method Post `
  -Headers @{
    "api-key" = $api_key
    "authorization" = "Bearer $access_token"
    "content-type" = "application/json"
  } `
  -Body (@{
    "name" = $skillset_name
    "description" = "Skillset to chunk documents and generate embeddings"
    "skills" = @(
      @{
        "@odata.type" = "#Microsoft.Skills.Text.SplitSkill"
        "description" = "Split skill to chunk documents"
        "context" = "/document"
        "inputs" = @(@{ "name" = "text"; "source" = "/document/content" })
        "outputs" = @(@{ "name" = "textItems"; "targetName" = "pages" })
        "textSplitMode" = "pages"
        "maximumPageLength" = 2000
        "pageOverlapLength" = 0
      },
      @{
        "@odata.type" = "#Microsoft.Skills.Text.AzureOpenAIEmbeddingSkill"
        "context" = "/document/pages/*"
        "modelName" = $model_name
        "inputs" = @(@{ "name" = "text"; "source" = "/document/pages/*" })
        "outputs" = @(@{ "name" = "embedding"; "targetName" = "text_vector" })
        "resourceUri" = $azure_openai_resource_uri
        "deploymentId" = $deployment_id
        "apiKey" = $azure_openai_api_key
      }
    )
    "indexProjections" = @{
      "selectors" = @(
        @{
          "targetIndexName" = $index_name
          "parentKeyFieldName" = "parent_id"
          "sourceContext" = "/document/pages/*"
          "mappings" = @(
            @{ "name" = "text_vector"; "source" = "/document/pages/*/text_vector" }
            @{ "name" = "chunk"; "source" = "/document/pages/*" }
            @{ "name" = "title"; "source" = "/document/title" }
          )
        }
      )
      "parameters" = @{
        "projectionMode" = "skipIndexingParentDocuments"
      }
    }
  } | ConvertTo-Json -Depth 10)

# Create Indexer
Invoke-RestMethod -Uri "https://${search_service_name}.search.windows.net/indexers?api-version=${api_version}" `
  -Method Post `
  -Headers @{
    "api-key" = $api_key
    "authorization" = "Bearer $access_token"
    "content-type" = "application/json"
  } `
  -Body (@{
    "name" = $indexer_name
    "dataSourceName" = $datasource_name
    "skillsetName" = $skillset_name
    "targetIndexName" = $index_name
    "schedule" = @{
      "interval" = "PT1H"
      "startTime" = $null
    }
    "parameters" = @{
      "configuration" = @{
        "dataToExtract" = "contentAndMetadata"
        "parsingMode" = "default"
      }
    }
    "fieldMappings" = @(
      @{ "sourceFieldName" = "metadata_storage_name"; "targetFieldName" = "title" }
    )
  } | ConvertTo-Json -Depth 10)
