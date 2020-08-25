import boto3
import tarfile
import json
import awswrangler as wr
import pandas as pd
import os

def read_tar_file(file_path):
    tar = tarfile.open(file_path, "r:gz")
    for member in tar.getmembers():
        f = tar.extractfile(member)
        if f is not None:
            content = f.read()
            return content


def aggregate_return_comprehend(file_name, comprehend_response):
    dict_count_type = {"ID" : file_name , "COMMERCIAL_ITEM" : 0, "DATE" : 0, "EVENT" : 0, 
        "LOCATION" : 0, "ORGANIZATION" : 0, "OTHER" : 0, "PERSON" : 0, "QUANTITY" : 0, "TITLE" : 0}
    for entities in comprehend_response["Entities"]:
        dict_count_type[entities.get("Type")] += 1

    return dict_count_type

def covert_df_to_parquet(df, s3_path, database_name, table):
    """
        Convert dataframe to parquet and create Glue Catalog
    """
    wr.s3.to_parquet(
        df=df,
        path=f"s3://{s3_path}",
        dataset=True,
        mode="append",
        database=database_name,
        table=table
    )


def get_s3_file(bucket_name, file_path_s3, file_path_local):
    s3 = boto3.client('s3')
    response = s3.download_file(bucket_name, file_path_s3, file_path_local)

    print(response)


def lambda_handler(event, context):
    # Get the file from S3 this will be passed from event
    file_path_local = "/tmp/output.tar.gz"
    file_path_s3 = event["Records"][0]["s3"]["object"]["key"]
    bucket_name = os.getenv("BUCKET_NAME", "")

    table_name = "book_insight_table"
    database_name_glue = "npl_textract_comprehend"
    table_name_glue= "analysis_table_comprehend"

    # TODO: Think in a way to link the file_name, randonly generate
    file_name = "ViagensNaMinhaTerra"

    get_s3_file(bucket_name, file_path_s3, file_path_local)

    lodaded_file = read_tar_file(file_path_local)
    
    dict_comprehend_analysis = json.loads(lodaded_file)
    
    aggregate_dictionary = aggregate_return_comprehend(file_name, dict_comprehend_analysis)

    df = pd.DataFrame([list(aggregate_dictionary.values())], columns=["ID", "COMMERCIAL_ITEM", "DATE", "EVENT", "LOCATION",
        "ORGANIZATION", "OTHER", "PERSON", "QUANTITY", "TITLE"])

    s3_path = f"{bucket_name}/stage_data/"

    if database_name_glue not in wr.catalog.databases().values:
        wr.catalog.create_database(database_name_glue)

    # Upload file to s3 and update the Glue Catalog
    covert_df_to_parquet(df, s3_path, database_name_glue, table_name_glue)