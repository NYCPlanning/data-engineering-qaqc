# TODO turn this into output_report_utils.py
import streamlit as st
import pandas as pd
from src.digital_ocean_utils import (
    OUTPUT_DATA_DIRECTORY_URL,
    get_latest_build_version,
    get_source_data_versions_from_build,
)

DATASET_NAME = "db-zoningtaxlots"
DATASET_QAQC_DB_SCHEMA = "db_zoningtaxlots"

DATASET_REPO_URL = "https://github.com/NYCPlanning/db-zoningtaxlots"

REFERENCE_VESION = "2023/03/01"
STAGING_VERSION = None


ZONING_FIELD_CATEGORIES = {
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


@st.cache_data
def get_output_data() -> tuple:
    last_build = get_latest_build_version()
    source_data_versions = get_source_data_versions_from_build()
    data_url = OUTPUT_DATA_DIRECTORY_URL(dataset=DATASET_NAME, version="latest")

    bbldiff = pd.read_csv(
        f"{data_url}qc_bbldiffs.csv",
        dtype=str,
        index_col=False,
    )
    bbldiff = bbldiff.fillna("NULL")
    qaqc_mismatch = pd.read_csv(
        f"{data_url}qaqc_mismatch.csv",
        index_col=False,
    )
    qaqc_bbl = pd.read_csv(
        f"{data_url}qaqc_bbl.csv",
        index_col=False,
    )
    qaqc_null = pd.read_csv(
        f"{data_url}qaqc_null.csv",
        index_col=False,
    )

    return (
        last_build,
        source_data_versions,
        bbldiff,
        qaqc_mismatch,
        qaqc_bbl,
        qaqc_null,
    )
