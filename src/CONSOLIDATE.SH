#!/bin/bash

# Create consolidated directories
mkdir -p docs/{architecture,deployment,security}
mkdir -p prisma
mkdir -p public/images
mkdir -p src/{app,components,lib,api,models}

# Move documentation (adjust paths if needed)
mv docs/implementation/* docs/architecture/ 2>/dev/null
mv docs/specifications/* docs/architecture/ 2>/dev/null
mv docs/troubleshooting/* docs/deployment/ 2>/dev/null

# Move template files to the new Next.js app folder
if [ -d "templates" ]; then
  mkdir -p src/app/login src/app/signup src/app/dashboard
  mv templates/index.html src/app/page.tsx
  mv templates/login.html src/app/login/page.tsx
  mv templates/signup.html src/app/signup/page.tsx
  mv templates/dashboard.html src/app/dashboard/page.tsx
  rm -rf templates/
fi

# Move static assets to public folder
if [ -d "src/static/images" ]; then
  mkdir -p public/images
  mv src/static/images/* public/images/
  rm -rf src/static
fi

# Move prisma schema if exists
if [ -f "src/models/schema.prisma" ]; then
  mv src/models/schema.prisma prisma/schema.prisma
fi

echo "Project structure consolidated successfully."
