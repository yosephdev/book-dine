#!/bin/bash
set -e

# Docker build script with optimization
echo "🐳 Building BookDine Docker images..."

# Enable BuildKit for better caching and performance
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build arguments
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF=$(git rev-parse --short HEAD)
VERSION=${VERSION:-latest}

echo "📦 Building production image..."
docker build \
    --file Dockerfile.prod \
    --tag bookdine:${VERSION} \
    --tag bookdine:latest \
    --build-arg BUILD_DATE="${BUILD_DATE}" \
    --build-arg VCS_REF="${VCS_REF}" \
    --build-arg VERSION="${VERSION}" \
    --cache-from bookdine:latest \
    .

echo "🔍 Analyzing image size..."
docker images bookdine:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo "🧪 Running security scan..."
if command -v docker-scout &> /dev/null; then
    docker scout cves bookdine:latest
else
    echo "⚠️  Docker Scout not available, skipping security scan"
fi

echo "✅ Build completed successfully!"
echo "📊 Image details:"
docker inspect bookdine:latest --format='{{.Config.Labels}}'