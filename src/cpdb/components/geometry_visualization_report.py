import streamlit as st  # type: ignore
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

    st.pyplot(data["cpdb_dcpattributes_pts"].plot(markersize=5, color=COLOR_SCHEME[0]).figure)

    st.pyplot(data["cpdb_dcpattributes_poly"].plot(color=COLOR_SCHEME[0]).figure)
