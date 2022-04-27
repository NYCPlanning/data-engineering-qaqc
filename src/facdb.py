def facdb():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os
    import pydeck as pdk
    import plotly.graph_objects as go
    import requests

    st.title("Facilities DB QAQC")

    def plotly_table(df):
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=list(df.columns),
                        line_color="darkslategray",
                        fill_color="gray",
                        font=dict(color="white", size=12),
                        align="center",
                    ),
                    cells=dict(
                        values=[df[i] for i in df.columns],
                        line_color="darkslategray",
                        fill_color="white",
                        align="left",
                    ),
                )
            ]
        )
        fig.update_layout(
            template="plotly_white", margin=go.layout.Margin(l=0, r=0, b=0, t=0)
        )
        st.plotly_chart(fig)

    def get_branches():
        url = "https://api.github.com/repos/nycplanning/db-facilities/branches"
        response = requests.get(url).json()
        return [r["name"] for r in response]

    branches = get_branches()
    branch = st.sidebar.selectbox(
        "select a branch",
        branches,
        index=branches.index("develop"),
    )

    general_or_classification = st.sidebar.selectbox(
        "Would you like to review general QAQC or changes by classification?",
        ("General review", "Review by classification level"),
    )
    st.subheader(general_or_classification)

    @st.cache(suppress_st_warning=True, allow_output_mutation=True)
    def get_data(branch=branch):
        url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-facilities/{branch}/latest/output"
        qc_diff = pd.read_csv(f"{url}/qc_diff.csv")
        qc_captype = pd.read_csv(f"{url}/qc_captype.csv")
        qc_classification = pd.read_csv(f"{url}/qc_classification.csv")
        qc_mapped = pd.read_csv(f"{url}/qc_mapped.csv")
        qc_operator = pd.read_csv(f"{url}/qc_operator.csv")
        qc_oversight = pd.read_csv(f"{url}/qc_oversight.csv")

        qc_tables = {
            "Facility subgroup classification": {
                "dataframe": qc_classification,
                "type": "dataframe",
            },
            "Operator": {"dataframe": qc_operator, "type": "dataframe"},
            "Oversight": {"dataframe": qc_oversight, "type": "dataframe"},
            "Capacity Types": {"dataframe": qc_captype, "type": "table"},
        }
        return qc_tables, qc_diff, qc_mapped

    qc_tables, qc_diff, qc_mapped = get_data(branch)

    def count_comparison(df, width=1000, height=1000):
        fig = go.Figure()
        for i in ["count_old", "count_new", "diff"]:
            fig.add_trace(go.Bar(y=df.index, x=df[i], name=i, orientation="h"))
        fig.update_layout(
            width=width,
            height=height,
            yaxis=dict(automargin=True),
            template="plotly_white",
            margin=go.layout.Margin(l=0, r=0, b=0, t=0),
        )
        st.plotly_chart(fig)

    def geom_comparison(df, width=1000, height=600):
        fig = go.Figure()
        for i in ["pctwogeom_old", "pctwogeom_new", "diff"]:
            if i == "pctwogeom_old":
                tooltip = df.wogeom_old
                txt = "old unmapped counts"
            elif i == "pctwogeom_new":
                tooltip = df.wogeom_new
                txt = "new unmapped counts"
            else:
                tooltip = df.wogeom_new - df.wogeom_old
                txt = "unmapped counts diff"
            fig.add_trace(
                go.Bar(
                    y=df.index,
                    x=df[i],
                    name=i,
                    text=[f"{txt}:{i}" for i in tooltip],
                    orientation="h",
                )
            )
        fig.update_layout(
            width=width,
            height=height,
            xaxis=dict(title="Percentage"),
            xaxis_tickformat="%",
            template="plotly_white",
            margin=go.layout.Margin(l=0, r=0, b=0, t=0),
        )
        st.plotly_chart(fig, config=dict({"scrollZoom": True}))

    def by_classification():
        """
        qc_diff visualization
        """
        level = st.sidebar.selectbox(
            "select a classification level",
            ["datasource", "factype", "facsubgrp", "facgroup", "facdomain"],
            index=0,
        )
        st.sidebar.success(
            """
            Use the dropdown input bar to select an attribute to review
            """
        )
        dff = qc_diff.groupby(level).sum()
        thresh = st.sidebar.number_input(
            "difference threshold",
            min_value=0,
            max_value=dff["diff"].max() - 1,
            value=5,
            step=1,
        )

        st.sidebar.success(
            """
            Use the number input bar to change the difference
            threshold
            """
        )
        st.header(f"Change in number of records by {level}")
        st.write(f"diff > {thresh}")

        dff = dff.loc[(dff["diff"] != 0) & (~dff["diff"].isna()), :]
        if level == "factype":
            st.warning(
                "plot not available for this level,\
                refer to the table below for more information"
            )
        else:
            count_comparison(dff.loc[dff["diff"].abs() > thresh, :].sort_values("diff"))

        st.header(f"Change in counts by {level}")
        dff.insert(0, level, dff.index)
        dff = dff.sort_values("diff")
        plotly_table(dff)

        """
        qc_mapped visualization
        """
        st.header(f"Change in percentage mapped records by {level}")
        st.write(
            """
            Only instances where there is change in the percent
            of mapped records and 100% of records are not mapped are reported
        """
        )
        dfff = qc_mapped.groupby(level).sum()
        dfff.insert(0, level, dfff.index)
        dfff["pctwogeom_old"] = dfff["wogeom_old"] / dfff["count_old"]
        dfff["pctwogeom_new"] = dfff["wogeom_new"] / dfff["count_new"]
        dfff["pctwogeom_old"] = dfff["pctwogeom_old"].round(2)
        dfff["pctwogeom_new"] = dfff["pctwogeom_new"].round(2)
        dfff["diff"] = dfff["pctwogeom_new"] - dfff["pctwogeom_old"]
        dfff["diff"] = dfff["diff"].round(2)
        dfff = dfff.loc[(dfff["diff"] != 0) & (~dfff["diff"].isna()), :]
        dfff = dfff.sort_values("diff")
        geom_comparison(dfff)
        st.header(f"Percentage mapped records by {level}")
        plotly_table(dfff)

    def general_review():
        st.header("New factypes")
        st.write("Facility types that do not appear in the previous FacDB")
        plotly_table(qc_diff.loc[qc_diff["count_old"] == 0, :])

        st.header("Old factypes (retired)")
        st.write(
            "Facility types that do appear in the previous FacDB, \
            but not in the latest version"
        )
        plotly_table(qc_diff.loc[qc_diff["count_new"] == 0, :])

        st.header("Full Panel Cross Version Comparison")
        st.write(
            "Reports the difference in the number of records at \
            the most micro level, which is the facility type and data source"
        )
        plotly_table(qc_diff)

        """
        important factypes
        """
        st.header("Changes in important factypes")
        st.write(
            "There should be little to no change in the \
            number of records with these facility types"
        )
        important_factype = [
            "FIREHOUSE",
            "POLICE STATION",
            "ACADEMIC LIBRARIES",
            "SPECIAL LIBRARIES",
            "EMERGENCY MEDICAL STATION",
            "HOSPITAL",
            "NURSING HOME",
            "ADULT DAY CARE",
            "SENIOR CENTER",
        ]
        important = (
            qc_diff.loc[qc_diff.factype.isin(important_factype), :]
            .groupby("factype")
            .sum()
        )
        count_comparison(important.sort_values("diff"), width=500, height=500)

        for key, value in qc_tables.items():
            st.header(key)
            if value["type"] == "dataframe":
                plotly_table(value["dataframe"])
            else:
                st.table(value["dataframe"])

    if general_or_classification == "General review":
        st.sidebar.success(
            "This option displays tables not specific to any classification level."
        )
        general_review()
    elif general_or_classification == "Review by classification level":
        st.sidebar.success(
            "This option displays info on change in total number of records and \
            change in number of records mapped"
        )
        by_classification()
