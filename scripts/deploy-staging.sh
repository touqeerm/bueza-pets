#!/usr/bin/env bash
# Deploys staging ONLY. Safe to re-run. Does not touch production.
#
# Usage: scripts/deploy-staging.sh
set -euo pipefail

REPO_DIR="/root/bueza-pets-staging"
COMPOSE_FILE="docker/compose.staging.yml"
ENV_FILE=".env.staging"
PROJECT="bueza-pets-staging"
HEALTH_URL="http://localhost:8001/health"

cd "$REPO_DIR"

echo "==> [staging] Fetching latest develop..."
git fetch origin develop
git checkout develop
git merge --ff-only origin/develop

echo "==> [staging] Building and starting the stack..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT" up -d --build

echo "==> [staging] Waiting for backend health..."
for i in $(seq 1 30); do
  if curl -sf "$HEALTH_URL" > /dev/null; then
    echo "==> [staging] Backend healthy."
    echo "==> [staging] Deployed $(git rev-parse --short HEAD)"
    exit 0
  fi
  sleep 2
done

echo "==> [staging] Backend did not become healthy in time." >&2
exit 1
