import boto3
import time
import os
import json

def start_job(s3BucketName, objectName):
    response = None
    client = boto3.client('textract')
    response = client.start_document_text_detection(
    DocumentLocation={
        'S3Object': {
            'Bucket': s3BucketName,
            'Name': objectName
        }
    })

    return response["JobId"]


def sqs_send_message(queue_name, body):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    response = queue.send_message(MessageBody=body)
    print(response)


if __name__ == "__main__":
    # The informations will came from s3 event
    s3BucketName = "textract-test-aneel"
    documentName = "textract/input/as_cidades_e_as_serras.pdf"

    QUEUE_NAME = os.getenv("SQS_QUEUE_NAME", "npl-queue")
    job_id = start_job(s3BucketName, documentName)
    
    print("Started job with id: {}".format(job_id))

    body = {"job_id" : job_id, "file_name" : documentName}
    json_body = json.dumps(body)

    sqs_send_message(QUEUE_NAME, json_body)