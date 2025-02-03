#!/bin/bash
set -e

ENVIRONMENT=$1
NAMESPACE="secureai-${ENVIRONMENT}"

echo "Running comprehensive deployment verification..."

# 1. Check pods status
echo "Checking pod status..."
kubectl get pods -n $NAMESPACE
kubectl describe pods -n $NAMESPACE | grep -A 5 Events:

# 2. Check service status
echo "Checking service status..."
kubectl get service secureai-platform -n $NAMESPACE
kubectl describe service secureai-platform -n $NAMESPACE

# 3. Check logs for errors
echo "Checking application logs..."
kubectl logs -l app=secureai-platform -n $NAMESPACE --tail=100

# 4. Check endpoints
echo "Checking endpoints..."
SERVICE_IP=$(kubectl get service secureai-platform -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -v "http://${SERVICE_IP}:8080/health"
curl -v "http://${SERVICE_IP}:8080/metrics"

# 5. Check monitoring
echo "Checking monitoring setup..."
kubectl get pods -n monitoring
kubectl get services -n monitoring

# 6. Verify Prometheus metrics
echo "Checking Prometheus metrics..."
PROMETHEUS_POD=$(kubectl get pods -n monitoring -l app=prometheus -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward -n monitoring $PROMETHEUS_POD 9090:9090 &
sleep 5
curl -s "http://localhost:9090/api/v1/targets" | jq '.data.activeTargets[] | select(.labels.job=="secureai-platform")'

# 7. Check alerts
echo "Checking alerting rules..."
kubectl get configmap -n monitoring prometheus-rules -o yaml

# 8. Verify resource usage
echo "Checking resource usage..."
kubectl top pods -n $NAMESPACE
