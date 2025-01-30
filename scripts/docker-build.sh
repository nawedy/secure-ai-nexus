#!/bin/bash
set -e

# Build the application image
echo "Building SecureAI application image..."
docker build -t secureai:latest .

# Check if we're in production mode
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running in production mode..."
    docker-compose -f docker-compose.prod.yml up -d
else
    echo "Running in development mode..."
    docker-compose up -d
fi

# Wait for health checks
echo "Waiting for services to be healthy..."
sleep 10

# Check service health
docker-compose ps

echo "Deployment complete! Services are running at:"
echo "- API: http://localhost:8000"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000"
