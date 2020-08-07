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

        qaqc_frequency = pd.read_csv(f"{url}qaqc_frequency.csv", index_col=False)
        qaqc_bbl = pd.read_csv(f"{url}qaqc_bbl.csv", index_col=False)
        qaqc_mismatch = pd.read_csv(f"{url}qaqc_mismatch.csv", index_col=False)

        bbldiff = pd.read_csv(f"{url}qc_bbldiffs.csv", dtype=str, index_col=False)
        bbldiff = bbldiff.fillna("NULL")

        last_build = requests.get(f"{url}version.txt").text

        qc_frequencychanges = pd.read_csv(
            f"{url}qc_frequencychanges.csv", index_col=False
        )
        qc_frequencychanges["percent"] = (
            qc_frequencychanges["countnew"] / qc_frequencychanges["countold"] - 1
        ) * 100
        qc_frequencychanges["percent"] = qc_frequencychanges["percent"].round(4)

        qc_versioncomparison = pd.read_csv(
            f"{url}qc_versioncomparison.csv", index_col=False
        )
        qc_versioncomparisonnownullcount = pd.read_csv(
            f"{url}qc_versioncomparisonnownullcount.csv", index_col=False
        )
        qc_versioncomparisonnownullcount["percent"] = (
            qc_versioncomparisonnownullcount["newnullcount"]
            / qc_versioncomparisonnownullcount["oldnullcount"]
            - 1
        ) * 100

        return (
            source_data_versions,
            bbldiff,
            last_build,
            qc_frequencychanges,
            qc_versioncomparison,
            qc_versioncomparisonnownullcount,
            qaqc_mismatch,
            qaqc_frequency,
            qaqc_bbl,
        )

    (
        source_data_versions,
        bbldiff,
        last_build,
        qc_frequencychanges,
        qc_versioncomparison,
        qc_versioncomparisonnownullcount,
        qaqc_mismatch,
        qaqc_frequency,
        qaqc_bbl,
    ) = get_data()

    st.title("Zoning Tax Lots QAQC")
    st.markdown(
        f"![CI](https://github.com/NYCPlanning/db-zoningtaxlots/workflows/CI/badge.svg) last build: {last_build}"
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
    lookup = {
        "commercialoverlay1": "co1",
        "commercialoverlay2": "co2",
        "zoningdistrict1": "zd1",
        "zoningdistrict2": "zd2",
        "zoningdistrict3": "zd3",
        "zoningdistrict4": "zd4",
        "specialdistrict1": "sd1",
        "specialdistrict2": "sd2",
        "specialdistrict3": "sd3",
        "zoningmapcode": "zmc",
        "zoningmapnumber": "zmn",
        "limitedheightdistrict": "lhd",
    }

    group = st.selectbox(
        "select column group:", list(meta.keys()), index=len(meta.keys()) - 1
    )
    if group != "All":
        column = st.selectbox("select column:", meta[group])

    st.header("qc_bbldiffs")
    if group == "All":
        df = bbldiff
    else:
        col = lookup[column]
        df = bbldiff.loc[
            bbldiff[f"{col}new"] != bbldiff[f"{col}prev"],
            ["bblnew", f"{col}new", f"{col}prev"],
        ]
        df = df.dropna(subset=[f"{col}new", f"{col}prev"])
        df.columns = ["bbl", f"{col}new", f"{col}prev"]

    st.dataframe(df)
    st.markdown(
        """
    Contains the old and new values for BBLs with changes from the last version.
    + Layer qc_bbldiffs, the new zoning shapefiles, and the current Digital tax map onto a map.
    + Sort qc_bbldiffs by BBL
    + Verify that the zoning changes for each BBL meet one of the following criteria:
        + Recent zoning change
        + Adjustment to boundary
        + Change in tax lot
    + Verify all lots in newly rezoned areas have new values
    """
    )

    def create_plot(df, group):
        fig = go.Figure()
        for i in group:
            average = df[i].mean().round().astype(int)
            fig.add_trace(
                go.Scatter(
                    x=df["version"],
                    y=df[i] - average,
                    mode="lines",
                    name=i,
                    text=[f"count:{j} average:{average}" for j in df[i]],
                )
            )
        fig.add_shape(
            type="line",
            x0=0,
            x1=df.shape[0],
            y1=0,
            y0=0,
            line=dict(color="MediumPurple", width=1, dash="dot"),
        )
        fig.update_layout(
            template="plotly_white",
            xaxis=dict(title="Version"),
            yaxis=dict(title="Difference from Average"),
        )
        st.plotly_chart(fig)

    st.header("Frequency Changes")
    st.dataframe(
        qc_frequencychanges.loc[
            qc_frequencychanges.field.isin(meta[group])
        ].style.format({"percent": "{:,.2f}%".format})
    )

    st.header(group)
    create_plot(qaqc_frequency, meta[group])
    # st.header('Zoning Districts')
    # create_plot(qaqc_frequency, zd)
    # st.header('Special Districts')
    # create_plot(qaqc_frequency, sp)
    # st.header('Other')
    # create_plot(qaqc_frequency, other)

    st.dataframe(qaqc_mismatch.loc[:, ["version", "version_prev"] + meta[group]])

    st.header("Version Comparison")
    st.dataframe(
        qc_versioncomparison.loc[
            qc_versioncomparison.field.isin(meta[group])
        ].style.format({"percent": "{:,.2f}%".format})
    )
    st.markdown(
        """
    Compares the value differences between this version and
    the previous version, showing the number of records with a
    change in value and the percentage of these fields that changed.
    """
    )

    st.header("Version Comparison -- Null Count")
    st.dataframe(
        qc_versioncomparisonnownullcount.loc[
            qc_versioncomparisonnownullcount.field.isin(meta[group])
        ].style.format({"percent": "{:,.2f}%".format})
    )
    st.markdown(
        """
    reports the number of records that changed
    from null to a value or vice versa.
    """
    )

    st.header("BBLs added/removed")
    create_plot(qaqc_bbl, ["added", "removed"])

    st.markdown(
        """
    Shows how many records have non-null values for each field
    in the old and new version. Note that changes to the number
    of records with a value may result from changes to null
    values or from BBL changes.
    """
    )

    st.header("Source Data Versions")
    st.table(source_data_versions.sort_values(by=["schema_name"], ascending=True))
