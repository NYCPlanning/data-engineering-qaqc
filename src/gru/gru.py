def check_table(workflows):
    import streamlit as st
    from .constants import tests
    from .helpers import render_status, after_workflow_dispatch
    from ..github import dispatch_workflow_button
   
    column_widths = (3, 3, 4, 3, 2) 
    cols = st.columns(column_widths)
    fields = ["Name", 'Sources', 'Latest results', 'Status', 'Run Check']
    for col, field_name in zip(cols, fields):
        col.write(field_name)

    st.session_state['currently_running'] = False

    for _, test in tests.iterrows():
        action_name=test['action_name']
        workflow = workflows[action_name]
        running = workflow['status'] in ['queued', 'in_progress']
        st.session_state['currently_running'] = st.session_state['currently_running'] or running

        name, sources, outputs, status, run = st.columns(column_widths)

        name.write(test['display_name'])

        sources.write('  \n'.join(test['sources']))
        
        folder = f'https://edm-publishing.nyc3.digitaloceanspaces.com/db-gru-qaqc/{action_name}/latest'
        files = '  \n'.join([f'[{filename}.csv]({folder}/{filename}.csv)' for filename in test['files']] + [f'[versions.csv]({folder}/versions.csv)'])
        outputs.write(files)

        with status: render_status(workflow)
        with run: 
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
    from .helpers import get_qaqc_runs, run_all_workflows

    st.header("GRU QAQC")
    st.write("This page runs automated QAQC checks for various GRU-maintained files, displays source data info and makes outputs available for download.")
    st.write("""Checks are performed either by comparing files to each other or by comparing a file to the latest Geosupport release.
        To perform a check, hit a button in the table below. The status column has a link to the latest Github workflow run for a given check""")
    st.write("Detailed instructions are in the [instructions folder](https://github.com/NYCPlanning/db-gru-qaqc/blob/update-docs/instructions/instructions.md) in GitHub.")
    
    st.header("Latest Source Data")
    

    st.header("QAQC Checks")
    workflows = get_qaqc_runs()
    running_workflows = [action_name for action_name in workflows if workflows[action_name]['status'] in ['queued', 'in_progress']]
    run_all_workflows(running_workflows)
    check_table(workflows)

    st.header("README")
    st.markdown(readme_markdown_text)

    # this state gets set when an action is triggered, set to false once it's complete
    while st.session_state['currently_running']:
        time.sleep(5)
        st.experimental_rerun()
