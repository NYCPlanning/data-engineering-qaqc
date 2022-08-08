import streamlit as st
import pdb
import pandas as pd
import plotly.express as px
from src.constants import COLOR_SCHEME


class FieldDistributionReport:
    def __init__(self, data) -> None:
        self.qaqc_field_distribution = data["qaqc_field_distribution"]

    def __call__(self):
        for report_type in ["Job_Status", "Job_Type"]:
            df = self.records_to_df(report_type)
            st.dataframe(df)
            self.display_field_distribution_graph(df, report_type)

    def display_field_distribution_graph(self, df, report_type):
        fig = px.bar(df, x=report_type.lower(), y="count")
        st.plotly_chart(fig)

    def job_type_df(self):
        return self.records_to_df("Job_Type")

    def job_status_df(self):
        return self.records_to_df("Job_Status")

    def records_to_df(self, field_name):
        # pdb.set_trace()
        return pd.DataFrame.from_records(
            self.qaqc_field_distribution.loc[
                self.qaqc_field_distribution.field_name == field_name
            ].iloc[0]["result"]
        )
