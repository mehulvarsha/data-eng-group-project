"""
Description:
1. Initialization:
Import necessary modules and initialize the Glue job with provided arguments.

2. Creating Dynamic Frame:
Create a dynamic frame from CSV data stored in an S3 bucket.
Options are specified to handle CSV format and to specify options like quote character, header presence, and separator.

3. Applying Mapping:
Apply mapping to the dynamic frame to rename fields and cast them to appropriate data types.
This step ensures consistency in the schema and prepares the data for further processing.

4. Writing Transformed Data:
Write the transformed data to another S3 location in Glue Parquet format.
Partition the data based on the "region" column.
Use Snappy compression for optimized storage.

5. Committing Job:
Commit the Glue job, indicating successful execution.
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Get job name from command-line arguments
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

# Initialize SparkContext
sc = SparkContext()

# Initialize GlueContext
glueContext = GlueContext(sc)

# Get SparkSession from GlueContext
spark = glueContext.spark_session

# Initialize Glue job
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Create dynamic frame from S3 CSV data
raw_data_node1 = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ",",
        "optimizePerformance": False,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": ["s3://de0166-youtube-raw-eunorth1-dev/youtube/raw_statistics_data/"],
        "recurse": True,
    },
    transformation_ctx="raw_data_node1",
)

# Apply mapping to dynamic frame
ApplyMapping_node2 = ApplyMapping.apply(
    frame=raw_data_node1,
    mappings=[
        ("video_id", "string", "video_id", "string"),
        ("trending_date", "string", "trending_date", "string"),
        ("title", "string", "title", "string"),
        ("channel_title", "string", "channel_title", "string"),
        ("category_id", "string", "category_id", "bigint"),
        ("publish_time", "string", "publish_time", "string"),
        ("tags", "string", "tags", "string"),
        ("views", "string", "views", "bigint"),
        ("likes", "string", "likes", "bigint"),
        ("dislikes", "string", "dislikes", "bigint"),
        ("comment_count", "string", "comment_count", "bigint"),
        ("thumbnail_link", "string", "thumbnail_link", "string"),
        ("comments_disabled", "string", "comments_disabled", "boolean"),
        ("ratings_disabled", "string", "ratings_disabled", "boolean"),
        ("description", "string", "description", "string"),
        ("region", "string", "region", "string"),
    ],
    transformation_ctx="ApplyMapping_node2",
)

# Write transformed data to S3 in Glue Parquet format
transformed_data_node3 = glueContext.write_dynamic_frame.from_options(
    frame=ApplyMapping_node2,
    connection_type="s3",
    format="glueparquet",
    connection_options={
        "path": "s3://de0166-youtube-cleansed-eunorth1-dev/youtube/raw_statistics/",
        "partitionKeys": ["region"],
    },
    format_options={"compression": "snappy"},
    transformation_ctx="transformed_data_node3",
)

# Commit the job
job.commit()
