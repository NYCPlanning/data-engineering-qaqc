def ztl(): 
    import streamlit as st
    import pandas as pd
    import numpy as np
    import requests
    import os 
    import pydeck as pdk
    import json

    @st.cache(suppress_st_warning=True, allow_output_mutation=True)
    def get_data():
        source_data_versions=pd.read_csv('https://edm-publishing.nyc3.cdn.digitaloceanspaces.com/db-zoningtaxlots/latest/output/source_data_versions.csv')
        
        bbldiff=pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/qc_bbldiffs.csv', dtype=str)
        bbldiff = bbldiff.fillna('NULL')
        bbldiff['longitude'] = bbldiff.longitude.astype(float)
        bbldiff['latitude'] = bbldiff.latitude.astype(float)
        
        last_build = requests.get('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/version.txt').text
        
        qc_frequencychanges = pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/qc_frequencychanges.csv')
        
        qc_versioncomparison = pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/qc_versioncomparison.csv')
        
        qc_versioncomparisonnownullcount = pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/qc_versioncomparisonnownullcount.csv')
        
        qc_bbls_count_added_removed = pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/qc_bbls_count_added_removed.csv')
        
        return source_data_versions, bbldiff, last_build, qc_frequencychanges, qc_versioncomparison, qc_versioncomparisonnownullcount, qc_bbls_count_added_removed
    
    source_data_versions, bbldiff, last_build, qc_frequencychanges, qc_versioncomparison, qc_versioncomparisonnownullcount, qc_bbls_count_added_removed = get_data()

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
    st.table(qc_frequencychanges)

    st.header('Version Comparison')
    st.table(qc_versioncomparison)
    st.markdown('''
    Compares the value differences between this version and 
    the previous version, showing the number of records with a 
    change in value and the percentage of these fields that changed.
    ''')

    st.header('Version Comparison -- Null Count')
    st.table(qc_versioncomparisonnownullcount)
    st.markdown('''
    reports the number of records that changed 
    from null to a value or vice versa.
    ''')

    st.header('BBLs added/removed')
    st.table(qc_bbls_count_added_removed)
    st.markdown('''
    Shows how many records have non-null values for each field 
    in the old and new version. Note that changes to the number 
    of records with a value may result from changes to null 
    values or from BBL changes.
    ''')

    st.header('Source Data Versions')
    st.table(source_data_versions)