import streamlit as st
from src.pluto.pluto import pluto
from src.ztl import ztl
from src.facdb.facdb import facdb
from src.devdb import devdb
from src.geocode import geocode
from src.home import home
import requests
import datetime

datasets = {
    "Home": home,
    "PLUTO": pluto,
    "Zoning Tax Lots": ztl,
    "Facilities DB": facdb,
    "Developments DB": devdb,
    "Geosupport Demo": geocode,
}


def run():
    st.set_page_config(page_title="Data Engineering QAQC", page_icon="📊")
    st.sidebar.markdown(
        """
        <div stule="margin-left: auto; margin-right: auto;">
        <img style='width:40%; margin: 0 auto 2rem auto;display:block;'
            src="https://raw.githubusercontent.com/NYCPlanning/logo/master/dcp_logo_772.png">
        </div>
        """,
        unsafe_allow_html=True,
    )

    datasets_list = list(datasets.keys())
    query_params = st.experimental_get_query_params()
    if query_params:
        name = st.sidebar.selectbox(
            "select a dataset for qaqc",
            datasets_list,
            index=datasets_list.index(query_params["page"][0]),
        )
    else:
        name = "Home"

    if name:
        st.experimental_set_query_params(page=datasets_list[datasets_list.index(name)])

    app = datasets[name]
    app()


if __name__ == "__main__":
    run()
