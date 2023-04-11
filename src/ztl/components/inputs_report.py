import streamlit as st
from src.ztl.helpers import REFERENCE_VESION, STAGING_VERSION, get_source_data_versions, load_source_data


def inputs_report():
    print("STARTING Source Data Review")
    st.header("Source Data Review")
    st.markdown(
        f"""
    This page reviews the status of all source data used to build this dataset.

    - the reference dataset version is `{REFERENCE_VESION}`
    - ...
    """
    )

    st.subheader("Compare Source Data Versions")
    reference_source_data_versions = get_source_data_versions(version=REFERENCE_VESION)
    latest_source_data_versions = get_source_data_versions(version=STAGING_VERSION)
    source_data_versions = reference_source_data_versions.merge(
        latest_source_data_versions,
        on="datalibrary_name",
        suffixes=("_reference", "_latest"),
    )
    source_data_versions.set_index("datalibrary_name", inplace=True)
    st.table(source_data_versions)

    if not st.session_state.get("source_load_button", False):
        st.session_state.data_loaded = False
        st.button(
            label="⬇️ Load source data",
            use_container_width=True,
            key="source_load_button",
        )
        return

    st.session_state.data_loaded = True
    st.button(
        label="🔄 Refrash page to reload source data",
        use_container_width=True,
        key="source_load_button",
        disabled=True,
    )

    # TODO add details about tables in ZTL QAQC postgress DB

    st.subheader("Compare Source Data Schemas")
    # TODO load all source datasets into a DB
    print("LOADING SOURCE DATA")
    dev_dataset = "dcp_zoningmapamendments"
    load_source_data(
        dataset=dev_dataset,
        version=source_data_versions.loc[dev_dataset, "version_reference"],
    )
    load_source_data(
        dataset=dev_dataset,
        version=source_data_versions.loc[dev_dataset, "version_latest"],
    )

    st.subheader("Compare Source Data Row Counts")
