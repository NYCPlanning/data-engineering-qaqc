def devdb(): 
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os 

    st.title('Developments DB QAQC')

    @st.cache(suppress_st_warning=True, allow_output_mutation=True)
    def get_data():
        u = 'https://raw.githubusercontent.com/NYCPlanning/db-developments/future/developments_build/output/'
        qc_jobtypestats = pd.read_csv(f'{u}qc_jobtypestats.csv', dtype=str)
        qc_countsstats = pd.read_csv(f'{u}qc_countsstats.csv', dtype=str)
        qc_units_complete_stats = pd.read_csv(f'{u}qc_units_complete_stats.csv', dtype=str)
        qc_geocodedstats = pd.read_csv(f'{u}qc_geocodedstats.csv', dtype=str)
        return qc_jobtypestats, qc_countsstats, qc_units_complete_stats, qc_geocodedstats
    
    qc_jobtypestats, qc_countsstats, qc_units_complete_stats, qc_geocodedstats = get_data()
    
    st.write(qc_jobtypestats)
    st.write(qc_countsstats)
    st.write(qc_units_complete_stats)
    st.write(qc_geocodedstats)
    