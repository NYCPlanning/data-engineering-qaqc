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


def get_output_folder_path(branch: str) -> str:
    return f"{REPO_NAME}/{branch}/latest/output"


def get_data(branch: str) -> Dict[str, pd.DataFrame]:
    rv = {}
    url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/{get_output_folder_path(branch)}"

    client = DigitalOceanClient(bucket_name=BUCKET_NAME, repo_name=REPO_NAME)
    kwargs = {"true_values": ["t"], "false_values": ["f"]}

    rv["df_mismatch"] = client.csv_from_DO(
        url=f"{url}/qaqc/qaqc_mismatch.csv", kwargs=kwargs
    )
    rv["df_null"] = client.csv_from_DO(url=f"{url}/qaqc/qaqc_null.csv", kwargs=kwargs)
    rv["df_aggregate"] = client.csv_from_DO(
        url=f"{url}/qaqc/qaqc_aggregate.csv", kwargs=kwargs
    )
    rv["df_expected"] = client.csv_from_DO(
        url=f"{url}/qaqc/qaqc_expected.csv",
        kwargs={"converters": {"expected": json.loads}} | kwargs,
    )
    rv["df_outlier"] = client.csv_from_DO(
        url=f"{url}/qaqc/qaqc_outlier.csv",
        kwargs={"converters": {"outlier": json.loads}} | kwargs,
    )

    rv = rv | get_changes(client, branch)

    rv["source_data_versions"] = client.csv_from_DO(
        url=f"{url}/source_data_versions.csv"
    )

    rv["version_text"] = get_version_text(rv["source_data_versions"])

    return rv


def get_changes(client: DigitalOceanClient, branch: str) -> Dict[str, pd.DataFrame]:
    rv = {}
    valid_changes_files_group = [
        {
            "zip_filename": "pluto_changes.zip",
            "applied_filename": "pluto_chanes_applied.csv",
            "not_applied_filename": "pluto_chanes_not_applied.csv",
        },
        {
            "zip_filename": "pluto_corrections.zip",
            "applied_filename": "pluto_corrections_applied.csv",
            "not_applied_filename": "pluto_corrections_not_applied.csv",
        },
    ]
    output_filenames = client.get_all_filenames_in_folder(
        folder_path=get_output_folder_path(branch)
    )

    for changes_files_group in valid_changes_files_group:
        if changes_files_group["zip_filename"] in output_filenames:
            pluto_changes_zip = client.zip_from_DO(
                zip_filename=f"db-pluto/{branch}/latest/output/{changes_files_group['zip_filename']}",
            )
            rv["pluto_corrections_applied"] = client.unzip_csv(
                csv_filename=changes_files_group["applied_filename"],
                zipfile=pluto_changes_zip,
            )
            rv["pluto_corrections_not_applied"] = client.unzip_csv(
                csv_filename=changes_files_group["applied_filename"],
                zipfile=pluto_changes_zip,
            )

            return rv

    raise FileNotFoundError(
        f"""
        No valid pluto changes zip file found!
        Files in branch folder "{branch}"
        {output_filenames}
        """
    )


def get_version_text(source_data_versions):
    sdv = source_data_versions.to_dict("records")
    version = {}
    for i in sdv:
        version[i["schema_name"]] = i["v"]
    return f"""
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


def get_branches():
    all_branches = DigitalOceanClient(
        bucket_name=BUCKET_NAME, repo_name=REPO_NAME
    ).get_all_folder_names_in_repo_folder()

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
