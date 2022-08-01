# from asyncio.windows_events import NULL
import csv
from io import StringIO
import streamlit as st
import os
import pandas as pd
import boto3
from dotenv import load_dotenv
import geopandas as gpd
from zipfile import ZipFile
from io import BytesIO
import pdb

load_dotenv()

BUCKET_NAME = "edm-private"

VIZKEY = {
    "all categories": {
        "projects": {"values": ["totalcount", "mapped"]},
        "commitments": {"values": ["totalcommit", "mappedcommit"]},
    },
    "fixed assets": {
        "projects": {"values": ["fixedasset", "fixedassetmapped"]},
        "commitments": {"values": ["fixedassetcommit", "fixedassetmappedcommit"]},
    },
}

"""a feedback from the group is to have a dictionary from the abbreviation for agency for something more explicity
where would this list comes from? """


def get_data(branch, table) -> dict:
    rv = {}
    # for table in ['magency', 'sagency']:
    rv[table] = csv_from_DO(
        url=f"db-cpdb/{branch}/latest/output/analysis/cpdb_summarystats_{table}.csv",
        bucket=BUCKET_NAME,
    )

    # this could be modified once open data for cpdb is set up
    rv["pre_" + table] = csv_from_DO(
        url=f"db-cpdb/{branch}/2022-04-15/output/analysis/cpdb_summarystats_{table}.csv",
        bucket=BUCKET_NAME,
    )

    return rv


def get_geometries(branch) -> dict:
    rv = {}
    points_zip = zip_from_DO(
        zip_filename=f"db-cpdb/{branch}/latest/output/cpdb_dcpattributes_pts.shp.zip",
        bucket=BUCKET_NAME,
    )
    rv["points"] = unzip_shapefile(
        zipfile=points_zip, shapefile_name="cpdb_dcpattributes_pts.shp"
    )


def get_commit_cols(df: pd.DataFrame):
    full_cols = df.columns
    cols = [c for c in full_cols if "commit" in c]
    return cols


def get_diff_dataframe(df: pd.DataFrame, df_pre: pd.DataFrame):
    diff = df.sub(df_pre, fill_value=0)
    return diff


def get_map_percent_diff(df: pd.DataFrame, df_pre: pd.DataFrame, keys: dict):

    diff = pd.DataFrame(
        columns=["percent_mapped", "pre_percent_mapped", "diff_percent_mapped"],
        index=df.index,
    )

    diff["percent_mapped"] = df[keys["values"][1]] / df[keys["values"][0]]
    diff["pre_percent_mapped"] = df_pre[keys["values"][1]] / df_pre[keys["values"][0]]
    diff["diff_percent_mapped"] = diff.percent_mapped - diff.pre_percent_mapped
    diff.sort_values(by="diff_percent_mapped", inplace=True, ascending=True)

    return diff


def sort_base_on_option(
    df: pd.DataFrame, subcategory, view_type, map_option, ascending=True
):

    df_sort = df.sort_values(
        by=VIZKEY[subcategory][view_type]["values"][map_option], ascending=ascending
    )

    return df_sort


def unzip_shapefile(shapefile_name, zipfile):
    try:
        with zipfile as zf:

            pdb.set_trace()
            # return gpd.read_file(shapefile)
    except:
        return None


def zip_from_DO(zip_filename, bucket):
    zip_obj = s3_resource().Object(bucket_name=bucket, key=zip_filename)
    buffer = BytesIO(zip_obj.get()["Body"].read())

    return ZipFile(buffer)


def csv_from_DO(url, bucket):
    obj = s3_resource().Object(bucket_name=BUCKET_NAME, key=url)
    s = str(obj.get()["Body"].read(), "utf8")
    data = StringIO(s)
    return pd.read_csv(data, encoding="utf8")


def s3_resource():
    return boto3.resource(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("AWS_S3_ENDPOINT"),
    )
