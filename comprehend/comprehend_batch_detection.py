import boto3
import os

def aws_connection(region="us-east-1", service="comprehend"):
    client = boto3.client(service, region_name=region)
    return client


def batch_detection_entities(client, bucket_name, file_prefix, comprehend_role):
    file_name_tgz = ((file_prefix.split("/")[-1]).split(".")[0]) + ".tar.gz"

    print(f"Starting comprehend detection JOB on file {file_name_tgz}")

    s3_uri = f"s3://{bucket_name}/{file_prefix}"
    response = client.start_entities_detection_job(
        InputDataConfig={
            'S3Uri': s3_uri,
            'InputFormat': 'ONE_DOC_PER_FILE'
        },
        OutputDataConfig={
            'S3Uri': f"s3://{bucket_name}/comprehend/output/",
        },
        DataAccessRoleArn=comprehend_role,
        LanguageCode='pt',
    )
    print(response)


def list_detection_jobs(client):
    response = client.list_entities_detection_jobs()
    print(response)

if __name__ == "__main__":

    # S3 file will be passed as an event to the Lambda function.
    bucket_name = "textract-test-aneel"
    file_prefix = "textract/output/o_cortico.txt"
    comprehend_role = "arn:aws:iam::0000000:role/comprehend_role_s3_full"

    client = aws_connection()

    # batch_detection_entities(client, bucket_name, file_prefix, comprehend_role)
    list_detection_jobs(client)