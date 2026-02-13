#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="${IMAGE_TAG:-cli-tools-test:latest}"

docker build -f Dockerfile.test -t "${IMAGE_TAG}" .
docker run --rm "${IMAGE_TAG}"
