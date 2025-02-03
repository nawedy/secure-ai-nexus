# Restore System Troubleshooting Guide

## Quick Diagnostics

### Health Check
```bash
# Check system status
restore-cli status

# Verify service health
curl -X GET https://api.secureai.com/health
```

### Common Status Codes
| Code | Meaning | Action Required |
|------|---------|----------------|
| 200 | Healthy | None |
| 503 | Service Unavailable | Check system resources |
| 429 | Rate Limited | Reduce request frequency |
| 507 | Insufficient Storage | Free up disk space |

## Common Issues & Solutions

### 1. Restore Operation Fails

#### Symptoms
- Restore operation returns error status
- Incomplete database restoration
- Verification failures

#### Diagnostic Steps
1. Check logs:
```bash
# View recent restore logs
tail -f /var/log/secureai/restore.log

# Check error logs
grep ERROR /var/log/secureai/restore.log
```

2. Verify system resources:
```bash
# Check disk space
df -h

# Check memory usage
free -m

# Check CPU usage
top
```

3. Verify database connectivity:
```bash
# Test PostgreSQL connection
psql -h $DB_HOST -U $DB_USER -d postgres -c "SELECT 1"
```

#### Solutions
1. **Insufficient Space**
```bash
# Clean up old backups
restore-cli cleanup --older-than 7d

# Expand disk space
kubectl scale pvc postgres-data --size=100Gi
```

2. **Database Connection Issues**
```bash
# Verify credentials
echo $DB_PASSWORD | psql -h $DB_HOST -U $DB_USER

# Check PostgreSQL logs
kubectl logs deployment/postgres
```

3. **Resource Constraints**
```bash
# Scale up resources
kubectl patch deployment secureai-restore -p '{"spec":{"resources":{"limits":{"memory":"2Gi"}}}}'
```

### 2. Backup Verification Failures

#### Symptoms
- Checksum mismatch
- Corrupt backup files
- Incomplete backups

#### Diagnostic Steps
1. Verify backup integrity:
```bash
# Check backup checksum
restore-cli verify backup_name.sql.gz

# List backup details
restore-cli list-backups --format=json
```

2. Check storage connectivity:
```python
from google.cloud import storage
client = storage.Client()
bucket = client.bucket(BACKUP_BUCKET)
blob = bucket.blob('backup_name.sql.gz')
print(f"Exists: {blob.exists()}, Size: {blob.size}")
```

#### Solutions
1. **Corrupt Backup**
```bash
# Restore from previous backup
restore-cli restore --backup-name previous_backup.sql.gz --target-db restored_db

# Verify backup contents
pg_restore --list backup_name.sql.gz
```

2. **Storage Issues**
```bash
# Verify GCS permissions
gcloud auth list
gcloud projects get-iam-policy $PROJECT_ID

# Test storage access
gsutil ls gs://$BACKUP_BUCKET
```

### 3. Performance Issues

#### Symptoms
- Slow restore operations
- High latency
- Timeouts

#### Diagnostic Steps
1. Monitor metrics:
```bash
# Check restore duration
curl -X GET https://api.secureai.com/metrics | grep restore_duration

# View current operations
restore-cli status --verbose
```

2. Check system performance:
```bash
# Monitor IO operations
iostat -x 1

# Check network performance
iperf -c $DB_HOST
```

#### Solutions
1. **Slow Restore Operations**
```bash
# Increase parallel workers
restore-cli restore --parallel-workers=8 backup_name.sql.gz

# Optimize PostgreSQL settings
kubectl apply -f k8s/configs/postgres-performance.yaml
```

2. **Network Issues**
```bash
# Test network latency
ping $DB_HOST

# Check network policies
kubectl get networkpolicies
```

### 4. Monitoring & Alerting Issues

#### Symptoms
- Missing alerts
- False positives
- Delayed notifications

#### Diagnostic Steps
1. Verify Prometheus configuration:
```bash
# Check Prometheus targets
curl -X GET http://prometheus:9090/api/v1/targets

# View alert rules
kubectl get prometheusrules -n monitoring
```

2. Check AlertManager:
```bash
# View alert status
curl -X GET http://alertmanager:9093/api/v1/alerts

# Check configuration
kubectl get configmap alertmanager-config -n monitoring -o yaml
```

#### Solutions
1. **Missing Alerts**
```yaml
# Update alert rules
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: restore-alerts
spec:
  groups:
  - name: restore.rules
    rules:
    - alert: RestoreFailure
      expr: increase(restore_failure_total[1h]) > 0
```

2. **Alert Configuration**
```bash
# Reload AlertManager
curl -X POST http://alertmanager:9093/-/reload

# Verify receivers
kubectl get secret alertmanager-notifications -o yaml
```

## Advanced Troubleshooting

### Database Analysis
```sql
-- Check restore progress
SELECT pid, query, state
FROM pg_stat_activity
WHERE query LIKE '%restore%';

-- Monitor locks
SELECT relation::regclass, mode, granted
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid;
```

### System Diagnostics
```bash
# Full system analysis
restore-cli diagnose --full

# Generate diagnostic report
restore-cli report --output=diagnostic_report.json
```

### Recovery Procedures

#### Emergency Restore
```bash
# Force stop current operations
restore-cli cancel-all

# Emergency restore with minimal verification
restore-cli restore --emergency --skip-verify backup_name.sql.gz
```

#### Data Recovery
```bash
# Attempt partial restore
pg_restore --data-only --table=critical_table backup_name.sql.gz

# Extract specific objects
pg_restore --list backup_name.sql.gz | grep table_name
```

## Preventive Measures

### Regular Maintenance
1. Schedule regular verifications:
```bash
# Add to crontab
0 0 * * * restore-cli verify-all --report
```

2. Monitor resource usage:
```bash
# Set up resource quotas
kubectl apply -f k8s/quotas/restore-resources.yaml
```

### Best Practices
1. Regular testing:
```bash
# Test restore procedure
restore-cli test-restore --sample-size=10MB

# Validate backup integrity
restore-cli verify-all --thorough
```

2. Documentation:
```bash
# Generate system report
restore-cli document --output=system_documentation.md

# Update runbooks
restore-cli update-runbooks
```
