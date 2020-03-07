def ztl(): 
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os 

    st.title('Zoning Tax Lots QAQC')
    st.markdown('![CI](https://github.com/NYCPlanning/db-zoningtaxlots/workflows/CI/badge.svg)')
    
    @st.cache(suppress_st_warning=True, allow_output_mutation=True)
    def get_data():
        source_data_versions=pd.read_csv('https://edm-publishing.nyc3.cdn.digitaloceanspaces.com/db-zoningtaxlots/latest/output/source_data_versions.csv')
        bbldiff=pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/qc_bbldiffs.csv')
        return [source_data_versions, bbldiff]
    
    data = get_data()
    source_data_versions = data[0]
    bbldiff = data[1]

    column = st.sidebar.selectbox('select column:', ['all', 'zd1', 'zd2', 'zd3', 'zd4','co1', 'co2', 'sd1', 'sd2', 'sd3','lhd'])
    st.text('BBLs with Zoning Changes')
    if column == 'all':
        df = bbldiff.rename(columns={'bblnew':'bbl'})
    else: 
        df=bbldiff.loc[bbldiff[f'{column}new'] != bbldiff[f'{column}prev'], ['bblnew', f'{column}new', f'{column}prev']]
        df=df.dropna(subset=[f'{column}new', f'{column}prev'])
        df.columns = ['bbl', f'{column}new', f'{column}prev']
    st.dataframe(df)
    bbl = st.selectbox('view a bbl on zola:', df.bbl.to_list())
    st.markdown(f'[click to view {bbl} on zola](https://zola.planning.nyc.gov/bbl/{bbl})')
    st.markdown(
        f"""
        <iframe src="https://zola.planning.nyc.gov/bbl/{bbl}" style='height:600px; width:100%'>
        </iframe>
        """, 
        unsafe_allow_html=True)

    st.text('Source Data Versions')
    st.table(source_data_versions)

