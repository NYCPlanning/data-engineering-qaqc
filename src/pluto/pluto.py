def pluto():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px
    import os
    from datetime import datetime
    import requests
    from src.pluto.helpers import get_branches, get_data
    from st_aggrid import AgGrid
    from numerize.numerize import numerize

    from src.constants import COLOR_SCHEME
    from src.pluto.components.corrections_report import CorrectionsReport
    from src.pluto.components.mismatch_report import MismatchReport
    from src.pluto.components.source_data_versions_report import (
        SourceDataVersionsReport,
    )
    from src.pluto.components.expected_value_differences_report import (
        ExpectedValueDifferencesReport,
    )

    st.title("PLUTO QAQC")
    st.markdown(
        """
    ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/NYCPlanning/db-pluto?label=version) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NYCPlanning/db-pluto/CI?label=CI) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NYCPlanning/db-pluto/CAMA%20Processing?label=CAMA) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NYCPlanning/db-pluto/PTS%20processing?label=PTS)
    """
    )

    branches = get_branches()
    branch = st.sidebar.selectbox(
        "select a branch",
        branches,
        index=branches.index("main"),
    )

    report_type = st.sidebar.selectbox(
        "Choose a Report Type",
        ["Compare with Previous Version", "Review Manual Corrections"],
    )

    data = get_data(branch)

    def version_comparison_report(data):
        versions = [
            "22v2",
            "22v1",
            "21v4",
            "21v3",
            "21v2",
            "21v1",
            "20v8",
            "20v7",
            "20v6",
            "20v5",
            "20v4",
            "20v3",
            "20v2",
            "20v1",
            "19v2",
            "19v1",
        ]

        v1 = st.sidebar.selectbox(
            "Pick a version of PLUTO:",
            versions[:-2],  # Can't produce comparison report for last two versions
        )

        v2 = versions[versions.index(v1) + 1]
        v3 = versions[versions.index(v1) + 2]

        condo = st.sidebar.checkbox("condo only")
        mapped = st.sidebar.checkbox("mapped only")

        st.text(
            f"Current version: {v1}, Previous version: {v2}, Previous Previous version: {v3}"
        )
        st.markdown(
            f"""
            This series of reports compares the version of PLUTO selected with the previous version ({v1} to {v2}) in blue, and the previous two versions ({v2} to {v3}) in red. \
            The graphs report the number of records that have a different value in a given field but share the same BBL between versions. \
            For example, you can read these graphs as "there are 300,000 records with the same BBL between {v1} to {v2}, but the exempttot value changed." \
            The graphs are useful to see if there are any dramatic changes in the values of fields between versions.

            There is an option to filter these graphs to just show condo lots. \
            Condos make up a small percentage of all lots, but they contain a large percentage of the residential housing. \
            A second filter enables you look at all lots or just mapped lots. \
            Unmapped lots are those with a record in PTS, but no corresponding record in DTM. \
            This happens because DOF updates are not in sync.

            In this series of graphs the x-axis is the field name and the y-axis is the total number of records. \
            Hover over the graph to see the percent of records that have a change.
        """
        )
        # test
        def create_null(df_null, v1, v2, v3, condo, mapped):
            x = [
                "borough",
                "block",
                "lot",
                "cd",
                # "bct2020",
                # "bctcb2020",
                "ct2010",
                "cb2010",
                "schooldist",
                "council",
                "zipcode",
                "firecomp",
                "policeprct",
                "healtharea",
                "sanitboro",
                "sanitsub",
                "address",
                "zonedist1",
                "zonedist2",
                "zonedist3",
                "zonedist4",
                "overlay1",
                "overlay2",
                "spdist1",
                "spdist2",
                "spdist3",
                "ltdheight",
                "splitzone",
                "bldgclass",
                "landuse",
                "easements",
                "ownertype",
                "ownername",
                "lotarea",
                "bldgarea",
                "comarea",
                "resarea",
                "officearea",
                "retailarea",
                "garagearea",
                "strgearea",
                "factryarea",
                "otherarea",
                "areasource",
                "numbldgs",
                "numfloors",
                "unitsres",
                "unitstotal",
                "lotfront",
                "lotdepth",
                "bldgfront",
                "bldgdepth",
                "ext",
                "proxcode",
                "irrlotcode",
                "lottype",
                "bsmtcode",
                "assessland",
                "assesstot",
                "exempttot",
                "yearbuilt",
                "yearalter1",
                "yearalter2",
                "histdist",
                "landmark",
                "builtfar",
                "residfar",
                "commfar",
                "facilfar",
                "borocode",
                "bbl",
                "condono",
                "tract2010",
                "xcoord",
                "ycoord",
                "longitude",
                "latitude",
                "zonemap",
                "zmcode",
                "sanborn",
                "taxmap",
                "edesignum",
                "appbbl",
                "appdate",
                "plutomapid",
                "version",
                "sanitdistrict",
                "healthcenterdistrict",
                "firm07_flag",
                "pfirm15_flag",
            ]

            def generate_graph(r, total, title):
                y = [r[i] for i in x]
                text = [f"{round(r[i]/total*100, 2)}%" for i in x]
                return go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    name=title,
                    hovertemplate="<b>%{x} %{text}</b>",
                    text=text,
                )

            df = df_null.loc[
                (df_null.condo == condo)
                & (df_null.mapped == mapped)
                & (df_null.pair.isin([f"{v1} - {v2}", f"{v2} - {v3}"])),
                :,
            ].drop_duplicates()

            v1v2 = df.loc[df_null.pair == f"{v1} - {v2}", :]
            v2v3 = df.loc[df_null.pair == f"{v2} - {v3}", :]

            fig = go.Figure()
            if v1v2.empty and v2v3.empty:
                st.write("Null Graph")
                st.info("There is no change in NULL values across three versions.")
                return
            if not v1v2.empty:
                v1v2 = v1v2.to_dict("records")[0]
                v1v2_total = v1v2.pop("total")
                fig.add_trace(generate_graph(v1v2, v1v2_total, f"{v1} - {v2}"))
            if not v2v3.empty:
                v2v3 = v2v3.to_dict("records")[0]
                v2v3_total = v2v3.pop("total")
                fig.add_trace(generate_graph(v2v3, v2v3_total, f"{v2} - {v3}"))

            fig.update_layout(
                title="Null graph", template="plotly_white", colorway=COLOR_SCHEME
            )
            st.plotly_chart(fig)
            st.info(
                """
                The above graph highlights records that formerly had a value and are now NULL, or vice versa.
                The number records going from NULL to not NULL or vice versa should be small for any field.
            """
            )
            st.write(df)

        def create_aggregate(df_aggregate, v1, v2, v3, condo, mapped):
            df = df_aggregate.loc[
                (df_aggregate.condo == condo)
                & (df_aggregate.mapped == mapped)
                & (df_aggregate.v.isin([v1, v2, v3])),
                :,
            ]
            v1 = df.loc[df.v == v1, :].to_dict("records")[0]
            v2 = df.loc[df.v == v2, :].to_dict("records")[0]
            v3 = df.loc[df.v == v3, :].to_dict("records")[0]

            def generate_graph(v1, v2):
                _v1 = v1["v"]
                _v2 = v2["v"]

                y = [
                    "unitsres",
                    "lotarea",
                    "bldgarea",
                    "comarea",
                    "resarea",
                    "officearea",
                    "retailarea",
                    "garagearea",
                    "strgearea",
                    "factryarea",
                    "otherarea",
                    "assessland",
                    "assesstot",
                    "exempttot",
                    "firm07_flag",
                    "pfirm15_flag",
                ]
                x = [(v1[i] / v2[i] - 1) * 100 for i in y]
                diff = [v1[i] - v2[i] for i in y]
                real_v1 = [v1[i] for i in y]
                real_v2 = [v2[i] for i in y]
                hovertemplate = "<b>%{x}</b> %{text}"
                text = []
                for n in range(len(y)):
                    text.append(
                        "Diff: {} | Current: {} | Prev: {}".format(
                            numerize(diff[n]),
                            numerize(real_v1[n]),
                            numerize(real_v2[n]),
                        )
                    )

                return go.Scatter(
                    x=y,
                    y=x,
                    mode="lines",
                    name=f"{_v1} - {_v2}",
                    hovertemplate=hovertemplate,
                    text=text,
                )

            fig = go.Figure()
            fig.add_trace(generate_graph(v1, v2))
            fig.add_trace(generate_graph(v2, v3))
            fig.add_hline(y=0, line_color="grey", opacity=0.5)
            fig.update_layout(
                title="Aggregate graph",
                template="plotly_white",
                yaxis={"title": "Percent Change"},
                colorway=COLOR_SCHEME,
            )
            st.plotly_chart(fig)
            st.write(df.sort_values(by="v", ascending=False))
            st.info(
                """
                In addition to looking at the number of lots with a changed value, it’s important to look at the magnitude of the change. 
                For example, the mismatch graph for finance may show that over 90% of lots get an updated assessment when the tentative roll is released. 
                The aggregate graph may show that the aggregated sum increased by 5%. 
                Totals for assessland, assesstot, and exempttot should only change after the tentative and final rolls. 
                Pay attention to any large changes to residential units (unitsres).

                The graph shows the percent increase or decrease in the sum of the field between version. 
                The table reports the raw numbers for more in depth analysis.
            """
            )

        def create_outlier(df, v1, v2, condo, mapped):
            versions = df.v.unique()
            if v1 not in versions:
                st.write("There is no outlier report available for selected version.")
                return

            outlier = df.loc[
                (df.condo == condo) & (df.mapped == mapped) & (df.v == v1),
                :,
            ]
            outlier_records = outlier.to_dict("records")
            v1_outlier = [i["outlier"] for i in outlier_records if i["v"] == v1][0]

            def fetch_dataframe(v1_outlier, field):
                records = [i["values"] for i in v1_outlier if i["field"] == field][0]
                if records:
                    df = pd.DataFrame(records)
                    if field == "building_area_increase":
                        df = df.drop(columns=["pair"])
                    df["bbl"] = pd.to_numeric(df["bbl"], downcast="integer")
                    return df
                else:
                    return pd.DataFrame()

            version_pair = f"{v1}-{v2}"
            markdown_dict = {
                "building_area_increase": f"### Table of BBLs with Unreasonable Increase in Building Area {version_pair}",
                "unitsres_resarea": f"### Report of BBLs with buildings containing unreasonably small apartments",
                "lotarea_numfloor": f"### Table of BBLs where bldgarea/lotarea > numfloors*2",
            }

            info_dict = {
                "building_area_increase": "The table displays all BBLs where building area is more than doubled since previous version.",
                "unitsres_resarea": "The table displays all BBLs where unitsres is more than 50 and resarea is greater than 0 but the ratio of resarea:unitsres is less than 300.",
                "lotarea_numfloor": "The table displays all BBLs where the ratio of bldgarea:lotarea is more than twice numfloors.",
            }

            def display_dataframe(v1_outlier, field):
                df = fetch_dataframe(v1_outlier, field)
                if df.empty:
                    st.markdown(markdown_dict[field])
                    st.write("There is no outlier.")
                    st.info(info_dict[field])
                else:
                    st.markdown(markdown_dict[field])
                    AgGrid(df)
                    st.write(f"There are {df.shape[0]} outliers in total.")
                    st.info(info_dict[field])

            display_dataframe(v1_outlier, "building_area_increase")

            display_dataframe(v1_outlier, "unitsres_resarea")

            display_dataframe(v1_outlier, "lotarea_numfloor")

        MismatchReport(
            data=data["df_mismatch"], v1=v1, v2=v2, v3=v3, condo=condo, mapped=mapped
        )()

        create_null(data["df_null"], v1, v2, v3, condo, mapped)

        create_aggregate(data["df_aggregate"], v1, v2, v3, condo, mapped)

        SourceDataVersionsReport(version_text=data["version_text"])()

        ExpectedValueDifferencesReport(data=data["df_expected"], v1=v1, v2=v2)()

        # OUTLIER VALUE
        st.header("OUTLIER ANALYSIS")
        create_outlier(data["df_outlier"], v1, v2, condo, mapped)

    if report_type == "Compare with Previous Version":
        version_comparison_report(data)
    elif report_type == "Review Manual Corrections":
        CorrectionsReport(data)()
