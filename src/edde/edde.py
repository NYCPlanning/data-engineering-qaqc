import streamlit as st

from src.constants import COLOR_SCHEME
from src.digital_ocean_utils import DigitalOceanClient
from src.report_utils import get_active_s3_folders
from src.edde.helpers import (
    demographic_categories,
    other_categories,
    geographies,
    get_demographics_data,
    get_other_data,
)
from src.edde.components import column_comparison_table


def edde():
    st.title("EDDE QAQC")

    branches = get_active_s3_folders(
        repo="db-equitable-development-tool", bucket_name="edm-publishing"
    )
    branch = st.sidebar.selectbox(
        "Select a branch (will use latest)",
        branches,
        index=branches.index("main"),
    )

    branch_comp = st.sidebar.selectbox(
        "Select a branch for comparison",
        branches,
        index=branches.index("main"),
    )

    date_comp = st.sidebar.selectbox(
        "Select an export for comparison",
        DigitalOceanClient(
            bucket_name="edm-publishing",
            repo_name=f"db-eddt/{branch_comp}",
        ).get_all_folder_names_in_repo_folder(
            index=2
        ),  ##todo - all other than latest if same branch, or latest if other branch
    )

    category_type = st.sidebar.selectbox(
        "Select category type", ["Demographics", "Housing/Quality of Life"]
    )

    if category_type == "Demographics":
        comparison_type = st.sidebar.selectbox(
            "Comparison Type",
            ["Between versions", "Between ACS years"],
            help="Each build, exports are made for each ACS year. Comparisons can be made between same export files (ACS year) for different builds OR between different ACS years in the current build",
        )

        old_data = get_demographics_data(branch_comp, date_comp)
        new_data = get_demographics_data(branch, "latest")

        for category in demographic_categories:
            for geography in geographies:
                old = old_data[category][geography]
                new = new_data[category][geography]
                keys = list(new.keys())
                keys.sort(key=lambda x: x[-2:])
                if comparison_type == "Between versions":
                    for year in keys:
                        st.header(f"{category}_{year}_{geography}.csv")
                        if year in old:
                            column_comparison_table(old[year], new[year])
                        else:
                            st.write("File not present in comparison build")

                elif comparison_type == "Between ACS years":
                    for i in range(len(keys) - 1):
                        old_acs_year = keys[i]
                        new_acs_year = keys[i + 1]
                        st.header(f"{category} {geography}: {old_acs_year} vs {new_acs_year}")
                        column_comparison_table(new[old_acs_year], new[new_acs_year])

    elif category_type == "Housing/Quality of Life":
        old_data = get_other_data(branch_comp, date_comp)
        new_data = get_other_data(branch, "latest")

        for category in other_categories:
            for geography in geographies:
                st.header(f"{category}_{geography}.csv")
                old = old_data[category][geography]
                new = new_data[category][geography]
                column_comparison_table(old, new)

    ## Columns - dropped or added from last version
