#!/bin/bash
set -e

# Azure Configuration
RESOURCE_GROUP="secureai-rg"
LOCATION="eastus"
KEY_VAULT_NAME="secureai-kv"
APP_NAME="secureai-app"
ACR_NAME="secureairegistry"

# Create Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Key Vault
az keyvault create \
    --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku standard

# Create Azure Container Registry
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Standard

# Build and push Docker image
az acr build --registry $ACR_NAME --image secureai:latest .

# Create App Service Plan
az appservice plan create \
    --name "${APP_NAME}-plan" \
    --resource-group $RESOURCE_GROUP \
    --sku P1V2 \
    --is-linux

# Create Web App
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan "${APP_NAME}-plan" \
    --name $APP_NAME \
    --deployment-container-image-name "${ACR_NAME}.azurecr.io/secureai:latest"

# Configure Web App settings
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    AZURE_TENANT_ID="<tenant-id>" \
    AZURE_CLIENT_ID="<client-id>" \
    AZURE_KEY_VAULT_URL="https://${KEY_VAULT_NAME}.vault.azure.net/" \
    WEBSITES_PORT=8000

# Enable managed identity
az webapp identity assign \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME

# Get the managed identity ID
IDENTITY_ID=$(az webapp identity show --resource-group $RESOURCE_GROUP --name $APP_NAME --query principalId --output tsv)

# Grant Key Vault access
az keyvault set-policy \
    --name $KEY_VAULT_NAME \
    --object-id $IDENTITY_ID \
    --secret-permissions get list set delete \
    --key-permissions get list create delete

echo "Deployment complete!"
