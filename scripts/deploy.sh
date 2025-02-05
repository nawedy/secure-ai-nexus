#!/bin/bash
set -e

# Configuration
ENVIRONMENT="${1}"
VERSION="${2}"
NAMESPACE="secureai-nexus-${ENVIRONMENT}"
IMAGE_NAME="gcr.io/secureai-nexus/secureai-platform"

# Validate inputs
if [[ -z "${ENVIRONMENT}" || -z "${VERSION}" ]]; then
  echo "Usage: deploy.sh <environment> <version>"
  exit 1
fi

# Set GCP project
gcloud config set project secureai-nexus

# Authenticate Docker
gcloud auth configure-docker

# Build and push Docker image
docker build -t "${IMAGE_NAME}:${VERSION}" .
docker push "${IMAGE_NAME}:${VERSION}"

# Create namespace if it doesn't exist
kubectl get namespace "${NAMESPACE}" > /dev/null 2>&1 || kubectl create namespace "${NAMESPACE}"

# Deploy application
sed -i "s|IMAGE_PLACEHOLDER|${IMAGE_NAME}:${VERSION}|g" k8s/overlays/${ENVIRONMENT}/deployment-patch.yaml
kubectl apply -k k8s/overlays/${ENVIRONMENT} -n "${NAMESPACE}"

#remove the image placeholder
sed -i "s|${IMAGE_NAME}:${VERSION}|IMAGE_PLACEHOLDER|g" k8s/overlays/${ENVIRONMENT}/deployment-patch.yaml

# Verify deployment

# Wait for deployment
kubectl rollout status deployment/secureai-platform -n ${NAMESPACE}

echo "Deployment to ${ENVIRONMENT} complete"
