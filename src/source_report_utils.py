# functions used to generate source data reports
import os
import streamlit as st
import pandas as pd
import requests
from src.digital_ocean_utils import (
    INPUT_DATA_URL,
    get_datatset_config,
    get_source_data_versions_from_build,
)

from src.postgres_utils import (
    SQL_FILE_DIRECTORY,
    SOURCE_TABLE_NAME,
    create_sql_schema,
    load_data_from_sql_dump,
    get_schemas,
    get_schema_tables,
    get_table_columns,
    get_table_row_count,
)

# TODO still wanna use a non default schema, make it something like source_data
QAQC_DB_SCHEMA_SOURCE_DATA = "db_zoningtaxlots"
REFERENCE_VESION = "2023/03/01"
STAGING_VERSION = None


def dataframe_style_source_report_results(value: bool):
    color = "rgba(0,155,0,.2)" if value else "rgba(155,0,0,.2)"
    return f"background-color: {color}"


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
        latest_table = SOURCE_TABLE_NAME(
            dataset_name, source_report_results[dataset_name]["version_latest"]
        )
        reference_columns = get_table_columns(
            table_schema=QAQC_DB_SCHEMA_SOURCE_DATA, table_name=reference_table
        )
        latest_columns = get_table_columns(
            table_schema=QAQC_DB_SCHEMA_SOURCE_DATA, table_name=latest_table
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
        latest_table = SOURCE_TABLE_NAME(
            dataset_name, source_report_results[dataset_name]["version_latest"]
        )
        reference_row_count = get_table_row_count(
            table_schema=QAQC_DB_SCHEMA_SOURCE_DATA, table_name=reference_table
        )
        latest_row_count = get_table_row_count(
            table_schema=QAQC_DB_SCHEMA_SOURCE_DATA, table_name=latest_table
        )
        source_report_results[dataset_name]["same_row_count"] = (
            reference_row_count == latest_row_count
        )
    return source_report_results


def create_source_data_schema() -> None:
    schema_names = get_schemas()
    if QAQC_DB_SCHEMA_SOURCE_DATA not in schema_names:
        schema_names = create_sql_schema(table_schema=QAQC_DB_SCHEMA_SOURCE_DATA)
    print("DEV schemas in DB EDM_DATA/edm-qaqc:")
    print(f"{schema_names}")


# def load_all_source_data(
#     dataset_names: list[str], source_data_versions: pd.DataFrame
# ) -> list:
#     pool = multiprocessing.Pool(processes=4)
#     pool.starmap(
#         load_source_data_to_compare,
#         zip(dataset_names, itertools.repeat(source_data_versions)),
#     )
#     table_names = get_schema_tables(table_schema=DATASET_QAQC_DB_SCHEMA)
#     return table_names


def load_source_data_to_compare(
    dataset: str, source_data_versions: pd.DataFrame
) -> list[str]:
    status_messages = []
    version_reference = source_data_versions.loc[dataset, "version_reference"]
    version_staging = source_data_versions.loc[dataset, "version_latest"]
    print(f"⏳ Loading {dataset} ({version_reference}, {version_staging}) ...")
    for version in [version_reference, version_staging]:
        status_message = load_source_data(dataset=dataset, version=version)
        status_messages.append(status_message)

    return status_messages


def load_source_data(dataset: str, version: str) -> str:
    status_message = None
    # TODO move some of this to digital_ocean_utils
    sql_dump_file_path_s3 = INPUT_DATA_URL(dataset, version)
    version_for_paths = str(version).replace("/", "_")
    dataset_by_version = SOURCE_TABLE_NAME(dataset, version_for_paths)
    sql_dump_file_path_local = SQL_FILE_DIRECTORY / f"{dataset_by_version}.sql"

    if not os.path.exists(SQL_FILE_DIRECTORY):
        os.makedirs(SQL_FILE_DIRECTORY)

    if os.path.exists(sql_dump_file_path_local):
        print(f"sql dump file already pulled : ({sql_dump_file_path_s3}")
    else:
        print(f"getting sql dump file : {sql_dump_file_path_s3} ...")
        data_mysqldump = requests.get(sql_dump_file_path_s3, timeout=10)
        with open(sql_dump_file_path_local, "wb") as f:
            f.write(data_mysqldump.content)

    schema_tables = get_schema_tables(table_schema=QAQC_DB_SCHEMA_SOURCE_DATA)
    if not dataset_by_version in schema_tables:
        load_data_from_sql_dump(
            table_schema=QAQC_DB_SCHEMA_SOURCE_DATA,
            dataset_by_version=dataset_by_version,
            dataset_name=dataset,
        )
        status_message = f"Loaded `{dataset_by_version}`"
    else:
        status_message = f"Database already has `{dataset_by_version}`"

    return status_message