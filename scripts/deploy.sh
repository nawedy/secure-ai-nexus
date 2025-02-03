#!/bin/bash
set -e

# Configuration
ENVIRONMENT=$1
VERSION=$2
NAMESPACE="secureai-${ENVIRONMENT}"

# Validate inputs
if [ -z "$ENVIRONMENT" ] || [ -z "$VERSION" ]; then
    echo "Usage: deploy.sh <environment> <version>"
    exit 1
fi

# Set GCP project
gcloud config set project secureai-nexus

# Build and push Docker image
docker build -t gcr.io/secureai-nexus/secureai-platform:${VERSION} .
docker push gcr.io/secureai-nexus/secureai-platform:${VERSION}

# Create namespace if it doesn't exist
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes configurations
kubectl apply -k k8s/overlays/${ENVIRONMENT}

# Wait for deployment
kubectl rollout status deployment/secureai-platform -n ${NAMESPACE}

echo "Deployment to ${ENVIRONMENT} complete"
