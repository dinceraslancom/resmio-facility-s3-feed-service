#!/bin/sh

set -e

MC_ALIAS="localminio"
MC_HOST="http://minio:9000"

echo "Create Bucket (Short): Configuring mc alias '${MC_ALIAS}' for host '${MC_HOST}'..."

mc alias set "${MC_ALIAS}" "${MC_HOST}" "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}"

echo "Create Bucket (Short): Ensuring bucket '${S3_BUCKET_NAME}' exists..."

mc stat "${MC_ALIAS}/${S3_BUCKET_NAME}" > /dev/null 2>&1 || mc mb "${MC_ALIAS}/${S3_BUCKET_NAME}"

echo "Create Bucket (Short): Bucket '${S3_BUCKET_NAME}' ensured."