# test s3 and sql data IO
from src.digital_ocean_utils import get_datatset_config

TEST_DATA_SOURCE_NAME = "dcp_zoningmapamendments"
TEST_DATA_SOURCE_VERSION = "20230404"

def test_dataset_config():
    dataset_confg = get_datatset_config(dataset=TEST_DATA_SOURCE_NAME, version=TEST_DATA_SOURCE_VERSION)
    assert isinstance(dataset_confg, dict)
    assert dataset_confg["dataset"]["name"] == TEST_DATA_SOURCE_NAME
    assert dataset_confg["dataset"]["version"] == TEST_DATA_SOURCE_VERSION