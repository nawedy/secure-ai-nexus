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

# Create namespace if it doesn't exist
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
    secureai-platform=ghcr.io/your-repo/secureai-platform:$VERSION \
    --namespace $NAMESPACE

# Wait for rollout
kubectl rollout status deployment/secureai-platform --namespace $NAMESPACE

echo "Deployment to $ENVIRONMENT complete" 