def colp():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os
    import pdb
    from src.colp.helpers import get_data

    st.title("City Owned and Leased Properties QAQC")
    branch = st.sidebar.selectbox("select a branch", ["main","dev"])

    data = get_data(branch)