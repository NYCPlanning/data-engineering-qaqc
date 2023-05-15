import streamlit as st
import pandas as pd


def get_latest_data(branch):
    url = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-facilities/{branch}/latest/output"
    qc_diff = pd.read_csv(f"{url}/qc_diff.csv")
    qc_captype = pd.read_csv(f"{url}/qc_captype.csv")
    qc_classification = pd.read_csv(f"{url}/qc_classification.csv")
    qc_mapped = pd.read_csv(f"{url}/qc_mapped.csv")
    qc_operator = pd.read_csv(f"{url}/qc_operator.csv")
    qc_oversight = pd.read_csv(f"{url}/qc_oversight.csv")

    qc_tables = {
        "Facility subgroup classification": {
            "dataframe": qc_classification,
            "type": "dataframe",
        },
        "Operator": {"dataframe": qc_operator, "type": "dataframe"},
        "Oversight": {"dataframe": qc_oversight, "type": "dataframe"},
        "Capacity Types": {"dataframe": qc_captype, "type": "table"},
    }
    return qc_tables, qc_diff, qc_mapped
