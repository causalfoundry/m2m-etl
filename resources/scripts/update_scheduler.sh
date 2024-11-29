#!/bin/bash

file_path=$1

# some env are inherent from the parent process
env

yq eval '. | keys' $file_path | sed 's/- //' | while read -r SCHEDULER; do
    # Extract schedule and job_name for each scheduler
    SCHEDULE=$(yq eval ".${SCHEDULER}.schedule" $file_path)
    JOB=$(yq eval ".${SCHEDULER}.job" $file_path)
    URI="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB:run" \
    
  if gcloud scheduler jobs describe "$SCHEDULER" --location "$REGION" > /dev/null 2>&1; then
    echo "Scheduler job '$JOB' exists. Updating..."
    gcloud scheduler jobs update http "$SCHEDULER" \
      --location "$REGION" \
      --schedule "$SCHEDULE" \
      --uri "$URI" \
      --http-method POST \
      --oauth-service-account-email "$SERVICE_ACCOUNT"
  else
    echo "Scheduler job '$JOB' does not exist. Creating..."
    gcloud scheduler jobs create http "$SCHEDULER" \
      --location "$REGION" \
      --schedule "$SCHEDULE" \
      --uri "$URI" \
      --http-method POST \
      --oauth-service-account-email "$SERVICE_ACCOUNT"
  fi
done
