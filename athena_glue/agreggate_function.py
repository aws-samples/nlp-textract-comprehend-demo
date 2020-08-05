import boto3
import tarfile
import json
import awswrangler as wr
import pandas as pd

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
    for entities in dict_comprehend_analysis["Entities"]:
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


if __name__ == "__main__":

    # Get the file from S3 this will be passed from event
    file_path_local = "/tmp/output.tar.gz"
    file_path_s3 = "comprehend/output/936068047509-NER-9d86562ddba8c746dfc773038126fb48/output/output.tar.gz"
    bucket_name = "textract-test-aneel"

    table_name = "book_insight_table"
    database_name_glue = "npl_textract_comprehend"
    table_name_glue= "analysis_table_comprehend"

    # TODO: Think in a way to link the file_name
    file_name = "AsCidadesEAsSerras"

    get_s3_file(bucket_name, file_path_s3, file_path_local)

    lodaded_file = read_tar_file(file_path_local)
    dict_comprehend_analysis = json.loads(lodaded_file)
    aggregate_dictionary = aggregate_return_comprehend(file_name, dict_comprehend_analysis)

    df = pd.DataFrame([list(aggregate_dictionary.values())], columns=["ID", "COMMERCIAL_ITEM", "DATE", "EVENT", "LOCATION",
        "ORGANIZATION", "OTHER", "PERSON", "QUANTITY", "TITLE"])

    s3_path = "textract-test-aneel/stage_data/"

    if database_name_glue not in wr.catalog.databases().values:
        wr.catalog.create_database(database_name_glue)

    # Upload file to s3 and update the Glue Catalog
    covert_df_to_parquet(df, s3_path, database_name_glue, table_name_glue)


