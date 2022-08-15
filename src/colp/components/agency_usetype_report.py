import streamlit as st
from src.constants import COLOR_SCHEME
from abc import ABC
import plotly.express as px


class CountRecordsReport(ABC):
    def __call__(self):
        if self.data is None:
            st.info(f"No Count of records by {self.x_axis_col}")
            return
        by_agency = ""
        middle_str = ""
        by_usetype = ""
        if self.by_agency:
            by_agency = " agency"
        if self.by_usetype:
            by_usetype = " use type"
        if self.by_agency and self.by_usetype:
            middle_str = " and"
        st.subheader(
            f"City owned and leased properties by {by_agency}{middle_str}{by_usetype}",
            anchor="corrections-applied",
        )
        self.plot()

    def plot(self):
        x_lim = st.number_input(
            label=f"{self.category_plural} to visualize",
            min_value=2,
            max_value=self.data.shape[0],
            value=12,
        )
        self.data.sort_values(by="count", ascending=False, inplace=True)
        fig1 = px.bar(
            self.data.iloc[
                :x_lim,
            ],
            x=self.x_axis_col,
            y="count",
            width=1000,
            color_discrete_sequence=COLOR_SCHEME,
        )

        fig1.update_xaxes(title=self.x_axis_col[0] + self.x_axis_col[1:].lower())
        fig1.update_layout(legend_title_text="Count")

        st.plotly_chart(fig1)


class RecordsByAgency(CountRecordsReport):
    def __init__(self, records_by_agency) -> None:
        self.data = records_by_agency
        self.by_agency = True
        self.x_axis_col = "AGENCY"
        self.by_usetype = False
        self.category_plural = "Agencies"


class RecordsByUsetype(CountRecordsReport):
    def __init__(self, records_by_usetype) -> None:
        self.data = records_by_usetype
        self.by_agency = False
        self.x_axis_col = "USETYPE"
        self.by_usetype = True
        self.category_plural = "Use types"


class RecordsByAgencyUsetype(CountRecordsReport):
    def __init__(self, records_by_agency_usetype) -> None:
        self.data = records_by_agency_usetype
        self.data["agency-use type"] = (
            self.data["AGENCY"] + " - " + self.data["USETYPE"]
        )
        self.by_agency = True
        self.x_axis_col = "agency-use type"
        self.by_usetype = True
        self.category_plural = "Agency-use type combinations"
