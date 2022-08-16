import streamlit as st
import pandas as pd
import json


class GeospatialCheck:
    def __init__(self, data):
        self.geospatial_check = data["geospatial_check"]

    def __call__(self):
        st.subheader("Geospatial Check")
        if self.geospatial_check is None:
            st.info("Geospatial Check Table Not Found")
            return
        df = self.geospatial_check
        df["result"] = df["result"].apply(json.loads)
        all_records = df.to_dict("records")
        self.display_not_in_nyc(all_records[0])
        self.display_nonmatch(all_records[1])

    def display_not_in_nyc(self, records):
        st.markdown("#### Properties That Are Not in NYC Borough Boundaries")
        records = records["result"][0]["values"]
        if records:
            df = pd.DataFrame(records)
            st.write(df)
        else:
            st.info("All properties are within NYC Borough Boundaries.")

    def display_nonmatch(self, records):
        st.markdown("#### Properties That Have Inconsistent Geographies")
        st.markdown(
            "We want to check whether the geocoded results lined up with other geography attributes in the data products.\
        The Borocode is checked against both Community District and BBL."
        )
        records = records["result"][0]["values"]
        if records:
            df = pd.DataFrame(records)
            st.write(df)
        else:
            st.info("No inconsistent geographies in the current version.")
