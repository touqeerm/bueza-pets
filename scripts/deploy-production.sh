#!/usr/bin/env bash
# Deploys production ONLY. Safe to re-run. Does not touch staging.
#
# Usage: scripts/deploy-production.sh
set -euo pipefail

REPO_DIR="/root/bueza-pets"
COMPOSE_FILE="docker/compose.prod.yml"
ENV_FILE=".env.production"
PROJECT="bueza-pets-prod"
HEALTH_URL="http://localhost:8000/health"

cd "$REPO_DIR"

echo "==> [production] Fetching latest main..."
git fetch origin main
git checkout main
git merge --ff-only origin/main

echo "==> [production] Building and starting the stack..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT" up -d --build

echo "==> [production] Waiting for backend health..."
for i in $(seq 1 30); do
  if curl -sf "$HEALTH_URL" > /dev/null; then
    echo "==> [production] Backend healthy."
    echo "==> [production] Deployed $(git rev-parse --short HEAD)"
    exit 0
  fi
  sleep 2
done

echo "==> [production] Backend did not become healthy in time." >&2
exit 1
