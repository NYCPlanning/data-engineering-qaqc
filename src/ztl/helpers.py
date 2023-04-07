import streamlit as st
import pandas as pd
import requests


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
