# GCP Deployment Troubleshooting Guide

## Authentication Issues

### Service Account Permissions
1. Check current permissions:
   ```bash
   # List service account roles
   gcloud projects get-iam-policy secureai-nexus \
     --flatten="bindings[].members" \
     --format='table(bindings.role)' \
     --filter="bindings.members:secureai-nexus@secureai-nexus.iam.gserviceaccount.com"
   ```

2. Verify required roles:
   ```bash
   # Add necessary roles if missing
   gcloud projects add-iam-policy-binding secureai-nexus \
     --member="serviceAccount:secureai-nexus@secureai-nexus.iam.gserviceaccount.com" \
     --role="roles/run.admin"

   gcloud projects add-iam-policy-binding secureai-nexus \
     --member="serviceAccount:secureai-nexus@secureai-nexus.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   ```

### Docker Authentication
1. Check Docker configuration:
   ```bash
   # View Docker config
   cat ~/.docker/config.json

   # Reconfigure Docker auth
   gcloud auth configure-docker
   ```

2. Test Docker access:
   ```bash
   # Try pulling a test image
   docker pull gcr.io/secureai-nexus/secureai-platform:latest

   # Check Docker daemon logs
   docker system info
   ```

### Secret Manager Access
1. Verify access:
   ```bash
   # Test secret access
   gcloud secrets versions access latest --secret=api-key

   # List accessible secrets
   gcloud secrets list
   ```

2. Fix permissions:
   ```bash
   # Grant Secret Manager access
   gcloud secrets add-iam-policy-binding api-key \
     --member="serviceAccount:secureai-nexus@secureai-nexus.iam.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

## Deployment Issues

### Cloud Run Logs
1. View deployment logs:
   ```bash
   # Get recent logs
   gcloud logging read "resource.type=cloud_run_revision" \
     --project=secureai-nexus \
     --limit=50

   # Stream logs in real-time
   gcloud logging tail "resource.type=cloud_run_revision" \
     --project=secureai-nexus
   ```

2. Common log issues:
   - Memory limits exceeded
   - Container startup timeout
   - Missing environment variables

### Container Health
1. Check container status:
   ```bash
   # View revision status
   gcloud run revisions list \
     --service=secureai-platform \
     --platform=managed \
     --region=us-central1

   # Get detailed revision info
   gcloud run revisions describe REVISION_NAME \
     --platform=managed \
     --region=us-central1
   ```

2. Test locally:
   ```bash
   # Build and run locally
   docker build -t secureai-local .
   docker run -p 8080:8080 secureai-local

   # Check container logs
   docker logs CONTAINER_ID
   ```

### Resource Allocation
1. Review current allocation:
   ```bash
   # Check service configuration
   gcloud run services describe secureai-platform \
     --platform=managed \
     --region=us-central1

   # View resource usage
   gcloud monitoring metrics list \
     --filter="metric.type=contains(\"cloud_run\")"
   ```

2. Adjust resources:
   ```bash
   # Update service resources
   gcloud run services update secureai-platform \
     --memory=1Gi \
     --cpu=1 \
     --platform=managed \
     --region=us-central1
   ```

## Quick Fixes

### Authentication Quick Fixes
```bash
# Regenerate service account key
gcloud iam service-accounts keys create new-key.json \
  --iam-account=secureai-nexus@secureai-nexus.iam.gserviceaccount.com

# Reset Docker authentication
docker logout gcr.io
gcloud auth configure-docker
```

### Deployment Quick Fixes
```bash
# Rollback to previous revision
gcloud run services rollback secureai-platform \
  --platform=managed \
  --region=us-central1

# Force new deployment
gcloud run deploy secureai-platform \
  --image=gcr.io/secureai-nexus/secureai-platform:latest \
  --platform=managed \
  --region=us-central1 \
  --no-traffic
```

### Resource Quick Fixes
```bash
# Scale up resources temporarily
gcloud run services update secureai-platform \
  --memory=2Gi \
  --cpu=2 \
  --concurrency=80 \
  --platform=managed \
  --region=us-central1

# Clear container cache
docker system prune -a
```

## Preventive Measures

### Regular Checks
1. Service health monitoring:
   ```bash
   # Create uptime check
   gcloud monitoring uptime-check-configs create http-check \
     --display-name="API Health Check" \
     --http-check-path="/health" \
     --period=300s
   ```

2. Resource monitoring:
   ```bash
   # Set up resource alerts
   gcloud monitoring channels create \
     --display-name="Resource Alerts" \
     --type=email \
     --email-address=alerts@secureai-nexus.com
   ```

### Automated Testing
1. Configure CI/CD tests:
   ```bash
   # Add to cloudbuild.yaml
   steps:
   - name: 'gcr.io/cloud-builders/docker'
     args: ['build', '-t', 'gcr.io/$PROJECT_ID/secureai-platform', '.']
   - name: 'gcr.io/cloud-builders/docker'
     args: ['run', 'gcr.io/$PROJECT_ID/secureai-platform', 'pytest']
   ```

## Emergency Procedures

### Service Outage
1. Check status:
   ```bash
   # View service status
   gcloud run services describe secureai-platform \
     --platform=managed \
     --region=us-central1
   ```

2. Emergency rollback:
   ```bash
   # List revisions
   gcloud run revisions list \
     --service=secureai-platform \
     --platform=managed \
     --region=us-central1

   # Rollback to last known good revision
   gcloud run services update-traffic secureai-platform \
     --to-revisions=REVISION_NAME=100 \
     --platform=managed \
     --region=us-central1
   ```

## Additional Troubleshooting Scenarios

### DNS and Domain Issues
1. Check DNS propagation:
   ```bash
   # Verify DNS records
   dig secureai.eriethio.com

   # Check Cloud DNS zone
   gcloud dns managed-zones describe eriethio

   # List DNS records
   gcloud dns record-sets list --zone=eriethio
   ```

2. SSL/TLS Issues:
   ```bash
   # Check certificate status
   gcloud certificate-manager certificates describe secureai-cert

   # Force certificate renewal
   gcloud certificate-manager certificates update secureai-cert \
     --domains="secureai.eriethio.com"
   ```

### Network Connectivity
1. Test internal connectivity:
   ```bash
   # Test from within Cloud Run
   gcloud run services describe secureai-platform \
     --platform=managed \
     --region=us-central1 \
     --format='get(status.url)' | xargs curl -v

   # Check VPC connector status
   gcloud compute networks vpc-access connectors describe secureai-connector \
     --region=us-central1
   ```

2. External access issues:
   ```bash
   # Check Cloud Armor rules
   gcloud compute security-policies describe secureai-policy

   # View blocked requests
   gcloud logging read "resource.type=cloud_armor_security_policy" \
     --project=secureai-nexus
   ```

## Enhanced Emergency Procedures

### Security Incidents
1. Immediate response:
   ```bash
   # Enable emergency lockdown
   gcloud run services update secureai-platform \
     --no-allow-unauthenticated \
     --platform=managed \
     --region=us-central1

   # Block all external traffic
   gcloud compute security-policies rules create 1 \
     --security-policy=secureai-policy \
     --description="Emergency block" \
     --action=deny-403
   ```

2. Incident investigation:
   ```bash
   # Export security logs
   gcloud logging read "severity>=WARNING" \
     --project=secureai-nexus \
     --format="csv(timestamp,resource.type,severity,textPayload)" \
     > security_incident_logs.csv

   # Check authentication attempts
   gcloud logging read "resource.type=cloud_run_revision AND textPayload=~\"authentication\"" \
     --project=secureai-nexus
   ```

### Data Recovery
1. Backup verification:
   ```bash
   # List available backups
   gsutil ls gs://secureai-backups/

   # Verify backup integrity
   gsutil stat gs://secureai-backups/latest.backup

   # Test restore in isolation
   gcloud run services clone secureai-platform \
     --from-revision=REVISION \
     --to-revision=recovery-test \
     --platform=managed \
     --region=us-central1
   ```

2. Emergency restore:
   ```bash
   # Restore from backup
   gsutil cp gs://secureai-backups/latest.backup ./
   gcloud run services update secureai-platform \
     --image=gcr.io/secureai-nexus/secureai-platform:backup \
     --platform=managed \
     --region=us-central1
   ```

## Advanced Monitoring Configuration

### Custom Metrics
1. Set up custom metrics:
   ```bash
   # Create custom metric descriptor
   gcloud monitoring metrics descriptors create \
     custom.googleapis.com/secureai/model_latency \
     --description="Model inference latency" \
     --metric-kind=gauge \
     --value-type=double \
     --unit=ms

   # Create dashboard
   gcloud monitoring dashboards create \
     --config-from-file=dashboard-config.yaml
   ```

2. Advanced alerting:
   ```bash
   # Create multi-condition alert
   gcloud monitoring alert-policies create \
     --display-name="Critical System Alert" \
     --condition-filter="resource.type=\"cloud_run_revision\" AND (metric.type=\"custom.googleapis.com/secureai/model_latency\" OR metric.type=\"run.googleapis.com/request_count\")" \
     --condition-threshold-duration=300s \
     --condition-threshold-value=1000 \
     --notification-channels="projects/$PROJECT_ID/notificationChannels/$CHANNEL_ID"
   ```

### Performance Monitoring
1. Load testing configuration:
   ```bash
   # Set up load test
   gcloud beta run jobs create load-test \
     --image=gcr.io/secureai-nexus/load-tester \
     --tasks=100 \
     --max-retries=3

   # Monitor performance
   gcloud monitoring metrics list \
     --filter="metric.type=contains(\"latency\")" \
     | grep "run.googleapis.com"
   ```

2. Resource utilization:
   ```bash
   # CPU monitoring
   gcloud monitoring metrics list \
     --filter="metric.type=contains(\"cpu\")" \
     | grep "run.googleapis.com"

   # Memory tracking
   gcloud monitoring metrics list \
     --filter="metric.type=contains(\"memory\")" \
     | grep "run.googleapis.com"
   ```

### Automated Response Actions
1. Configure auto-scaling:
   ```bash
   # Set up auto-scaling policy
   gcloud run services update secureai-platform \
     --min-instances=2 \
     --max-instances=10 \
     --platform=managed \
     --region=us-central1

   # Configure scaling metrics
   gcloud run services update secureai-platform \
     --cpu-throttling \
     --concurrency=80 \
     --platform=managed \
     --region=us-central1
   ```

2. Automated incident response:
   ```bash
   # Create incident response function
   gcloud functions deploy incident-response \
     --runtime python39 \
     --trigger-topic=security-alerts \
     --entry-point=handle_incident

   # Set up alert routing
   gcloud monitoring channels create \
     --display-name="Incident Response" \
     --type=pubsub \
     --pubsub-topic=projects/$PROJECT_ID/topics/security-alerts
   ```

## Model-Specific Troubleshooting

### Model Loading Issues
1. Memory problems:
   ```bash
   # Check memory usage
   gcloud monitoring metrics list \
     --filter="metric.type=contains(\"memory\")" \
     | grep "run.googleapis.com"

   # Increase memory allocation
   gcloud run services update secureai-platform \
     --memory=4Gi \
     --platform=managed \
     --region=us-central1
   ```

2. Model initialization failures:
   ```bash
   # Check model loading logs
   gcloud logging read "resource.type=cloud_run_revision AND textPayload=~\"model.*initialization\"" \
     --project=secureai-nexus

   # Verify model artifacts
   gsutil ls gs://secureai-nexus-models/
   gsutil stat gs://secureai-nexus-models/latest/
   ```

### Inference Performance
1. Latency monitoring:
   ```bash
   # Create latency alert
   gcloud monitoring alert-policies create \
     --display-name="High Inference Latency" \
     --condition-filter="metric.type=\"custom.googleapis.com/secureai/inference_latency\" AND metric.labels.model_name=\"deepseek\"" \
     --duration=5m \
     --threshold-value=1000
   ```

2. GPU utilization:
   ```bash
   # Monitor GPU usage
   gcloud monitoring metrics list \
     --filter="metric.type=contains(\"gpu\")" \
     | grep "run.googleapis.com"
   ```

## Cost Optimization

### Resource Usage Analysis
1. Cost monitoring:
   ```bash
   # Set up budget alert
   gcloud billing budgets create \
     --billing-account=$BILLING_ACCOUNT_ID \
     --display-name="Monthly Budget" \
     --budget-amount=1000 \
     --threshold-rules=percent=0.8

   # View current costs
   gcloud billing accounts get-spend-information \
     --billing-account=$BILLING_ACCOUNT_ID
   ```

2. Resource optimization:
   ```bash
   # Identify unused resources
   gcloud asset search-all-resources \
     --scope=projects/$PROJECT_ID \
     --query="state:INACTIVE"

   # Clean up unused resources
   gcloud container images list-tags gcr.io/$PROJECT_ID/secureai-platform \
     --filter="NOT tags:*" --format="get(digest)" | \
     xargs -I {} gcloud container images delete "gcr.io/$PROJECT_ID/secureai-platform@{}" --quiet
   ```

## Enhanced Backup and Recovery

### Automated Backup Procedures
1. Set up scheduled backups:
   ```bash
   # Create backup schedule
   gcloud scheduler jobs create http backup-job \
     --schedule="0 */6 * * *" \
     --uri="https://secureai.eriethio.com/api/backup" \
     --http-method=POST \
     --headers="Authorization=Bearer ${API_KEY}"

   # Configure backup retention
   gsutil lifecycle set backup-lifecycle.json gs://secureai-backups/
   ```

2. Backup validation:
   ```bash
   # Verify backup contents
   gsutil cat gs://secureai-backups/latest/manifest.json

   # Test backup integrity
   gcloud run jobs create backup-verify \
     --image=gcr.io/secureai-nexus/backup-verifier \
     --args="--backup-path=gs://secureai-backups/latest/"
   ```

### Disaster Recovery Testing
1. Regular DR tests:
   ```bash
   # Create DR test environment
   gcloud run services clone secureai-platform \
     --from-revision=REVISION \
     --to-revision=dr-test \
     --platform=managed \
     --region=us-west1

   # Validate DR environment
   gcloud run services describe dr-test \
     --platform=managed \
     --region=us-west1
   ```

2. Failover procedures:
   ```bash
   # Update DNS for failover
   gcloud dns record-sets transaction start --zone=eriethio
   gcloud dns record-sets transaction remove secureai.eriethio.com. \
     --name=secureai.eriethio.com. \
     --type=A \
     --zone=eriethio
   gcloud dns record-sets transaction add DR_IP \
     --name=secureai.eriethio.com. \
     --type=A \
     --zone=eriethio
   gcloud dns record-sets transaction execute --zone=eriethio
   ```

## Security Compliance

### Audit Procedures
1. Regular security audits:
   ```bash
   # Export IAM policy
   gcloud projects get-iam-policy secureai-nexus \
     --format=json > iam-policy.json

   # Review audit logs
   gcloud logging read "protoPayload.methodName=google.iam" \
     --project=secureai-nexus \
     --format=json > iam-audit.json
   ```

2. Compliance monitoring:
   ```bash
   # Check security policies
   gcloud security policies list

   # Review security findings
   gcloud scc findings list \
     --organization=$ORG_ID \
     --filter="state=ACTIVE" \
     --format="table(category,severity,eventTime)"
   ```

### Access Review
1. Regular access review:
   ```bash
   # List service accounts
   gcloud iam service-accounts list

   # Review permissions
   for sa in $(gcloud iam service-accounts list --format="value(email)"); do
     echo "Reviewing $sa"
     gcloud projects get-iam-policy secureai-nexus \
       --flatten="bindings[].members" \
       --filter="bindings.members:$sa"
   done
   ```

2. Key rotation:
   ```bash
   # Rotate service account keys
   gcloud iam service-accounts keys create new-key.json \
     --iam-account=secureai-nexus@secureai-nexus.iam.gserviceaccount.com

   # Update secrets
   gcloud secrets versions add service-account-key \
     --data-file=new-key.json
   ```
[Previous sections remain the same...]

## API-Specific Troubleshooting

### Rate Limiting Issues
1. Check current limits:
   ```bash
   # View rate limit metrics
   gcloud monitoring metrics list \
     --filter="metric.type=contains(\"request_count\")" \
     | grep "run.googleapis.com"

   # Adjust rate limits
   gcloud run services update secureai-platform \
     --concurrency=80 \
     --max-instances=10 \
     --platform=managed \
     --region=us-central1
   ```

2. Monitor API usage:
   ```bash
   # Create usage dashboard
   gcloud monitoring dashboards create api-usage \
     --display-name="API Usage Dashboard" \
     --config-from-file=api-dashboard.yaml

   # Set up usage alerts
   gcloud monitoring alert-policies create \
     --display-name="High API Usage" \
     --condition-filter="resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" > 1000" \
     --duration=5m
   ```

### Model Performance Optimization

1. Batch processing setup:
   ```bash
   # Configure batch settings
   gcloud run services update secureai-platform \
     --set-env-vars="BATCH_SIZE=16,MAX_BATCH_LATENCY=100" \
     --platform=managed \
     --region=us-central1

   # Monitor batch performance
   gcloud monitoring metrics list \
     --filter="metric.type=contains(\"batch\")" \
     | grep "custom.googleapis.com"
   ```

2. Cache optimization:
   ```bash
   # Set up Cloud CDN
   gcloud compute backend-services update secureai-backend \
     --enable-cdn \
     --cdn-policy-cache-mode=CACHE_ALL_STATIC

   # Configure model caching
   gcloud run services update secureai-platform \
     --set-env-vars="ENABLE_MODEL_CACHE=true,CACHE_TTL=3600" \
     --platform=managed \
     --region=us-central1
   ```

### Advanced Security Measures

1. DDoS protection:
   ```bash
   # Configure Cloud Armor advanced rules
   gcloud compute security-policies rules create 2000 \
     --security-policy=secureai-policy \
     --expression="evaluatePreconfiguredExpr('xss-stable')" \
     --action=deny-403

   # Set up rate limiting
   gcloud compute security-policies rules create 2001 \
     --security-policy=secureai-policy \
     --expression="rate(requests.count, 60s) > 100" \
     --action=rate-limit \
     --rate-limit-threshold-count=100
   ```

2. Enhanced logging:
   ```bash
   # Enable detailed audit logging
   gcloud projects update-iam-audit-config secureai-nexus \
     --service=cloudrun.googleapis.com \
     --log-type=ADMIN_READ \
     --log-type=DATA_READ \
     --log-type=DATA_WRITE

   # Set up log exports
   gcloud logging sinks create security-audit \
     storage.googleapis.com/secureai-audit-logs \
     --log-filter="resource.type=\"cloud_run_revision\" AND severity>=WARNING"
   ```

### Performance Testing and Optimization

1. Load testing setup:
   ```bash
   # Create load test configuration
   cat > load-test-config.yaml << EOF
   scenarios:
     - name: "API Load Test"
       duration: 300
       vus: 50
       ramp-up: 30
   EOF

   # Run load test
   gcloud run jobs create load-test \
     --image=gcr.io/secureai-nexus/k6-load-tester \
     --args="--config=load-test-config.yaml" \
     --set-env-vars="TARGET_URL=https://secureai.eriethio.com"
   ```

2. Performance monitoring:
   ```bash
   # Set up performance dashboard
   gcloud monitoring dashboards create performance \
     --display-name="Performance Dashboard" \
     --config-from-file=performance-dashboard.yaml

   # Configure performance alerts
   gcloud monitoring alert-policies create \
     --display-name="Performance Degradation" \
     --condition-filter="resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\" > 1000" \
     --duration=5m
   ```

### Automated Recovery Procedures

1. Self-healing configuration:
   ```bash
   # Set up health check
   gcloud run services update secureai-platform \
     --set-env-vars="HEALTH_CHECK_PATH=/health" \
     --platform=managed \
     --region=us-central1

   # Configure auto-recovery
   gcloud run services update secureai-platform \
     --min-instances=2 \
     --max-instances=10 \
     --platform=managed \
     --region=us-central1
   ```

2. Automated rollback:
   ```bash
   # Create rollback trigger
   gcloud beta run services update-traffic secureai-platform \
     --to-revisions=REVISION=100 \
     --platform=managed \
     --region=us-central1 \
     --tag=stable

   # Set up monitoring
   gcloud monitoring alert-policies create \
     --display-name="Auto Rollback Trigger" \
     --condition-filter="resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code=\"5xx\" > 10" \
     --duration=1m
   ```


