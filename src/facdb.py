def facdb(): 
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os 
    import pydeck as pdk

    st.title('Facilities DB QAQC')
    
    @st.cache(suppress_st_warning=True, allow_output_mutation=True)
    def get_data():
        url = 'https://edm-publishing.nyc3.digitaloceanspaces.com/db-facilities/latest/output'
        qc_diff = pd.read_csv(f'{url}/qc_diff.csv')
        facdb = pd.read_csv(f'{url}/facilities.csv')
        _facdb = pd.read_csv('https://raw.githubusercontent.com/NYCPlanning/db-facilities/84b90bfc8f6966a30f699dbdc2768934a7781484/output/facilities.csv')
        facdb['version'] = 'new'
        _facdb['version'] = 'old'
        facdb = facdb.round(5)
        _facdb = _facdb.round(5)
        combined = pd.concat([facdb, _facdb])
        combined = combined.drop_duplicates(subset=['longitude', 'latitude'])
        return qc_diff, facdb, _facdb, combined

    qc_diff, facdb, _facdb, combined = get_data()
    datasource = st.selectbox('select a datasource', qc_diff.datasource.unique())
    st.dataframe(qc_diff.loc[(qc_diff.datasource == datasource)&(qc_diff.diff != 0), :])
    
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v9',
        initial_view_state=pdk.ViewState(
            latitude=40.7128,
            longitude=-74.0006,
            zoom=11,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=combined.loc[
                        (combined.datasource == datasource)&
                        (combined.version=='new'), 
                        ['longitude', 'latitude']]\
                            .dropna(subset=['longitude', 'latitude']),
                get_position='[longitude, latitude]',
                get_color='[255, 0, 0, 160]',
                get_radius=40,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=combined.loc[
                        (combined.datasource == datasource)&
                        (combined.version=='old'), 
                        ['longitude', 'latitude']]\
                            .dropna(subset=['longitude', 'latitude']),
                get_position='[longitude, latitude]',
                get_color='[255, 255, 0, 160]',
                get_radius=40,
            )
        ],
    ))