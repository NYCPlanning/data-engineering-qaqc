from io import StringIO
import streamlit as st
import os
import pandas as pd
import boto3
from dotenv import load_dotenv

load_dotenv()

def get_data(branch) -> dict:
    rv = {}

    client = boto3.client(
        "s3",
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url = os.getenv("AWS_S3_ENDPOINT")
    )
    for table in ['magency', 'sagency']:
        obj = client.get_object(
            Bucket="edm-private",
            Key=f"db-cpdb/{branch}/latest/output/analysis/cpdb_summarystats_{table}.csv",
        )
        s = str(obj["Body"].read(), "utf8")
        data = StringIO(s)
        df = pd.read_csv(data, encoding='utf8')
        rv[table] = df

        # this could be modified once open data for cpdb is set up
        obj = client.get_object(
            Bucket="edm-private",
            Key=f"db-cpdb/{branch}/2022-04-15/output/analysis/cpdb_summarystats_{table}.csv",
        )
        s = str(obj["Body"].read(), "utf8")
        data = StringIO(s)
        df = pd.read_csv(data, encoding='utf8')
        rv['pre_' + table] = df

    return rv