import streamlit as st
import pandas as pd


class ManualCorrection:
    def __init__(self, data):
        self.modifications_applied = data["modifications_applied"]
        self.modifications_not_applied = data["modifications_not_applied"]

    def __call__(self):
        st.subheader("Manual Correction Report")

        if (
            self.modifications_applied is None
            and self.modifications_not_applied is None
        ):
            st.info("No Manual Correction Table Available.")
            return
        self.display_manual_correction()

    def display_manual_correction(self):
        applied = self.modifications_applied
        not_applied = self.modifications_not_applied
        if not applied.empty:
            count1 = applied.groupby("field").size()
            count1 = count1.reset_index()
            count1.rename(
                columns={"field": "Field", 0: "Number of Records"}, inplace=True
            )
            st.subheader("Numbers of Manual Corrections Applied By Field")
            st.write(count1)
        if not not_applied.empty:
            count2 = not_applied.groupby("field").size()
            count2 = count2.reset_index()
            count2.rename(
                columns={"field": "Field", 0: "Number of Records"}, inplace=True
            )
            st.subheader("Numbers of Manual Corrections Not Applied By Field")
            st.write(count2)
            not_applied = not_applied.sort_values(by=["field"])
            st.subheader("Table of Manual Corrections Not Applied")
            st.write(not_applied)
