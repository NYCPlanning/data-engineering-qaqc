import streamlit as st  # type: ignore
import pandas as pd
import geopandas as gpd
from src.cpdb.helpers import (
    get_data,
    get_commit_cols,
    get_diff_dataframe,
    get_map_percent_diff,
    sort_base_on_option,
    VIZKEY,
)
import plotly.express as px
import plotly.graph_objects as go
from src.constants import COLOR_SCHEME

def geometry_visualization_report(geometries: gpd.GeoDataFrame):

    st.header(
        f"Visualize Geometries"
    )

    st.markdown(
        f"""
        Is there any differences in the adminstrative boundary values in previous vs. latest version? 
        The intended result is that the list is empty and all the admin boundaries are still present in the new output.
        Otherwise it might indicate that some of spatial join with admin boundaries have failed. 
        """
    )

    print(geometries.type)  

    #fig = geometries.plot()

    st.pyplot(geometries.plot().figure)
