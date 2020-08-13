import boto3
import time
import os
import json

def is_job_complete(jobId):
    """
    That function is responsible to validate if a started job in textract is completed or not
    """
    client = boto3.client('textract')
    response = client.get_document_text_detection(JobId=jobId)
    status = response["JobStatus"]
    print("Job status: {}".format(status))

    try:
        while(status == "IN_PROGRESS"):
            time.sleep(2)
            response = client.get_document_text_detection(JobId=jobId)
            status = response["JobStatus"]
            print("Job status: {}".format(status))

        return True
    except Exception as e:
        print(str(e))
        return False


def get_job_results(jobId):
    pages = []

    time.sleep(3)

    client = boto3.client('textract')
    response = client.get_document_text_detection(JobId=jobId)
    
    pages.append(response)
    print("Resultset page recieved: {}".format(len(pages)))
    nextToken = None
    if('NextToken' in response):
        nextToken = response['NextToken']

    # Next token necessary because the number of pages is huge
    while(nextToken):
        response = client.get_document_text_detection(JobId=jobId, NextToken=nextToken)

        pages.append(response)
        print("Resultset page recieved: {}".format(len(pages)))
        nextToken = None
        if('NextToken' in response):
            nextToken = response['NextToken']

    return pages


def write_extract_to_file(response, documentNametxt):
    # write detected text into a txt file
    for result_page in response:
        for item in result_page["Blocks"]:
            if item["BlockType"] == "LINE":
                with open(f"/tmp/{documentNametxt}", "a+") as file_object:
                    # Move read cursor to the start of file.
                    file_object.seek(0)
                    # If file is not empty then append '\n'
                    data = file_object.read(100)
                    if len(data) > 0 :
                        file_object.write("\n")
                    # Append text at the end of file
                    file_object.write(item["Text"])


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == "__main__":
    QUEUE_NAME = os.getenv("QUEUE_NAME", "")
    S3_BUCKET_NAME = os.getenv("BUCKET_NAME","")
    S3_TEXTRACT_OUTPUT_PATH = "textract/output"

    sqs = boto3.resource('sqs', region_name="us-east-1")
    queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)

    while 1:
        try:
            messages = queue.receive_messages(WaitTimeSeconds=5)
            for message in messages:
                message_body = json.loads(message.body)

                print(message_body)

                # Get results from SQS queue
                job_id = message_body.get("job_id")
                documentName = message_body.get("file_name")

                # Loop inside function
                validation = is_job_complete(job_id)

                if not validation:
                    print("Error when validate the JOB")
                    
                response = get_job_results(job_id)

                # Change the format of document to TXT
                documentNametxt = ((documentName.split("/")[-1]).split(".")[0])+".txt"

                write_extract_to_file(response, documentNametxt)
                
                upload_file(f"/tmp/{documentNametxt}", S3_BUCKET_NAME, 
                    f"{S3_TEXTRACT_OUTPUT_PATH}/{documentNametxt}")

                message.delete()
        except Exception as e:
            print(e)
            continue
