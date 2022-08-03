import streamlit as st  # type: ignore
import pandas as pd
from src.cpdb.helpers import (
    get_data,
    get_geometries,
    get_commit_cols,
    get_diff_dataframe,
    get_map_percent_diff,
    sort_base_on_option,
    VIZKEY,
)
import plotly.express as px
import plotly.graph_objects as go
from src.constants import COLOR_SCHEME
from src.cpdb.components.geometry_visualization_report import geometry_visualization_report
from src.cpdb.components.adminbounds import adminbounds
from src.cpdb.components.withinNYC_check import withinNYC_check


def cpdb():
    st.title("Capital Projects Database QAQC")
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
    view_type_unit = (
        "Number of Projects" if view_type == "projects" else "Commitments Amount (USD)"
    )

    subcategory = st.sidebar.selectbox(
        "choose a subcategory or entire portfolio", ["all categories", "fixed assets"]
    )

    data = get_data(branch=branch)

    st.markdown(
        body="""
        
        ### ABOUT CAPITAL PROJECTS DATABASE

        The Capital Projects Database (CPDB), a data product produced by the New York City (NYC) Department of City Planning (DCP) Capital Planning division, captures key data points on potential, planned, and ongoing capital projects sponsored or managed by a capital agency in and around NYC.

        Information reported in the Capital Commitment Plan published by the NYC Office of Management and Budget (OMB) three times per year is the foundation that CPDB is then built off of; therefore, only the capital projects that appear in the Capital Commitment Plan are reflected in CPDB. Other open data resources are also leveraged to map the capital projects.

        CPDB supports the most comprehensive map of potential, planned, and ongoing capital projects taking place across NYC enabling Planners to better understand and communicate New York City’s capital project portfolio within and across particular agencies. This integrated but not exhaustive view provides a broad understanding of what projects are taking place within a certain area, and a starting point to discovering opportunities for strategic neighborhood planning.

        ### ABOUT QAQC 

        The QAQC page is designed to highlight key measures that can indicate potential data issues in a CPDB build. These graphs are aggregated at the agency level and there are essentially 3 cuts of the data that can be selected and viewed (w/ additional variation at the graph level):

        1. Type of agency: sponsoring agency OR managing agency 
        2. Focus on the commitment (Total sum ($) of all commitments) level data OR project (total number/count of projects) level data for each specific agency
        3. Select by project/commitment category type: entire portfolio/all categories (fixed asset, lump sum, ITT, Vehicles & equpment) OR only fixed asset

        Additionally, we have created basic geographic checks to facilitate the QAQC process of the disparate source data we recieve from various city agencies. These checks are not meant to be comprehensive but indicate if a source data geometry is falling outside of the NYC spatial boundaries.

        ### Key CPDB QAQC terms: 

        **Mapped** - refers to a record that is succesfully geocoded and "mapped" to a location in NYC (point, polygon or line)
        
        #### Additional Links
        - [CPDB Github Repo Wiki Page](https://github.com/NYCPlanning/db-cpdb/wiki) 
        - [Medium Blog on CPDB](https://medium.com/nyc-planning-digital/welcome-to-the-world-dcps-capital-projects-database-693a8b9782ac)

        """
    )

    df = data["cpdb_summarystats_" + agency_type].set_index(agency_type + "acro")
    df_pre = data["pre_cpdb_summarystats_" + agency_type].set_index(
        agency_type + "acro"
    )
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
    #print(df_bar.index)
    fig1 = px.bar(
        df_bar,
        x=df_bar.index,
        y=VIZKEY[subcategory][view_type]["values"],
        labels=dict(sagencyacro="Sponsoring Agency", magencyacro="Managing Agency"),
        barmode="group",
        width=1000,
        color_discrete_sequence=COLOR_SCHEME,
    )

    fig1.update_yaxes(title=view_type_unit)

    fig1.update_layout(legend_title_text="Variable")

    st.plotly_chart(fig1)

    st.caption(
        f"""This graph highlights the {view_type_unit} by {agency_type_title} for {subcategory} broken up by Mapped and Unmapped records grouped by unique NYC municipal agencies. 
        Typically, large city agencies including DPR (Dept. Parks and Rec.), DEP (Dept. of Environmental Protection), DOT (Dept. of Transportation), DCAS (Dept of Citywide Admin. Services) have the largest count of projects and, generally, the highest capital expenditure. 
        Some agencies (e.g. HPD [Housing Preservation & Development] often have less total projects but high capital expenditure because of the nature of their projects which are related to building housing across NYC."""
    )

    # ----- 2nd Graph
    st.header(
        f"Compare the Total {view_type_unit} in the Previous Version vs. the Latest Version of CPDB by {agency_type_title}"
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
                visible="legendonly",
            ),
            go.Bar(
                name="Previous Version",
                x=df_pre[VIZKEY[subcategory][view_type]["values"][map_option]],
                y=df_pre.index,
                orientation="h",
                visible="legendonly",
            ),
        ]
    )
    fig2.update_layout(
        barmode="group",
        width=1000,
        height=1000,
        title_text=f"Total {view_type_unit} by Version and {agency_type_title} ({map_title_text})",
        colorway=COLOR_SCHEME,
    )

    fig2.update_xaxes(title=f"Total {view_type_unit} ({map_title_text})")

    fig2.update_yaxes(title=agency_type_title)

    st.plotly_chart(fig2)

    st.caption(
        f"""  
        This graph visualizes the difference in the {view_type_unit} by {agency_type_title} between two distinct versions of CPDB.
        Even though the underlying Capital Commitment Plan is meant to change between versions, this graph and any outliers should help to guide the engineer if there are any anomolies between versions and indicate if there might be a specific agency to look into their capital projects further. 
        This chart also gives the viewer the flexibility to change between all projects by {view_type_unit} (both mapped and unmapped) along with an option to just view the mapped (geolocated) projects.
        Click the "Latest Version" and "Previous Version" labels in the legend to display the total {view_type_unit} for each.
        """
    )

    #### ----- 3rd Graph
    st.header(
        f"Compare Mapping of {view_type.capitalize()} between Previous and Latest Versions by {agency_type_title}"
    )

    st.markdown(
        f"""
        Another important aspect about the summary stats tables can display to us is the question:
        How many of the {view_type} are successfully mapped? 
        This chart shows the change in the percentage of the {view_type} that are mapped between the last two versions. 
        Click the "Latest Version" and "Previous Version" labels in the legend to display the percentage mapped for each.
        """
    )

    diff_perc = get_map_percent_diff(df, df_pre, VIZKEY[subcategory][view_type])

    fig3 = go.Figure(
        [
            go.Bar(
                name="Difference",
                x=diff_perc.diff_percent_mapped,
                y=diff_perc.index,
                orientation="h",
            ),
            go.Bar(
                name="Latest Version",
                x=diff_perc.percent_mapped,
                y=diff_perc.index,
                orientation="h",
                visible="legendonly",
            ),
            go.Bar(
                name="Previous Version",
                x=diff_perc.pre_percent_mapped,
                y=diff_perc.index,
                orientation="h",
                visible="legendonly",
            ),
        ]
    )

    fig3.update_layout(
        width=1000,
        height=1000,
        title_text=f"Percentage Mapped of {view_type_title} by Version and {agency_type_title}",
        colorway=COLOR_SCHEME,
    )

    fig3.update_xaxes(title=f"Percentage", tickformat=".2%")
    fig3.update_yaxes(title=agency_type_title)
    st.plotly_chart(fig3)

    adminbounds(data)

    withinNYC_check(data)

    geometry_visualization_report(data)