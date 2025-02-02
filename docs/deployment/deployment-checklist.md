# Deployment Checklist

## Pre-Deployment
- [ ] Ensure all configuration files are updated with actual values.
- [ ] Validate all YAML files for placeholders.
- [ ] Verify Kubernetes context and namespace.
- [ ] Ensure Docker image is built and pushed to GCR.

## Deployment
- [ ] Apply ConfigMap and Secrets.
- [ ] Deploy the application using `kubectl apply -f k8s/deployment.yaml`.
- [ ] Monitor deployment status with `kubectl rollout status`.

## Post-Deployment
- [ ] Verify service availability.
- [ ] Check application logs for errors.
- [ ] Validate health and metrics endpoints.
- [ ] Confirm monitoring and alerts are active.

## Additional Checks
- [ ] Ensure SSL/TLS is configured for services.
- [ ] Verify resource limits and requests.
- [ ] Confirm all environment variables are set correctly.
