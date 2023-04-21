def check_table():
    import streamlit as st
    from .constants import tests
    from .helpers import get_qaqc_runs, status, after_workflow_dispatch
    from ..github import dispatch_workflow_button

    cols = st.columns((5, 4, 3, 3, 2))
    fields = ["Name", 'Latest result', 'Source version', 'Status', 'Run']
    for col, field_name in zip(cols, fields):
        col.write(field_name)

    workflows = get_qaqc_runs()
    st.session_state['currently_running'] = False

    for _, test in tests.iterrows():
        action_name=test['action_name']
        workflow = workflows[action_name]
        running = workflow['status'] in ['queued', 'in_progress']
        st.session_state['currently_running'] = st.session_state['currently_running'] or running

        col1, col2, col3, col4, col5 = st.columns((5, 4, 3, 3, 2))

        col1.write(test['display_name'])

        folder = f'https://edm-publishing.nyc3.digitaloceanspaces.com/db-gru-qaqc/{action_name}/latest'
        for filename in test['filename']:
            filename = filename + '.csv'
            col2.write(f'[{filename}]({folder}/{filename})')
        col3.write(f'[versions.csv]({folder}/versions.csv)')

        with col4: status(workflow)
        with col5: 
            dispatch_workflow_button(
                'db-gru-qaqc', 
                'main.yml', 
                disabled=running,
                key=test['action_name'], 
                name=test['action_name'], 
                run_after=after_workflow_dispatch) ## refresh after 2 so that status has hopefully


def gru():
    import streamlit as st
    import time
    from .constants import readme_markdown_text

    st.header("GRU QAQC")
    st.write("This page runs automated QAQC checks for various GRU-maintained files, displays source data info and makes outputs available for download.")
    st.write("""Checks are performed either by comparing files to each other or by comparing a file to the latest Geosupport release.
        To perform a check, hit a button in the table below. The status column has a link to the latest Github workflow run for a given check""")
    st.write("Detailed instructions are in the [instructions folder](https://github.com/NYCPlanning/db-gru-qaqc/blob/update-docs/instructions/instructions.md) in GitHub.")
    
    st.header("Latest Source Data")

    st.header("QAQC Checks")
    check_table()

    st.header("README")
    st.markdown(readme_markdown_text)

    while st.session_state['currently_running']:
        time.sleep(5)
        st.experimental_rerun()
