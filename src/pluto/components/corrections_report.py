import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from st_aggrid import AgGrid
from src.constants import COLOR_SCHEME


def corrections_report(data):
    st.header("Manual Corrections")

    st.markdown(
        """
        PLUTO is created using the best available data from a number of city agencies. To further
        improve data quality, the Department of City Planning (DCP) applies changes to selected field
        values.

        Each Field Correction is labeled for a version of PLUTO. For programmatic changes, this is version in which the programmatic change was
        implemented. For research and user reported changes, this is the version in which the BBL
        change was added to PLUTO_input_research.csv.

        For more information about the structure of the pluto corrections report,
        see the [Pluto Changelog Readme](https://www1.nyc.gov/assets/planning/download/pdf/data-maps/open-data/pluto_change_file_readme.pdf?r=22v1).
        """
    )

    applied_corrections = data["pluto_corrections_applied"]
    not_applied_corrections = data["pluto_corrections_not_applied"]

    if applied_corrections is None or not_applied_corrections is None:
        st.info(
            "There are no available corrections reports for this branch. This is likely due to a problem on the backend with the files on Digital Ocean."
        )
        return

    version_dropdown = np.insert(
        np.flip(np.sort(data["pluto_corrections"].version.dropna().unique())),
        0,
        "All",
    )
    version = st.sidebar.selectbox(
        "Filter the field corrections by the PLUTO Version in which they were first introduced",
        version_dropdown,
    )

    applied_corrections_section(applied_corrections, version)
    not_applied_corrections_section(not_applied_corrections, version)

    st.info(
        """
        See [here](https://www1.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page) for a full accounting of the changes made for the latest version
        in the PLUTO change file.
        """
    )


def applied_corrections_section(corrections, version):
    st.subheader("Manual Corrections Applied", anchor="corrections-applied")
    st.markdown(
        """
        For each record in the PLUTO Corrections table, PLUTO attempts to change a record to the New Value column by matching on the BBL and the 
        Old Value column. The graph and table below outline the records in the pluto corrections table that were successfully applied to PLUTO.
        """
    )
    corrections = filter_by_version(corrections, version)

    if corrections.empty:
        st.info(f"No Corrections introduced in {version_text(version)} were applied.")
    else:
        title_text = (
            f"Applied Manual Corrections introduced in {version_text(version)} by Field"
        )
        display_corrections_figures(corrections, title_text)


def not_applied_corrections_section(corrections, version):
    st.subheader("Manual Corrections Not Applied", anchor="corrections-not-applied")
    st.markdown(
        """ 
        For each record in the PLUTO Corrections table, PLUTO attempts to correct a record by matching on the BBL and the 
        Old Value column. As the underlying datasources change and improve, PLUTO records may no longer match the old value 
        specified in the pluto corrections table. The graph and table below outline the records in the pluto corrections table that failed to be applied for this reason.
        """
    )
    corrections = filter_by_version(corrections, version)

    if corrections.empty:
        st.info(f"All Corrections introduced in {version_text(version)} were applied.")
    else:
        title_text = f"Manual Corrections not Applied introduced in {version_text(version)} by Field"
        display_corrections_figures(corrections, title_text)


def filter_by_version(df, version):
    if version == "All":
        return df
    else:
        return df.loc[df["version"] == version]


def version_text(version):
    return "All Versions" if version == "All" else f"Version {version}"


def display_corrections_figures(df, title):
    figure = generate_graph(field_correction_counts(df), title)
    st.plotly_chart(figure)

    display_corrections_df(df)


def generate_graph(corrections, title):
    return px.bar(
        corrections,
        x="field",
        y="size",
        text="size",
        title=title,
        labels={"size": "Count of Records", "field": "Altered Field"},
        color_discrete_sequence=COLOR_SCHEME,
    )


def display_corrections_df(corrections):
    corrections = corrections.sort_values(
        by=["version", "reason", "bbl"], ascending=[False, True, True]
    )

    AgGrid(corrections)


def field_correction_counts(df):
    return df.groupby(["field"]).size().to_frame("size").reset_index()
