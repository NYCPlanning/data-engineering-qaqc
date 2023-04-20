def table():
    import streamlit as st
    from .helpers import tests, get_qaqc_runs, status
    from ..github import dispatch_workflow_button
    cols = st.columns((1, 2, 1, 1, 1))
    fields = ["Name", 'Latest result', 'Source version', 'Status', 'Run']
    workflows = get_qaqc_runs()
    for col, field_name in zip(cols, fields):
        # header
        col.write(field_name)

    for _, test in tests.iterrows():
        col1, col2, col3, col4, col5 = st.columns((1, 2, 1, 1, 1))
        col1.write(test['display_name'])
        col2.write(test['filename'][0] + 'csv')
        col3.write('versions.csv')
        with col4: status(workflows[test['action_name']])   # email status
        with col5: dispatch_workflow_button('db-gru-qaqc', 'main.yml', key=test['action_name'], name=test['action_name'])


def gru():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import requests
    import os
    import json
    import plotly.graph_objects as go
    from src.constants import COLOR_SCHEME

    pd.options.display.float_format = "{:.2f}%".format

    # LINEGRAPH BY EACH BOUNDARY TYPE ========================
    st.header("GRU QAQC")
    table()
