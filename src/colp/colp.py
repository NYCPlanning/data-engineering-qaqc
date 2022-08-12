def colp():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os
    import pdb
    from src.colp.helpers import get_data
    from src.colp.components.agency_usetype_report import (
        RecordsByAgency,
        RecordsByUsetype,
        RecordsByAgencyUsetype,
    )

    st.title("City Owned and Leased Properties QAQC")
    branch = st.sidebar.selectbox(
        "select a branch", ["main", "212-Records-by-Agency-Usetype"]
    )
    st.markdown(
        body="""
        ### About COLP Database

        COLP is a list of uses on city owned and leased properties that includes geographic information as well as the type of use, agency and other related information. \
        The input data for COLP is the Integrated Property Information System (IPIS), a real estate database maintained by the Department of Citywide Administrative Services (DCAS).
        
        ### About QAQC

        The QAQC page is designed to highlight key scenarios that can indicate potential data issues in a COLP Database build.
        """
    )

    data = get_data(branch)

    RecordsByAgency(records_by_agency=data["records_by_agency"])()
    RecordsByUsetype(records_by_usetype=data["records_by_usetype"])()
    RecordsByAgencyUsetype(
        records_by_agency_usetype=data["records_by_agency_usetype"]
    )()
