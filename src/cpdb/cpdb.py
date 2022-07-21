import streamlit as st  # type: ignore
import pandas as pd
from src.cpdb.helpers import get_data, get_commit_cols, get_diff_dataframe, get_map_percent_diff, sort_base_on_option,VIZKEY
import plotly.express as px
import plotly.graph_objects as go


def cpdb():
    st.title("Capital Projects DB QAQC")
    branch = st.sidebar.selectbox(
        "select a branch",
        ['main']
    )
    agency_label = {'sagency': "Sponsoring Agency", 'magency': "Managing Agency"}
    agency_type = st.sidebar.selectbox(
        "select an agency type",
        ['sagency', 'magency'],
        format_func=lambda x: agency_label.get(x)
    )
    view_type = st.sidebar.selectbox(
        "select to view by number of projects or values of commitments in dollars",
        ['projects', 'commitments']
    )
    
    subcategory = st.sidebar.selectbox(
        "choose a subcategoy or entire portfolio",
        ['all categories', 'fixed assets']
    )
    
    data = get_data(branch, agency_type)
    
    st.caption(
        body="""There are mainly three ways to look at the existing qaqc tables. 
        First, you can either focus on the managing agencies or the sponsoring agencies for the projects. 
        Second, you can choose either to focus on the number of projects by your choice of agency type or the commitment amount for the projects. 
        Third, you could view the only a subcategory of the projects that outlined by the Capital Planning database. 
        """
    )
    #st.header(f'Sorted By Number of {view_type} in the Latest {agency_label} Summary Stats')

    df = data[agency_type].set_index(agency_type + "acro")
    print(df)
    df_pre = data["pre_" + agency_type].set_index(agency_type + "acro") 
    if view_type == "commitments":
        st.header(f'Dollar ($) Value of Commitments by {agency_type} for {subcategory} (Mapped vs Unmapped)')
        df = df[get_commit_cols(df)]
        df_pre = df_pre[get_commit_cols(df_pre)]
    else: 
        st.header(f'Number of Projects by {agency_type} for {subcategory} (Mapped vs Unmapped)')
        df.drop(labels=get_commit_cols(df), axis=1, inplace=True)
        df_pre.drop(labels=get_commit_cols(df_pre), axis=1, inplace=True)

    # sort the values based on projects/commitments and get the top ten agencies
    df_bar = sort_base_on_option(df, subcategory, view_type, map_option=0, ascending=False)
    print(df_bar.index)
    fig1 = px.bar(
            df_bar, 
            x=df_bar.index, 
            y=VIZKEY[subcategory][view_type]["values"],
            labels = dict(sagencyacro = "Sponsoring Agency", magencyacro = "Managing Agency"),
            barmode='group',
            width=1000,
            color_discrete_map={
                "totalcount": "#2f4b7c",
                "mapped": "#ff7c43",
                "totalcommit" : "#003f5c",
                "mappedcommit": "#ffa600",
                "fixedasset": "#a05195",
                "fixedassetmapped": "#ffa600",
                "fixedassetcommit": "#665191",
                "fixedassetmappedcommit": "#f95d6a"
            }
        )

    fig1.update_yaxes(
        title="Number of Projects" if view_type == "projects" else "Commitments Amount (USD)"
    )
    
    st.plotly_chart(fig1)

    st.caption(
        body="""This graph highlights """)
    

    st.header(f"Compare Previous vs. Latest {agency_type} Table")
    st.caption(
        body="""Comparing the latest summary stats table with the same table from the last version. 
        It highlights any changes from version to version. Even though as the underlying data Capital Commitment Plan does not meant to be identical 
        over time but the outliers scenarios still should raise red flags.  
        the key functionality for this graphics that is distinct from rest of the application is the choice to view the total projects vs. mapped projects
        using the dropdown box below. 
        """
    )
    map_option = {0: "all projects", 1: "mapped only"}
    map_option = st.radio(label="choose either all projects to compare or mapped projects only.",
            options=[0, 1],
            format_func=lambda x: map_option.get(x)
    )
    # get the difference dataframe
    diff = get_diff_dataframe(df, df_pre)
    df_bar_diff = sort_base_on_option(diff, subcategory, view_type, map_option=map_option)
    fig2 = go.Figure(
        [
            go.Bar(name="diff",
                x=df_bar_diff[VIZKEY[subcategory][view_type]["values"][map_option]], 
                y=df_bar_diff.index,
                orientation='h'
            ),
            go.Bar(name="latest",
                x=df[VIZKEY[subcategory][view_type]["values"][map_option]], 
                y=df.index,
                orientation='h'
            ),
            go.Bar(name="previous",
                x=df_pre[VIZKEY[subcategory][view_type]["values"][map_option]], 
                y=df_pre.index,
                orientation='h'
            ),
        ]
    )

    fig2.update_layout(
        barmode="group",
        width=1000,
        height=1000
    )

    fig2.update_xaxes(
        title="Number of Projects" if view_type == "projects" else "Commitments Amount (USD)"
    )

    st.plotly_chart(fig2)

    st.header("Compare Mapping from Previous to Latest Managing Agency Table")
    
    st.caption(
        body="""
        Another important aspect about the summary stats tables can display to us is the question:
        How many of the projects/commitments are successfully mapped?  
        The following chart show the difference between the versions in what percentage of the projects/commitments are mapped. 
        using the dropdown box below. 
        """
    )
    
    diff_perc = get_map_percent_diff(df, df_pre, VIZKEY[subcategory][view_type])

    fig3 = go.Figure(
        [
            go.Bar(name="diff",
                x=diff_perc.diff_percent_mapped, 
                y=diff_perc.index,
                orientation='h'
            ),
            go.Bar(name="latest",
                x=diff_perc.percent_mapped, 
                y=diff_perc.index,
                orientation='h'
            ),
            go.Bar(name="previous",
                x=diff_perc.pre_percent_mapped, 
                y=diff_perc.index,
                orientation='h'
            )
        ]
    ) 

    fig3.update_layout(
        width=1000,
        height=1000
    )

    fig3.update_xaxes(
        title="Percentage Change in Mapped Projects" if view_type == "project" else "Percentage Change in Mapped Commitments" 
    )
    
    st.plotly_chart(fig3)