import streamlit as st
import pandas as pd
from src.digital_ocean_utils import get_latest_build_version
from src.ztl.components.outputs_report import output_report
from src.ztl.components.sources_report import sources_report

DATASET_REPO_URL = "https://github.com/NYCPlanning/db-zoningtaxlots"

def ztl():
    pd.options.display.float_format = "{:.2f}%".format

    st.title("Zoning Tax Lots QAQC")
    col1, col2, col3 = st.columns(3)
    col1.markdown(
        f"""[![Build](https://github.com/NYCPlanning/db-zoningtaxlots/actions/workflows/build.yml/badge.svg)](https://github.com/NYCPlanning/db-zoningtaxlots/actions/workflows/build.yml)"""
    )
    col2.markdown(f"latest build version: `{get_latest_build_version()}`")
    col3.markdown(f"[github repo]({DATASET_REPO_URL})")

    report_type = st.sidebar.radio(
        "Select a report type",
        (
            "Sources",
            "Outputs",
        ),
    )

    if report_type == "Sources":
        sources_report()
    elif report_type == "Outputs":
        output_report()
    else:
        raise KeyError(f"Invalid ZTL report type {report_type}")
