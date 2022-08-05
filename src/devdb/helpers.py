import pandas as pd
from typing import Dict

BUCKET_NAME = "edm-publishing"


def get_data(branch):
    rv = {}
    url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-developments/{branch}/latest/output"

    rv["qaqc_app"] = csv_from_DO(
        f"{url}/qaqc_app.csv", kwargs={"dtype": {"job_number": "str"}}
    )

    return rv


def csv_from_DO(url, kwargs={}):
    return pd.read_csv(url, **kwargs)
