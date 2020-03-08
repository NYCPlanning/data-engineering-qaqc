def facdb(): 
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os 
    import pydeck as pdk

    st.title('Facilities DB QAQC')
    
    @st.cache(suppress_st_warning=True, allow_output_mutation=True)
    def get_data():
        # geo_rejects = pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-facilities/latest/output/geo_rejects.csv')
        # qc_diff = pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-facilities/latest/output/qc_diff.csv')
        facdb = pd.read_csv('https://edm-publishing.nyc3.digitaloceanspaces.com/db-facilities/latest/output/facilities.csv')
        # facdb_old = pd.read_csv('https://www1.nyc.gov/assets/planning/download/zip/data-maps/open-data/facilities_csv_201901.zip')       
        # return geo_rejects, qc_diff, facdb, facdb_old
        # URL = 'https://raw.githubusercontent.com/ajduberstein/data_sets/master/beijing_subway_station.csv'
        # df = pd.read_csv(URL)
        # df = pd.DataFrame(
        #     np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
        #     columns=['lat', 'lon'])
        return facdb

    # geo_rejects, qc_diff, facdb, facdb_old = get_data()
    facdb = get_data()
    # st.write(facdb.head())
    # scatterplot = Layer(
    #     'ScatterplotLayer',
    #     df,
    #     id='scatterplot-layer',
    #     get_radius=50,
    #     # get_fill_color='color',
    #     get_position='[lng, lat]')

    # r = Deck(layers=[scatterplot])
    # st.pydeck_chart(r)
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=40.7128,
            longitude=-74.0006,
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'HexagonLayer',
                data=facdb[['longitude', 'latitude']]\
                    .dropna(subset=['longitude', 'latitude']),
                get_position='[longitude, latitude]',
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=facdb[['longitude', 'latitude']]\
                    .dropna(subset=['longitude', 'latitude']),
                get_position='[longitude, latitude]',
                get_color='[200, 30, 0, 160]',
                get_radius=20,
            ),
        ],
    ))