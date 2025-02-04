#!/bin/bash

# Reorganization Script for SecureAI Project
# This script executes the project reorganization process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print with timestamp
log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Check if running in correct directory
if [ ! -f "setup.py" ] || [ ! -d "src" ]; then
    log "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    log "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required packages
log "${YELLOW}Installing required packages...${NC}"
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run pre-reorganization checks
log "${YELLOW}Running pre-reorganization checks...${NC}"

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    log "${RED}Warning: You have uncommitted changes${NC}"
    log "${YELLOW}Please commit or stash your changes before proceeding${NC}"
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "${RED}Aborting...${NC}"
        exit 1
    fi
fi

# Create backup directory
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
log "${YELLOW}Creating backup in $BACKUP_DIR...${NC}"
mkdir -p "$BACKUP_DIR"

# Run the reorganization script
log "${YELLOW}Running reorganization script...${NC}"
python scripts/reorganize_project.py

# Run post-reorganization checks
log "${YELLOW}Running post-reorganization checks...${NC}"

# Run tests to ensure nothing is broken
log "${YELLOW}Running tests...${NC}"
pytest

# Update git index
log "${YELLOW}Updating git index...${NC}"
git add .

# Print summary
log "${GREEN}Reorganization completed successfully!${NC}"
log "Summary of changes:"
log "- Consolidated test files"
log "- Reorganized source code structure"
log "- Consolidated documentation"
log "- Updated import statements"
log "- Cleaned up temporary files"

log "${YELLOW}Please review the changes and commit them to git${NC}"
log "A backup of the original structure is available in: $BACKUP_DIR"

# Deactivate virtual environment
deactivate
