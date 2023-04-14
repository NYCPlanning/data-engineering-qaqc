import requests
import json
import boto3
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
from io import StringIO
import os
from dotenv import load_dotenv
import streamlit as st
import geopandas as gpd

# DEV temprary
DATASET_NAME = "db-zoningtaxlots"

INPUT_DATA_URL = lambda dataset, version: (
    f"https://edm-recipes.nyc3.cdn.digitaloceanspaces.com/datasets/{dataset}/{version}/{dataset}.sql"
)

INPUT_CONFIG_URL = lambda dataset, version: (
    f"https://edm-recipes.nyc3.cdn.digitaloceanspaces.com/datasets/{dataset}/{version}/config.json"
)

OUTPUT_DATA_DIRECTORY_URL = lambda dataset, version: (
    f"https://edm-publishing.nyc3.digitaloceanspaces.com/{dataset}/{version}/output/"
)

load_dotenv()


def get_datatset_config(dataset: str, version: str) -> dict:
    response = requests.get(
        INPUT_CONFIG_URL(dataset=dataset, version=version), timeout=10
    )
    return json.loads(response.text)


@st.cache_data
def get_latest_build_version() -> str:
    return requests.get(
        f"{OUTPUT_DATA_DIRECTORY_URL(dataset=DATASET_NAME, version='latest')}version.txt",
        timeout=10,
    ).text


@st.cache_data
def get_source_data_versions_from_build(version: str) -> pd.DataFrame:
    source_data_versions = pd.read_csv(
        f"{OUTPUT_DATA_DIRECTORY_URL(dataset=DATASET_NAME, version=version)}source_data_versions.csv",
        index_col=False,
        dtype=str,
    )
    source_data_versions.rename(
        columns={
            "schema_name": "datalibrary_name",
            "v": "version",
        },
        errors="raise",
        inplace=True,
    )
    source_data_versions.sort_values(
        by=["datalibrary_name"], ascending=True
    ).reset_index(drop=True, inplace=True)
    source_data_versions.set_index("datalibrary_name", inplace=True)
    return source_data_versions


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

    def get_all_filenames_in_folder(self, folder_path: str):
        filenames = set()
        for object in self.bucket.objects.filter(Prefix=f"{folder_path}/"):
            filenames.add(object.key.split("/")[-1])
        return filenames

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
