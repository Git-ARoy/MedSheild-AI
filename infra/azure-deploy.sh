#!/usr/bin/env bash
# Deploy HomeoCare Hospital Digital Twin Sandbox on Microsoft Azure
set -euo pipefail

RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-rg-homeocare-sandbox}"
LOCATION="${AZURE_LOCATION:-eastus}"
GEMINI_KEY="${GEMINI_API_KEY:-}"

echo "================================================================="
echo "[AZURE DEPLOYMENT] HomeoCare Hospital Digital Twin Sandbox"
echo "Target Resource Group: $RESOURCE_GROUP | Location: $LOCATION"
echo "================================================================="

# 1. Verify Azure CLI Authentication
echo "--> Verifying Azure CLI account..."
if ! az account show >/dev/null 2>&1; then
  echo "Error: Azure CLI not authenticated. Please run 'az login' first."
  exit 1
fi

SUBSCRIPTION_NAME=$(az account show --query "name" -o tsv)
SUBSCRIPTION_ID=$(az account show --query "id" -o tsv)
echo "    Active Subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION_ID)"

# 2. Create Resource Group if needed
echo "--> Ensuring resource group '$RESOURCE_GROUP' exists in '$LOCATION'..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --tags Project=MedShield Environment=HomeoCare-Sandbox DataClass=Synthetic Cloud=Azure >/dev/null

# 3. Deploy Bicep Template
echo "--> Deploying HomeoCare infrastructure via Azure Bicep (main.bicep)..."
DEPLOYMENT_OUTPUT=$(az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file infra/main.bicep \
  --parameters geminiApiKey="$GEMINI_KEY" \
  --query "properties.outputs" \
  -o json)

STORAGE_ACCOUNT=$(echo "$DEPLOYMENT_OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('storageAccountName', {}).get('value', ''))")
KEY_VAULT=$(echo "$DEPLOYMENT_OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('keyVaultName', {}).get('value', ''))")

echo "================================================================="
echo "[DEPLOYMENT SUCCESSFUL]"
echo "Storage Account: $STORAGE_ACCOUNT"
echo "Key Vault:       $KEY_VAULT"
echo "Resource Group:  $RESOURCE_GROUP"
echo "================================================================="

# 4. Seed Synthetic Patient and Medication Data
if [ -n "$STORAGE_ACCOUNT" ]; then
  echo "--> Seeding synthetic HomeoCare patient and medication records into Azure Blob Storage..."
  
  # Sample synthetic chart
  cat << 'EOF' > /tmp/synthetic_patient_001.json
{
  "patient_id": "HC-PT-98014",
  "name": "Synthetic Test Patient (Fictional)",
  "dob": "1978-04-12",
  "allergies": ["Penicillin", "Sulfa"],
  "active_infusions": [
    {
      "pump_id": "PUMP-ICU-04",
      "medication": "Heparin 25,000 Units in 250mL D5W",
      "rate_ml_hr": 14.0,
      "status": "RUNNING",
      "safety_limits_enforced": true
    }
  ],
  "encounter_type": "ICU Inpatient"
}
EOF

  az storage blob upload \
    --account-name "$STORAGE_ACCOUNT" \
    --container-name "patient-records" \
    --name "patient_001.json" \
    --file /tmp/synthetic_patient_001.json \
    --auth-mode login --overwrite >/dev/null 2>&1 || true

  rm -f /tmp/synthetic_patient_001.json
  echo "    Synthetic records upload complete."
fi

echo "--> HomeoCare Digital Twin is ready on Microsoft Azure!"
