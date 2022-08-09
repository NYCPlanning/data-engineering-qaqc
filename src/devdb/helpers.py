import pandas as pd
from typing import Dict
from urllib.error import HTTPError
import streamlit as st

BUCKET_NAME = "edm-publishing"

QAQC_CHECK_SECTIONS = {
    "Class B": "These checks are related to class A and class B unit distinctions.",
    "Units": "These checks are related to missing or suspicious unit counts.",
    "Duplicates": "These checks are related to identifying possible duplicates",
    "Geography": "These checks are related to potentially missing geographic information",
    "Other/Unique": "Miscellaneuous Checks",
    "Outlier": "These checks are related to outlying or unexpected values",
}
QAQC_CHECK_DICTIONARY = {
    "b_likely_occ_desc": {
        "description": "Likely Class B Units: OCC Initial or Proposed contains hotel, assisted, etc. or job description contains Hotel, Motel, etc.",
        "field_type": "boolean",
        "section": "Class B",
    },
    "b_large_alt_reduction": {
        "description": "Alterations with large (>5) reductions in Class A units",
        "field_type": "boolean",
        "section": "Class B",
    },
    "b_nonres_with_units": {
        "description": "Non-Residential Jobs with Non-Zero Class A initial or proposed units",
        "field_type": "boolean",
        "section": "Class B",
    },
    "units_co_prop_mismatch": {
        "description": "New Building and Alterations Jobs Where Class A proposed units is not equal to co_latest_units",
        "field_type": "boolean",
        "section": "Units",
    },
    "partially_complete": {
        "description": "Job Status of 4. Partially Completed",
        "field_type": "boolean",
        "section": "Other/Unique",
    },
    "units_init_null": {
        "description": "Demolitions and Alterations in Residential Jobs with Null Class A Initial Units",
        "field_type": "boolean",
        "section": "Units",
    },
    "units_prop_null": {
        "description": "New Buildings and Alterations in Residential Jobs with Null Class A Proposed Units",
        "field_type": "boolean",
        "section": "Units",
    },
    "units_res_accessory": {
        "description": "Work only done on nonresidential structure (Garage, Shed, etc.)",
        "field_type": "boolean",
        "section": "Units",
    },
    "outlier_demo_20plus": {
        "description": "Demolition Jobs with larger than 19 Class A Initial Units",
        "field_type": "boolean",
        "section": "Outlier",
    },
    "outlier_nb_500plus": {
        "description": "New Building Jobs with more than 499 Class A proposed units",
        "field_type": "boolean",
        "section": "Outlier",
    },
    "outlier_top_alt_increase": {
        "description": "The 20 largest alterations by increase in Class A units",
        "field_type": "boolean",
    },
    "dup_bbl_address_units": {
        "description": "Duplicate BBL Address Units",
        "field_type": "string",
        "section": "Duplicates",
    },
    "dup_bbl_address": {
        "description": "Duplicate BBL Address",
        "field_type": "string",
        "section": "Duplicates",
    },
    "inactive_with_update": {
        "description": "Date Last Updated > Last Captured Date and Job Inactive is set to new value",
        "field_type": "boolean",
        "section": "Other/Unique",
    },
    "no_work_job": {
        "description": "Jobs without work to be done",
        "field_type": "boolean",
        "section": "Other/Unique",
    },
    "geo_water": {
        "description": "Jobs located in the water",
        "field_type": "boolean",
        "section": "Geography",
    },
    "geo_taxlot": {
        "description": "Jobs with a missing BBL",
        "field_type": "boolean",
        "section": "Geography",
    },
    "geo_null_latlong": {
        "description": "Jobs with a NULL Lat/Long Field",
        "field_type": "boolean",
        "section": "Geography",
    },
    "geo_null_boundary": {
        "description": "Jobs with a NULL boundary field",
        "field_type": "boolean",
        "section": "Geography",
    },
    "invalid_date_filed": {
        "description": "Date Filed is not a date or is before 1990",
        "field_type": "boolean",
        "section": "Invalid Dates",
    },
    "invalid_date_lastupdt": {
        "description": "Date Last Updated is not a date or is before 1990",
        "field_type": "boolean",
        "section": "Invalid Dates",
    },
    "invalid_date_statusd": {
        "description": "Date Statusd is not a date or is before 1990",
        "field_type": "boolean",
        "section": "Invalid Dates",
    },
    "invalid_date_statusp": {
        "description": "Date Statusp is not a date or is before 1990",
        "field_type": "boolean",
        "section": "Invalid Dates",
    },
    "invalid_date_statusr": {
        "description": "Date Statusr is not a date or is before 1990",
        "field_type": "boolean",
        "section": "Invalid Dates",
    },
    "invalid_date_statusx": {
        "description": "Date Statusx is not a date or is before 1990",
        "field_type": "boolean",
        "section": "Invalid Dates",
    },
    "incomp_tract_home": {
        "description": "Tracthomes flag is Y and job status in 1,2,3",
        "field_type": "boolean",
        "section": "Other/Unique",
    },
    "dem_nb_overlap": {
        "description": "Duplicates between new buildings and demolitions",
        "field_type": "boolean",
        "section": "Other/Unique",
    },
    "classa_net_mismatch": {
        "description": "Class A Net units is not equal to Class A proposed - Class A init",
        "field_type": "boolean",
        "section": "n/a",
    },
}


def get_data(branch):
    rv = {}
    url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-developments/{branch}/latest/output"

    rv["qaqc_app"] = csv_from_DO(
        f"{url}/qaqc_app.csv",
        kwargs={"dtype": {"job_number": "str"}},
    )

    rv["qaqc_historic"] = csv_from_DO(f"{url}/qaqc_historic.csv")

    return rv


def csv_from_DO(url, kwargs={}):
    try:
        return pd.read_csv(url, **kwargs)
    except HTTPError:
        st.warning(f"{url} not found")
