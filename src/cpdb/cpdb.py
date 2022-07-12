import streamlit as st  # type: ignore
import pandas as pd
from src.cpdb.helpers import get_data

def cpdb():
    st.title("Capital Projects DB QAQC")
    branch = st.sidebar.selectbox(
        "select a branch",
        ['main']
    )
    data = get_data(branch)

    st.header('Managing Agency Summary Stats')
    st.dataframe(data['magency'])

    st.header("Sponsoring Agency Summary Stats")
    st.dataframe(data['sagency'])