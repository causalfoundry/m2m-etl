#!/bin/bash

file_path=$1

set -e

# some env are inherent from the parent process
env

yq eval '. | keys' $file_path | sed 's/- //' | while read -r NAME; do
    # Extract schedule and job_name for each scheduler
    SCHEDULE=$(yq eval ".${NAME}.schedule" $file_path)
    CPU=$(yq eval ".${NAME}.cpu" $file_path)
    MEMORY=$(yq eval ".${NAME}.memory" $file_path)
    ENV_VAR=$(yq eval ".${NAME}.env" $file_path)
    URI="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB:run" \

    echo 'start creating temp job yaml...'
    # update job
    yq "
      .metadata.name=\"$NAME\" |
      .metadata.namespace=\"$PROJECT_ID\" |
      .spec.template.spec.template.spec.containers[0].image=\"$IMAGE\" |
      .spec.template.spec.template.spec.containers[0].env[0].value=\"$ENV_VAR\" |
      .spec.template.spec.template.spec.containers[0].resources.limits.cpu=\"$CPU\" |
      .spec.template.spec.template.spec.containers[0].resources.limits.memory=\"$MEMORY\" |
      .spec.template.spec.template.spec.serviceAccountName=\"$SERVICE_ACCOUNT\"
    " ./resources/job_template.yml > ./resources/$NAME.yml
    echo '-------------'
    cat ./resources/$NAME.yml

    gcloud run jobs replace ./resources/$NAME.yml --region $REGION

    # update scheduler
    if gcloud scheduler jobs describe "$NAME" --location europe-west1 > /dev/null 2>&1; then
      echo "Scheduler job '$NAME' exists. Updating..."
      gcloud scheduler jobs update http "$NAME" \
        --location europe-west1 \
        --schedule "$SCHEDULE" \
        --uri "$URI" \
        --http-method POST \
        --oauth-service-account-email "$SERVICE_ACCOUNT"
    else
      echo "Scheduler job '$NAME' does not exist. Creating..."
      gcloud scheduler jobs create http "$NAME" \
        --location europe-west1 \
        --schedule "$SCHEDULE" \
        --uri "$URI" \
        --http-method POST \
        --oauth-service-account-email "$SERVICE_ACCOUNT"
    fi
done
