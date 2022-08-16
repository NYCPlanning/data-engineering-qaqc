def colp():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os
    import pdb
    from src.colp.helpers import get_data
    from src.colp.components.outlier_report import OutlierReport
    from src.colp.components.manual_correction_report import ManualCorrection

    st.title("City Owned and Leased Properties QAQC")
    branch = st.sidebar.selectbox("select a branch", ["dev", "main"])
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
    OutlierReport(data=data)()
    ManualCorrection(data=data)()
