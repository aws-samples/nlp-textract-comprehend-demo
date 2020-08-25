import boto3
import time
import os
import json

def start_job(s3_bucket_name, document_name):
    response = None
    client = boto3.client('textract')
    response = client.start_document_text_detection(
    DocumentLocation={
        'S3Object': {
            'Bucket': s3_bucket_name,
            'Name': document_name
        }
    })

    return response["JobId"]


def sqs_send_message(queue_name, body):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    response = queue.send_message(MessageBody=body)
    print(response)


def lambda_handler(event, context):
    
    QUEUE_NAME = os.getenv("SQS_QUEUE_NAME", "")
    s3_bucket_name = os.getenv("BUCKET_NAME", "")

    # The information of document is originated by s3
    document_name = event["Records"][0]["s3"]["object"]["key"]

    job_id = start_job(s3_bucket_name, document_name)
    
    print("Started job with id: {}".format(job_id))

    body = {"job_id" : job_id, "file_name" : document_name}
    json_body = json.dumps(body)

    sqs_send_message(QUEUE_NAME, json_body)