import boto3
import sys
from botocore.exceptions import ClientError
import zipfile
import docker
from base64 import b64decode
from termcolor import colored

def aws_connection(service_name, region_name="us-east-1"):
    client = boto3.client(service_name, region_name=region_name)
    return client


def create_ecr_respository(client, repository_name):
    response = client.create_repository(repositoryName=repository_name)
    respository_uri = response["repository"]["repositoryUri"]
    return respository_uri


def create_bucket(client, bucket_name):
    response = client.create_bucket(
        ACL = "private",
        Bucket = bucket_name
    )
    return response["Location"]


def zip_all_functions(dict_lambda):

    for lambda_zip_file, file_path in dict_lambda.items():
        zip_file_name = lambda_zip_file.split("/")[1]
        zip_file = zipfile.ZipFile(f"/tmp/{zip_file_name}", 'w')
        zip_file.write(file_path, compress_type=zipfile.ZIP_DEFLATED)
        zip_file.close()
        print(f"File zipped: {zip_file_name}")


def ecr_build_image_and_push(image_uri_repository, version_number):
    
    # The ECR Repository URI
    repo = image_uri_repository
    # The region your ECR repo is in
    region = "us-east-1"
    # How you want to tag your project locally
    local_tag = "ai-ml-comprehend"
    # Path where Dockerfile is stored
    dockerfile_path = "./textract/textract_worker/"
    #Set up a session
    session = boto3.Session(region_name=region)
    ecr = session.client('ecr')

    docker_api = docker.APIClient()

    # Build image with local tag
    response = docker_api.build(path=dockerfile_path, tag=local_tag)

    # Make auth call and parse out results
    auth = ecr.get_authorization_token()
    token = b64decode(auth['authorizationData'][0]['authorizationToken'])
    username, password = token.decode('utf-8').split(':', 1)

    endpoint = auth["authorizationData"][0]["proxyEndpoint"]

    auth_config_payload = {'username': username, 'password': password}
    version_tag = repo + ':latest'

    # Tagging local version to ecr version
    if docker_api.tag(local_tag, version_tag) is False:
        raise RuntimeError("Tag appeared to fail: " + version_tag)

    # Pushing image to repository ECR
    response = docker_api.push(version_tag, auth_config=auth_config_payload)

    # Removing taged deployment images
    # You will still have the local_tag image if you need to troubleshoot
    docker_api.remove_image(version_tag, force=True)
    return version_tag


def upload_file(s3_client, file_name, bucket, object_name=None):
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
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def main():
    print("Starting environment setup...\n")
    # bucket_s3_lambda_code = input("Type the s3 bucket that will be created to store your lambda code: ")
    # ecr_repository_name = input("Type the desired ECR repository name: ")

    bucket_s3_lambda_code = sys.argv[1]
    ecr_repository_name = sys.argv[2]
    
    ecr_client = aws_connection("ecr", "us-east-1")
    print("\nCreating ECR Repository...")
    repository_uri = create_ecr_respository(ecr_client, ecr_repository_name)
    print(f"Created ECR Repository: {repository_uri}\n")
    s3_client = aws_connection("s3", "us-east-1")
    print("Creating S3 Bucket...")
    create_bucket(s3_client, bucket_s3_lambda_code)
    print(f"Created S3 Bucket: {bucket_s3_lambda_code}\n")

    dict_lambda = {"lambda/lambda_comprehend.zip" : "./comprehend/lambda_function.py", 
        "lambda/lambda_textract.zip" : "./textract/lambda_function.py",
        "lambda/lambda_data_wrangler.zip" : "./athena_glue/lambda_function.py"}
    
    # Zip all lambda code that will be uploaded to s3
    zip_all_functions(dict_lambda)

    # Build docker image and push to Amazon ECR
    print("\nBuilding docker image and pushing to ecr...\n")
    image_url = ecr_build_image_and_push(repository_uri, "latest")
    print("Uploading all required files to S3...\n")
    # Uploading files to Amazon S3
    for object_name, code_path in dict_lambda.items():
        zip_file_name = "/tmp/" + (object_name.split("/")[1])
        upload_file(s3_client, zip_file_name, bucket_s3_lambda_code, object_name)
    
    lambda_layer_path = "./athena_glue/awswrangler-layer-1.8.1-py3.6.zip"
    lambda_layer_object_name = "layer/awswrangler-layer-1.8.1-py3.6.zip"
    upload_file(s3_client, lambda_layer_path, bucket_s3_lambda_code, lambda_layer_object_name)
    print(colored('"Information that will be used in CloudFormation:":', 'green'))
    # TODO: Colored Printing the information that will be used in CloudFormation
    print(colored('BucketLambdaCode:', 'red'), bucket_s3_lambda_code)
    print(colored('ImageUrl:', 'red'), image_url)

if __name__ == "__main__":
    main()