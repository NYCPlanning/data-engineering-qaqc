import boto3
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
from io import StringIO
import os
from dotenv import load_dotenv
import pdb
import streamlit as st

load_dotenv()


class DigitalOceanClient:
    def __init__(self, bucket_name, repo_name):
        self.bucket_name = bucket_name
        self.repo_name = repo_name

    def cache_key(self, url):
        return str(
            self.s3_resource()
            .ObjectSummary(bucket_name=self.bucket_name, key=url)
            .last_modified
        )

    def bucket(self):
        return self.s3_resource().Bucket(self.bucket_name)

    def get_folders(self):
        return self.bucket().objects.filter(Prefix=f"{self.repo_name}/")

    def unzip_csv(self, csv_filename, zipfile):
        try:
            with zipfile.open(csv_filename) as csv:
                return pd.read_csv(csv, true_values=["t"], false_values=["f"])
        except:
            return None

    def s3_resource(self):
        return boto3.resource(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            endpoint_url=os.getenv("AWS_S3_ENDPOINT"),
        )

    # @st.experimental_memo
    def csv_from_DO(_self, url, cache_key, _kwargs={}):
        try:
            if _self.bucket_name == "edm-publishing":
                return pd.read_csv(url, **_kwargs)
            else:
                return _self.private_csv_from_DO(url, _kwargs)
        except:
            return None

    def private_csv_from_DO(self, url, kwargs):
        obj = self.s3_resource().Object(bucket_name=self.bucket_name, key=url)
        s = str(obj.get()["Body"].read(), "utf8")
        data = StringIO(s)

        return pd.read_csv(data, encoding="utf8", **kwargs)

    def zip_from_DO(self, zip_filename):
        zip_obj = self.s3_resource().Object(
            bucket_name=self.bucket_name, key=zip_filename
        )
        buffer = BytesIO(zip_obj.get()["Body"].read())

        return ZipFile(buffer)
