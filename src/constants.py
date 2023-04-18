from pathlib import Path
import pandas as pd

COLOR_SCHEME = ["#003f5c", "#ffa600", "#58508d", "#ff6361", "#bc5090"]

SQL_FILE_DIRECTORY = Path().absolute() / ".data/sql"

DATASET_PAGES = {
    "Home": "home",
    "PLUTO": "pluto",
    "Zoning Tax Lots": "ztl",
    "Facilities DB": "facdb",
    "Developments DB": "devdb",
    "Geosupport Demo": "geocode",
    "Capital Projects DB": "cpdb",
    "City Owned and Leased Properties": "colp",
    "Template Repo DB": "trdb",
}

DATASET_NAMES = {
    "ztl": "db-zoningtaxlots",
    "facdb": "db-facilities",
}

DATASET_SOURCE_VERSIONS = {
    "db-facilities": pd.DataFrame.from_records(
        [
            ("doitt_buildingfootprints", "XXX"),
            ("dcp_mappluto_wi", "XXX"),
            ("dcp_boroboundaries_wi", "XXX"),
            ("dcp_school_districts", "XXX"),
            ("dcp_policeprecincts", "XXX"),
            ("doitt_zipcodeboundaries", "XXX"),
            ("dcp_facilities_with_unmapped", "XXX"),
            ("dcp_ct2010", "XXX"),
            ("dcp_ct2020", "XXX"),
            ("dcp_councildistricts", "XXX"),
            ("dcp_cdboundaries", "XXX"),
            ("dcp_nta2010", "XXX"),
            ("dcp_nta2020", "XXX"),
        ],
        columns=["schema_name", "v"],
    )
}

fn_dataset_by_version = lambda dataset, version: f"{dataset}_{version.replace('/', '_')}"
