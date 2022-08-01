from zipfile import ZipFile
from io import BytesIO
import boto3
import os


def zip_from_DO(zip_filename, bucket):
    zip_obj = s3_resource().Object(bucket_name=bucket, key=zip_filename)
    buffer = BytesIO(zip_obj.get()["Body"].read())

    return ZipFile(buffer)


def s3_resource():
    return boto3.resource(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("AWS_S3_ENDPOINT"),
    )
