import boto3
import os
import sys

def aws_connection(region="us-east-1", service="comprehend"):
    client = boto3.client(service, region_name=region)
    return client


def batch_detection_entities(client, bucket_name, file_prefix, comprehend_role):
    # Give a name to the Job using random string
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
    # Implement list using filter
    response = client.list_entities_detection_jobs( 
        Filter={
            'JobStatus' : 'IN_PROGRESS'
        }
    )
    print(response)

if __name__ == "__main__":

    # S3 file will be passed as an event to the Lambda function.
    bucket_name = os.getenv("BUCKET_NAME", "")
    file_prefix = "textract/output/viagens_da_minha_terra.txt"

    # Role that comprehend will use
    comprehend_role = os.getenv("COMPREHEND_ROLE", "arn:aws:iam::000000:role/comprehend_role_s3_full")

    client = aws_connection()

    if "detect" in sys.argv[1]:
        batch_detection_entities(client, bucket_name, file_prefix, comprehend_role)

    list_detection_jobs(client)