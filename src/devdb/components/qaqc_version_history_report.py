import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.constants import COLOR_SCHEME
import pdb


class QAQCVersionHistoryReport:
    def __init__(self, data, qaqc_check_dict, qaqc_check_sections) -> None:
        self.qaqc_version_history = data["qaqc_historic"]
        self.qaqc_checks = qaqc_check_dict
        self.qaqc_check_sections = qaqc_check_sections

    def __call__(self):
        st.subheader("Version History for QAQC Checks")
        for section_name, section_description in self.qaqc_check_sections.items():
            st.markdown(
                f"""
                ### {section_name} section
                {section_description}
                """
            )
            self.display_check_distribution(section_name)

    def display_check_distribution(self, section):
        checks = self.checks_by_section(section)
        df = self.filter_by_checks(checks)

        fig = go.Figure()

        for check in checks:
            fig.add_trace(self.generate_trace(check=check, df=df))

        fig.update_layout(title=section, template="plotly_white", colorway=COLOR_SCHEME)
        st.plotly_chart(fig)

    def filter_by_checks(self, checks):
        return self.qaqc_version_history[checks + ["version"]]

    def checks_by_section(self, section):
        return [
            check
            for check, value in self.qaqc_checks.items()
            if value["section"] == section
        ]

    def generate_trace(self, check, df):
        return go.Scatter(
            x=df.version,
            y=df[check],
            mode="lines",
            name=check,
        )
