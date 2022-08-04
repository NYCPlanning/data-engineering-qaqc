import streamlit as st  # type: ignore
from src.constants import COLOR_SCHEME

def geometry_visualization_report(data: dict):

    st.header(
        f"Visualize Geometries"
    )

    st.caption(
        f"""
        The idea behind these maps is to guide engineers in figuring out if the shapefiles are corrupted 
        but also (in conjunction with the table) which source spatial data files might be causing the issue 
        (which historically has been an issue in the data library upload specifically with the source to destination projection). 
        If records are falling outside of NYC from a specific agency, that might indicate an issue upstream with how the data is being 
        uploaded into data library
        """
    )

    st.pyplot(data["cpdb_dcpattributes_pts"].plot(markersize=5, color=COLOR_SCHEME[0]).figure)

    st.pyplot(data["cpdb_dcpattributes_poly"].plot(color=COLOR_SCHEME[0]).figure)
