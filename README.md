# nlp-analysis-demo

A project that allows you to analyze unstructured data and generate insights and trends from it using Amazon Comprehend and Amazon Textract

# Architecture

<p align="center"> 
<img src="images/nlp-demo.png">
</p>

# TODO
- Break textract fili into smaller ones that will be used to provision the lambda functions.
- From textract create the worker that will run in a Docker container using ECS (Process textract job resultset)