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

    @property
    def bucket(self):
        return self.s3_resource.Bucket(self.bucket_name)

    @property
    def bucket_is_public(self):
        return self.bucket_name == "edm-publishing"

    @property
    def repo(self):
        return self.bucket.objects.filter(Prefix=f"{self.repo_name}/")

    @property
    def s3_resource(self):
        return boto3.resource(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            endpoint_url=os.getenv("AWS_S3_ENDPOINT"),
        )

    def get_all_folder_names_in_repo_folder(self):
        all_folders = set()

        for obj in self.repo:
            all_folders.add(obj._key.split("/")[1])

        return all_folders

    def get_all_filenames_in_folder(self, folder: str):
        # TODO
        return None

    def unzip_csv(self, csv_filename, zipfile):
        try:
            with zipfile.open(csv_filename) as csv:
                return pd.read_csv(csv, true_values=["t"], false_values=["f"])
        except:
            return None

    def shapefile_from_DO(self, shapefile_zip):
        try:
            zip_obj = self.s3_resource.Object(
                bucket_name=self.bucket_name, key=shapefile_zip
            )
            buffer = BytesIO(zip_obj.get()["Body"].read())

            return gpd.read_file(buffer)
        except:
            st.info(
                f"There was an issue downloading {shapefile_zip} from Digital Ocean"
            )

    def csv_from_DO(self, url, kwargs={}):
        try:
            if self.bucket_is_public:
                return self.public_csv_from_DO(url, kwargs)
            else:
                return self.private_csv_from_DO(url, kwargs)
        except:
            st.info(f"There was an issue downloading {url} from Digital Ocean.")

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
