import pandas as pd
from typing import Dict

BUCKET_NAME = "edm-publishing"


def get_data(branch):
    rv = {}
    url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-colp/{branch}/latest/output"

    rv["ipis_cd_errors"] = csv_from_DO(f"{url}/ipis_cd_errors.csv")
    return rv


def csv_from_DO(url, kwargs={}):
    return pd.read_csv(url, **kwargs)
