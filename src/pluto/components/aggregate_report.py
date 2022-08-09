import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.constants import COLOR_SCHEME
import pdb


class AggregateReport:
    def __init__(self, data, v1, v2, v3, condo, mapped):
        self.df_aggregate = data
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.condo = condo
        self.mapped = mapped

    def __call__(self):
        df = self.filter_by_options(self.df_aggregate)

        v1 = self.filter_by_version(df, self.v1)
        v2 = self.filter_by_version(df, self.v2)
        v3 = self.filter_by_version(df, self.v3)

        self.display_graph(v1, v2, v3)

    def display_graph(self, v1, v2, v3):
        fig = go.Figure()

        fig.add_trace(self.generate_graph(v1, v2))
        fig.add_trace(self.generate_graph(v2, v3))
        fig.update_layout(
            title="Aggregate graph",
            template="plotly_white",
            yaxis={"title": "Percent Change"},
            colorway=COLOR_SCHEME,
        )
        st.plotly_chart(fig)

    def columns(self):
        return [
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

    def version_text(self, df):
        return df["v"].iloc[0]

    def filter_by_columns(self, df, columns, version):
        return df[columns].iloc[0].to_frame(name=version)

    def create_version_pair(self, v1, v2, v1_text, v2_text):
        filtered_v1 = self.filter_by_columns(v1, self.columns(), v1_text)
        filtered_v2 = self.filter_by_columns(v1, self.columns(), v2_text)
        version_pair_df = filtered_v1.join(filtered_v2)
        pair_string = f"{v1_text} - {v2_text}"
        version_pair_df[pair_string] = (
            version_pair_df[v1_text] / version_pair_df[v2_text] - 1
        ) * 100
        version_pair_df[
            "text"
        ] = "Percent Change: {:.2f}%<br>Prev: {:.2E} Current: {:.2E}".format(
            version_pair_df[pair_string],
            version_pair_df[v1_text],
            version_pair_df[v2_text],
        )
        return version_pair_df

    def generate_graph(self, v1, v2):
        v1_text = self.version_text(v1)
        v2_text = self.version_text(v2)
        pair_string = f"{v1_text} - {v2_text}"
        version_pair_df = self.create_version_pair(v1, v2, v1_text, v2_text)
        hovertemplate = "<b>%{x}</b> %{text}"

        return go.Scatter(
            x=version_pair_df.index,
            y=version_pair_df[pair_string],
            mode="lines",
            name=pair_string,
            hovertemplate=hovertemplate,
            text=version_pair_df["text"],
        )

    def filter_by_version(self, df, version):
        return df.loc[df.v == version, :]

    def filter_by_options(self, df):
        return df.loc[
            (df.condo == self.condo)
            & (df.mapped == self.mapped)
            & (df.v.isin([self.v1, self.v2, self.v3])),
            :,
        ]
