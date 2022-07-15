def pluto():
    import streamlit as st
    import pandas as pd
    import numpy as np
    from sqlalchemy import create_engine
    import plotly.graph_objects as go
    import os
    from datetime import datetime
    import requests
    from src.pluto.helpers import get_branches, get_data

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

    data = get_data(branch)

    versions = [
        '22v2',
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
        versions,  # index=len(versions) - 1
    )

    v2 = versions[versions.index(v1) + 1]
    v3 = versions[versions.index(v1) + 2]

    condo = st.sidebar.checkbox("condo only")
    mapped = st.sidebar.checkbox("mapped only")
    st.sidebar.markdown(
        """
    These reports compare the version selected with the previous version (in blue)
    and the differences between the previous two versions (in red).

    There is an option to look at just **condo lots**. Condos make up a small percentage of lots,
    but contain a large percentage of the residential housing.

    A second option lets you look at all lots or just **mapped lots**.
    Unmapped lots are those with a record in PTS, but no corresponding record in DTM.
    This happens because DOF updates are not in sync.
    """
    )
    st.text(
        f"Current version: {v1}, Previous version: {v2}, Previous Previous version: {v3}"
    )
    # test
    def create_mismatch(df_mismatch, v1, v2, v3, condo, mapped):
        finance_columns = [
            "assessland",
            "assesstot",
            "exempttot",
            "taxmap",
            "appbbl",
            "appdate",
            "plutomapid",
        ]

        area_columns = [
            "lotarea",
            "bldgarea",
            "builtfar",
            "comarea",
            "resarea",
            "officearea",
            "retailarea",
            "garagearea",
            "strgearea",
            "factryarea",
            "otherarea",
            "areasource",
        ]

        zoning_columns = [
            "residfar",
            "commfar",
            "facilfar",
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
            "zonemap",
            "zmcode",
            "edesignum",
        ]

        geo_columns = [
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
            "borocode",
            "bbl",
            "tract2010",
            "xcoord",
            "ycoord",
            "longitude",
            "latitude",
            "sanborn",
            "edesignum",
            "sanitdistrict",
            "healthcenterdistrict",
            "histdist",
            "firm07_flag",
            "pfirm15_flag",
        ]

        bldg_columns = [
            "bldgclass",
            "landuse",
            "easements",
            "ownertype",
            "ownername",
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
            "yearbuilt",
            "yearalter1",
            "yearalter2",
            "landmark",
            "condono",
        ]

        groups = [
            {
                "title": "Mismatch graph -- finance",
                "columns": finance_columns,
                "description": """
                Assessment and exempt values are updated **twice** a year by DOF.
                The tentative roll is released in *mid-January* and the final roll is released in *late May*.
                For PLUTO versions created in February, most lots will show a change in assesstot,
                with a smaller number of changes for the `assessland` and `exempttot`.
                There will also be changes in the June version. Other months should see almost no change for these fields.
                """,
            },
            {
                "title": "Mismatch graph -- area",
                "columns": area_columns,
                "description": """
                The primary source for these fields is **CAMA**.
                Updates reflect new construction, as well as updates by assessors for the tentative roll.
                Several thousand lots may have updates in February.
            """,
            },
            {
                "title": "Mismatch graph -- zoning",
                "columns": zoning_columns,
                "description": """
                Unless DCP does a major rezoning, the number of lots with changed values should be **no more than a couple of hundred**.
                Lots may get a changed value due to a split/merge or if TRD is cleaning up boundaries between zoning districts.
                `Residfar`, `commfar`, and `facilfar` should change only when there is a change to `zonedist1` or `overlay1`.
            """,
            },
            {
                "title": "Mismatch graph -- geo",
                "columns": geo_columns,
                "description": """
                These fields are updated from **Geosupport**. Changes should be minimal unless a municipal service
                area changes or more high-rise buildings opt into the composite recycling program.
                Check with GRU if more than a small number of lots have changes to municipal service areas.
            """,
            },
            {
                "title": "Mismatch graph -- building",
                "columns": bldg_columns,
                "description": """
                Changes in these fields are most common in February, after the tentative roll has been released.
                Several fields in this group are changed by DCP to improve data quality, including `ownername` and `yearbuilt`.
                When these changes are first applied, there will be a spike in the number of lots changed.
            """,
            },
        ]

        df = df_mismatch.loc[
            (df_mismatch.condo == condo)
            & (df_mismatch.mapped == mapped)
            & (df_mismatch.pair.isin([f"{v1} - {v2}", f"{v2} - {v3}"])),
            :,
        ]

        v1v2 = df.loc[df.pair == f"{v1} - {v2}", :].to_dict("records")[0]
        v2v3 = df.loc[df.pair == f"{v2} - {v3}", :].to_dict("records")[0]
        v1v2_total = v1v2.pop("total")
        v2v3_total = v2v3.pop("total")

        def generate_graph_data(r, total, name, group):
            r = {key: value for (key, value) in r.items() if key in group}
            y = [r[i] for i in group]
            x = group
            hovertemplate = "<b>%{x} %{text}</b>"
            text = [f"{round(r[i]/total*100, 2)}%" for i in group]
            return go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name=name,
                hovertemplate=hovertemplate,
                text=text,
            )

        def generate_graph(v1v2, v2v3, v1v2_total, v2v3_total, group):
            fig = go.Figure()
            fig.add_trace(generate_graph_data(v1v2, v1v2_total, v1v2["pair"], group))
            fig.add_trace(generate_graph_data(v2v3, v2v3_total, v2v3["pair"], group))
            return fig

        for group in groups:
            fig = generate_graph(v1v2, v2v3, v1v2_total, v2v3_total, group["columns"])
            fig.update_layout(title=group["title"], template="plotly_white")
            st.plotly_chart(fig)
            st.info(group["description"])
        st.write(df)

    def create_null(df_null, v1, v2, v3, condo, mapped):
        df = df_null.loc[
            (df_null.condo == condo)
            & (df_null.mapped == mapped)
            & (df_null.pair.isin([f"{v1} - {v2}", f"{v2} - {v3}"])),
            :,
        ]
        v1v2 = df.loc[df_null.pair == f"{v1} - {v2}", :].to_dict("records")[0]
        v2v3 = df.loc[df_null.pair == f"{v2} - {v3}", :].to_dict("records")[0]
        v1v2_total = v1v2.pop("total")
        v2v3_total = v2v3.pop("total")

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

        fig = go.Figure()
        fig.add_trace(generate_graph(v1v2, v1v2_total, f"{v1} - {v2}"))
        fig.add_trace(generate_graph(v2v3, v2v3_total, f"{v2} - {v3}"))
        fig.update_layout(title="Null graph", template="plotly_white")
        st.plotly_chart(fig)
        st.write(df)
        st.info(
            """
        The mismatch graphs do not include lots that formerly had a value and are now null, or vice versa.
        These differences are captured in the null graph, which shows the percent change in lots with a null value.
        Hovering over a point shows you the number of null records in the more recent file. The number of such changes should be small.
        """
        )

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
            real_v1 = [v1[i] for i in y]
            real_v2 = [v2[i] for i in y]
            hovertemplate = "<b>%{x}</b> %{text}"
            text = []
            for n in range(len(y)):
                text.append(
                    "Percent Change: {:.2f}%<br>Prev: {:.2E} Current: {:.2E}".format(
                        x[n], real_v1[n], real_v2[n]
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
        fig.update_layout(
            title="Aggregate graph",
            template="plotly_white",
            yaxis={"title": "Percent Change"},
        )
        st.plotly_chart(fig)
        st.write(df)
        st.info(
            """
         The aggregate graph provides insights into the magnitude of changes, complementing the mismatch graph's functionality of showing the number of lots with a changed value.
         For example, the mismatch graph for finance may show that over 90% of lots get an updated assessment when the tentative roll is released.
         The aggregate graph may show that the aggregated sum of assessments increased by 5% compared with the previous version.\n
         Totals for assessland, assesstot, and exempttot should only change in February and June.\n
         Special Notes:\n
         1. Y-axis represents percent change over the previous version. \n
         2. Totals for assessland, assesstot, and exempttot should only change in February and June.\n
         3. Pay attention to any large changes to residential units (unitsres).
        """
        )

    def create_expected(df, v1, v2):

        exp = df[df["v"].isin([v1, v2])]

        exp_records = exp.to_dict("records")
        v1_exp = [i["expected"] for i in exp_records if i["v"] == v1][0]
        v2_exp = [i["expected"] for i in exp_records if i["v"] == v2][0]
        for field in [
            "zonedist1",
            "zonedist2",
            "zonedist3",
            "zonedist4",
            "overlay1",
            "overlay2",
            "spdist1",
            "spdist2",
            "spdist3",
            "ext",
            "proxcode",
            "irrlotcode",
            "lottype",
            "bsmtcode",
            "bldgclasslanduse",
        ]:
            val1 = [i["values"] for i in v1_exp if i["field"] == field][0]
            val2 = [i["values"] for i in v2_exp if i["field"] == field][0]
            in1not2 = [i for i in val1 if i not in val2]
            in2not1 = [i for i in val2 if i not in val1]
            if len(in1not2) == 0 and len(in2not1) == 0:
                pass
            else:
                st.markdown(f"### Expected value difference for {field}")
                if len(in1not2) != 0:
                    st.markdown(f"* in {v1} but not in {v2}:")
                    st.write(in1not2)
                if len(in2not1) != 0:
                    st.markdown(f"* in {v2} but not in {v1}:")
                    st.write(in2not1)

    def create_corrections(df):
        def generate_trace(v1):
            hovertemplate = "<b>%{x} - %{y}</b>"
            return go.Scatter(
                y=v1,
                x=v1.index,
                mode="lines",
                name="Pluto Corrections",
                hovertemplate=hovertemplate,
                text=v1.index
            )
        def generate_graph(v1):
            fig = go.Figure()
            fig.add_trace(generate_trace(v1))
            fig.update_yaxes(title_text="# of Corrected Records")
            fig.update_xaxes(title_text="Field")
            fig.update_layout(title="Corrected Records by Field", template="plotly_white")
            return fig

        def field_correction_counts(df):
            return df.groupby(['field']).size()
        
        figure = generate_graph(field_correction_counts(df))
        
        st.header("Corrections")
        st.plotly_chart(figure)
        st.info(
            """
            This report shows the number of records altered by DCP to correct errors in the underlying data, grouped by the field altered. See [here](https://www1.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page) for a full accounting of the changes made for the latest version
            in the PLUTO change file.
            """
        )

    create_mismatch(data["df_mismatch"], v1, v2, v3, condo, mapped)

    create_null(data["df_null"], v1, v2, v3, condo, mapped)

    create_aggregate(data["df_aggregate"], v1, v2, v3, condo, mapped)

    st.header("Source Data Versions")
    code = st.checkbox("code")
    if code:
        st.code(data["version_text"])
    else:
        st.markdown(data["version_text"])

    # EXPECTED VALUE
    st.header("Expected Value Comparison")
    st.write(
        "if nothing showed up, then it means there aren't any expected value change"
    )

    create_expected(data["df_expected"], v1, v2)

    create_corrections(data["pluto_corrections"])

