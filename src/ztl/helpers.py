import os
import streamlit as st
import pandas as pd
import requests
import multiprocessing
import itertools
from src.digital_ocean_utils import (
    INPUT_DATA_URL,
    OUTPUT_DATA_DIRECTORY_URL,
    get_datatset_config,
)
from src.postgres_utils import (
    SQL_FILE_DIRECTORY,
    SOURCE_TABLE_NAME,
    create_sql_schema,
    load_data_from_sql_dump,
    get_schema_tables,
    get_table_columns,
    get_table_row_count,
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
def get_latest_build_version() -> str:
    return requests.get(
        f"{OUTPUT_DATA_DIRECTORY_URL(dataset=DATASET_NAME, version='latest')}version.txt",
        timeout=10,
    ).text


@st.cache_data
def get_source_data_versions_from_build(version: str) -> pd.DataFrame:
    source_data_versions = pd.read_csv(
        f"{OUTPUT_DATA_DIRECTORY_URL(dataset=DATASET_NAME, version=version)}source_data_versions.csv",
        index_col=False,
        dtype=str,
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
    source_data_versions.set_index("datalibrary_name", inplace=True)
    return source_data_versions


@st.cache_data
def get_source_dataset_names() -> pd.DataFrame:
    source_data_versions = get_source_data_versions_from_build(version=REFERENCE_VESION)
    return sorted(source_data_versions.index.values.tolist())


@st.cache_data
def get_latest_source_data_versions() -> pd.DataFrame:
    source_data_versions = get_source_data_versions_from_build(version=REFERENCE_VESION)
    source_data_versions["version"] = source_data_versions.index.map(
        lambda dataset: get_datatset_config(
            dataset=dataset,
            version="latest",
        )[
            "dataset"
        ]["version"]
    )
    return source_data_versions


def compare_source_data_columns(source_report_results: dict) -> dict:
    for dataset_name in source_report_results:
        reference_table = SOURCE_TABLE_NAME(
            dataset_name, source_report_results[dataset_name]["version_reference"]
        )
        reference_columns = get_table_columns(
            table_schema=DATASET_QAQC_DB_SCHEMA, table_name=reference_table
        )
        latest_table = SOURCE_TABLE_NAME(
            dataset_name, source_report_results[dataset_name]["version_latest"]
        )
        latest_columns = get_table_columns(
            table_schema=DATASET_QAQC_DB_SCHEMA, table_name=latest_table
        )
        source_report_results[dataset_name]["same_columns"] = (
            reference_columns == latest_columns
        )
    return source_report_results


def compare_source_data_row_count(source_report_results: dict) -> dict:
    for dataset_name in source_report_results:
        reference_table = SOURCE_TABLE_NAME(
            dataset_name, source_report_results[dataset_name]["version_reference"]
        )
        reference_row_count = get_table_row_count(
            table_schema=DATASET_QAQC_DB_SCHEMA, table_name=reference_table
        )
        latest_table = SOURCE_TABLE_NAME(
            dataset_name, source_report_results[dataset_name]["version_latest"]
        )
        latest_row_count = get_table_row_count(
            table_schema=DATASET_QAQC_DB_SCHEMA, table_name=latest_table
        )
        source_report_results[dataset_name]["same_row_count"] = (
            reference_row_count == latest_row_count
        )
    return source_report_results


def create_source_data_schema() -> None:
    table_schema_names = create_sql_schema(table_schema=DATASET_QAQC_DB_SCHEMA)
    print("DEV schemas in DB EDM_DATA/edm-qaqc:")
    print(f"{table_schema_names}")


def load_all_source_data(
    dataset_names: list[str], source_data_versions: pd.DataFrame
) -> list:
    pool = multiprocessing.Pool(processes=4)
    pool.starmap(
        load_source_data_to_compare,
        zip(dataset_names, itertools.repeat(source_data_versions)),
    )
    table_names = get_schema_tables(table_schema=DATASET_QAQC_DB_SCHEMA)
    return table_names


def load_source_data_to_compare(
    dataset: str, source_data_versions: pd.DataFrame
) -> None:
    version_reference = source_data_versions.loc[dataset, "version_reference"]
    version_staging = source_data_versions.loc[dataset, "version_latest"]
    print(f"⏳ Loading {dataset} ({version_reference}, {version_staging}) ...")
    load_source_data(dataset=dataset, version=version_reference)
    load_source_data(dataset=dataset, version=version_staging)


def load_source_data(dataset: str, version: str) -> None:
    # TODO move some of this to digital_ocean_utils
    sql_dump_file_path_s3 = INPUT_DATA_URL(dataset, version)
    version_for_paths = str(version).replace("/", "_")
    dataset_by_version = SOURCE_TABLE_NAME(dataset, version_for_paths)
    file_name = f"{dataset_by_version}.sql"
    sql_dump_file_path_local = f"{SQL_FILE_DIRECTORY}/{file_name}"

    print(f"getting sql dump file {sql_dump_file_path_s3}")

    data_mysqldump = requests.get(sql_dump_file_path_s3, timeout=10)
    if not os.path.exists(SQL_FILE_DIRECTORY):
        os.makedirs(SQL_FILE_DIRECTORY)
    with open(sql_dump_file_path_local, "wb") as f:
        f.write(data_mysqldump.content)

    table_names = load_data_from_sql_dump(
        table_schema=DATASET_QAQC_DB_SCHEMA,
        dataset_by_version=dataset_by_version,
        dataset_name=dataset,
    )
    print(f"DEV tables in DB EDM_DATA/edm-qaqc:{DATASET_QAQC_DB_SCHEMA}")
    print(f"{table_names}")


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
