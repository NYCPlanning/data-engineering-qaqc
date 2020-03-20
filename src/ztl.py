def ztl(): 
    import streamlit as st
    import pandas as pd
    import numpy as np
    import requests
    import os 
    import json
    import plotly.graph_objects as go

    @st.cache(suppress_st_warning=True, allow_output_mutation=True)
    def get_data():
        url='https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/'
        source_data_versions=pd.read_csv(f'{url}source_data_versions.csv', index_col=False)
        
        qaqc_frequency = pd.read_csv(f'{url}qaqc_frequency.csv', index_col=False)
        qaqc_bbl = pd.read_csv(f'{url}qaqc_bbl.csv', index_col=False)

        bbldiff=pd.read_csv(f'{url}qc_bbldiffs.csv', dtype=str, index_col=False)
        bbldiff = bbldiff.fillna('NULL')
        bbldiff['longitude'] = bbldiff.longitude.astype(float)
        bbldiff['latitude'] = bbldiff.latitude.astype(float)
        
        last_build = requests.get(f'{url}version.txt').text
        
        qc_frequencychanges = pd.read_csv(f'{url}qc_frequencychanges.csv', index_col=False)
        qc_frequencychanges['percent'] = qc_frequencychanges['countnew']/qc_frequencychanges['countold'] -1
        qc_frequencychanges['percent'] = qc_frequencychanges['percent'].round(4)

        qc_versioncomparison = pd.read_csv(f'{url}qc_versioncomparison.csv', index_col=False)
        qc_versioncomparisonnownullcount = pd.read_csv(f'{url}qc_versioncomparisonnownullcount.csv', index_col=False)
        qc_versioncomparisonnownullcount['percent'] = qc_versioncomparisonnownullcount['newnullcount']/qc_versioncomparisonnownullcount['oldnullcount']-1
        
        return source_data_versions, bbldiff, last_build, \
                qc_frequencychanges, qc_versioncomparison, \
                qc_versioncomparisonnownullcount, qaqc_frequency, qaqc_bbl
    
    source_data_versions, bbldiff, last_build, \
    qc_frequencychanges, qc_versioncomparison, \
    qc_versioncomparisonnownullcount, \
    qaqc_frequency, qaqc_bbl= get_data()

    st.title('Zoning Tax Lots QAQC')
    st.markdown(f'![CI](https://github.com/NYCPlanning/db-zoningtaxlots/workflows/CI/badge.svg) last build: {last_build}')

    column = st.sidebar.selectbox('select column:', ['all', 'zd1', 'zd2', 'zd3', 'zd4','co1', 'co2', 'sd1', 'sd2', 'sd3','lhd'])
    st.header('qc_bbldiffs')
    if column == 'all':
        df = bbldiff.rename(columns={'bblnew':'bbl'})
    else: 
        df=bbldiff.loc[bbldiff[f'{column}new'] != bbldiff[f'{column}prev'], ['bblnew', f'{column}new', f'{column}prev']]
        df=df.dropna(subset=[f'{column}new', f'{column}prev'])
        df.columns = ['bbl', f'{column}new', f'{column}prev']
    st.dataframe(df)
    st.markdown('''
    Contains the old and new values for BBLs with changes from the last version.
    + Layer qc_bbldiffs, the new zoning shapefiles, and the current Digital tax map onto a map. 
    + Sort qc_bbldiffs by BBL
    + Verify that the zoning changes for each BBL meet one of the following criteria:
        + Recent zoning change
        + Adjustment to boundary
        + Change in tax lot 
    + Verify all lots in newly rezoned areas have new values
    ''')

    st.header('Frequency Changes')
    st.dataframe(qc_frequencychanges)

    co = ['commercialoverlay1', 'commercialoverlay2']
    zd = ['zoningdistrict1', 'zoningdistrict2', 'zoningdistrict3','zoningdistrict4']
    sp = ['specialdistrict1', 'specialdistrict2', 'specialdistrict3']
    other = ['zoningmapcode', 'zoningmapnumber', 'limitedheightdistrict']
    def create_plot(df, group):
        fig = go.Figure()
        for i in group:
            fig.add_trace(go.Scatter(
                            x=df['version'],
                            y=df[i]-df[i].mean(),
                            mode='lines',
                            name=i,
                            text=df[i]))
        fig.add_shape(
                type='line', 
                x0=0, 
                x1=df.shape[0], 
                y1=0, 
                y0=0,
                line=dict(
                    color="MediumPurple",
                    width=1,
                    dash="dot"
        ))
        fig.update_layout(template='plotly_white')
        st.plotly_chart(fig)

    st.header('Commercial Overlay')
    create_plot(qaqc_frequency, co)
    st.header('Zoning Districts')
    create_plot(qaqc_frequency, zd)
    st.header('Special Districts')
    create_plot(qaqc_frequency, sp)
    st.header('Other')
    create_plot(qaqc_frequency, other)


    st.header('Version Comparison')
    st.dataframe(qc_versioncomparison)
    st.markdown('''
    Compares the value differences between this version and 
    the previous version, showing the number of records with a 
    change in value and the percentage of these fields that changed.
    ''')

    st.header('Version Comparison -- Null Count')
    st.dataframe(qc_versioncomparisonnownullcount)
    st.markdown('''
    reports the number of records that changed 
    from null to a value or vice versa.
    ''')

    st.header('BBLs added/removed')
    create_plot(qaqc_bbl, ['added', 'removed'])

    st.markdown('''
    Shows how many records have non-null values for each field 
    in the old and new version. Note that changes to the number 
    of records with a value may result from changes to null 
    values or from BBL changes.
    ''')

    st.header('Source Data Versions')
    st.table(source_data_versions.sort_values(by=['schema_name'], ascending=True))