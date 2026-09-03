@description('Primary Azure region for HomeoCare resources')
param location string = resourceGroup().location

@description('Target environment label')
param environment string = 'HomeoCare-Sandbox'

@description('Google Gemini API Key stored securely in Azure Key Vault')
@secure()
param geminiApiKey string = ''

var uniqueSuffix = toLower(uniqueString(resourceGroup().id))
var baseTags = {
  Project: 'MedShield'
  Environment: environment
  DataClass: 'Synthetic'
  Cloud: 'Azure'
}

// 1. Central Log Analytics Workspace for telemetry
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'law-homeocare-${uniqueSuffix}'
  location: location
  tags: baseTags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// 2. Azure Storage Account (Blobs for synthetic EHR/Prescriptions, Tables for incident metadata)
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: take('sthomeocare${uniqueSuffix}', 24)
  location: location
  tags: baseTags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource patientRecordsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'patient-records'
  properties: {
    publicAccess: 'None'
  }
}

resource medicationStateContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'medication-state'
  properties: {
    publicAccess: 'None'
  }
}

// 3. Azure Key Vault for confidential credential management
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: take('kv-homeo-${uniqueSuffix}', 24)
  location: location
  tags: baseTags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
  }
}

resource geminiSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'gemini-api-key'
  properties: {
    value: geminiApiKey
  }
}

// 4. Network Security Groups for Clinical and DMZ segmentation
resource nsgDmz 'Microsoft.Network/networkSecurityGroups@2023-05-01' = {
  name: 'nsg-dmz'
  location: location
  tags: baseTags
  properties: {
    securityRules: [
      {
        name: 'Allow-HTTPS-Inbound'
        properties: {
          priority: 200
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
    ]
  }
}

resource nsgClinical 'Microsoft.Network/networkSecurityGroups@2023-05-01' = {
  name: 'nsg-clinical'
  location: location
  tags: baseTags
  properties: {
    securityRules: [
      {
        name: 'Allow-Internal-VNet-Only'
        properties: {
          priority: 300
          direction: 'Inbound'
          access: 'Allow'
          protocol: '*'
          sourceAddressPrefix: 'VirtualNetwork'
          sourcePortRange: '*'
          destinationAddressPrefix: 'VirtualNetwork'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

// 5. Azure Virtual Network with segmented clinical and DMZ subnets
resource vnet 'Microsoft.Network/virtualNetworks@2023-05-01' = {
  name: 'vnet-homeocare'
  location: location
  tags: baseTags
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
    subnets: [
      {
        name: 'snet-dmz'
        properties: {
          addressPrefix: '10.0.1.0/24'
          networkSecurityGroup: {
            id: nsgDmz.id
          }
        }
      }
      {
        name: 'snet-clinical'
        properties: {
          addressPrefix: '10.0.2.0/24'
          networkSecurityGroup: {
            id: nsgClinical.id
          }
        }
      }
      {
        name: 'snet-device'
        properties: {
          addressPrefix: '10.0.3.0/24'
          networkSecurityGroup: {
            id: nsgClinical.id
          }
        }
      }
    ]
  }
}

output resourceGroupName string = resourceGroup().name
output storageAccountName string = storageAccount.name
output keyVaultName string = keyVault.name
output logAnalyticsWorkspaceId string = logAnalytics.properties.customerId
output vnetName string = vnet.name
output patientRecordsContainerUrl string = '${storageAccount.properties.primaryEndpoints.blob}patient-records'
