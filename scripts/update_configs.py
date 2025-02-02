#!/usr/bin/env python3
import os
import subprocess
import yaml
import base64

def get_project_id():
    """Retrieve the GCP project ID."""
    return subprocess.check_output(
        ['gcloud', 'config', 'get-value', 'project'],
        text=True
    ).strip()

def update_deployment_yaml(project_id):
    """Update the deployment YAML with the actual project ID."""
    with open('k8s/deployment.yaml', 'r') as file:
        deployment = yaml.safe_load(file)

    deployment['spec']['template']['spec']['containers'][0]['image'] = (
        f"gcr.io/{project_id}/secureai-platform:1.0.0"
    )

    with open('k8s/deployment.yaml', 'w') as file:
        yaml.dump(deployment, file)

def update_secrets_yaml():
    """Update the secrets YAML with base64 encoded values."""
    secrets = {
        'MODEL_REGISTRY_KEY': base64.b64encode(b'your_model_registry_key').decode('utf-8'),
        'API_KEY': base64.b64encode(b'your_api_key').decode('utf-8'),
        'MONITORING_TOKEN': base64.b64encode(b'your_monitoring_token').decode('utf-8')
    }

    with open('k8s/secrets.yaml', 'r') as file:
        secret_data = yaml.safe_load(file)

    secret_data['data'].update(secrets)

    with open('k8s/secrets.yaml', 'w') as file:
        yaml.dump(secret_data, file)

def main():
    project_id = get_project_id()
    update_deployment_yaml(project_id)
    update_secrets_yaml()
    print("Configuration files updated successfully.")

if __name__ == "__main__":
    main()
