import boto3
import zipfile

def main():
    print("Starting environment setup...")
    s3_lambda_code = input("Type the s3 bucket that will be created to store your lambda code: ")
    ecr_repository_name = input("Type the desired ECR repository name: ")

if __name__ == "__main__":
    main()