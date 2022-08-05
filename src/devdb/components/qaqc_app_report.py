import streamlit as st


class QAQCAppReport:
    def __init__(self, data) -> None:
        self.qaqc_app = data["qaqc_app"]
        self.qaqc_checks = {
            "b_likely_occ_desc": {
                "description": "Likely a OCC Desc",
                "field_type": "boolean",
            },
            "b_large_alt_reduction": {
                "description": "Alterations with large (>5) reductions in Class A units",
                "field_type": "boolean",
            },
            "b_nonres_with_units": {
                "description": "Non-Residential Jobs with Non-Zero Class A initial or proposed units",
                "field_type": "boolean",
            },
            "units_co_prop_mismatch": {
                "description": "New Building and Alterations Jobs Where Class A proposed units is not equal to co_latest_units",
                "field_type": "boolean",
            },
            "partially_complete": {
                "description": "Job Status of 4. Partially Completed",
                "field_type": "boolean",
            },
            "units_init_null": {
                "description": "Demolitions and Alterations in Residential Jobs with Null Class A Initial Units",
                "field_type": "boolean",
            },
            "units_prop_null": {
                "description": "New Buildings and Alterations in Residential Jobs with Null Class A Proposed Units",
                "field_type": "boolean",
            },
            "units_res_accessory": {
                "description": "Is an ADU",
                "field_type": "boolean",
            },
            "outlier_demo_20plus": {
                "description": "Demolition Jobs with larger than 19 Class A Initial Units",
                "field_type": "boolean",
            },
            "outlier_nb_500plus": {
                "description": "New Building Jobs with more than 499 Class A proposed units",
                "field_type": "boolean",
            },
            "outlier_top_alt_increase": {
                "description": "The 20 largest alterations by increase in Class A units",
                "field_type": "boolean",
            },
            "dup_bbl_address_units": {
                "description": "Duplicate BBL Address Units",
                "field_type": "string",
            },
            "dup_bbl_address": {
                "description": "Duplicate BBL Address",
                "field_type": "string",
            },
            "inactive_with_update": {
                "description": "Date Last Updated > Last Captured Date and Job Inactive is set to new value",
                "field_type": "boolean",
            },
            "no_work_job": {
                "description": "Jobs without work to be done",
                "field_type": "boolean",
            },
            "geo_water": {
                "description": "Jobs located in the water",
                "field_type": "boolean",
            },
            "geo_taxlot": {
                "description": "Jobs with a missing BBL",
                "field_type": "boolean",
            },
            "geo_null_latlong": {
                "description": "Jobs with a NULL Lat/Long Field",
                "field_type": "boolean",
            },
            "geo_null_boundary": {
                "description": "Jobs with a NULL boundary field",
                "field_type": "boolean",
            },
            "invalid_date_filed": {
                "description": "Date Filed is not a date or is before 1990",
                "field_type": "boolean",
            },
            "invalid_date_lastupdt": {
                "description": "Date Last Updated is not a date or is before 1990",
                "field_type": "boolean",
            },
            "invalid_date_statusd": {
                "description": "Date Statusd is not a date or is before 1990",
                "field_type": "boolean",
            },
            "invalid_date_statusp": {
                "description": "Date Statusp is not a date or is before 1990",
                "field_type": "boolean",
            },
            "invalid_date_statusr": {
                "description": "Date Statusr is not a date or is before 1990",
                "field_type": "boolean",
            },
            "invalid_date_statusx": {
                "description": "Date Statusx is not a date or is before 1990",
                "field_type": "boolean",
            },
            "incomp_tract_home": {
                "description": "Tracthomes flag is Y and job status in 1,2,3",
                "field_type": "boolean",
            },
            "dem_nb_overlap": {
                "description": "Duplicates between new buildings and demolitions",
                "field_type": "boolean",
            },
            "classa_net_mismatch": {
                "description": "Class A Net units is not equal to Class A proposed - Class A init",
                "field_type": "boolean",
            },
        }

    def __call__(self):
        st.subheader("Flagged Jobs by QAQC Check")
        st.markdown(
            "Each of these tables lists job numbers with specific highlighted potential issues."
        )

        qaqc_check = st.selectbox(
            "Choose a QAQC Check to View Flagged Records",
            options=self.qaqc_checks.keys(),
            format_func=lambda x: f"{self.qaqc_checks[x]['description']}: {x}",
        )

        self.display_check(qaqc_check)

    def display_check(self, qaqc_check):
        df = self.filter_by_check(qaqc_check)

        if df.empty:
            st.write("There are no jobs with this status.")
        else:
            st.write(df)

    def filter_by_check(self, check):
        if self.qaqc_checks[check]["field_type"] == "boolean":
            return self.qaqc_app.loc[self.qaqc_app[check] == 1][["job_number"]]
        elif self.qaqc_checks[check]["field_type"] == "string":
            return self.qaqc_app.loc[self.qaqc_app[check].notnull()][
                ["job_number", check]
            ]
