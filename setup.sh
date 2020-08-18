#!/bin/bash
set -ex

DIR_NAME=$(dirname "$PWD")
VOLUME_SOCK_MAPPING="/var/run/docker.sock:/var/run/docker.sock"
IMAGE_TAG_NAME="building-image-setup:latest"
S3_BUCKET_NAME_CODE="lambdacodeavcbvcb"
ECR_REPOSITORY_NAME="ai-comprehend-ml-new"

echo "Building Docker image to setup environment"

docker build -t ${IMAGE_TAG_NAME} .

echo "Run Docker container for environemnt setup"

docker run \
 -v "${VOLUME_SOCK_MAPPING}" \
 -v "${HOME}/.aws/credentials":"/root/.aws/credentials" \
    ${IMAGE_TAG_NAME} ${S3_BUCKET_NAME_CODE} ${ECR_REPOSITORY_NAME}