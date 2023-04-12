import streamlit as st
from src.ztl.helpers import (
    REFERENCE_VESION,
    STAGING_VERSION,
    get_source_data_versions_from_build,
    get_latest_source_data_versions,
    create_source_data_schema,
    load_source_data,
)


def sources_report():
    print("STARTING Source Data Review")
    st.header("Source Data Review")
    st.markdown(
        f"""
    This page reviews the status of all source data used to build this dataset.

    - the reference dataset version is `{REFERENCE_VESION}`
    - ...
    """
    )

    st.subheader("Compare source data versions")
    # TODO get latest versions of datasets, not versions used in the latest build
    # TODO (nice-to-have) add column with links to data-library yaml templates
    reference_source_data_versions = get_source_data_versions_from_build(
        version=REFERENCE_VESION
    )
    latest_source_data_versions = get_source_data_versions_from_build(
        version=STAGING_VERSION
    )
    # latest_source_data_versions = get_latest_source_data_versions()
    source_data_versions = reference_source_data_versions.merge(
        latest_source_data_versions,
        left_index=True,
        right_index=True,
        suffixes=("_reference", "_latest"),
    )
    st.table(source_data_versions)

    if not st.session_state.get("source_load_button", False):
        st.session_state.data_loaded = False
        st.button(
            label="⬇️ Load source data",
            use_container_width=True,
            key="source_load_button",
        )
        return

    st.button(
        label="🔄 Refrash page to reload source data",
        use_container_width=True,
        key="source_load_button",
        disabled=True,
    )

    create_source_data_schema()
    print("LOADING SOURCE DATA")
    # for source_dataset in
    dev_dataset = "dcp_zoningmapamendments"
    with st.spinner(f"⏳ Loading {dev_dataset} ..."):
        load_source_data(
            dataset=dev_dataset,
            version=source_data_versions.loc[dev_dataset, "version_reference"],
        )
        load_source_data(
            dataset=dev_dataset,
            version=source_data_versions.loc[dev_dataset, "version_latest"],
        )
    
    st.subheader("Compare source data schemas")

    st.subheader("Compare source data row counts")
