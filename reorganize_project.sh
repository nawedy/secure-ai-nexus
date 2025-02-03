#!/bin/bash

# Create necessary directories
mkdir -p src/{app,components,lib,api,models,cache}
mkdir -p docs/{architecture,deployment}
mkdir -p k8s/{base,overlays/production,monitoring}
mkdir -p prisma/migrations
mkdir -p tests/{unit,integration,e2e}
mkdir -p public/images

# Move configuration files
mv .env .env.template .eslintrc.js .prettierrc.js .lintstagedrc.js .gitignore tsconfig.json cloudbuild.yaml docker-compose.yml Dockerfile Dockerfile.test package-lock.json package.json pnpm-lock.yaml pytest.ini README.md requirements-test.txt requirements.txt setup.py ./

# Move documentation
mv docs/architecture/* docs/architecture/
mv docs/deployment/* docs/deployment/

# Move source code
mv src/models/* src/models/
mv src/cache/distributed_cache.py src/cache/

# Move infrastructure files
mv k8s/base/* k8s/base/
mv k8s/overlays/production/* k8s/overlays/production/
mv k8s/monitoring/* k8s/monitoring/

# Move database files
mv prisma/migrations/* prisma/migrations/
mv prisma/schema.prisma prisma/

# Move test files
mv tests/unit/* tests/unit/
mv tests/integration/* tests/integration/
mv tests/e2e/* tests/e2e/

# Move public assets
mv public/images/* public/images/

# Remove unnecessary files
rm -rf .venv node_modules secureai_nexus.egg-info static Logo Images

echo "Project reorganization complete."
