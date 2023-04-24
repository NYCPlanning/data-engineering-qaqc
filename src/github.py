import os
import requests
import streamlit as st

ORG = 'NYCPlanning'
PERSONAL_TOKEN = os.environ['GHP_TOKEN']
headers = {'Authorization': 'Bearer %s' % PERSONAL_TOKEN}
BASE_URL=f'https://api.github.com/repos/{ORG}'

def parse_workflow(workflow):
    return {
        "status": workflow['status'],
        'conclusion': workflow['conclusion'],
        'timestamp': workflow['updated_at'],
        'url': workflow['html_url']
    }

def get_workflow(repo, name): 
    url = f"{BASE_URL}/{repo}/actions/workflows/{name}"
    r = requests.get(url, headers=headers)
    return r.json()

def __get_workflow_runs_helper(url, params=None):
    response = requests.get(url, headers=headers, params=params).json()
    if 'workflow_runs' in response:
        return response['workflow_runs']
    else:
        raise Exception(f'Error retreiving workflow runs from Github. If error persists, contact Data Engineering. Github API response: {response}')

def get_workflow_runs(repo, workflow_name = None, items_per_page = None, total_items = None):
    if workflow_name: 
        url = f"{BASE_URL}/{repo}/actions/workflows/{workflow_name}/runs"
    else:
        url = f"{BASE_URL}/{repo}/actions/runs"
    if items_per_page is None and total_items is None:
        return __get_workflow_runs_helper(url)
    elif items_per_page is None:
        return __get_workflow_runs_helper(url, params={'per_page': items_per_page})
    else:
        workflows = []
        page = 0
        res = []
        while (total_items is None and (page == 0 or len(res) != 0)) or (total_items is not None and len(workflows) < total_items):
            page += 1
            res = __get_workflow_runs_helper(url, params={'items_per_page': items_per_page, 'page': page})
            workflows = workflows.append(res)
            if total_items is not None and len(workflows) < total_items: 
                workflows = workflows[:total_items]
        return workflows

def dispatch_workflow(repo, workflow_name, **inputs):
    params = {'ref': 'fvk-2023-Q2-maintenance', 'inputs': inputs}
    url = f"{BASE_URL}/{repo}/actions/workflows/{workflow_name}/dispatches"
    response = requests.post(url, headers=headers, json=params)
    if response.status_code != 204:
        raise Exception(f'Dispatch workflow failed with status code {response.status_code}')

def dispatch_workflow_button(repo, workflow_name, key, label='Run', disabled=False, run_after=None, **inputs):
    def on_click():
        dispatch_workflow(repo, workflow_name, **inputs)
        if run_after is not None: run_after()
    return st.button(label, key=key, on_click=on_click, disabled=disabled)