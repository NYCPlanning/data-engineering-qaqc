import pandas as pd
from typing import Dict

BUCKET_NAME = "edm-publishing"


def get_data(branch):
    rv = {}
    if branch == "dev":
        url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-colp/{branch}/latest/output/qaqc"
    else:
        url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-colp/{branch}/latest/output"

    rv["ipis_cd_errors"] = csv_from_DO(f"{url}/ipis_cd_errors.csv")
    rv["geospatial_check"] = csv_from_DO(f"{url}/geospatial_check.csv")
    return rv


def csv_from_DO(url, kwargs={}):
    return pd.read_csv(url, **kwargs)
