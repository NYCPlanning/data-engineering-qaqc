from datetime import datetime
import pytz
import streamlit as st

from .constants import tests
from .helpers import get_source_versions, after_workflow_dispatch
from ..github import dispatch_workflow_button


def status_details(workflow):
    timestamp = (
        datetime.fromisoformat(workflow["timestamp"])
        .astimezone(pytz.timezone("US/Eastern"))
        .strftime("%Y-%m-%d %H:%M")
    )
    format = lambda status: f"{status}  \n[{timestamp}]({workflow['url']})"
    if workflow["status"] in ["queued", "in_progress"]:
        st.warning(format(workflow["status"].capitalize().replace("_", " ")))
        st.spinner()
    elif workflow["status"] == "completed":
        if workflow["conclusion"] == "success":
            st.success(format("Success"))
        elif workflow["conclusion"] == "cancelled":
            st.info(format("Cancelled"))
        elif workflow["conclusion"] == "failure":
            st.error(format("Failed"))
        else:
            st.write(workflow["conclusion"])


def source_table():
    column_widths = (4, 5, 3)
    cols = st.columns(column_widths)
    fields = ["Name", "Latest version archived by DE", "Date of archival"]
    for col, field_name in zip(cols, fields):
        col.write(f"**{field_name}**")
    source_versions = get_source_versions()
    for source in source_versions:
        col1, col2, col3 = st.columns(column_widths)
        col1.write(source)
        col2.write(source_versions[source]["version"])
        col3.write(source_versions[source]["date"])


def check_table(workflows):
    column_widths = (3, 3, 4, 3, 2)
    cols = st.columns(column_widths)
    fields = ["Name", "Sources", "Latest results", "Status", "Run Check"]
    for col, field_name in zip(cols, fields):
        col.write(f"**{field_name}**")

    st.session_state["currently_running"] = False

    for _, test in tests.iterrows():
        action_name = test["action_name"]

        name, sources, outputs, status, run = st.columns(column_widths)

        name.write(test["display_name"])

        sources.write("  \n".join(test["sources"]))

        folder = f"https://edm-publishing.nyc3.digitaloceanspaces.com/db-gru-qaqc/{action_name}/latest"
        files = "  \n".join(
            [f"[{filename}.csv]({folder}/{filename}.csv)" for filename in test["files"]]
            + [f"[versions.csv]({folder}/versions.csv)"]
        )
        outputs.write(files)

        with status:
            if action_name in workflows:
                workflow = workflows[action_name]
                status_details(workflow)
                running = workflow["status"] in ["queued", "in_progress"]
                st.session_state["currently_running"] = (
                    st.session_state["currently_running"] or running
                )
            else:
                st.info(format("No past run found"))

        with run:
            dispatch_workflow_button(
                "db-gru-qaqc",
                "main.yml",
                disabled=running,
                key=test["action_name"],
                name=test["action_name"],
                run_after=after_workflow_dispatch,
            )  ## refresh after 2 so that status has hopefully
