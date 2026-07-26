#!/usr/bin/env bash
# Rolls back one environment to an older commit and redeploys it.
# Leaves that worktree in a detached HEAD state at the target commit —
# the next regular deploy script re-attaches to the branch and moves
# forward again normally.
#
# Usage: scripts/rollback.sh production [git-ref]
#        scripts/rollback.sh staging [git-ref]
# git-ref defaults to HEAD~1 (the commit before whatever's live now).
set -euo pipefail

ENVIRONMENT="${1:?Usage: rollback.sh <production|staging> [git-ref]}"
REF="${2:-HEAD~1}"

case "$ENVIRONMENT" in
  production)
    REPO_DIR="/root/bueza-pets"
    COMPOSE_FILE="docker/compose.prod.yml"
    ENV_FILE=".env.production"
    PROJECT="bueza-pets-prod"
    HEALTH_URL="http://localhost:8000/health"
    ;;
  staging)
    REPO_DIR="/root/bueza-pets-staging"
    COMPOSE_FILE="docker/compose.staging.yml"
    ENV_FILE=".env.staging"
    PROJECT="bueza-pets-staging"
    HEALTH_URL="http://localhost:8001/health"
    ;;
  *)
    echo "Unknown environment: $ENVIRONMENT (expected 'production' or 'staging')" >&2
    exit 1
    ;;
esac

cd "$REPO_DIR"

CURRENT=$(git rev-parse --short HEAD)
TARGET=$(git rev-parse --short "$REF")

echo "==> [$ENVIRONMENT] Currently at $CURRENT, rolling back to $TARGET"
read -r -p "Continue? [y/N] " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

git checkout "$REF" --detach

echo "==> [$ENVIRONMENT] Rebuilding and restarting at $TARGET..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" -p "$PROJECT" up -d --build

echo "==> [$ENVIRONMENT] Waiting for backend health..."
for i in $(seq 1 30); do
  if curl -sf "$HEALTH_URL" > /dev/null; then
    echo "==> [$ENVIRONMENT] Backend healthy at $TARGET."
    exit 0
  fi
  sleep 2
done

echo "==> [$ENVIRONMENT] Backend did not become healthy after rollback." >&2
exit 1
