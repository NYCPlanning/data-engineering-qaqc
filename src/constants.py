from pathlib import Path

SQL_FILE_DIRECTORY = Path().absolute() / ".data/sql"
DATASET_BY_VERSION = lambda dataset, version: f"{dataset}_{version.replace('/', '_')}"
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

COLOR_SCHEME = ["#003f5c", "#ffa600", "#58508d", "#ff6361", "#bc5090"]
