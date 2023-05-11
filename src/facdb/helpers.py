import streamlit as st
import pandas as pd
from src.digital_ocean_utils import DigitalOceanClient
from src.github import get_default_branch, get_branches

BUCKET_NAME = "edm-publishing"
REPO_NAME = "db-facilities"

def get_active_s3_folders():
    default_branch = get_default_branch(repo=REPO_NAME)
    all_branches = get_branches(repo=REPO_NAME, branches_blacklist=[])
    all_folders = DigitalOceanClient(
        bucket_name=BUCKET_NAME, repo_name=REPO_NAME,
    ).get_all_folder_names_in_repo_folder()

    folders = sorted(list(set(all_folders).intersection(set(all_branches))))
    folders.remove(default_branch)
    folders = [default_branch] + folders
    return folders

def get_latest_data(branch):
    url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-facilities/{branch}/latest/output"
    qc_diff = pd.read_csv(f"{url}/qc_diff.csv")
    qc_captype = pd.read_csv(f"{url}/qc_captype.csv")
    qc_classification = pd.read_csv(f"{url}/qc_classification.csv")
    qc_mapped = pd.read_csv(f"{url}/qc_mapped.csv")
    qc_operator = pd.read_csv(f"{url}/qc_operator.csv")
    qc_oversight = pd.read_csv(f"{url}/qc_oversight.csv")

    qc_tables = {
        "Facility subgroup classification": {
            "dataframe": qc_classification,
            "type": "dataframe",
        },
        "Operator": {"dataframe": qc_operator, "type": "dataframe"},
        "Oversight": {"dataframe": qc_oversight, "type": "dataframe"},
        "Capacity Types": {"dataframe": qc_captype, "type": "table"},
    }
    return qc_tables, qc_diff, qc_mapped
