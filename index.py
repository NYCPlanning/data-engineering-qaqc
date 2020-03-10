import streamlit as st
from src.pluto import pluto
from src.ztl import ztl
from src.facdb import facdb
from src.devdb import devdb
from src.geocode import geocode


datasets = {
    '-':None,
    'PLUTO':pluto, 
    'Zoning Tax Lots': ztl,
    'Facilities DB': facdb,
    'Developments DB': devdb,
    'Geosupport Demo': geocode
}

def run():
    name = st.sidebar.selectbox('select a dataset for qaqc', list(datasets.keys()), index=0)
    app = datasets[name]
    if name == '-':
        st.sidebar.success("Select a dataset above.")
        # st.text('welcome to the qaqc app')
        st.markdown('''
        <img style='height:15%; width:15%'
        src="https://raw.githubusercontent.com/NYCPlanning/logo/master/dcp_logo_772.png">
        ''', unsafe_allow_html=True)

        st.title('EDM Data Engineering')
        
        st.header('Data Products:')
        st.markdown(''' 
        + [PLUTO](https://github.com/NYCPlanning/db-pluto/)
        + [Zoning Tax Lots](https://github.com/NYCPlanning/db-zoningtaxlots)
        + Facilities DB (coming soon)
        + Developments DB (coming soon)
        ''', unsafe_allow_html=True)

        st.header('Read more on Medium')

        st.markdown('''
        <blockquote class="embedly-card"><h4><a href="https://medium.com/nyc-planning-digital/geosupport-%EF%B8%8Fpython-a094a2d30fbe">Geosupport❤️Python !</a></h4><p>Geocoding has been a difficult task for our data production processes because we were missing an easy, scalable and reproducible geocoding interface. Our old geocoding process relied heavily on Geoclient, an API service created by the Department of Information Technology and Telecommunications (DoITT).</p></blockquote>
        <script async src="//cdn.embedly.com/widgets/platform.js" charset="UTF-8"></script>
        <blockquote class="embedly-card"><h4><a href="https://medium.com/nyc-planning-digital/geoclient-in-excel-75e98606516b">Geoclient in Excel</a></h4><p>In order to make Geoclient API calls, you need to get your own Geoclient API id and API key, which you can get from the Geoclient developer portal. To get started, populate your spreadsheet with parsed addresses and place your API id (B1) and API key (B2) in separate reference cells.</p></blockquote>
        <script async src="//cdn.embedly.com/widgets/platform.js" charset="UTF-8"></script>
        <blockquote class="embedly-card"><h4><a href="https://medium.com/nyc-planning-digital/geosupport-%EF%B8%8F-api-987554581a09">Geosupport ➡️ API</a></h4><p>Previously we introduced how to use the python-geosupport package to geocode addresses at scale. Bringing Geosupport to Python opens up a lot of possibilities. Building on top of python-geosupport we can easily turn the package into a web service and share the power of Geosupport across the internet 🎉, so that people can access Geosupport without having to go through any installation headaches.</p></blockquote>
        <script async src="//cdn.embedly.com/widgets/platform.js" charset="UTF-8"></script>
        ''', unsafe_allow_html=True)
    else:
        app()

if __name__ == "__main__":
    run()