# test generation of source data reports
import pandas as pd
from src.constants import DATASET_NAMES
from src.source_report_utils import (
    get_source_dataset_names,
    get_latest_source_data_versions,
    compare_source_data_columns,
    compare_source_data_row_count,
)
from src.ztl.ztl import REFERENCE_VESION

TEST_DATASET_NAME = DATASET_NAMES["ztl"]
TEST_DATASET_REFERENCE_VERSION = REFERENCE_VESION
TEST_DATA_SOURCE_NAME = "dcp_zoningmapamendments"
TEST_DATA_SOURCE_VERSION = "20230404"
TEST_DATA_SOURCE_NAMES = [
    "dcp_commercialoverlay",
    "dcp_limitedheight",
    "dcp_specialpurpose",
    "dcp_specialpurposesubdistricts",
    "dcp_zoningdistricts",
    "dcp_zoningmapamendments",
    "dcp_zoningmapindex",
    "dof_dtm",
]
TEST_SOURCE_REPORT_RESULTS = {
    TEST_DATA_SOURCE_NAME: {
        "version_reference": "20230306",
        "version_latest": "20230404",
    }
}


def test_get_latest_source_data_versions():
    source_data_versions = get_latest_source_data_versions(
        dataset=TEST_DATASET_NAME
    )
    assert isinstance(source_data_versions, pd.DataFrame)
    assert (
        source_data_versions.loc[TEST_DATA_SOURCE_NAME, "version"]
        == TEST_DATA_SOURCE_VERSION
    )


def test_get_source_dataset_names():
    source_dataset_names = get_source_dataset_names(
        dataset=TEST_DATASET_NAME, version=REFERENCE_VESION
    )
    assert source_dataset_names == TEST_DATA_SOURCE_NAMES


def test_compare_source_data_columns():
    source_report_results = compare_source_data_columns(TEST_SOURCE_REPORT_RESULTS)
    assert isinstance(
        source_report_results[TEST_DATA_SOURCE_NAME]["same_columns"], bool
    )
    assert source_report_results[TEST_DATA_SOURCE_NAME]["same_columns"] is True


def test_compare_source_data_row_count():
    source_report_results = compare_source_data_row_count(TEST_SOURCE_REPORT_RESULTS)
    assert isinstance(
        source_report_results[TEST_DATA_SOURCE_NAME]["same_row_count"], bool
    )
    assert source_report_results[TEST_DATA_SOURCE_NAME]["same_row_count"] is False
