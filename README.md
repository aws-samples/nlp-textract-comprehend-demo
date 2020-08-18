# nlp-analysis-demo

The purpose of this demo is to build a stack that uses Amazon Comprehend and Amazon Textract to analyze unstructured data and generate insights and trendsn from it.

# Overview

In this demonstration we are going to build a stack to extract text from a PDF document that will be uploaded in Amazon S3, run comprehend against the text to generate aggregate and generate insights using **start_entities_detection_job** API call.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [awscli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
- [Pre configured AWS credentials](https://docs.aws.amazon.com/amazonswf/latest/awsrbflowguide/set-up-creds.html)
- [Pre configured VPC with minimun of 2 public subnets]()


# Architecture Diagram

<p align="center"> 
<img src="images/nlp-demo.png">
</p>


# Setup instructions

First of all we need to setup the foundation for our solution, that consists of create the bucket to store our lambda code and the ECR to store our worker docker image.

A script was developed to help in that task, simple run:

```bash
./setup.sh
```

The output will be the follow:

```yaml
Starting environment setup...


Creating ECR Repository...
Created ECR Repository: xxxxx.dkr.ecr.us-east-1.amazonaws.com/ai-comprehend-ml

Creating S3 Bucket...
Created S3 Bucket: lambdacode-sadasd

File zipped: lambda_comprehend.zip
File zipped: lambda_textract.zip
File zipped: lambda_data_wrangler.zip

Building docker image and pushing to ecr...

Uploading all required files to S3...

"Information that will be used in CloudFormation:":
BucketLambdaCode: lambdacode-sadasd
ImageUrl: xxxx.dkr.ecr.us-east-1.amazonaws.com/ai-comprehend-ml:latest
```

We are going to use the **BucketLambdaCode** and **ImageUrl** later on the demonstration.

## CloudFormation

In this repository we have two CloudFormation Templates that we are going to use to provision the stack.

### Serveless Stack Template:

```bash
aws cloudformation create-stack --stack-name serverless-npl-stack \
--template-body file://cloudformation/serverless-stack.yaml --parameters \ 
ParameterKey=BucketName,ParameterValue=<BUCKET_NAME> \
ParameterKey=BucketLambdaCode,ParameterValue=<BUCKET_LAMBDA_CODE> \
ParameterKey=LanguageCode,ParameterValue=pt --capabilities CAPABILITY_IAM
```

### ECS Worker Stack Template:

```bash
aws cloudformation create-stack --stack-name ecs-npl-stack \
--template-body file://cloudformation/ecs-stack.yaml --parameters \ 
ParameterKey=ClusterName,ParameterValue=ecs-cluster-demo \ 
ParameterKey=ServiceName,ParameterValue=textract-worker \
ParameterKey=ImageUrl,ParameterValue=<IMAGE_URL> \ 
ParameterKey=BucketName,ParameterValue=<BUCKET_NAME> \ 
ParameterKey=QueueName,ParameterValue=<QUEUE_NAME> \ 
ParameterKey=VpcId,ParameterValue=<VPC_ID> \ 
ParameterKey=VpcCidr,ParameterValue=<VPC_CIDR> \ 
ParameterKey=PubSubnet1Id,ParameterValue=<PUB_SUBNET_1_ID> \ 
ParameterKey=PubSubnet2Id,ParameterValue=<PUB_SUBNET_2_ID> \ 
--capabilities CAPABILITY_IAM
```

# TODO

- Update README (Instructions and Quicksight Dashboard Creation)