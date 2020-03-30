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

    for key, value in qc_tables.items():
        st.header(key)
        if value['type'] == 'dataframe':
            st.dataframe(value['dataframe'])
        else:
            st.table(value['dataframe'])

    