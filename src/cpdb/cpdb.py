import streamlit as st  # type: ignore
import pandas as pd
from src.cpdb.helpers import (
    get_data,
    get_commit_cols,
    get_diff_dataframe,
    get_map_percent_diff,
    sort_base_on_option,
    VIZKEY,
)
import plotly.express as px
import plotly.graph_objects as go


def cpdb():
    st.title("Capital Projects DB QAQC")
    branch = st.sidebar.selectbox("select a branch", ["main"])
    agency_label = {"sagency": "Sponsoring Agency", "magency": "Managing Agency"}
    agency_type = st.sidebar.selectbox(
        "select an agency type",
        ["sagency", "magency"],
        format_func=lambda x: agency_label.get(x),
    )
    agency_type_title = agency_label[agency_type]
    
    view_type = st.sidebar.selectbox(
        "select to view by number of projects or values of commitments in dollars",
        ["projects", "commitments"],
    )
    view_type_title = view_type.capitalize()
    view_type_unit = "Number of Projects" if view_type == "projects" else "Commitments Amount (USD)"

    subcategory = st.sidebar.selectbox(
        "choose a subcategoy or entire portfolio", ["all categories", "fixed assets"]
    )

    data = get_data(branch, agency_type)

    st.caption(
        body="""There are mainly three ways to look at the existing qaqc tables. 
        First, you can either focus on the managing agencies or the sponsoring agencies for the projects. 
        Second, you can choose either to focus on the number of projects by your choice of agency type or the commitment amount for the projects. 
        Third, you could view the only a subcategory of the projects that outlined by the Capital Planning database. 
        """
    )

    df = data[agency_type].set_index(agency_type + "acro")
    df_pre = data["pre_" + agency_type].set_index(agency_type + "acro")
    if view_type == "commitments":
        st.header(
            f"Dollar ($) Value of Commitments by {agency_type_title} for {subcategory} (Mapped vs Unmapped)"
        )
        df = df[get_commit_cols(df)]
        df_pre = df_pre[get_commit_cols(df_pre)]
    else:
        st.header(
            f"Number of Projects by {agency_type_title} for {subcategory} (Mapped vs Unmapped)"
        )
        df.drop(labels=get_commit_cols(df), axis=1, inplace=True)
        df_pre.drop(labels=get_commit_cols(df_pre), axis=1, inplace=True)

    # sort the values based on projects/commitments and get the top ten agencies
    df_bar = sort_base_on_option(
        df, subcategory, view_type, map_option=0, ascending=False
    )
    print(df_bar.index)
    fig1 = px.bar(
        df_bar,
        x=df_bar.index,
        y=VIZKEY[subcategory][view_type]["values"],
        labels=dict(sagencyacro="Sponsoring Agency", magencyacro="Managing Agency"),
        barmode="group",
        width=1000,
        color_discrete_map={
            "totalcount": "#2f4b7c",
            "mapped": "#ff7c43",
            "totalcommit": "#003f5c",
            "mappedcommit": "#ffa600",
            "fixedasset": "#a05195",
            "fixedassetmapped": "#ffa600",
            "fixedassetcommit": "#665191",
            "fixedassetmappedcommit": "#f95d6a",
        },
    )

    fig1.update_yaxes(
        title=view_type_unit
    )

    fig1.update_layout(legend_title_text="Variable")

    st.plotly_chart(fig1)

    st.header(f"Compare the Total {view_type_unit} in the Previous Version vs. the Latest Version of CPDB by {agency_type_title}")
    st.markdown(f"""  
        Even though the underlying Capital Commitment Plan is meant to change over time, the outliers scenarios still should raise red flags. 
        This chart highlights the top-line changes in {view_type_unit}, with the additional option to view the either all {view_type} or mapped {view_type} only
        using the dropdown box below. Click the "Latest Version" and "Previous Version" labels in the legend to display the total {view_type_unit} for each.
        """
    )
    map_options = {0: f"all {view_type}", 1: f"mapped {view_type} only"}
    map_option = st.radio(
        label=f"Choose to compare either all {view_type} or mapped {view_type} only.",
        options=[0, 1],
        format_func=lambda x: map_options.get(x),
    )
    map_title_text = "Mapped and Unmapped" if map_option == 0 else "Mapped Only"
    # get the difference dataframe
    diff = get_diff_dataframe(df, df_pre)
    df_bar_diff = sort_base_on_option(
        diff, subcategory, view_type, map_option=map_option
    )
    fig2 = go.Figure(
        [
            go.Bar(
                name="Difference",
                x=df_bar_diff[VIZKEY[subcategory][view_type]["values"][map_option]],
                y=df_bar_diff.index,
                orientation="h",
            ),
            go.Bar(
                name="Latest Version",
                x=df[VIZKEY[subcategory][view_type]["values"][map_option]],
                y=df.index,
                orientation="h",
                visible='legendonly'
            ),
            go.Bar(
                name="Previous Version",
                x=df_pre[VIZKEY[subcategory][view_type]["values"][map_option]],
                y=df_pre.index,
                orientation="h",
                visible='legendonly'
            ),
        ]
    )
    fig2.update_layout(
        barmode="group", 
        width=1000, 
        height=1000,
        title_text=f"Total {view_type_unit} by Version and {agency_type_title} ({map_title_text})"
    )

    fig2.update_xaxes(
        title=f"Total {view_type_unit} ({map_title_text})"
    )

    fig2.update_yaxes(title=agency_type_title)

    st.plotly_chart(fig2)

    st.header(f"Compare Mapping of {view_type.capitalize()} between Previous and Latest Versions by {agency_type_title}")
    
    st.markdown(f"""
        Another important aspect about the summary stats tables can display to us is the question:
        How many of the {view_type} are successfully mapped? 
        This chart shows the change in the percentage of the {view_type} that are mapped between the last two versions. 
        Click the "Latest Version" and "Previous Version" labels in the legend to display the percentage mapped for each.
        """
    )

    diff_perc = get_map_percent_diff(df, df_pre, VIZKEY[subcategory][view_type])

    fig3 = go.Figure(
        [
            go.Bar(name="Difference",
                x=diff_perc.diff_percent_mapped, 
                y=diff_perc.index,
                orientation="h",
            ),
            go.Bar(name="Latest Version",
                x=diff_perc.percent_mapped, 
                y=diff_perc.index,
                orientation='h',
                visible='legendonly'
            ),
            go.Bar(name="Previous Version",
                x=diff_perc.pre_percent_mapped, 
                y=diff_perc.index,
                orientation='h',
                visible='legendonly'
            )
        ]
    ) 

    fig3.update_layout(
        width=1000,
        height=1000,
        title_text=f"Percentage Mapped of {view_type_title} by Version and {agency_type_title}"
    )

    fig3.update_xaxes(
        title=f"Percentage",
        tickformat= '.2%'
    )
    fig3.update_yaxes(title=agency_type_title)
    st.plotly_chart(fig3)
