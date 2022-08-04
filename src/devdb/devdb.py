def devdb():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os
    import pdb
    from src.devdb.helpers import get_data
    from src.devdb.components.qaqc_app_report import QAQCAppReport

    st.title("Developments DB QAQC")
    branch = st.sidebar.selectbox("select a branch", ["main"])

    data = get_data(branch)

    QAQCAppReport(data)()
