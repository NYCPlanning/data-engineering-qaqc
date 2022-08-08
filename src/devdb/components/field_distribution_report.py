import streamlit as st
import pdb
import pandas as pd
import plotly.express as px
from src.constants import COLOR_SCHEME


class FieldDistributionReport:
    def __init__(self, data) -> None:
        self.qaqc_field_distribution = data["qaqc_field_distribution"]
        self.report_sections = {
            "Job_Status": {"title": "Job Status", "description": ""},
            "Job_Type": {"title": "Job Type", "description": ""},
        }

    def __call__(self):
        for field_name, field_descriptions in self.report_sections.items():
            st.subheader(field_descriptions["title"])

            df = self.records_to_df(field_name)

            self.display_field_distribution_graph(
                df, field_name.lower(), field_descriptions
            )

    def display_field_distribution_graph(self, df, field_name, field_descriptions):
        fig = px.bar(
            df,
            x=field_name,
            y="count",
            color_discrete_sequence=COLOR_SCHEME,
            labels={
                "count": "Count of Records",
                field_name: field_descriptions["title"],
            },
        )

        st.plotly_chart(fig)

    def job_type_df(self):
        return self.records_to_df("Job_Type")

    def job_status_df(self):
        return self.records_to_df("Job_Status")

    def records_to_df(self, field_name):
        return pd.DataFrame.from_records(
            self.qaqc_field_distribution.loc[
                self.qaqc_field_distribution.field_name == field_name
            ].iloc[0]["result"]
        )
