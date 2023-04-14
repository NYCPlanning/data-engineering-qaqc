# test s3 and sql data IO
# TODO abstract these functions out of ztl directory
from src.postgres_utils import get_table_columns
from src.digital_ocean_utils import get_datatset_config
from src.ztl.helpers import DATASET_QAQC_DB_SCHEMA

TEST_DATASET_NAME = DATASET_QAQC_DB_SCHEMA
TEST_DATA_SOURCE_NAME = "dcp_zoningmapamendments"
TEST_DATA_SOURCE_VERSION = "20230404"
TEST_DATA_SOURCE_COLUMNS = [
    "effective",
    "lucats",
    "ogc_fid",
    "project_na",
    "shape_area",
    "shape_leng",
    "status",
    "ulurpno",
    "wkb_geometry",
]


def test_dataset_config():
    dataset_confg = get_datatset_config(
        dataset=TEST_DATA_SOURCE_NAME, version=TEST_DATA_SOURCE_VERSION
    )
    assert isinstance(dataset_confg, dict)
    assert dataset_confg["dataset"]["name"] == TEST_DATA_SOURCE_NAME
    assert dataset_confg["dataset"]["version"] == TEST_DATA_SOURCE_VERSION


def test_get_table_columns():
    columns = get_table_columns(
        # table_schema="db_zoningtaxlots",
        # table_name="dcp_zoningmapamendments_20230306",
        table_schema=TEST_DATASET_NAME,
        table_name=f"{TEST_DATA_SOURCE_NAME}_{TEST_DATA_SOURCE_VERSION}",
    )
    assert columns == TEST_DATA_SOURCE_COLUMNS
