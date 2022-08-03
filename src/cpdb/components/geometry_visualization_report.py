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

def geometry_visualization_report(data: dict):

    st.header(
        f"Visualize Geometries"
    )

    st.markdown(
        f"""
        To quickly assess whether the geometries from the shapefiles are corrupted or not. 
        First the point geometries in the first figure. 
        Then the polygon geometires in the second figure. 
        """
    )

    st.pyplot(data["cpdb_dcpattributes_pts"].plot(markersize=5).figure)

    st.pyplot(data["cpdb_dcpattributes_poly"].plot().figure)
