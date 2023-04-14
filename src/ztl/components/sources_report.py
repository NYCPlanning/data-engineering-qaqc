# TODO get this out of ztl folder
import pandas as pd
import streamlit as st
from src.source_report_utils import (
    QAQC_DB_SCHEMA_SOURCE_DATA,
    REFERENCE_VESION,
    STAGING_VERSION,
    get_latest_source_data_versions,
    create_source_data_schema,
    load_source_data_to_compare,
    get_schema_tables,
    get_source_dataset_names,
    compare_source_data_columns,
    compare_source_data_row_count,
    dataframe_style_source_report_results,
)
from src.digital_ocean_utils import (
    get_source_data_versions_from_build,
    DATASET_NAME,
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
    st.dataframe(source_data_versions)
    source_report_results = source_data_versions.to_dict(orient="index")

    # source_dataset_names = get_source_dataset_names()
    source_dataset_names = ["dcp_zoningmapamendments", "dcp_limitedheight"]
    # remove non-dev source datasets from full source_report_results
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
    create_source_data_schema()
    for dataset in source_dataset_names:
        with st.spinner(f"⏳ Loading {dataset} versions ..."):
            status_messages = load_source_data_to_compare(
                dataset=dataset, source_data_versions=source_data_versions
            )
        success_message = "\n\n".join(status_messages)
        st.success(success_message)

    table_names = get_schema_tables(table_schema=QAQC_DB_SCHEMA_SOURCE_DATA)
    # TODO consider adding table names to source_report_results

    st.subheader("Compare source data shapes")
    with st.spinner(f"⏳ Comparing columns ..."):
        source_report_results = compare_source_data_columns(source_report_results)
    with st.spinner(f"⏳ Comparing row counts ..."):
        source_report_results = compare_source_data_row_count(source_report_results)

    df_source_report_results = pd.DataFrame.from_dict(
        source_report_results, orient="index"
    )
    st.dataframe(
        df_source_report_results.style.applymap(
            dataframe_style_source_report_results,
            subset=["same_columns", "same_row_count"],
        )
    )

    st.header("DEV DEBUG SECTION")
    st.dataframe(df_source_report_results)
    st.table(df_source_report_results)
    st.json(source_report_results)
    st.success(
        f"""
        Tables in QAQC databse schema {QAQC_DB_SCHEMA_SOURCE_DATA}:
        {table_names}
        """
    )
