# SecureAI Platform MVP Deployment Guide

## Pre-Deployment Checklist

### 1. Required Azure Resources
- [ ] Azure Subscription
- [ ] Azure AD Admin access
- [ ] Resource creation permissions
- [ ] Domain for deployment

### 2. Local Environment Setup
- [ ] Python 3.9+
- [ ] Docker
- [ ] Azure CLI
- [ ] kubectl
- [ ] Git

## Step 1: Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/nawedy/secure-ai-nexus
   cd secure-ai-nexus
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Log in to Azure:
   ```bash
   az login
   # Verify login
   az account show
   ```

## Step 2: Azure Resource Setup

1. Create Resource Group:
   ```bash
   export RG_NAME="secureai-rg"
   export LOCATION="eastus"

   az group create \
     --name $RG_NAME \
     --location $LOCATION
   ```

2. Create Service Principal:
   ```bash
   # Create and capture service principal details
   SP_OUTPUT=$(az ad sp create-for-rbac \
     --name "secureai-nexus-sp" \
     --role contributor \
     --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RG_NAME")

   # Save these values securely - you'll need them later
   echo $SP_OUTPUT | jq .

   # Set environment variables
   export AZURE_CLIENT_ID=$(echo $SP_OUTPUT | jq -r .appId)
   export AZURE_CLIENT_SECRET=$(echo $SP_OUTPUT | jq -r .password)
   export AZURE_TENANT_ID=$(echo $SP_OUTPUT | jq -r .tenant)
   ```

3. Create Key Vault:
   ```bash
   export KV_NAME="secureai-kv-$(openssl rand -hex 4)"

   az keyvault create \
     --name $KV_NAME \
     --resource-group $RG_NAME \
     --location $LOCATION \
     --sku Premium

   # Grant service principal access
   az keyvault set-policy \
     --name $KV_NAME \
     --spn $AZURE_CLIENT_ID \
     --secret-permissions get list set delete \
     --key-permissions get list create delete
   ```

## Step 3: Security Configuration

1. Create initial API key and store in Key Vault:
   ```bash
   # Generate secure API key
   API_KEY=$(openssl rand -base64 32)

   # Store in Key Vault
   az keyvault secret set \
     --vault-name $KV_NAME \
     --name "api-key" \
     --value $API_KEY
   ```

2. Create environment file:
   ```bash
   cat > .env << EOF
   AZURE_TENANT_ID=$AZURE_TENANT_ID
   AZURE_CLIENT_ID=$AZURE_CLIENT_ID
   AZURE_CLIENT_SECRET=$AZURE_CLIENT_SECRET
   AZURE_KEY_VAULT_URL=https://$KV_NAME.vault.azure.net/
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   EOF
   ```

## Step 4: Container Setup

1. Build Docker image:
   ```bash
   # Create Azure Container Registry
   export ACR_NAME="secureainexus"

   az acr create \
     --resource-group $RG_NAME \
     --name $ACR_NAME \
     --sku Standard

   # Build and push image
   az acr build \
     --registry $ACR_NAME \
     --image secureai-platform:latest .
   ```

## Step 5: Kubernetes Deployment

1. Create AKS cluster:
   ```bash
   export CLUSTER_NAME="secureai-aks"

   az aks create \
     --resource-group $RG_NAME \
     --name $CLUSTER_NAME \
     --node-count 2 \
     --enable-managed-identity \
     --attach-acr $ACR_NAME

   # Get credentials
   az aks get-credentials \
     --resource-group $RG_NAME \
     --name $CLUSTER_NAME
   ```

2. Deploy application:
   ```bash
   # Create namespace
   kubectl create namespace secureai

   # Create secrets
   kubectl create secret generic azure-credentials \
     --namespace secureai \
     --from-literal=tenant-id=$AZURE_TENANT_ID \
     --from-literal=client-id=$AZURE_CLIENT_ID \
     --from-literal=client-secret=$AZURE_CLIENT_SECRET

   # Deploy base components
   kubectl apply -k k8s/base/
   ```

## Step 6: Verification

1. Check deployment status:
   ```bash
   # Check pods
   kubectl get pods -n secureai

   # Check services
   kubectl get services -n secureai
   ```

2. Test API:
   ```bash
   # Get external IP
   export SERVICE_IP=$(kubectl get service secureai-platform -n secureai -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

   # Test health endpoint
   curl http://$SERVICE_IP:8000/health
   ```

## Common Issues & Solutions

### Pod Startup Issues
```bash
# Check pod details
kubectl describe pod <pod-name> -n secureai

# Check logs
kubectl logs <pod-name> -n secureai
```

### Key Vault Access Issues
```bash
# Verify Key Vault access
az keyvault secret list --vault-name $KV_NAME
```

### Image Pull Issues
```bash
# Verify ACR access
az aks check-acr \
  --resource-group $RG_NAME \
  --name $CLUSTER_NAME \
  --acr $ACR_NAME.azurecr.io
```

## Next Steps
1. Set up monitoring
2. Configure backups
3. Enable SSL/TLS
4. Set up CI/CD pipeline
