"""
AWS Lambda function for processing JSON files from an S3 bucket and storing the extracted data in Parquet format.

This Lambda function listens to an S3 bucket for new JSON files. Upon detecting a new file, it reads the JSON data,
extracts the required columns, and stores the processed data in Parquet format in another location specified by
environment variables. The function utilizes AWS Glue Catalog to maintain metadata about the stored data.

Environment Variables:
- s3_cleansed_layer: The S3 path where the processed data will be stored in Parquet format.
- glue_catalog_db_name: The name of the AWS Glue catalog database.
- glue_catalog_table_name: The name of the table in the AWS Glue catalog.
- write_data_operation: The mode of operation for writing data (e.g., 'overwrite', 'append').

Libraries Used:
- awswrangler: A utility library that allows to access files from S3

"""

import awswrangler as wr
import pandas as pd
import urllib.parse
import os

# Retrieving environment variables
os_input_s3_cleansed_layer = os.environ['s3_cleansed_layer']
os_input_glue_catalog_db_name = os.environ['glue_catalog_db_name']
os_input_glue_catalog_table_name = os.environ['glue_catalog_table_name']
os_input_write_data_operation = os.environ['write_data_operation']

def lambda_handler(event, context):
    # Extracting bucket and key from S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        # Reading JSON data from S3
        df_raw = wr.s3.read_json('s3://{}/{}'.format(bucket, key))

        # Extracting required columns from JSON
        df_step_1 = pd.json_normalize(df_raw['items'])

        # Writing DataFrame to Parquet format in S3 and Glue catalog
        wr_response = wr.s3.to_parquet(
            df=df_step_1,
            path=os_input_s3_cleansed_layer,
            dataset=True,
            database=os_input_glue_catalog_db_name,
            table=os_input_glue_catalog_table_name,
            mode=os_input_write_data_operation
        )

        return wr_response
    except Exception as e:
        # Handling exceptions
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
