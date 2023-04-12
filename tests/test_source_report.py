import pandas as pd
from src.ztl.helpers import get_latest_source_data_versions

TEST_DATA_SOURCE_NAME = "dcp_zoningmapamendments"
TEST_DATA_SOURCE_VERSION = "20230404"

def test_get_latest_source_data_versions():
    source_data_versions = get_latest_source_data_versions()
    assert isinstance(source_data_versions, pd.DataFrame)
    assert source_data_versions.loc[TEST_DATA_SOURCE_NAME, "version"] == TEST_DATA_SOURCE_VERSION