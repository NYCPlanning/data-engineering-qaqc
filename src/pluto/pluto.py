def pluto():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px
    import os
    from datetime import datetime
    import requests
    from src.pluto.helpers import get_branches, get_data
    from st_aggrid import AgGrid
    from numerize.numerize import numerize

    from src.constants import COLOR_SCHEME
    from src.pluto.components.corrections_report import CorrectionsReport
    from src.pluto.components.mismatch_report import MismatchReport
    from src.pluto.components.null_graph import NullReport
    from src.pluto.components.source_data_versions_report import (
        SourceDataVersionsReport,
    )
    from src.pluto.components.expected_value_differences_report import (
        ExpectedValueDifferencesReport,
    )
    from src.pluto.components.outlier_report import OutlierReport
    from src.pluto.components.aggregate_report import AggregateReport

    st.title("PLUTO QAQC")
    st.markdown(
        """
    ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/NYCPlanning/db-pluto?label=version) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NYCPlanning/db-pluto/CI?label=CI) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NYCPlanning/db-pluto/CAMA%20Processing?label=CAMA) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NYCPlanning/db-pluto/PTS%20processing?label=PTS)
    """
    )

    branches = get_branches()
    branch = st.sidebar.selectbox(
        "select a branch",
        branches,
        index=branches.index("main"),
    )

    report_type = st.sidebar.selectbox(
        "Choose a Report Type",
        ["Compare with Previous Version", "Review Manual Corrections"],
    )

    data = get_data(branch)

    def version_comparison_report(data):
        versions = [
            "22v3.1",
            "22v3",
            "22v2",
            "22v1",
            "21v4",
            "21v3",
            "21v2",
            "21v1",
            "20v8",
            "20v7",
            "20v6",
            "20v5",
            "20v4",
            "20v3",
            "20v2",
            "20v1",
            "19v2",
            "19v1",
        ]

        v1 = st.sidebar.selectbox(
            "Pick a version of PLUTO:",
            versions[:-2],  # Can't produce comparison report for last two versions
        )

        v2 = versions[versions.index(v1) + 1]
        v3 = versions[versions.index(v1) + 2]

        condo = st.sidebar.checkbox("condo only")
        mapped = st.sidebar.checkbox("mapped only")

        st.markdown(
            f"Current version: {v1}, Previous version: {v2}, Previous Previous version: {v3}"
        )
        st.text(
            f"""
            The graphs report the number of records that have a different value in a given field but share the same BBL between versions. \
            This series of reports compares the version of PLUTO selected with the previous version ({v1} to {v2}) in blue, and the previous two versions ({v2} to {v3}) in red. \
            For example, you can read these graphs as "there are 300,000 records with the same BBL between {v1} to {v2}, but the exempttot value changed." \
            The graphs are useful to see if there are any dramatic changes in the values of fields between versions.

            There is an option to filter these graphs to just show condo lots. \
            Condos make up a small percentage of all lots, but they contain a large percentage of the residential housing. \
            A second filter enables you look at all lots or just mapped lots. \
            Unmapped lots are those with a record in PTS, but no corresponding record in DTM. \
            This happens because DOF updates are not in sync.

            In this series of graphs the x-axis is the field name and the y-axis is the total number of records. \
            Hover over the graph to see the percent of records that have a change.
        """
        )

        MismatchReport(
            data=data["df_mismatch"], v1=v1, v2=v2, v3=v3, condo=condo, mapped=mapped
        )()

        AggregateReport(
            data=data["df_aggregate"], v1=v1, v2=v2, v3=v3, condo=condo, mapped=mapped
        )()

        NullReport(
            data=data["df_null"], v1=v1, v2=v2, v3=v3, condo=condo, mapped=mapped
        )()

        SourceDataVersionsReport(version_text=data["version_text"])()

        ExpectedValueDifferencesReport(data=data["df_expected"], v1=v1, v2=v2)()

        OutlierReport(
            data=data["df_outlier"], v1=v1, v2=v2, condo=condo, mapped=mapped
        )()

    if report_type == "Compare with Previous Version":
        version_comparison_report(data)
    elif report_type == "Review Manual Corrections":
        CorrectionsReport(data)()
