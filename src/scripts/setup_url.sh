#!/bin/bash

# Set the correct project
gcloud config set project secureai-nexus

DOMAIN="getaisecured.com"
PROJECT_ID=$(gcloud config get-value project)

# Configure DNS
gcloud dns record-sets transaction start --zone=$DOMAIN
gcloud dns record-sets transaction add --name=$DOMAIN. --type=A --ttl=300 "YOUR_LOAD_BALANCER_IP" --zone=$DOMAIN
gcloud dns record-sets transaction execute --zone=$DOMAIN

# Set up SSL
gcloud certificate-manager certificates create secureai-cert --domains=$DOMAIN --project=$PROJECT_ID

echo "URL setup complete for $DOMAIN"
