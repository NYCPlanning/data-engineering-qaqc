def pluto():
    import streamlit as st
    import pandas as pd
    import numpy as np
    from sqlalchemy import create_engine
    import plotly.graph_objects as go
    import os
    from datetime import datetime
    import requests

    ENGINE = os.environ["ENGINE"]

    st.title("PLUTO QAQC")
    st.markdown(
        """
    ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/NYCPlanning/db-pluto?label=version) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NYCPlanning/db-pluto/CI?label=CI) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NYCPlanning/db-pluto/CAMA%20Processing?label=CAMA) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NYCPlanning/db-pluto/PTS%20processing?label=PTS)
    """
    )

    engine = create_engine(ENGINE)

    @st.cache(suppress_st_warning=True, allow_output_mutation=True)
    def get_data():
        def convert(dt):
            try:
                d = datetime.strptime(dt, "%Y/%m/%d")
                return d.strftime("%m/%d/%y")
            except BaseException:
                return dt

        engine = create_engine(ENGINE)
        df_mismatch = pd.read_sql("SELECT * FROM dcp_pluto.qaqc_mismatch", con=engine)
        df_null = pd.read_sql("SELECT * FROM dcp_pluto.qaqc_null", con=engine)
        df_aggregate = pd.read_sql("SELECT * FROM dcp_pluto.qaqc_aggregate", con=engine)
        source_data_versions = pd.read_csv(
            "https://edm-publishing.nyc3.digitaloceanspaces.com/db-pluto/latest/output/source_data_versions.csv"
        )
        sdv = source_data_versions.to_dict("records")
        version = {}
        for i in sdv:
            version[i["schema_name"]] = i["v"]
        version_text = f"""
            Department of City Planning – E-Designations: ***{convert(version['dcp_edesignation'])}***  
            Department of City Planning – Georeferenced NYC Zoning Maps: ***{convert(version['dcp_zoningmapindex'])}***  
            Department of City Planning – NYC City Owned and Leased Properties: ***{convert(version['dcp_colp'])}***  
            Department of City Planning – NYC GIS Zoning Features: ***{convert(version['dcp_zoningdistricts'])}***  
            Department of City Planning – Political and Administrative Districts: ***{convert(version['dcp_cdboundaries'])}***  
            Department of City Planning – Geosupport version: ***{convert(version['dcp_cdboundaries'])}***  
            Department of Finance – Digital Tax Map (DTM): ***{convert(version['dof_dtm'])}***  
            Department of Finance – Mass Appraisal System (CAMA): ***{convert(version['pluto_input_cama_dof'])}***  
            Department of Finance – Property Tax System (PTS): ***{convert(version['pluto_pts'])}***  
            Landmarks Preservation Commission – Historic Districts: ***{convert(version['lpc_historic_districts'])}***  
            Landmarks Preservation Commission – Individual Landmarks: ***{convert(version['lpc_landmarks'])}***  
        """
        log = requests.get(
            "https://raw.githubusercontent.com/NYCPlanning/db-pluto/master/maintenance/log.md"
        ).text
        return (
            df_mismatch,
            df_null,
            df_aggregate,
            source_data_versions,
            version_text,
            log,
        )

    (
        df_mismatch,
        df_null,
        df_aggregate,
        source_data_versions,
        version_text,
        log,
    ) = get_data()

    versions = [
        i[0]
        for i in engine.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'dcp_pluto'
            AND table_name !~*'qaqc|latest';
            """
        ).fetchall()
    ]

    versions_order = [
        "19v1",
        "19v2",
        "20v1",
        "20v2",
        "20v3",
        "20v4",
        "20v5",
        "20v6",
        "20v7",
        "20v8",
        "20v9",
        "20v10",
        "20v11",
        "20v12",
    ]

    v1 = st.sidebar.selectbox(
        "Pick a version of PLUTO:", versions, index=len(versions) - 1
    )
    
    v2 = versions_order[versions_order.index(v1) - 1]
    v3 = versions_order[versions_order.index(v1) - 2]

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

        v1v2 = df.loc[df_mismatch.pair == f"{v1} - {v2}", :].to_dict("records")[0]
        v2v3 = df.loc[df_mismatch.pair == f"{v2} - {v3}", :].to_dict("records")[0]
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
            & (df_null.v.isin([v1, v2, v3])),
            :,
        ]
        v1 = df.loc[df.v == v1, :].to_dict("records")[0]
        v2 = df.loc[df.v == v2, :].to_dict("records")[0]
        v3 = df.loc[df.v == v3, :].to_dict("records")[0]

        def generate_graph(v1, v2):
            _v1 = v1["v"]
            _v2 = v2["v"]
            total1 = v1["total"]
            total2 = v2["total"]

            y = [
                "borough",
                "block",
                "lot",
                "cd",
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

            x = []
            for i in y:
                pct1 = v1[i] / total1
                pct2 = v2[i] / total2
                if pct2 != 0:
                    x.append(round(100 * (pct1 - pct2) / pct2, 4))
                else:
                    x.append(None)

            return go.Scatter(
                x=y,
                y=x,
                mode="lines",
                name=f"{_v1} - {_v2}",
                text=[f"count_in_{_v1} : {v1[i]}" for i in y],
            )

        fig = go.Figure()
        fig.add_trace(generate_graph(v1, v2))
        fig.add_trace(generate_graph(v2, v3))
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
            hovertemplate = "<b>%{x} %{text}</b>"
            return go.Scatter(
                x=y,
                y=x,
                mode="lines",
                name=f"{_v1} - {_v2}",
                hovertemplate=hovertemplate,
                text=[f"{round(i,2)}%" for i in x],
            )

        fig = go.Figure()
        fig.add_trace(generate_graph(v1, v2))
        fig.add_trace(generate_graph(v2, v3))
        fig.update_layout(title="Aggregate graph", template="plotly_white")
        st.plotly_chart(fig)
        st.write(df)
        st.info(
            """
         In addition to looking at the number of lots with a changed value, it’s important to look at the magnitude of the change.
         For example, the mismatch graph for finance may show that over 90% of lots get an updated assessment when the tentative roll is released.
         The aggregate graph may show that the aggregated sum increased by 5%. Totals for assessland, assesstot, and exempttot should only change in February and June.
         Pay attention to any large changes to residential units (unitsres).
        """
        )

    create_mismatch(df_mismatch, v1, v2, v3, condo, mapped)

    create_null(df_null, v1, v2, v3, condo, mapped)

    create_aggregate(df_aggregate, v1, v2, v3, condo, mapped)

    st.header("Source Data Versions")
    code = st.checkbox("code")
    if code:
        st.code(version_text)
    else:
        st.markdown(version_text)

    # EXPECTED VALUE
    st.header("Expected Value Comparison")
    st.write(
        "if nothing showed up, then it means there aren't any expected value change"
    )

    @st.cache(suppress_st_warning=True, allow_output_mutation=True)
    def get_expected_value(v1, v2):
        engine = create_engine(ENGINE)
        df = pd.read_sql(
            f"SELECT * FROM dcp_pluto.qaqc_expected where v ~* '{v1}|{v2}'", con=engine
        )
        return df

    exp = get_expected_value(v1, v2)
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

    seelog = st.sidebar.checkbox("see build log?")
    if seelog:
        st.sidebar.markdown(log)
