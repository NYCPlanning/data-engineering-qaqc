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
        qc_classification = pd.read_csv(f'{url}/qc_classification.csv')
        qc_mapped = pd.read_csv(f'{url}/qc_mapped.csv')
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
        return qc_tables, qc_diff, qc_mapped

    qc_tables, qc_diff, qc_mapped = get_data()

    def count_comparison(df, width=1000, height=1000): 
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
    
    def geom_comparison(df, width=1000, height=600):
        df['pctwogeom_old'] = df['wogeom_old']/df['count_old']*100
        df['pctwogeom_new'] = df['wogeom_new']/df['count_new']*100
        df['diff'] = df['pctwogeom_new'] - df['pctwogeom_old']
        df = df.loc[df['diff']!= 0, :]
        df = df.sort_values('diff')
        fig = go.Figure()
        for i in ['pctwogeom_old', 'pctwogeom_new', 'diff']:
            fig.add_trace(
                go.Bar(
                    y=df.index,
                    x=df[i].round(2),
                    name=i,
                    orientation='h'))
        fig.update_layout(
            width=width,
            height=height,
            xaxis=dict(title='Percentage'), 
            template='plotly_white'
        )
        st.plotly_chart(fig)

    """
    qc_diff visualization
    """
    thresh=st.sidebar.slider('difference threshold', min_value=0, max_value=300, value=5, step=1)
    level=st.sidebar.selectbox('select a classification level', 
                            ['datasource', 'factype', 'facsubgrp', 'facgroup', 'facdomain'], index=0)
    st.sidebar.success('''
        Use the slide bar and drop down to change the difference 
        threshold and select the attribute to review
        ''')
    dff = qc_diff.groupby(level).sum()
    st.header(f'Change in number of records by {level}')
    st.write(f'diff > {thresh}')
    count_comparison(dff.loc[dff['diff'].abs() > thresh, :].sort_values('diff'))

    st.header(f'Change in percentage mapped records by {level}')
    st.write('''
        Only instances where there is change in the percent 
        of mapped records and 100% of records are not mapped are reported
    ''')
    dfff = qc_mapped.groupby(level).sum()
    geom_comparison(dfff)


    st.header('Changes in important factypes')
    st.write('There should be little to no change in the number of records with these facility types')
    important_factype = ['FIREHOUSE', 
                        'POLICE STATION',
                        'ACADEMIC LIBRARIES',
                        'SPECIAL LIBRARIES',
                        'EMERGENCY MEDICAL STATION', 
                        'HOSPITAL',
                        'NURSING HOME', 
                        'ADULT DAY CARE', 
                        'SENIOR CENTER']
    important=qc_diff.loc[qc_diff.factype.isin(important_factype), :].groupby('factype').sum()
    count_comparison(important.sort_values('diff'), width=500, height=500)


    def plotly_table(df):
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(df.columns),
                        line_color='darkslategray',
                        fill_color='gray',
                        font=dict(color='white', size=12),
                        align='left'),
            cells=dict(values=[df[i] for i in df.columns],
                    line_color='darkslategray',
                    fill_color='white',
                    align='left'))
        ])
        fig.update_layout(width=1000, height=600)
        st.plotly_chart(fig)

    st.header('New factypes')
    st.write('Facility types that do not appear in the previous FacDB')
    plotly_table(qc_diff.loc[qc_diff['count_old']==0, :])
    st.header('Old factypes (retired)')
    st.write('Facility types that do appear in the previous FacDB, but not in the latest version')
    plotly_table(qc_diff.loc[qc_diff['count_new']==0, :])
    st.header('Full Panel Cross Version Comparison')
    st.write('Reports the difference in the number of records at the most micro level, which is the facility type and data source')
    plotly_table(qc_diff)
    
    for key, value in qc_tables.items():
        st.header(key)
        if value['type'] == 'dataframe':
            plotly_table(value['dataframe'])
        else:
            st.table(value['dataframe'])

    