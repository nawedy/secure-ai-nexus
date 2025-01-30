#!/bin/bash
set -e

ENVIRONMENT=$1
BASE_URL="https://api-${ENVIRONMENT}.secureai.example.com"

echo "Running security tests for ${ENVIRONMENT} environment..."

# Install security testing tools
pip install owasp-zap-api-python requests safety

# Run OWASP ZAP scan
echo "Running OWASP ZAP scan..."
python - <<EOF
from zapv2 import ZAPv2
import time

target = "${BASE_URL}"
zap = ZAPv2()

# Spider the target
print('Spidering target...')
scan_id = zap.spider.scan(target)
while int(zap.spider.status(scan_id)) < 100:
    print('Spider progress: {}%'.format(zap.spider.status(scan_id)))
    time.sleep(5)

# Active scan
print('Active scanning target...')
scan_id = zap.ascan.scan(target)
while int(zap.ascan.status(scan_id)) < 100:
    print('Scan progress: {}%'.format(zap.ascan.status(scan_id)))
    time.sleep(5)

# Generate report
print('Generating report...')
with open('zap-report.html', 'w') as f:
    f.write(zap.core.htmlreport())
EOF

# Run SSL/TLS scan
echo "Running SSL/TLS scan..."
sslyze --regular "${BASE_URL}" --json_out ssl-report.json

# Check for security headers
echo "Checking security headers..."
python - <<EOF
import requests
import sys

headers = requests.get("${BASE_URL}").headers
required_headers = {
    'Strict-Transport-Security',
    'Content-Security-Policy',
    'X-Content-Type-Options',
    'X-Frame-Options',
    'X-XSS-Protection'
}

missing = required_headers - set(headers.keys())
if missing:
    print(f"Missing security headers: {missing}")
    sys.exit(1)
EOF

echo "Security tests completed successfully!"
