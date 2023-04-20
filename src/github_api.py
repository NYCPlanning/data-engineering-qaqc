import os
from github import Github
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date

ORG = 'NYCPlanning'
PERSONAL_TOKEN = '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' # Your app token
headers = {'Authorization': 'Bearer %s' % PERSONAL_TOKEN}
params = {'filter': 'all', 'per_page': 100}
BASE_URL=f'https://api.github.com/repos/{ORG}'

action_types = [
    'address-points-vs-pad',
    'addresses-spatial',
    'footprints-vs-pad',
    'housing',
    'pad-vs-footprint',
    'dcm-streetname',
    'saf-vs-pad',
]

def parse_workflow(workflow):
    return {
        "status": workflow['status'],
        'conclusion': workflow['conclusion'],
        'timestamp': workflow['updated_at'],
    }

def get_workflow(repo, name): ## unnecessary since we can just use the name to get the runs
    url = f"{BASE_URL}/{repo}/actions/workflows/{name}"
    r = requests.get(url, headers=headers)
    return r.json()

def get_workflow_runs(repo, workflow_name = None): # /repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs
    #if workflow_name: 
    url = f"{BASE_URL}/{repo}/actions/workflows/{workflow_name}/runs"
    #else:
    #    url = f"{BASE_URL}/{repo}/actions/runs"
    workflows = {}
    for run in requests.get(url, headers=headers, params=params).json()['workflow_runs']:
        if len(workflows) == 7: break
        if '[' in run['display_title']: ## runs triggered by issues
            name = run['display_title'].split('[', 1)[1].split(']')[0]
        else: ## runs triggered by this app
            name = run['name']
        if name in action_types:
            if name not in workflows:
                workflows.update(name, parse_workflow(run))
    return workflows

def dispatch_workflow(repo, workflow_name, **inputs):
    params = {'ref': 'main', 'inputs': inputs}
    url = f"{BASE_URL}/{repo}/actions/workflows/{workflow_name}/dispatches"
    response = requests.post(url, headers=headers, params=params)
    if not response.json()['Status'] == '204':
        raise "aaaagh"
