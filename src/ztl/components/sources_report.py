import streamlit as st
from src.ztl.helpers import (
    DATASET_NAME,
    DATASET_QAQC_DB_SCHEMA,
    REFERENCE_VESION,
    STAGING_VERSION,
    get_source_data_versions_from_build,
    get_latest_source_data_versions,
    create_source_data_schema,
    load_all_source_data,
    compare_source_data_columns,
    compare_source_data_row_count,
)


def sources_report():
    print("STARTING Source Data Review")
    st.header("Source Data Review")
    st.markdown(
        f"""
    This page reviews the status of all source data used to build this dataset.
    It compares the latest versions of source data to those used in the build of a reference version of this dataset.
    
    The reference dataset version is `{REFERENCE_VESION}`.
    """
    )

    st.subheader("Compare source data versions")
    # TODO (nice-to-have) add column with links to data-library yaml templates
    reference_source_data_versions = get_source_data_versions_from_build(
        version=REFERENCE_VESION
    )
    if not STAGING_VERSION:
        latest_source_data_versions = get_latest_source_data_versions()
    else:
        latest_source_data_versions = get_source_data_versions_from_build(
            version=STAGING_VERSION
        )
    source_data_versions = reference_source_data_versions.merge(
        latest_source_data_versions,
        left_index=True,
        right_index=True,
        suffixes=("_reference", "_latest"),
    )
    source_data_versions.sort_index(ascending=True, inplace=True)
    st.table(source_data_versions)
    source_report_results = source_data_versions.to_dict(orient="index")

    # TODO use the real list based on reference version
    # source_dataset_names = get_source_dataset_names()
    source_dataset_names = ["dcp_zoningmapamendments", "dcp_limitedheight"]
    # DEV remove non-dev source datasets from full source_report_results
    source_report_results = {
        dataset_name: source_report_results[dataset_name]
        for dataset_name in source_dataset_names
    }
    st.warning(f"Only using DEV source datasets {source_dataset_names}")

    if not st.session_state.get("source_load_button", False):
        st.session_state.data_loaded = False
        st.button(
            label="⬇️ Load source data",
            use_container_width=True,
            key="source_load_button",
        )
        return

    st.button(
        label="🔄 Refresh page to reload source data",
        use_container_width=True,
        key="source_load_button",
        disabled=True,
    )

    print(f"LOADING SOURCE DATA FOR {DATASET_NAME}")
    with st.spinner(f"⏳ Loading source data ..."):
        create_source_data_schema()
        table_names = load_all_source_data(
            dataset_names=source_dataset_names,
            source_data_versions=source_data_versions,
        )
    # TODO consider adding table names to source_report_results

    st.subheader("Compare source data schemas")
    source_report_results = compare_source_data_columns(source_report_results)
    st.subheader("Compare source data row counts")
    source_report_results = compare_source_data_row_count(source_report_results)

    st.subheader("DEV DEBUG SECTION")
    st.success(
        f"""
        Tables in QAQC databse schema {DATASET_QAQC_DB_SCHEMA}:
        {table_names}
        """
    )
    st.json(source_report_results)
