# nlp-analysis-demo

A project that allows you to analyze unstructured data and generate insights and trends from it using Amazon Comprehend and Amazon Textract

# Architecture

<p align="center"> 
<img src="images/nlp-demo.png">
</p>

# TODO

- Create python script to upload all the information to s3 and prepare the environment.
    - Create S3 to upload lambda code
    - Create ECR Registry
    - Zip all lambda code and upload do S3
    - Upload lambda layer
    - Build docker image and upload to ECR

- Update README (Instructions and Quicksight Dashboard Creation)