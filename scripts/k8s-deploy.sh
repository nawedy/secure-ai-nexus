#!/bin/bash
set -e

ENVIRONMENT=$1
VERSION=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$VERSION" ]; then
    echo "Usage: k8s-deploy.sh <environment> <version>"
    exit 1
fi

# Validate environment
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo "Environment must be either 'staging' or 'production'"
    exit 1
fi

echo "Deploying version $VERSION to $ENVIRONMENT..."

# Update kustomization.yaml with new image version
cd k8s/overlays/$ENVIRONMENT
kustomize edit set image secureairegistry.azurecr.io/secureai-platform:$VERSION

# Apply configurations
kubectl apply -k .

# Wait for rollout
kubectl -n secureai-$ENVIRONMENT rollout status deployment/secureai-platform

# Verify deployment
kubectl -n secureai-$ENVIRONMENT get pods

echo "Deployment to $ENVIRONMENT complete!"
