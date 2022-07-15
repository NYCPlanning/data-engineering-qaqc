from operator import index
from unicodedata import name
import streamlit as st  # type: ignore
import pandas as pd
from src.cpdb.helpers import get_data, get_commit_cols, get_diff_dataframe
import plotly.express as px
import plotly.graph_objects as go


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
    
    st.caption(
        body="""There are mainly three ways to look at the existing qaqc tables. 
        First, you can either focus on the managing agencies or the sponsoring agencies for the projects. 
        Second, you can choose either to focus on the number of projects by your choice of agency type or the commitment amount for the projects. 
        Third, you could view the only a subcategory of the projects that outlined by the Capital Planning database. 
        """
    )
    #st.dataframe(data['pre_magency'])

    # getting the 
    st.subheader('Top Ten Managing Agencies By Project Count or Commitment')
    # sorter = st.selectbox('Sort Agencies Based On',
    #     options=('Total Projects', 'Total Commitment Amount'), index=0)

    viz_keys = {
        'projects': {
            "values": ['totalcount', 'mapped'] 
        }, 
        'commitments': {
            "values": ['totalcommit', 'mappedcommit'] 
        }
    }
    df = data[agency_type].set_index(agency_type + "acro")
    df_pre = data["pre_" + agency_type].set_index(agency_type + "acro")
    #com_cols = get_commit_cols(df)
    if view_type == "commitments":
        df = df[get_commit_cols(df)]
        df_pre = df_pre[get_commit_cols(df_pre)]
    else: 
        df.drop(labels=get_commit_cols(df), axis=1, inplace=True)
        df_pre.drop(labels=get_commit_cols(df_pre), axis=1, inplace=True)

    # sort the values based on projects/commitments and get the top ten agencies
    df_bar = df.sort_values(by=viz_keys[view_type]["values"][0], ascending=False).head(10)
    st.plotly_chart(
        px.bar(
            df_bar, 
            x=df_bar.index, 
            y=viz_keys[view_type]["values"],
            barmode='group'
        )
    )

    st.header("Compare Previous vs. Latest Managing Agency Table")
    st.caption(
        body="""Comparing the latest summary stats table with the same table from the last version. 
        It highlights any changes from version to version. Even though as the underlying data Capital Commitment Plan does not meant to be identical 
        over time but the outliers scenarios still should raise red flags. 
        """
    )

    diff = get_diff_dataframe(df, df_pre)
    #st.dataframe(diff)
    #st.dataframe(df)

    df_bar_diff = diff.sort_values(by=viz_keys[view_type]["values"][0], ascending=True)
    
    fig = go.Figure(
        [
            go.Bar(name="diff",
                x=df_bar_diff[viz_keys[view_type]["values"][0]], 
                y=df_bar_diff.index,
                orientation='h'
            ),
            go.Bar(name="latest",
                x=df[viz_keys[view_type]["values"][0]], 
                y=df.index,
                orientation='h'
            ),
            go.Bar(name="previous",
                x=df_pre[viz_keys[view_type]["values"][0]], 
                y=df_pre.index,
                orientation='h'
            ),
        ]
    )

    fig.update_layout(
        barmode="group"
    )

    
    st.plotly_chart(fig)