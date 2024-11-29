# m2m-etl

This repo contains ETL code for various data source for m2m.
Each merge / push will trigger CI/CD pipeline to build the code into docker container, and publish to image registry on the cloud.
And the containers are run on `Cloud Run`, and is scheduled with `Cloud Scheduler`.

### Infra Intro
The pipeline is packaged into docker container, and deployed as `GCP Cloud Run Job`, which is then triggered by `GCP Cloud Scheduler`.
in the `./resources` folder, `cron.yml` file defines the cron job configuration. In this format
```
<job_name>:
  schedule: <cron_tab>
  timezone: <timezone>
  cpu: <cpu>
  memory: <args>
  env:
    - name: xx
      value: xx
```
This is a complete config defining a pipeline, how much resource, what's the env vars to invoke the container etc.
And the CI pipeline will take this config, create a `Cloud Run Job`, and a `Cloud Scheduler`

#### Assumption
All pipeline comes from the same docker image, only difference is the invoking parameters are different

### Cloud Run deployment example
```
gcloud run deploy SERVICE_NAME \
  --image gcr.io/PROJECT_ID/IMAGE_NAME:TAG \
  --platform managed \
  --region REGION \
  --memory 4Gi \
  --cpu 2
```

### Cloud Scheduler example
- find the run url via `gcloud run services describe SERVICE_NAME --region REGION --platform managed`
- create jobs 
```
gcloud scheduler jobs create http JOB_NAME \
  --schedule "0 2 * * *" \
  --uri https://SERVICE_NAME-xxxxxxxxxx.a.run.app \
  --http-method GET \
  --time-zone "YOUR_TIME_ZONE" \
  --headers "Authorization=Bearer $(gcloud auth application-default print-access-token)"
```
