#!/usr/bin/env bash
# ==============================================================================
# deploy.sh
# Deployment script executed via SSH on the EC2 Host
# Usage: ./deploy.sh <image_name> <commit_sha> <app_port> <health_endpoint> <owner>
# ==============================================================================
set -euo pipefail

IMAGE_NAME="${1:-learning-service}"
COMMIT_SHA="${2:-latest}"
APP_PORT="${3:-8000}"
HEALTH_ENDPOINT="${4:-/health}"
OWNER="${5:-}"

if [[ -z "$OWNER" ]]; then
  echo "❌ Error: Repository owner must be provided."
  exit 1
fi

OWNER_LOWER=$(echo "$OWNER" | tr '[:upper:]' '[:lower:]')
IMAGE_URI="ghcr.io/${OWNER_LOWER}/${IMAGE_NAME}:${COMMIT_SHA}"
CONTAINER_NAME="${IMAGE_NAME}"

echo "=========================================================="
echo "🚀 Deploying ${CONTAINER_NAME} on AWS EC2..."
echo "📦 Image Target: ${IMAGE_URI}"
echo "🔌 Target Port: ${APP_PORT}"
echo "=========================================================="

# 1. Pull the immutable container image from GHCR
echo "📥 Pulling container image from GHCR..."
docker pull "${IMAGE_URI}"

# 2. Stop and remove any currently running container
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "⏹️ Stopping existing container: ${CONTAINER_NAME}..."
    docker stop "${CONTAINER_NAME}" || true
    docker rm "${CONTAINER_NAME}" || true
fi

# 3. Run the new container
echo "▶️ Starting new container: ${CONTAINER_NAME}..."
docker run -d \
  --name "${CONTAINER_NAME}" \
  --restart unless-stopped \
  -p "${APP_PORT}:${APP_PORT}" \
  "${IMAGE_URI}"

# 4. Verification & Smoke Test
echo "⏳ Waiting for service to initialize..."
sleep 4

HEALTH_URL="http://localhost:${APP_PORT}${HEALTH_ENDPOINT}"
echo "🔍 Verifying health at ${HEALTH_URL}..."

if curl --silent --fail "${HEALTH_URL}" > /dev/null; then
    echo "=========================================================="
    echo "✅ DEPLOYMENT SUCCESSFUL!"
    echo "Container ${CONTAINER_NAME} is live and healthy."
    echo "=========================================================="
else
    echo "=========================================================="
    echo "❌ HEALTH CHECK FAILED!"
    echo "Dumping container logs for inspection:"
    docker logs --tail 30 "${CONTAINER_NAME}"
    exit 1
fi
