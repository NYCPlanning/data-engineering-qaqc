import streamlit as st
import pandas as pd
import pdb


class ExpectedValueDifferencesReport:
    def __init__(self, data, v1, v2):
        self.df = data
        self.v1 = v1
        self.v2 = v2

    def __call__(self):
        # EXPECTED VALUE
        st.header("Expected Value Comparison")
        st.write(
            """
            For some fields we report the expected values and descriptions in appendixes of the ReadMe document. 
            Therefore, it's important for us to know when new values are added to field or a value is no longer present in a field. 
            If the below is blank, that means that there are no changes in the values in selected fields between the selected and previous version.
        """
        )

        for field in self.fields:
            v1_values = self.values_by_field(self.v1_expected_records, field)
            v2_values = self.values_by_field(self.v2_expected_records, field)

            in1not2 = self.value_differences(v1_values, v2_values)
            in2not1 = self.value_differences(v2_values, v1_values)

            if len(in1not2) == 0 and len(in2not1) == 0:
                pass
            else:
                st.markdown(f"### Expected value difference for {field}")
                if len(in1not2) != 0:
                    st.markdown(f"* in {self.v1} but not in {self.v2}:")
                    st.write(in1not2)
                if len(in2not1) != 0:
                    st.markdown(f"* in {self.v2} but not in {self.v1}:")
                    st.write(in2not1)

    @property
    def expected_records(self):
        return self.df[self.df["v"].isin([self.v1, self.v2])].to_dict("records")

    @property
    def v1_expected_records(self):
        return self.expected_records_by_version(self.v1)

    @property
    def v2_expected_records(self):
        return self.expected_records_by_version(self.v2)

    def expected_records_by_version(self, version):
        return [i["expected"] for i in self.expected_records if i["v"] == version][0]

    @property
    def fields(self):
        return [
            "zonedist1",
            "zonedist2",
            "zonedist3",
            "zonedist4",
            "overlay1",
            "overlay2",
            "spdist1",
            "spdist2",
            "spdist3",
            "ext",
            "proxcode",
            "irrlotcode",
            "lottype",
            "bsmtcode",
            "bldgclasslanduse",
        ]

    def values_by_field(self, df, field):
        return [i["values"] for i in df if i["field"] == field][0]

    def value_differences(self, df1, df2):
        return [i for i in df1 if i not in df2]
