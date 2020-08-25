#!/bin/bash
# set -ex

DIR_NAME=$(dirname "$PWD")
VOLUME_SOCK_MAPPING="/var/run/docker.sock:/var/run/docker.sock"
IMAGE_TAG_NAME="building-image-setup:latest"

read -p "Enter the name of the bucket that will be create to store your lambda code: "  S3_BUCKET_NAME_CODE
read -p "Enter the name of the ECR that will be create to store your lambda code: "  ECR_REPOSITORY_NAME
# S3_BUCKET_NAME_CODE="lambdacodeavcbvcb"
# ECR_REPOSITORY_NAME="ai-comprehend-ml-new"
echo "Downloading Datawrangler"
wget https://github.com/awslabs/aws-data-wrangler/releases/download/1.8.1/awswrangler-layer-1.8.1-py3.6.zip -P ./athena_glue/

echo "Building Docker image to setup environment"

docker build -t ${IMAGE_TAG_NAME} .

echo "Run Docker container for environemnt setup"

docker run \
 -v "${VOLUME_SOCK_MAPPING}" \
 -v "${HOME}/.aws/credentials":"/root/.aws/credentials" \
    ${IMAGE_TAG_NAME} ${S3_BUCKET_NAME_CODE} ${ECR_REPOSITORY_NAME}