def devdb():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os
    import pdb
    from src.devdb.helpers import get_data

    st.title("Developments DB QAQC")
    branch = st.sidebar.selectbox("select a branch", ["dev", "main"])

    data = get_data(branch)
