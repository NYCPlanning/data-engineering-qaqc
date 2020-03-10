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
        bbldiff=pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/qc_bbldiffs.csv')
        last_build = requests.get('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/version.txt').text
        qc_frequencychanges = pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/qc_frequencychanges.csv')
        qc_versioncomparison = pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/qc_versioncomparison.csv')
        qc_versioncomparisonnownullcount = pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/qc_versioncomparisonnownullcount.csv')
        qc_bbls_count_added_removed = pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/qc_bbls_count_added_removed.csv')
        DATA_URL='https://edm-publishing.nyc3.digitaloceanspaces.com/db-zoningtaxlots/latest/output/qc_bbldiffs.geojson'
        geojson = requests.get(DATA_URL).json()
        return source_data_versions, bbldiff, last_build, qc_frequencychanges, qc_versioncomparison, qc_versioncomparisonnownullcount, qc_bbls_count_added_removed, geojson
    
    source_data_versions, bbldiff, last_build, qc_frequencychanges, qc_versioncomparison, qc_versioncomparisonnownullcount, qc_bbls_count_added_removed, geojson = get_data()

    st.title('Zoning Tax Lots QAQC')
    st.markdown(f'![CI](https://github.com/NYCPlanning/db-zoningtaxlots/workflows/CI/badge.svg) last build: {last_build}')

    column = st.sidebar.selectbox('select column:', ['all', 'zd1', 'zd2', 'zd3', 'zd4','co1', 'co2', 'sd1', 'sd2', 'sd3','lhd'])
    st.text('BBLs with Zoning Changes')
    if column == 'all':
        df = bbldiff.rename(columns={'bblnew':'bbl'})
    else: 
        df=bbldiff.loc[bbldiff[f'{column}new'] != bbldiff[f'{column}prev'], ['bblnew', f'{column}new', f'{column}prev']]
        df=df.dropna(subset=[f'{column}new', f'{column}prev'])
        df.columns = ['bbl', f'{column}new', f'{column}prev']
    st.dataframe(df)

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=40.7128,
            longitude=-74.0006,
            zoom=11,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'GeoJsonLayer',
                data=geojson,
                opacity=0.8,
                pickable=True,
                wireframe=True,
                stroked=False,
                filled=True,
                auto_highlight=True,
                get_line_color=[255, 255, 255]
            )
        ],
        # tooltip={
        #     "html": '''
        #      <div><b>BBL &nbsp;</b></div>
        #     <div><div>${object.properties.area}</div></div>
        #     <div><b>Growth</b></div>
        #     <div>${properties}%</div>
        #     ''',
        #     "style": {
        #             "backgroundColor": "steelblue",
        #             "color": "white"
        #     }
        # }
    ))

    # bbl = st.selectbox('view a bbl on zola:', df.bbl.to_list())
    # st.markdown(f'[click to view {bbl} on zola](https://zola.planning.nyc.gov/bbl/{bbl})')
    # st.markdown(
    #     f"""
    #     <iframe src="https://zola.planning.nyc.gov/bbl/{bbl}" style='height:600px; width:100%'>
    #     </iframe>
    #     """, 
    #     unsafe_allow_html=True)

    st.header('Source Data Versions')
    st.table(source_data_versions)

    st.header('Frequency Changes')
    st.table(qc_frequencychanges)

    st.header('Version Comparison')
    st.table(qc_versioncomparison)

    st.header('Version Comparison -- Null Count')
    st.table(qc_versioncomparisonnownullcount)

    st.header('BBLs added/removed')
    st.table(qc_bbls_count_added_removed)