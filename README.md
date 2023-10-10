# SE Oppts Automation PDF

This is a Serverless Framework Python AWS Lambda, it receives the pageId from the [se-oppts-automation](https://github.com/solacese/se-oppts-automation) trigger after a SE TSD page is created or updated, then performs below actions:

1. Export the SE TSD pages into a PDF file
1. then upload it to the Hub folder

## Configuration

This Lambda function is configured in the [serverless.yml](https://github.com/solacese/se-oppts-automation/blob/main/serverless.yml) file, it needs the following environment variables to access the Atlassian Forge API to export the SE TSD pages into a PDF file, and upload it to the Hub folder on Azure Sharepoint folder:

```yml
        FORGE_EMAIL: ${env:FORGE_EMAIL, param:forge-email}
        FORGE_API_TOKEN: ${env:FORGE_API_TOKEN, param:forge-api-token}
        AZURE_CLIENT_ID: ${env:AZURE_CLIENT_ID, param:azure-client-id}
        AZURE_TENANT_ID: ${env:AZURE_TENANT_ID, param:azure-tenant-id}
        AZURE_CLIENT_SECRET: ${env:AZURE_CLIENT_SECRET, param:azure-client-secret}
```

After running deploy, you should see output similar to:

```bash
❯ sls deploy -s prod
Running "serverless" from node_modules
service: se-tsd-automation
stage: prod
region: us-east-1
stack: se-tsd-automation-prod
endpoint: POST - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/produce
functions:
  producer: se-tsd-automation-prod-producer
  jobsWorker: se-tsd-automation-prod-jobsWorker
jobs: https://sqs.us-east-1.amazonaws.com/231935536054/se-tsd-automation-prod-jobs

```

Then update the `trigger.jsx` file of the [se-oppts-automation](https://github.com/solacese/se-oppts-automation) with the `lambdaUrl` set to the endpoint of the Lambda function.
