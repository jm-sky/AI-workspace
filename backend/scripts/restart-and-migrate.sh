#!/bin/bash

# Script to restart Docker Compose (dev.yml) and run database migrations
# Usage: ./restart-and-migrate.sh

set -e  # Exit on error

COMPOSE_FILE="docker-compose.dev.yml"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

cd "$BACKEND_DIR"

echo "🔄 Stopping Docker Compose services..."
docker compose -f "$COMPOSE_FILE" down

echo ""
echo "🚀 Starting Docker Compose services..."
docker compose -f "$COMPOSE_FILE" up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

echo ""
echo "🔄 Running database migrations..."
docker compose -f "$COMPOSE_FILE" exec app python cli.py db migrate

echo ""
echo "✅ Done! Services restarted and migrations applied."
