from src.github import get_workflow_runs, parse_workflow
import pandas as pd
import streamlit as st
from datetime import datetime
import pytz
import time

tests = pd.DataFrame([
    ('Address Points vs PAD', 'address-points-vs-pad', ['rejects_pad_addrpts']),
    ('Adress Points (Spatial) vs GRID', 'addresses-spatial', ['geocode_diffs_address_spatial']),
    ('Footprint BINs vs PAD', 'footprints-vs-pad', ['rejects_footprintbin_padbin']),
    ('TBINs vs. C/Os', 'housing', ['tbins_certf_occp']),
    ('PAD BINs vs Footprint BINs', 'pad-vs-footprint', ['rejects_padbin_footprintbin']),
    ('DCM Names vs SND Names', 'dcm-streetname', ['rejects_sn_dcm_snd']),
    ('Generic SAF Addresses vs PAD Roadbed SAF Addresses vs PAD', 'saf-vs-pad', ['saf_gen_1A_pad', 'saf_gen_1R_pad', 'saf_gen_1_pad', 'saf_rb_1A_pad', 'saf_rb_1R_pad', 'saf_rb_1_pad'] )
], columns =['display_name', 'action_name', 'filename'])

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

def status(workflow):
    timestamp = datetime.fromisoformat(workflow['timestamp']).astimezone(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M')
    format = lambda status: f"{status} - [{timestamp}](google.com)"
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