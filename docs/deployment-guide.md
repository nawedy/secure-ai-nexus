# SecureAI Platform Deployment Guide
Version 1.0 | January 2025

## Table of Contents
1. Prerequisites
2. Initial Setup
3. Deployment Steps
4. Verification
5. Troubleshooting
6. Maintenance

## 1. Prerequisites

### 1.1 Required Tools
- kubectl (v1.24+)
- gcloud CLI (latest version)
- Docker (20.10+)
- Python 3.9+
- Git

### 1.2 Access Requirements
- GCP Project Admin access
- GitHub repository access
- Docker registry access

### 1.3 Environment Setup
```bash
# Install required tools
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Configure Docker
gcloud auth configure-docker
```

## 2. Initial Setup

### 2.1 Clone Repository
```bash
git clone https://github.com/your-org/secureai-platform.git
cd secureai-platform
```

### 2.2 Configure Environment
```bash
# Create environment file
cp .env.example .env

# Generate API key
export API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "API_KEY=$API_KEY" >> .env

# Configure GCP project
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID
```

## 3. Deployment Steps

### 3.1 Infrastructure Setup
```bash
# Create GKE cluster
gcloud container clusters create secureai-cluster \
    --machine-type=n1-standard-4 \
    --num-nodes=3 \
    --zone=us-east1-b \
    --cluster-version=latest \
    --enable-autoscaling \
    --min-nodes=3 \
    --max-nodes=10

# Configure kubectl
gcloud container clusters get-credentials secureai-cluster --zone=us-east1-b

# Create namespaces
kubectl create namespace secureai-prod
kubectl create namespace secureai-staging
```

### 3.2 Deploy Core Components
```bash
# Apply base configurations
kubectl apply -k k8s/base

# Deploy monitoring stack
kubectl apply -k k8s/monitoring

# Deploy backup system
kubectl apply -k k8s/backup

# Configure scaling
kubectl apply -k k8s/scaling
```

### 3.3 Deploy Application
```bash
# Build and push Docker image
docker build -t ghcr.io/your-org/secureai-platform:latest .
docker push ghcr.io/your-org/secureai-platform:latest

# Deploy application
kubectl apply -f k8s/base/deployment.yaml
kubectl apply -f k8s/base/service.yaml
```

## 4. Verification

### 4.1 Check Deployment Status
```bash
# Verify pods are running
kubectl get pods -n secureai-prod

# Check services
kubectl get services -n secureai-prod

# Verify ingress
kubectl get ingress -n secureai-prod
```

### 4.2 Test API
```bash
# Test health endpoint
curl https://api.secureai.example.com/health

# Test model endpoint
curl -X POST https://api.secureai.example.com/generate \
     -H "X-API-Key: $API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"text": "Test prompt", "model_name": "deepseek"}'
```

## 5. Troubleshooting

### 5.1 Common Issues

#### Pods Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n secureai-prod

# Check logs
kubectl logs <pod-name> -n secureai-prod
```

#### Model Loading Issues
```bash
# Check model service logs
kubectl logs -l app=secureai-platform -n secureai-prod -c model-service

# Verify storage
kubectl describe pvc model-cache-pvc -n secureai-prod
```

### 5.2 Monitoring Alerts
- Access Grafana dashboard: https://monitoring.secureai.example.com
- Check Prometheus alerts: https://alerts.secureai.example.com

## 6. Maintenance

### 6.1 Backup Verification
```bash
# Check backup status
kubectl get cronjob backup-verification -n secureai-prod
kubectl get job -n secureai-prod | grep backup-verification
```

### 6.2 Updates and Upgrades
```bash
# Update application
./scripts/deploy.sh prod v1.0.1

# Update infrastructure
gcloud container clusters upgrade secureai-cluster --master --cluster-version=1.25
```

### 6.3 Scaling
```bash
# Check HPA status
kubectl get hpa -n secureai-prod

# Manual scaling (if needed)
kubectl scale deployment secureai-platform --replicas=5 -n secureai-prod
``` 