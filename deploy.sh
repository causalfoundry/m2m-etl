#!/usr/bin/env bash

set -e

# create cloud run
gcloud run deploy SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$IMAGE_NAME:$TAG \
  --platform managed \
  --region REGION \
  --memory 4Gi \
  --cpu 2

# create cloud scheduler

