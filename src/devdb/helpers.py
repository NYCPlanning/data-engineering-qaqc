import boto3
import re
import pandas as pd
from datetime import datetime
import json
from typing import Dict
import os
from dotenv import load_dotenv
from zipfile import ZipFile
from io import BytesIO

load_dotenv()

BUCKET_NAME = "edm-publishing"


def get_data() -> Dict[str, pd.DataFrame]:
    rv = {}
    url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-developments/latest/output"
    rv["qaqc_app"] = csv_from_DO(f"{url}/qaqc_app.csv")

    return rv


def csv_from_DO(url, kwargs={}):
    return pd.read_csv(url, **kwargs)
