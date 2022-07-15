import boto3
import re
import pandas as pd
from datetime import datetime
import json
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()


def get_data(branch) -> Dict[str, pd.DataFrame]:
    rv = {}
    url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-pluto/{branch}/latest/output/qaqc"
    rv["df_mismatch"] = csv_from_DO(f"{url}/qaqc_mismatch.csv")
    rv["df_null"] = csv_from_DO(f"{url}/qaqc_null.csv")
    rv["df_aggregate"] = csv_from_DO(f"{url}/qaqc_aggregate.csv")
    df_expected = csv_from_DO(f"{url}/qaqc_expected.csv")
    df_expected["expected"] = df_expected["expected"].apply(json.loads)
    rv["df_expected"] = df_expected

    source_data_versions = pd.read_csv(
        f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-pluto/{branch}/latest/output/source_data_versions.csv"
    )
    rv["source_data_version"] = source_data_versions
    sdv = source_data_versions.to_dict("records")
    version = {}
    for i in sdv:
        version[i["schema_name"]] = i["v"]
    rv[
        "version_text"
    ] = f"""
        Department of City Planning – E-Designations: ***{convert(version['dcp_edesignation'])}***  
        Department of City Planning – Georeferenced NYC Zoning Maps: ***{convert(version['dcp_zoningmapindex'])}***  
        Department of City Planning – NYC City Owned and Leased Properties: ***{convert(version['dcp_colp'])}***  
        Department of City Planning – NYC GIS Zoning Features: ***{convert(version['dcp_zoningdistricts'])}***  
        Department of City Planning – Political and Administrative Districts: ***{convert(version['dcp_cdboundaries_wi'])}***  
        Department of City Planning – Geosupport version: ***{convert(version['dcp_cdboundaries_wi'])}***  
        Department of Finance – Digital Tax Map (DTM): ***{convert(version['dof_dtm'])}***  
        Department of Finance – Mass Appraisal System (CAMA): ***{convert(version['pluto_input_cama_dof'])}***  
        Department of Finance – Property Tax System (PTS): ***{convert(version['pluto_pts'])}***  
        Landmarks Preservation Commission – Historic Districts: ***{convert(version['lpc_historic_districts'])}***  
        Landmarks Preservation Commission – Individual Landmarks: ***{convert(version['lpc_landmarks'])}***  
    """

    return rv


def get_branches():
    all_branches = set()
    resource = boto3.resource(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("AWS_S3_ENDPOINT"),
    )
    pub_bucket = resource.Bucket("edm-publishing")
    for obj in pub_bucket.objects.filter(Prefix="db-pluto/"):
        all_branches.add(obj._key.split("/")[1])
    rv = blacklist_branches(all_branches)
    return rv


def convert(dt):
    try:
        d = datetime.strptime(dt, "%Y/%m/%d")
        return d.strftime("%m/%d/%y")
    except BaseException:
        return dt


def blacklist_branches(branches):
    """For pluto this is done by programmatically, can also be hard-coded"""
    rv = []
    for b in branches:
        if (
            re.match(r"[0-9]{2}v[0-9]", b) is None
            and re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", b) is None
        ) and b != 'latest':
            rv.append(b)
    return rv


def csv_from_DO(url):
    return pd.read_csv(url, true_values=["t"], false_values=["f"])