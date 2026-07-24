#!/bin/bash

# Frontend Build and Deploy Script
# This script installs dependencies, builds the frontend, and deploys to /var/www/ai-workspace
#
# Usage: scripts/frontend_build_deploy.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_DIR="/var/www/ai-workspace"

echo -e "${GREEN}🔨 Starting frontend build and deploy...${NC}"

# Install frontend dependencies
echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
cd "$PROJECT_DIR"
pnpm install --frozen-lockfile

# Build frontend
echo -e "${YELLOW}🔨 Building frontend...${NC}"
# Clean up dist directory to avoid permission issues
rm -rf dist
# Cap Node heap below typical free RAM on this VPS (no swap).
# Run type-check and vite sequentially — `pnpm build` uses run-p and doubles peak RSS (OOM / exit 137).
export NODE_OPTIONS="--max-old-space-size=2048"
pnpm type-check
pnpm build-only
echo -e "${GREEN}✅ Frontend build completed${NC}"

# Deploy to /var/www/ai-workspace
echo -e "${YELLOW}📋 Deploying to ${DEPLOY_DIR}...${NC}"

# Remove old files
sudo rm -rf "${DEPLOY_DIR:?}"/*

# Copy new build
sudo cp -r dist/* "$DEPLOY_DIR/"

# Fix ownership to caddy:deploy
sudo chown -R caddy:deploy "$DEPLOY_DIR"

echo -e "${GREEN}✅ Deployed to ${DEPLOY_DIR}${NC}"
echo -e "${GREEN}✅ Frontend build and deploy completed successfully!${NC}"

