import streamlit as st
from src.ztl.helpers import REFERENCE_VESION, get_source_data_versions, get_source_data


def inputs_report():
    st.header("Source Data Review")
    st.markdown(
        f"""
    This page reviews the status of all source data used to build this dataset.

    For the purposes of this review:
    - the reference version is `{REFERENCE_VESION}`
    - ...
    """
    )

    st.subheader("Source Data Versions")
    reference_source_data_versions = get_source_data_versions(REFERENCE_VESION)
    latests_source_data_versions = get_source_data_versions()
    source_data_versions = reference_source_data_versions.merge(
        latests_source_data_versions,
        on="datalibrary_name",
        suffixes=('_reference', '_latest'),
    )
    st.table(source_data_versions)

    st.subheader("Source Data Schemas")
    ex_source_data = get_source_data("dcp_zoningmapamendments")

    st.subheader("Source Data Row Counts")
