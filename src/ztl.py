def ztl():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import requests
    import os
    import json
    import plotly.graph_objects as go

    pd.options.display.float_format = "{:.2f}%".format

    @st.cache(suppress_st_warning=True, allow_output_mutation=True)
    def get_data():
        url = "https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/"
        source_data_versions = pd.read_csv(
            f"{url}source_data_versions.csv", index_col=False
        )
        qaqc_bbl = pd.read_csv(f"{url}qaqc_bbl.csv", index_col=False)
        qaqc_mismatch = pd.read_csv(f"{url}qaqc_mismatch.csv", index_col=False)
        bbldiff = pd.read_csv(f"{url}qc_bbldiffs.csv", dtype=str, index_col=False)
        bbldiff = bbldiff.fillna("NULL")
        qaqc_null = pd.read_csv(f"{url}qaqc_null.csv", index_col=False)
        last_build = requests.get(f"{url}version.txt").text

        return (
            source_data_versions,
            bbldiff,
            last_build,
            qaqc_mismatch,
            qaqc_bbl,
            qaqc_null,
        )

    (
        source_data_versions,
        bbldiff,
        last_build,
        qaqc_mismatch,
        qaqc_bbl,
        qaqc_null,
    ) = get_data()

    st.title("Zoning Tax Lots QAQC")
    st.markdown(
        f"[![Build](https://github.com/NYCPlanning/db-zoningtaxlots/actions/workflows/build.yml/badge.svg)](https://github.com/NYCPlanning/db-zoningtaxlots/actions/workflows/build.yml) last build: {last_build}"
    )

    meta = {
        "Commercial Overlay": ["commercialoverlay1", "commercialoverlay2"],
        "Zoning Districts": [
            "zoningdistrict1",
            "zoningdistrict2",
            "zoningdistrict3",
            "zoningdistrict4",
        ],
        "Special Districts": [
            "specialdistrict1",
            "specialdistrict2",
            "specialdistrict3",
        ],
        "Other": ["zoningmapcode", "zoningmapnumber", "limitedheightdistrict"],
        "All": [
            "commercialoverlay1",
            "commercialoverlay2",
            "zoningdistrict1",
            "zoningdistrict2",
            "zoningdistrict3",
            "zoningdistrict4",
            "specialdistrict1",
            "specialdistrict2",
            "specialdistrict3",
            "zoningmapcode",
            "zoningmapnumber",
            "limitedheightdistrict",
        ],
    }

    # TOTAL QAQC DIFF BY BOROUGH =============================
    total_diff_by_borough = bbldiff.groupby(["boroughcode"]).size().to_dict()
    st.header("Total BBL Counts with Value Changes by Borough")
    st.markdown(
        f"""
    Manhattan: **{total_diff_by_borough.get('1', '0')}**, Bronx: **{total_diff_by_borough.get('2', '0')}**, 
    Brooklyn: **{total_diff_by_borough.get('3', '0')}**, Queens: **{total_diff_by_borough.get('4', '0')}**,
    Staten Island: **{total_diff_by_borough.get('5', '0')}**
    """
    )
    # TOTAL QAQC DIFF BY BOROUGH =============================

    # Aggregated QAQC MISMATCH ===============================
    total_mismatch = qaqc_mismatch[["version", "version_prev"]]
    total_mismatch["total difference"] = qaqc_mismatch[
        [
            "zoningdistrict1",
            "zoningdistrict2",
            "zoningdistrict3",
            "zoningdistrict4",
            "commercialoverlay1",
            "commercialoverlay2",
            "specialdistrict1",
            "specialdistrict2",
            "specialdistrict3",
            "limitedheightdistrict",
            "zoningmapnumber",
            "zoningmapcode",
        ]
    ].sum(axis=1)

    st.header("Total BBL Pairwise Value Mismatch by Version")
    st.write(total_mismatch)
    st.write("Total number of BBLs that have differing values between versions")
    # Aggregated QAQC MISMATCH ===============================

    # PLOTTING FUNCTION ======================================
    def create_plot(df, group, key):
        # metric = st.radio(
        #     "Pick which metric you would like to see for the plot",
        #     ("raw counts", "raw counts - average"),
        #     key=key,
        # )
        fig = go.Figure()
        for i in group:
            fig.add_trace(
                go.Scatter(
                    x=df["version"],
                    y=df[i],
                    mode="lines",
                    name=i,
                    text=[f"count:{j}" for j in df[i]],
                )
            )
        fig.update_layout(
            template="plotly_white",
            xaxis=dict(title="Version"),
            yaxis=dict(title="Difference"),
        )
        st.plotly_chart(fig)

    # PLOTTING FUNCTION ======================================

    # LINEGRAPH BY EACH BOUNDARY TYPE ========================
    st.header("BBL Pairwise Value Mismatch by Field Category")
    change_by_category = qaqc_mismatch[["version", "version_prev"]]
    category = ["Commercial Overlay", "Zoning Districts", "Special Districts", "Other"]
    for cat in category:
        change_by_category[cat] = qaqc_mismatch[meta[cat]].sum(axis=1)
    create_plot(change_by_category, category, key="cat")
    st.markdown(
        """
    This plot shows the total number of bbls with a value mismatch for different zoning field categories
    """
    )
    # LINEGRAPH BY EACH BOUNDARY TYPE ========================

    # Value to NULL Comparison ===============================
    st.header("BBL Pairwise NULL to Value and Value to NULL Counts")
    st.write(qaqc_null[["field", "value_to_null", "null_to_value"]])
    st.markdown(
        """
    - `value_to_null`: for given field, count of records with values in previous version and NULL in current version
    - `null_to_value`: for given field, count of records with NULL in previous version and values in current version
    """
    )
    # Value to NULL Comparison ===============================

    # BBL ADDED / REMOVED ====================================
    st.header("BBLs added/removed")
    create_plot(qaqc_bbl, ["added", "removed"], key="bbl")
    st.markdown(
        """
    - Number of new bbl added (in current version but not in previous version) 
    - Number of old bbl removed (in previous version but not in current version)
    """
    )
    # BBL ADDED / REMOVED ====================================

    # SOURCE DATA REPORT  ====================================
    st.header("Source Data Versions")
    st.table(source_data_versions.sort_values(by=["schema_name"], ascending=True))
    # SOURCE DATA REPORT  ====================================
