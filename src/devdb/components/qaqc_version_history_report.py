import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.constants import COLOR_SCHEME
import pdb


class QAQCVersionHistoryReport:
    def __init__(self, data, qaqc_check_dict, qaqc_check_groups) -> None:
        self.qaqc_version_history = data["qaqc_historic"]
        self.qaqc_checks = qaqc_check_dict
        self.qaqc_check_groups = qaqc_check_groups

    def __call__(self):
        st.subheader("Version History for QAQC Checks")
        for group_name, group_description in self.qaqc_check_groups.items():
            st.markdown(
                f"""
                ### {group_name} Group
                {group_description}
                """
            )
            self.display_check_distribution(group_name)

    def display_check_distribution(self, group):
        checks = self.checks_by_group(group)
        df = self.filter_by_checks(checks)
        versions = ["21Q4", "21Q2", "20Q4"]

        fig = go.Figure()

        for version in versions:
            fig.add_trace(
                self.generate_graph_data(checks=checks, version=version, df=df)
            )

        fig.update_layout(title=group, template="plotly_white", colorway=COLOR_SCHEME)
        st.plotly_chart(fig)

    def filter_by_checks(self, checks):
        return self.qaqc_version_history[checks + ["version"]]

    def checks_by_group(self, group):
        return [
            check
            for check, value in self.qaqc_checks.items()
            if value["group"] == group
        ]

    def generate_graph_data(self, checks, version, df):
        return go.Scatter(
            x=checks,
            y=df.loc[df["version"] == version].squeeze(),
            mode="lines",
            name=version,
        )
