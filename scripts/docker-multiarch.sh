#!/bin/bash
set -e

# Multi-architecture build script
echo "🏗️  Building multi-architecture images..."

# Create and use buildx builder
docker buildx create --name bookdine-builder --use --bootstrap || true

# Build for multiple architectures
docker buildx build \
    --file Dockerfile.prod \
    --platform linux/amd64,linux/arm64 \
    --tag bookdine:latest \
    --tag bookdine:$(git rev-parse --short HEAD) \
    --cache-from type=registry,ref=bookdine:buildcache \
    --cache-to type=registry,ref=bookdine:buildcache,mode=max \
    --push \
    .

echo "✅ Multi-architecture build completed!"