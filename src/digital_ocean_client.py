import boto3
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
from io import StringIO
import os
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime
import shutil
import geopandas as gpd

load_dotenv()


class DigitalOceanClient:
    def __init__(self, bucket_name, repo_name):
        self.bucket_name = bucket_name
        self.repo_name = repo_name
        self.s3_resource = self.get_s3_resource()

    def bucket(self):
        return self.s3_resource.Bucket(self.bucket_name)

    def bucket_is_public(self):
        return self.bucket_name == "edm-publishing"

    def get_folders(self):
        return self.bucket().objects.filter(Prefix=f"{self.repo_name}/")

    def unzip_csv(self, csv_filename, zipfile):
        try:
            with zipfile.open(csv_filename) as csv:
                return pd.read_csv(csv, true_values=["t"], false_values=["f"])
        except:
            return None

    def unzip_shapefile(self, table, zipfile):
        try:
            with zipfile as zf:
                time = str(datetime.now().timestamp)
                zf.extractall(path=f".library/{time}/{table}/")
                gdf = gpd.read_file(f".library/{time}/{table}/{table}.shp")
                shutil.rmtree(path=f".library/{time}")
                return gdf
        except:
            return None

    def get_s3_resource(self):
        return boto3.resource(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            endpoint_url=os.getenv("AWS_S3_ENDPOINT"),
        )

    def csv_from_DO(self, url, kwargs={}):
        try:
            if self.bucket_is_public():
                return self.public_csv_from_DO(url, kwargs)
            else:
                return self.private_csv_from_DO(url, kwargs)
        except:
            return None

    def public_csv_from_DO(self, url, kwargs):
        return pd.read_csv(url, **kwargs)

    def private_csv_from_DO(self, url, kwargs):
        obj = self.s3_resource.Object(bucket_name=self.bucket_name, key=url)
        s = str(obj.get()["Body"].read(), "utf8")
        data = StringIO(s)

        return pd.read_csv(data, encoding="utf8", **kwargs)

    def zip_from_DO(self, zip_filename):
        zip_obj = self.s3_resource.Object(
            bucket_name=self.bucket_name, key=zip_filename
        )
        buffer = BytesIO(zip_obj.get()["Body"].read())

        return ZipFile(buffer)
