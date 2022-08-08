import re
import pandas as pd
from datetime import datetime
import json
from typing import Dict
from dotenv import load_dotenv
from src.digital_ocean_client import DigitalOceanClient

load_dotenv()

BUCKET_NAME = "edm-publishing"
REPO_NAME = "db-pluto"


def get_data(branch) -> Dict[str, pd.DataFrame]:
    rv = {}
    url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-pluto/{branch}/latest/output"

    client = digital_ocean_client()
    kwargs = {"true_values": ["t"], "false_values": ["t"]}
    rv["df_mismatch"] = client.csv_from_DO(f"{url}/qaqc/qaqc_mismatch.csv", kwargs)
    rv["df_null"] = client.csv_from_DO(f"{url}/qaqc/qaqc_null.csv", kwargs)
    rv["df_aggregate"] = client.csv_from_DO(f"{url}/qaqc/qaqc_aggregate.csv", kwargs)
    rv["df_expected"] = client.csv_from_DO(
        f"{url}/qaqc/qaqc_expected.csv",
        kwargs={"converters": {"expected": json.loads}} | kwargs,
    )
    rv["df_outlier"] = client.csv_from_DO(
        f"{url}/qaqc/qaqc_outlier.csv",
        kwargs={"converters": {"outlier": json.loads}} | kwargs,
    )

    pluto_corrections_zip = client.zip_from_DO(
        zip_filename=f"db-pluto/{branch}/latest/output/qaqc/pluto_corrections.zip",
    )

    rv["pluto_corrections"] = client.unzip_csv(
        csv_filename="pluto_corrections.csv", zipfile=pluto_corrections_zip
    )

    rv["pluto_corrections_applied"] = client.unzip_csv(
        csv_filename="pluto_corrections_applied.csv", zipfile=pluto_corrections_zip
    )
    rv["pluto_corrections_not_applied"] = client.unzip_csv(
        csv_filename="pluto_corrections_not_applied.csv", zipfile=pluto_corrections_zip
    )

    source_data_versions = client.csv_from_DO(f"{url}source_data_versions.csv")

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

    for obj in digital_ocean_client().get_folders():
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
    version_regex = r"[0-9]{2}v[0-9]"
    data_regex = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
    for b in branches:
        if (
            re.match(version_regex, b) is None and re.match(data_regex, b) is None
        ) and b != "latest":
            rv.append(b)
    return rv


def digital_ocean_client():
    return DigitalOceanClient(bucket_name=BUCKET_NAME, repo_name=REPO_NAME)
