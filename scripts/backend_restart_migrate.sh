#!/bin/bash

# Backend Restart and Migrate Script
# This script restarts the backend Docker Compose services and runs database migrations
#
# Usage: scripts/backend_restart_migrate.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
COMPOSE_FILE="docker-compose.dev.yml"

echo -e "${GREEN}🐳 Starting backend restart and migration...${NC}"

if [ -d "$BACKEND_DIR" ] && [ -f "$BACKEND_DIR/$COMPOSE_FILE" ]; then
  cd "$BACKEND_DIR"

  echo -e "${YELLOW}🔨 Building app image...${NC}"
  docker compose -f "$COMPOSE_FILE" build app

  echo ""
  echo -e "${YELLOW}🔄 Restarting app container...${NC}"
  docker compose -f "$COMPOSE_FILE" up -d --force-recreate app

  echo ""
  echo -e "${YELLOW}⏳ Waiting for app to be healthy...${NC}"
  sleep 5

  echo ""
  echo -e "${YELLOW}🔄 Running database migrations...${NC}"
  docker compose -f "$COMPOSE_FILE" exec app python cli.py db migrate

  echo -e "${GREEN}✅ Backend restarted and migrations applied${NC}"
else
  echo -e "${YELLOW}⚠️  Backend not found or docker-compose.dev.yml missing, skipping backend deployment${NC}"
  exit 0
fi

echo -e "${GREEN}✅ Backend restart and migration completed successfully!${NC}"

