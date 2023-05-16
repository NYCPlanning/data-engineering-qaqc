import streamlit as st  # type: ignore
import pandas as pd
import numpy as np
import requests
from src.constants import COLOR_SCHEME
from src.digital_ocean_utils import DigitalOceanClient
from helpers import get_data, compare_columns

categories = [
    "demographics",
    "economics",
    "housing_prodution",
    "housing_security",
    "quality_of_life"
]

geographies = [
    "citywide",
    "borough",
    "puma"
]

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

    try_pairing = st.sidebar.checkbox(
        label="Try to match altered columns",
        help="Some datasets have columns which remain effectively the same but update year in header.\nThis will try to identify those"
    )

    for geography in geographies:
        for category in category:
            st.header(f"{category} - {geography}")
            old = old_data[category][geography]
            new = new_data[category][geography]

            lost, added, union, paired = compare_columns(old, new, try_pairing)
            nrows_mismatch = max(len(lost), len(added))

            st.write(f"{len(union)} matching columns")
            col1, col2 = st.columns(2)
            col1.write("Lost")
            col2.write("Added")
            
            for (old_column, matched_columns) in paired:
                with col1: st.warning(old_column)
                with col2: st.warning(", ".join(matched_columns))

            for i in range(nrows_mismatch):
                with col1: st.error(lost[i])
                with col2: st.success(added[i])


    ## Columns - dropped or added from last version
