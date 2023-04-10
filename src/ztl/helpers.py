import streamlit as st
import pandas as pd
import requests
from mysqltotsv import Splitter
import regex

REFERENCE_VESION = "2023/03/01"

INPUT_DATA_URL = lambda dataset, version: (
    f"https://edm-recipes.nyc3.cdn.digitaloceanspaces.com/datasets/{dataset}/{version}/{dataset}.sql"
)

OUTPUT_DATA_DIRECTORY_URL = lambda version: (
    f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/{version}/output/"
)

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
def get_data_columns(data_url: str) -> list[str]:
    return pd.read_csv(data_url, nrows=1).columns.tolist()


@st.cache_data
def get_latest_build_version() -> str:
    return requests.get(
        f"{OUTPUT_DATA_DIRECTORY_URL('latest')}version.txt", timeout=10
    ).text


@st.cache_data
def get_source_data_versions(version: str = "latest") -> pd.DataFrame:
    source_data_versions = pd.read_csv(
        f"{OUTPUT_DATA_DIRECTORY_URL(version)}source_data_versions.csv",
        index_col=False,
    )
    source_data_versions.rename(
        columns={
            "schema_name": "datalibrary_name",
            "v": "version",
        },
        errors="raise",
        inplace=True,
    )
    source_data_versions.sort_values(
        by=["datalibrary_name"], ascending=True
    ).reset_index(drop=True, inplace=True)
    return source_data_versions


@st.cache_data
def get_source_data(dataset: str, version: int = "latest") -> pd.DataFrame:
    # TODO gotta assume it's a sql file like
    # https://edm-recipes.nyc3.cdn.digitaloceanspaces.com/datasets/dcp_zoningmapamendments/latest/dcp_zoningmapamendments.sql
    # return pd.read_sql(INPUT_DATA_URL(dataset, version))

    tsv = Splitter({"file": INPUT_DATA_URL(dataset, version)})
    return pd.read_table(tsv)


@st.cache_data
def get_output_data() -> tuple:
    last_build = get_latest_build_version()
    source_data_versions = get_source_data_versions()
    data_url = OUTPUT_DATA_DIRECTORY_URL("latest")

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
