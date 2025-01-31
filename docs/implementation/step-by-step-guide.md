# SecureAI Platform GCP Implementation Guide

## Prerequisites
1. GCP Account with billing enabled
2. Local development tools installed (Python 3.9+, Docker)
3. Google Cloud SDK installed
4. Service account with necessary permissions

## Step-by-Step Setup

### 1. Initial Configuration
```bash
# Install Google Cloud SDK
brew install google-cloud-sdk  # For macOS

# Login to GCP
gcloud auth login

# Set project
gcloud config set project secureai-nexus

# Create service account
gcloud iam service-accounts create secureai-nexus \
  --display-name="SecureAI Platform Service Account"
```

### 2. Development Environment Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/nawedy/secure-ai-nexus
   cd secure-ai-nexus
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   # Copy template and edit with your values
   cp .env.template .env
   ```

### 3. Enable Required GCP Services
```bash
# Enable necessary APIs
gcloud services enable \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com \
  cloudkms.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  secretmanager.googleapis.com
```

### 4. Security Setup
1. Set up Secret Manager:
   ```bash
   # Create secrets
   echo -n "your-api-key" | \
     gcloud secrets create api-key \
     --data-file=- \
     --replication-policy="automatic"
   ```

2. Configure IAM permissions:
   ```bash
   # Grant service account access to secrets
   gcloud secrets add-iam-policy-binding api-key \
     --member="serviceAccount:secureai-nexus@secureai-nexus.iam.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

### 5. Build and Deploy
1. Build Docker image:
   ```bash
   # Build the image
   docker build -t gcr.io/secureai-nexus/secureai-platform:latest .

   # Configure Docker auth
   gcloud auth configure-docker

   # Push to Container Registry
   docker push gcr.io/secureai-nexus/secureai-platform:latest
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy secureai-platform \
     --image gcr.io/secureai-nexus/secureai-platform:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "ENVIRONMENT=production"
   ```

### 5. DNS and Domain Configuration
1. Set up Cloud DNS:
   ```bash
   # Create DNS zone if not exists
   gcloud dns managed-zones create eriethio \
     --dns-name="eriethio.com." \
     --description="Main domain zone"

   # Add subdomain record for secureai
   gcloud dns record-sets create secureai.eriethio.com. \
     --type=A \
     --zone=eriethio \
     --rrdatas=$(gcloud run services describe secureai-platform \
       --platform managed \
       --region us-central1 \
       --format='get(status.url)' | sed 's/https:\/\///')
   ```

2. Configure SSL Certificate:
   ```bash
   # Create certificate
   gcloud certificate-manager certificates create secureai-cert \
     --domains="secureai.eriethio.com"

   # Map certificate to Cloud Run service
   gcloud run services update secureai-platform \
     --region us-central1 \
     --certificate=secureai-cert
   ```

3. Update DNS Provider:
   - Log in to your DNS provider (where eriethio.com is registered)
   - Add these records:
     ```
     Type  | Name    | Value
     CNAME | secureai| ghs.googlehosted.com.
     TXT   | secureai| google-site-verification=<verification-code>
     ```

4. Verify DNS Configuration:
   ```bash
   # Check DNS propagation
   dig secureai.eriethio.com

   # Verify SSL certificate
   curl -v https://secureai.eriethio.com/health
   ```

### 6. Security Hardening
1. Configure Cloud Armor:
   ```bash
   # Create security policy
   gcloud compute security-policies create secureai-policy \
     --description="Security policy for SecureAI Platform"

   # Add WAF rules
   gcloud compute security-policies rules create 1000 \
     --security-policy=secureai-policy \
     --expression="evaluatePreconfiguredWaf('crs-v2', {'sensitivity': 1})" \
     --action=deny-403

   # Apply to Cloud Run
   gcloud run services update secureai-platform \
     --region us-central1 \
     --security-policy=secureai-policy
   ```

2. Set up VPC Service Controls:
   ```bash
   # Create service perimeter
   gcloud access-context-manager perimeters create secureai-perimeter \
     --title="SecureAI Perimeter" \
     --resources="projects/$GCP_PROJECT_NUMBER" \
     --restricted-services="run.googleapis.com,containerregistry.googleapis.com"
   ```

### 7. Monitoring and Alerting
1. Create Alert Policies:
   ```bash
   # Create latency alert
   gcloud monitoring alert-policies create \
     --display-name="High Latency Alert" \
     --condition-filter="metric.type=\"run.googleapis.com/request_latencies\" resource.type=\"cloud_run_revision\"" \
     --duration="5m" \
     --threshold-value=1000 \
     --comparison="COMPARISON_GT"

   # Create error rate alert
   gcloud monitoring alert-policies create \
     --display-name="Error Rate Alert" \
     --condition-filter="metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\" metric.labels.response_code_class=\"5xx\"" \
     --duration="5m" \
     --threshold-value=5 \
     --comparison="COMPARISON_GT"
   ```

2. Configure Log Exports:
   ```bash
   # Create log bucket
   gcloud logging buckets create secureai-logs \
     --location=global

   # Set up log routing
   gcloud logging sinks create secureai-sink \
     logging.googleapis.com/projects/$GCP_PROJECT_ID/locations/global/buckets/secureai-logs \
     --log-filter="resource.type=\"cloud_run_revision\""
   ```

### 8. Verify Deployment
1. Check deployment status:
   ```bash
   # List Cloud Run services
   gcloud run services list

   # Get service URL
   gcloud run services describe secureai-platform \
     --platform managed \
     --region us-central1 \
     --format='value(status.url)'
   ```

2. Test the API:
   ```bash
   # Test health endpoint
   curl $(gcloud run services describe secureai-platform \
     --platform managed \
     --region us-central1 \
     --format='value(status.url)')/health
   ```

## Common Issues and Solutions

### Authentication Issues
- Check service account permissions
- Verify Docker authentication
- Review Secret Manager access

### Deployment Issues
- Check Cloud Run logs
- Verify container health
- Review resource allocation

## Next Steps
1. Set up CI/CD pipeline
2. Configure custom domain
3. Implement backup strategy
4. Set up additional security measures

## Getting Help
- Check the troubleshooting guide
- Review logs for specific errors
- Contact support if needed

## Production Checklist
- [ ] Domain and SSL configured correctly
- [ ] Security policies and WAF rules active
- [ ] Monitoring and alerting set up
- [ ] Backup strategy implemented
- [ ] Rate limiting configured
- [ ] Error handling tested
- [ ] Load testing completed
- [ ] Security scanning automated
- [ ] Documentation updated
- [ ] Emergency procedures documented

## Maintenance Procedures
1. Certificate Renewal:
   ```bash
   # Check certificate status
   gcloud certificate-manager certificates describe secureai-cert
   ```

2. Security Updates:
   ```bash
   # Update base image
   docker pull python:3.9-slim
   docker build --no-cache -t gcr.io/secureai-nexus/secureai-platform:latest .
   ```

3. Monitoring Review:
   ```bash
   # Check recent alerts
   gcloud monitoring alert-policies list

   # Review logs
   gcloud logging read "resource.type=cloud_run_revision" --limit=10
   ```
