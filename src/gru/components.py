import streamlit as st
from .constants import tests
from .helpers import get_source_versions, render_status, after_workflow_dispatch
from ..github import dispatch_workflow_button


def source_table():
    column_widths = (1, 2)
    cols = st.columns(column_widths)
    fields = ["Name", "Latest Version Archived by DE"]
    for col, field_name in zip(cols, fields):
        col.write(f"**{field_name}**")
    source_versions = get_source_versions()
    for source in source_versions:
        col1, col2 = st.columns(column_widths)
        col1.write(source)
        col2.write(source_versions[source])


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
                render_status(workflow)
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
