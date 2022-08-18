import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.constants import COLOR_SCHEME
import pdb


class NullReport:
    def __init__(self, data, v1, v2, v3, condo, mapped):
        self.df_null = data
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.condo = condo
        self.mapped = mapped

    def __call__(self):
        st.subheader("Null Graph")
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

        field_range = st.slider(
            "Select a range of values",
            min_value=0,
            max_value=len(x),
            value=[0, 12],
        )

        df = self.df_null
        df = df.loc[
            (df.condo == self.condo)
            & (df.mapped == self.mapped)
            & (df.pair.isin([f"{self.v1} - {self.v2}", f"{self.v2} - {self.v3}"])),
            :,
        ].drop_duplicates()

        df_transformed = df.drop(columns=["condo", "mapped", "total"])
        df_transformed = self.sort_and_filter_df(df_transformed, field_range)

        v1v2 = f"{self.v1} - {self.v2}" in df_transformed.version.unique()
        v2v3 = f"{self.v2} - {self.v3}" in df_transformed.version.unique()

        if not (v1v2 or v2v3):
            st.write("Null Graph")
            st.info("There is no change in NULL values across three versions.")
            return
        if v1v2 and not v2v3:
            self.display_graph(df_transformed, field_range, False)
        elif v2v3 and not v1v2:
            self.display_graph(df_transformed, field_range, False)
        else:
            self.display_graph(df_transformed, field_range, True)

        st.info(
            """
                The above graph highlights records that formerly had a value and are now NULL, or vice versa.
                The number records going from NULL to not NULL or vice versa should be small for any field.
            """
        )
        st.write(df)

    def sort_and_filter_df(self, df, range):
        df = df[["pair"] + df.columns.tolist()[range[0] + 1 : range[1] + 1]]
        df_transformed = (
            df.set_index("pair")
            .stack()
            .reset_index()
            .rename(columns={"pair": "version", "level_1": "field", 0: "change"})
            .sort_values(by="change", ascending=False)
        )
        return df_transformed

    def display_graph(self, df_transformed, range, grouped=True):
        if grouped:
            fig1 = px.bar(
                data_frame=df_transformed,
                y="change",
                x="field",
                barmode="group",
                color="version",
                color_discrete_sequence=COLOR_SCHEME,
                height=400,
                width=850,
                text_auto=True,
                title="Null Graph",
            )
            fig1.update_layout(legend_title_text="Version")
        else:
            fig1 = px.bar(
                data_frame=df_transformed,
                y="change",
                x="field",
                color_discrete_sequence=COLOR_SCHEME,
                height=400,
                width=850,
                text_auto=True,
                title="Null Graph",
            )
        fig1.update_xaxes(title="Field")
        fig1.update_yaxes(title="Change in Null")

        st.plotly_chart(fig1)
