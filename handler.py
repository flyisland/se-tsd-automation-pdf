import json
import logging
import os

import boto3

import confluence
import graph

logger = logging.getLogger()

QUEUE_URL = os.getenv("QUEUE_URL")
SQS = boto3.client("sqs")


def producer(event, context):
    status_code = 200
    message = ""

    if not event.get("body"):
        return {"statusCode": 400, "body": json.dumps({"message": "No body was found"})}

    try:
        body = json.loads(event["body"])
        logger.info(f"Message body: {body}")
        if not body.get("pageId"):
            logger.exception("No pageId was found")
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "No pageId was found"}),
            }
        logger.info(f"PageId: {body['pageId']}")
        SQS.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=event["body"],
        )
        message = "Message accepted!"
    except Exception as e:
        logger.exception("Sending message to SQS queue failed!")
        message = str(e)
        status_code = 500

    return {"statusCode": status_code, "body": json.dumps({"message": message})}


def consumer(event, context):
    kwargs = {
        "forge_email": os.getenv("FORGE_EMAIL"),
        "forge_api_token": os.getenv("FORGE_API_TOKEN"),
        "azure_client_id": os.getenv("AZURE_CLIENT_ID"),
        "azure_tenant_id": os.getenv("AZURE_TENANT_ID"),
        "azure_client_secret": os.getenv("AZURE_CLIENT_SECRET"),
        "domain": "sol-jira",
        "space": "AT",
        "page_id": "",
        "all": False,
    }

    confluence.init(kwargs)
    graph.init(kwargs)
    for record in event["Records"]:
        logger.info(f'Message body: {record["body"]}')
        body = json.loads(record["body"])
        if not body.get("pageId"):
            logger.exception("No pageId was found")
            return
        confluence.export_page(body["pageId"])
    return
