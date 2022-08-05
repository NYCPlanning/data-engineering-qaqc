def devdb():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os
    import pdb
    from src.devdb.helpers import get_data
    from src.devdb.components.qaqc_app_report import QAQCAppReport
    from src.devdb.components.qaqc_version_history_report import (
        QAQCVersionHistoryReport,
    )
    QAQC_CHECK_GROUPS = {
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
            "group": "Class B",
        },
        "b_large_alt_reduction": {
            "description": "Alterations with large (>5) reductions in Class A units",
            "field_type": "boolean",
            "group": "Class B",
        },
        "b_nonres_with_units": {
            "description": "Non-Residential Jobs with Non-Zero Class A initial or proposed units",
            "field_type": "boolean",
            "group": "Class B",
        },
        "units_co_prop_mismatch": {
            "description": "New Building and Alterations Jobs Where Class A proposed units is not equal to co_latest_units",
            "field_type": "boolean",
            "group": "Units",
        },
        "partially_complete": {
            "description": "Job Status of 4. Partially Completed",
            "field_type": "boolean",
            "group": "Other/Unique",
        },
        "units_init_null": {
            "description": "Demolitions and Alterations in Residential Jobs with Null Class A Initial Units",
            "field_type": "boolean",
            "group": "Units",
        },
        "units_prop_null": {
            "description": "New Buildings and Alterations in Residential Jobs with Null Class A Proposed Units",
            "field_type": "boolean",
            "group": "Units",
        },
        "units_res_accessory": {
            "description": "Work only done on nonresidential structure (Garage, Shed, etc.)",
            "field_type": "boolean",
            "group": "Units",
        },
        "outlier_demo_20plus": {
            "description": "Demolition Jobs with larger than 19 Class A Initial Units",
            "field_type": "boolean",
            "group": "Outlier",
        },
        "outlier_nb_500plus": {
            "description": "New Building Jobs with more than 499 Class A proposed units",
            "field_type": "boolean",
            "group": "Outlier",
        },
        "outlier_top_alt_increase": {
            "description": "The 20 largest alterations by increase in Class A units",
            "field_type": "boolean",
            "group": "Outlier",
        },
        "dup_bbl_address_units": {
            "description": "Duplicate BBL Address Units",
            "field_type": "string",
            "group": "Duplicates",
        },
        "dup_bbl_address": {
            "description": "Duplicate BBL Address",
            "field_type": "string",
            "group": "Duplicates",
        },
        "inactive_with_update": {
            "description": "Date Last Updated > Last Captured Date and Job Inactive is set to new value",
            "field_type": "boolean",
            "group": "Other/Unique",
        },
        "no_work_job": {
            "description": "Jobs without work to be done",
            "field_type": "boolean",
            "group": "Other/Unique",
        },
        "geo_water": {
            "description": "Jobs located in the water",
            "field_type": "boolean",
            "group": "Geography",
        },
        "geo_taxlot": {
            "description": "Jobs with a missing BBL",
            "field_type": "boolean",
            "group": "Geography",
        },
        "geo_null_latlong": {
            "description": "Jobs with a NULL Lat/Long Field",
            "field_type": "boolean",
            "group": "Geography",
        },
        "geo_null_boundary": {
            "description": "Jobs with a NULL boundary field",
            "field_type": "boolean",
            "group": "Geography",
        },
        "invalid_date_filed": {
            "description": "Date Filed is not a date or is before 1990",
            "field_type": "boolean",
            "group": "Invalid Dates",
        },
        "invalid_date_lastupdt": {
            "description": "Date Last Updated is not a date or is before 1990",
            "field_type": "boolean",
            "group": "Invalid Dates",
        },
        "invalid_date_statusd": {
            "description": "Date Statusd is not a date or is before 1990",
            "field_type": "boolean",
            "group": "Invalid Dates",
        },
        "invalid_date_statusp": {
            "description": "Date Statusp is not a date or is before 1990",
            "field_type": "boolean",
            "group": "Invalid Dates",
        },
        "invalid_date_statusr": {
            "description": "Date Statusr is not a date or is before 1990",
            "field_type": "boolean",
            "group": "Invalid Dates",
        },
        "invalid_date_statusx": {
            "description": "Date Statusx is not a date or is before 1990",
            "field_type": "boolean",
            "group": "Invalid Dates",
        },
        "incomp_tract_home": {
            "description": "Tracthomes flag is Y and job status in 1,2,3",
            "field_type": "boolean",
            "group": "Other/Unique",
        },
        "dem_nb_overlap": {
            "description": "Duplicates between new buildings and demolitions",
            "field_type": "boolean",
            "group": "Other/Unique",
        },
        "classa_net_mismatch": {
            "description": "Class A Net units is not equal to Class A proposed - Class A init",
            "field_type": "boolean",
        },
    }
   
    st.title("Developments Database QAQC")
    st.markdown(
        body="""
        ### ABOUT DEVELOPMENTS DATABASE

        DCP’s Developments Database is the agency’s foundational dataset used for tracking construction and providing high accuracy estimates of current and near-term housing growth and analysis of housing trends. 
        It is the only source that can determine past and future change in Class A (permanent occupancy) and Class B (transient occupancy) housing units. 

        The NYC Department of City Planning’s (DCP) Housing Database Project-Level Files contain all NYC Department of Buildings (DOB)-approved housing construction and demolition jobs filed or completed in NYC since January 1, 2010. 
        It includes all three construction job types that add or remove residential units: new buildings, major alterations, and demolitions, and can be used to determine the change in legal housing units across time and space. 
        Records in the Housing Database Project-Level Files are geocoded to the greatest level of precision possible, subject to numerous quality assurance and control checks, recoded for usability, and joined to other housing data sources relevant to city planners and analysts.
    
        ### ABOUT QAQC

        The QAQC page is designed to highlight key scenarios that can indicate potential data issues in a Developments Database build.

        #### Additional Links
        - [DevDB Github Repo Wiki Page](https://github.com/NYCPlanning/db-developments/wiki)
        - [Medium Blog on DevDB](https://medium.com/nyc-planning-digital/introducing-dcps-housing-database-dcp-s-latest-open-data-product-b581aee97a51)
        """
    )

    branch = st.sidebar.selectbox("select a branch", ["main"])

    data = get_data(branch)

    QAQCAppReport(data)()

    QAQCVersionHistoryReport(
        data=data,
        qaqc_check_dict=QAQC_CHECK_DICTIONARY,
        qaqc_check_groups=QAQC_CHECK_GROUPS,
    )()
