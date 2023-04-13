# TODO abstract these functions out of ztl directory
import pandas as pd
from src.ztl.helpers import get_latest_source_data_versions, get_source_dataset_names

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

def test_get_latest_source_data_versions():
    source_data_versions = get_latest_source_data_versions()
    assert isinstance(source_data_versions, pd.DataFrame)
    assert source_data_versions.loc[TEST_DATA_SOURCE_NAME, "version"] == TEST_DATA_SOURCE_VERSION


def test_get_source_dataset_names():
    source_dataset_names = get_source_dataset_names()
    assert source_dataset_names == TEST_DATA_SOURCE_NAMES