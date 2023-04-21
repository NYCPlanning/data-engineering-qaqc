from src.github import get_workflow_runs, parse_workflow, dispatch_workflow
import streamlit as st
from datetime import datetime
import pytz
import time
from .constants import tests

def get_qaqc_runs():
    workflows = {}
    for run in get_workflow_runs('db-gru-qaqc', 'main.yml'):
        if len(workflows) == 7: break
        if '[' in run['display_title']: ## runs triggered by issues
            name = run['display_title'].split('[', 1)[1].split(']')[0]
        else: ## runs triggered by this app
            name = run['name']
        if name in tests['action_name'].values:
            if name not in workflows:
                workflows[name] = parse_workflow(run)
    return workflows

def render_status(workflow):
    timestamp = datetime.fromisoformat(workflow['timestamp']).astimezone(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M')
    format = lambda status: f"{status}  \n[{timestamp}](google.com)"
    if workflow['status'] in ['queued', 'in_progress']:
        st.warning(format(workflow['status']))
        st.spinner()
    elif workflow['status'] == 'completed':
        if workflow['conclusion'] == 'success':
            st.success(format('Success'))
        elif workflow['conclusion'] == 'cancelled':
            st.info(format('Cancelled')) 
        elif workflow['conclusion'] == 'failed':
            st.error(format('Failed'))
        else:
            st.write(workflow['conclusion'])

def after_workflow_dispatch():
    st.session_state['currently_running'] = True
    time.sleep(2)
    
def run_all_workflows(actions):
    def on_click():
        for action in actions:
            dispatch_workflow('db-gru-qaqc', 'main.yml', name=action)
        after_workflow_dispatch()
    return st.button('Run all', key='all', on_click=on_click)