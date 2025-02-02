#!/usr/bin/env python3
import yaml
import re

def validate_yaml(file_path):
    """Validate YAML file for placeholders."""
    with open(file_path, 'r') as file:
        content = file.read()
        if re.search(r'YOUR_PROJECT_ID|your_model_registry_key|your_api_key|your_monitoring_token', content):
            raise ValueError(f"Placeholder found in {file_path}")

def main():
    files_to_check = [
        'k8s/deployment.yaml',
        'k8s/secrets.yaml',
        'k8s/configmap.yaml',
        'k8s/service.yaml'
    ]

    for file_path in files_to_check:
        validate_yaml(file_path)

    print("All configuration files are valid.")

if __name__ == "__main__":
    main()
