import streamlit as st  # type: ignore
import pandas as pd
import numpy as np
import requests
from src.constants import COLOR_SCHEME
from src.digital_ocean_utils import DigitalOceanClient
from helpers import get_data

def get_default_branch(repo:str):
    url = f"https://api.github.com/repos/nycplanning/{repo}"
    response = requests.get(url).json()
    return response["default_branch"]


def get_branches(repo:str, branches_blacklist:list):
    url = f"https://api.github.com/repos/nycplanning/{repo}/branches"
    response = requests.get(url).json()
    all_branches = [branch_info["name"] for branch_info in response]
    return [
        b for b in all_branches if b not in branches_blacklist
    ]

def get_active_s3_folders(repo:str, bucket_name:str):
    default_branch = get_default_branch(repo=repo)
    all_branches = get_branches(repo=repo, branches_blacklist=[])
    all_folders = DigitalOceanClient(
        bucket_name=bucket_name, repo_name=repo,
    ).get_all_folder_names_in_repo_folder()

    folders = sorted(list(set(all_folders).intersection(set(all_branches))))
    folders.remove(default_branch)
    folders = [default_branch] + folders
    return folders

def edde():
    st.title("EDDE QAQC")

    branches = get_active_s3_folders(repo="db-equitable-development-tool", bucket_name="edm-publishing")
    branch = st.sidebar.selectbox(
        "Select a branch (will use latest)",
        branches,
        index=branches.index("main"),
    )

    branch_comp = st.sidebar.selectbox(
        "select a branch for comparison",
        branches,
        index=branches.index("main"),
    )

    date_comp = st.sidebar.selectbox(
        "select a branch for comparison",
        [], ##todo - all other than latest if same branch, or latest if other branch
    )
    if st.sidebar.button(
        label="Refresh data", help="Download newest files from Digital Ocean"
    ):

        st.cache_data.clear()
        get_data(branch)

    old_data = get_data(branch_comp, date_comp)
    new_data = get_data(branch, "latest")

    ## side bar - select by category? Or by geography?

    ## Columns - dropped or added from last version
