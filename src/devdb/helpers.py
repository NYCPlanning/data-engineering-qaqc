import pandas as pd
from typing import Dict
from dotenv import load_dotenv


load_dotenv()

BUCKET_NAME = "edm-publishing"


def get_data(branch):
    rv = {}
    url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-developments/latest/output"

    rv["qaqc_app"] = csv_from_DO(
        f"{url}/qaqc_app.csv", kwargs={"dtype": {"job_number": "str"}}
    )

    return rv


def csv_from_DO(url, kwargs={}):
    return pd.read_csv(url, **kwargs)
