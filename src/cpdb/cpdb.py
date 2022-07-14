import streamlit as st  # type: ignore
import pandas as pd
from src.cpdb.helpers import get_data, get_commit_cols
import plotly.express as px

def cpdb():
    st.title("Capital Projects DB QAQC")
    branch = st.sidebar.selectbox(
        "select a branch",
        ['main']
    )
    agency_type = st.sidebar.selectbox(
        "select an agency type",
        ['sagency', 'magency']
    )
    view_type = st.sidebar.selectbox(
        "select to view by projects or commitment",
        ['projects', 'commitments']
    )
    data = get_data(branch, agency_type)

    st.header('Previous Managing Agency Summary Stats')
    
    #st.dataframe(data['pre_magency'])

    # getting the 
    st.subheader('Top Ten Managing Agencies By Project Count or Commitment')
    sorter = st.selectbox('Sort Agencies Based On',
        options=('Total Projects', 'Total Commitment Amount'), index=0)

    viz_keys = {
        'projects': {
            "values": ['totalcount', 'mapped'] 
        }, 
        'commitments': {
            "values": ['totalcommit', 'mappedcommit'] 
        }
    }
    df = data[agency_type]
    #com_cols = get_commit_cols(df)
    if view_type == "commitments":
        df = df[[agency_type + "acro"] + get_commit_cols(df)]
    else: 
        df.drop(labels=get_commit_cols(df), axis=1, inplace=True)

    st.plotly_chart(
        px.bar(df.sort_values(by=viz_keys[view_type]["values"][0], ascending=False).head(10), 
            x=agency_type + 'acro', 
            y=viz_keys[view_type]["values"],
            barmode='group'
        )
    )

    st.header("Compare Previous vs. Latest Managing Agency Table")
    diff_manage = data['magency'][["magencyacro"] + get_commit_cols(data['sagency'])]

    st.dataframe(merge_manage)