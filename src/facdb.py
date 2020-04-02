def facdb(): 
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os 
    import pydeck as pdk
    import plotly.graph_objects as go

    st.title('Facilities DB QAQC')
    
    @st.cache(suppress_st_warning=True, allow_output_mutation=True)
    def get_data():
        url = 'https://edm-publishing.nyc3.digitaloceanspaces.com/db-facilities/latest/output'
        qc_diff = pd.read_csv(f'{url}/qc_diff.csv')
        qc_captype = pd.read_csv(f'{url}/qc_captype.csv')
        qc_capvalues = pd.read_csv(f'{url}/qc_capvalues.csv')
        qc_classification = pd.read_csv(f'{url}/qc_classification.csv')
        qc_mapped_datasource = pd.read_csv(f'{url}/qc_mapped_datasource.csv')
        qc_mapped_subgroup = pd.read_csv(f'{url}/qc_mapped_subgroup.csv')
        qc_operator = pd.read_csv(f'{url}/qc_operator.csv')
        qc_oversight = pd.read_csv(f'{url}/qc_oversight.csv')
        qc_proptype = pd.read_csv(f'{url}/qc_proptype.csv')

        def color_negative_red(val):
            """
            Takes a scalar and returns a string with
            the css property `'color: red'` for negative
            strings, black otherwise.
            """
            color = 'red' if val < 0 else 'black'
            return 'color: %s' % color
            
        qc_tables = {
                'Full Panel Cross Version Comparison':{
                    'dataframe': qc_diff,
                    'type': 'dataframe'
                }, 
                'Counts by Classification' : {
                    'dataframe': qc_classification,
                    'type': 'dataframe'
                }, 
                'Percentage Mapped by datasource' : {
                    'dataframe': qc_mapped_datasource,
                    'type': 'dataframe'
                }, 
                'Percentage Mapped by subgroup' : {
                    'dataframe': qc_mapped_subgroup,
                    'type': 'dataframe'
                }, 
                'Operator Counts' : {
                    'dataframe': qc_operator,
                    'type': 'dataframe'
                }, 
                'Oversight Counts' : {
                    'dataframe': qc_oversight,
                    'type': 'dataframe'
                }, 
                'Property Types' : {
                    'dataframe': qc_proptype,
                    'type': 'table'
                }, 
                'Capacity Types' : {
                    'dataframe': qc_captype,
                    'type': 'table'
                }, 
            }
        return qc_tables

    qc_tables = get_data()

    def count_comparison(df, width=1000, height=600): 
        fig = go.Figure()
        for i in ['count_old', 'count_new', 'diff']:
            fig.add_trace(
                go.Bar(
                    y=df.index,
                    x=df[i],
                    name=i,
                    orientation='h'))
        fig.update_layout(
            width=width,
            height=height,
            template='plotly_white'
        )
        st.plotly_chart(fig)

    """
    qc_diff visualization
    """
    qc_diff=qc_tables['Full Panel Cross Version Comparison']['dataframe']
    thresh=st.slider('difference threshold', min_value=0, max_value=300, value=5, step=1)
    qc_diff_factype=qc_diff.groupby('factype').sum()
    qc_diff_facsubgrp=qc_diff.groupby('facsubgrp').sum()
    qc_diff_facgroup=qc_diff.groupby('facgroup').sum()
    qc_diff_facdomain=qc_diff.groupby('facdomain').sum()
    st.header('Change in Number of Records by factype')
    st.write(f'diff > {thresh}')
    count_comparison(qc_diff_factype.loc[qc_diff_factype['diff'].abs() > thresh, :].sort_values('diff'), height=1000)
    
    st.header('Change in Number of Records by facsubgrp')
    st.write(f'diff > {thresh}')
    count_comparison(qc_diff_facsubgrp.loc[qc_diff_facsubgrp['diff'].abs() > thresh, :].sort_values('diff'))
    
    st.header('Change in Number of Records by facgroup')
    st.write(f'diff > {thresh}')
    count_comparison(qc_diff_facgroup.loc[qc_diff_facgroup['diff'].abs() > thresh, :].sort_values('diff'))
    
    st.header('Change in Number of Records by facdomain')
    st.write(f'diff > {thresh}')
    count_comparison(qc_diff_facdomain.loc[qc_diff_facdomain['diff'].abs() > thresh, :].sort_values('diff'))

    st.header('Changes in important factypes')
    sensitive_factype = ['FIREHOUSE', 'POLICE STATION']
    st.write(' ,'.join(sensitive_factype))
    count_comparison(qc_diff_factype.loc[qc_diff_factype.index.isin(sensitive_factype), :].sort_values('diff'))


    st.header('New factypes')
    st.dataframe(qc_diff.loc[qc_diff['count_old'].isna(), :])
    st.header('Old factypes (retired)')
    st.dataframe(qc_diff.loc[qc_diff['count_new'].isna(), :])

    for key, value in qc_tables.items():
        st.header(key)
        if value['type'] == 'dataframe':
            st.dataframe(value['dataframe'])
        else:
            st.table(value['dataframe'])

    