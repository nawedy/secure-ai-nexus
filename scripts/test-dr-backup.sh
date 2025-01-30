#!/bin/bash
set -e

echo "Starting backup and DR test..."

# Test backup creation
echo "Creating test backup..."
velero backup create test-backup \
    --include-namespaces secureai \
    --wait

# Verify backup
echo "Verifying backup..."
velero backup describe test-backup
velero backup logs test-backup

# Test restore in DR environment
echo "Testing restore in DR environment..."
velero restore create test-restore \
    --from-backup test-backup \
    --namespace-mappings secureai:secureai-dr \
    --wait

# Verify restore
echo "Verifying restore..."
kubectl -n secureai-dr get all
kubectl -n secureai-dr get pods

# Clean up
echo "Cleaning up test resources..."
velero backup delete test-backup
kubectl delete namespace secureai-dr

echo "Backup and DR test completed successfully!"
