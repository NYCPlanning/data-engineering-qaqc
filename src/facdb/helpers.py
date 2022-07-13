import streamlit as st
import pandas as pd

remove_branches = [
    "524_AddPOPSNumber",
    "528-Manager-Address-Approach",
    "528-usairports-update-source",
    "530-docker-compose-postgres-install-issue",
    "532-update-moeo-socialservicesitelocations",
    "534-q2-update-check-dataloading",
    "535-Fix-Fooddrops",
    "543-No-Build-On-Push",
    "546-Metadata-Output",
    "547-update-dcp-pops-version",
    "549-QAQC-compare-to-all-records",
    "553-Clarify-QAQC-Mapped",
    "554-update-dot-data",
    "558-remove-special-character-moeo-sonyc",
    "559-update-projection-shapefile",
    "560-doe-lcgms-latest",
    "563-Update-TextileDrop",
    "567_MOEOProgramName",
    "574-Rename-POPS-Number",
    "Address-Poetry-Merge-Conflict",
    "dataloading-issue-template",
]


@st.experimental_memo
def get_data(branch):
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
