import streamlit as st
from src.constants import COLOR_SCHEME
from abc import ABC
import plotly.express as px


class CountRecordsReport(ABC):
    def __call__(self):
        if self.data is None:
            st.info(f"No Count of records by {self.y_axis_col}")
            return
        self.set_title()
        self.plot()

    def set_title(self):
        by_agency = ""
        middle_str = ""
        by_usetype = ""
        by_agency = "agency" if self.by_agency else ""
        by_usetype = " use type" if self.by_usetype else ""
        middle_str = " and" if self.by_agency and self.by_usetype else ""
        st.subheader(
            f"City owned and leased properties by {by_agency}{middle_str}{by_usetype}",
            anchor="corrections-applied",
        )

    def plot(self):
        slider_input = st.select_slider(
            label=f"Most common {self.category_plural} to visualize",
            options=range(1, self.data.shape[0] + 1),
            value=(1, 12),
        )
        self.data.sort_values(by="count", ascending=False, inplace=True)
        fig1 = px.bar(
            self.data.iloc[
                slider_input[0] : slider_input[1],
            ].sort_values(by="count", ascending=True),
            y=self.y_axis_col,
            x="count",
            orientation="h",
            barmode="group",
            width=850,
            height=500,
            color_discrete_sequence=COLOR_SCHEME,
        )

        fig1.update_yaxes(title=self.y_axis_label)
        fig1.update_layout(legend_title_text="Count")

        st.plotly_chart(fig1)


class RecordsByAgency(CountRecordsReport):
    def __init__(self, records_by_agency) -> None:
        self.data = records_by_agency
        self.by_agency = True
        self.y_axis_col = "AGENCY"
        self.y_axis_label = "Agency"
        self.by_usetype = False
        self.category_plural = "Agencies"


class RecordsByUsetype(CountRecordsReport):
    def __init__(self, records_by_usetype) -> None:
        self.data = records_by_usetype
        self.by_agency = False
        self.y_axis_col = "USETYPE"
        self.y_axis_label = "Use type"
        self.by_usetype = True
        self.category_plural = "Use types"


class RecordsByAgencyUsetype(CountRecordsReport):
    def __init__(self, records_by_agency_usetype) -> None:
        self.data = records_by_agency_usetype
        self.data["agency-use type"] = (
            self.data["AGENCY"] + " - " + self.data["USETYPE"].str.replace("-", "/")
        )
        self.by_agency = True
        self.y_axis_col = "agency-use type"
        self.y_axis_label = "Agency/use type combination"
        self.by_usetype = True
        self.category_plural = "Agency-use type combinations"
