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
            st.info("No Manual Correction Table.")
            return
        self.display_manual_correction()

    def display_manual_correction(self):
        applied = self.modifications_applied
        not_applied = self.modifications_not_applied
        if not applied.empty:
            count1 = applied.groupby("field").size()
            count1.rename("Number of Records", inplace=True)
            st.markdown("##### Numbers of Manual Corrections Applied By Field")
            st.write(count1)
        if not not_applied.empty:
            count2 = not_applied.groupby("field").size()
            count2.rename("Number of Records", inplace=True)
            st.markdown("##### Numbers of Manual Corrections Not Applied By Field")
            st.write(count2)
            uid = not_applied["uid"]
            not_applied = not_applied.drop(columns=["uid"]).sort_values(by=["field"])
            not_applied = pd.concat([not_applied, uid], axis=1)
            st.markdown("##### Table of Manual Corrections Not Applied")
            st.write(not_applied)
