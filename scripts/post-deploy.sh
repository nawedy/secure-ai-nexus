#!/bin/bash
set -e

ENVIRONMENT=$1
BASE_URL="https://api-${ENVIRONMENT}.secureai.example.com"

echo "Running post-deployment checks for ${ENVIRONMENT}..."

# Health check
echo "Checking API health..."
health_status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/health")
if [ $health_status -ne 200 ]; then
    echo "Health check failed with status: ${health_status}"
    exit 1
fi

# Check monitoring
echo "Verifying monitoring setup..."
az monitor app-insights component show \
    --resource-group secureai-rg \
    --app secureai-app \
    --query 'instrumentationKey' \
    --output tsv

# Check security features
echo "Verifying security features..."
python - <<EOF
import requests
import sys

def check_security():
    # Check authentication
    try:
        r = requests.get("${BASE_URL}/secure")
        assert r.status_code == 401, "Authentication bypass possible!"
    except requests.exceptions.RequestException as e:
        print(f"Security check failed: {e}")
        sys.exit(1)

    # Check rate limiting
    responses = [requests.get("${BASE_URL}/health") for _ in range(100)]
    if all(r.status_code == 200 for r in responses):
        print("Rate limiting may not be properly configured!")
        sys.exit(1)

check_security()
EOF

echo "Post-deployment checks completed successfully!"
