def gru():
    import streamlit as st
    import time
    from .constants import readme_markdown_text, tests
    from .helpers import get_qaqc_runs, run_all_workflows, get_geosupport_versions
    from .components import source_table, check_table

    geosupport_versions = get_geosupport_versions()
    geosupport_version= st.sidebar.selectbox(
        label="Choose a Geosupport version",
        options=list(geosupport_versions.keys())
    )
    geosupport_version_to_run = geosupport_versions[geosupport_version]

    st.header("GRU QAQC")
    st.write(
        """This page runs automated QAQC checks for various GRU-maintained files, displays source data info and makes outputs available for download.  \n
Checks are performed either by comparing files to each other or by comparing a file to the latest Geosupport release.
To perform a check, hit a button in the table below. The status column has a link to the latest Github workflow run for a given check  \n
Github repo found [here](https://github.com/NYCPlanning/db-gru-qaqc/)."""
    )

    st.header("Latest Source Data")
    source_table()

    st.header("QAQC Checks")
    workflows = get_qaqc_runs(geosupport_version)
    not_running_workflows = [
        action_name
        for action_name in tests["action_name"]
        if action_name not in workflows
        or (workflows[action_name]["status"] not in ["queued", "in_progress"])
    ]
    run_all_workflows(not_running_workflows, geosupport_version_to_run)
    check_table(workflows, geosupport_version=geosupport_version_to_run)

    st.header("README")
    st.markdown(readme_markdown_text)

    # this state gets set when an action is triggered, set to false once it's complete
    while st.session_state["currently_running"]:
        time.sleep(5)
        st.experimental_rerun()
