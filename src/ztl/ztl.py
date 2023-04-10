import streamlit as st
import pandas as pd
from src.ztl.components.outputs_report import output_report
from src.ztl.components.inputs_report import inputs_report
from src.ztl.helpers import get_latest_build_version


def ztl():
    pd.options.display.float_format = "{:.2f}%".format

    st.title("Zoning Tax Lots QAQC")
    last_build = get_latest_build_version()
    st.markdown(
        f"[![Build](https://github.com/NYCPlanning/db-zoningtaxlots/actions/workflows/build.yml/badge.svg)](https://github.com/NYCPlanning/db-zoningtaxlots/actions/workflows/build.yml) last build: {last_build}"
    )

    report_type = st.sidebar.radio(
        "Select a report type",
        ("Inputs", "Outputs"),
    )

    if report_type == "Inputs":
        inputs_report()
    elif report_type == "Outputs":
        output_report()
    else:
        raise KeyError(f"Invalid ZTL report type {report_type}")
