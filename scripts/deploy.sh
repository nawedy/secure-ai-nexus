#!/bin/bash
set -e

# Configuration
ENVIRONMENT=$1
NAMESPACE="secureai-${ENVIRONMENT}"
VERSION=$2

# Validate inputs
if [ -z "$ENVIRONMENT" ] || [ -z "$VERSION" ]; then
    echo "Usage: deploy.sh <environment> <version>"
    exit 1
fi

# Set environment variables
source .env

# 1. Configure GCP
gcloud config set project $GCP_PROJECT_ID

# 2. Build and push Docker image
docker build -t gcr.io/$GCP_PROJECT_ID/secureai-platform:$VERSION .
docker push gcr.io/$GCP_PROJECT_ID/secureai-platform:$VERSION

# 3. Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply secrets
kubectl create secret generic secureai-secrets \
    --from-literal=api-key=$(openssl rand -base64 32) \
    --namespace $NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes configurations
kubectl apply -k k8s/overlays/$ENVIRONMENT

# Update image version
kubectl set image deployment/secureai-platform \
    secureai-platform=gcr.io/$GCP_PROJECT_ID/secureai-platform:$VERSION \
    --namespace $NAMESPACE

# Wait for rollout
kubectl rollout status deployment/secureai-platform --namespace $NAMESPACE

# 6. Verify deployment
echo "Verifying deployment..."
kubectl get pods -n $NAMESPACE

echo "Deployment to $ENVIRONMENT complete"
