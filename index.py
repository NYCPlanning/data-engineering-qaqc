import streamlit as st
from src.pluto import pluto
from src.ztl import ztl
from src.facdb import facdb
from src.devdb import devdb
from src.geocode import geocode
import requests
import datetime

datasets = {
    '-':None,
    'PLUTO':pluto, 
    'Zoning Tax Lots': ztl,
    'Facilities DB': facdb,
    'Developments DB': devdb,
    'Geosupport Demo': geocode
}

def get_blogs(): 
    r = requests.get('https://labs-home-api.herokuapp.com/posts?tag=data')
    result = r.json()['items']
    for i in result: 
        # st.image(i['image'], width=100)
        st.markdown(f'''
        ### [__{i['title']}__]({i['url']})
        {datetime.datetime.fromtimestamp(i['created']/1000).strftime("%B %d, %Y")}
        >{i['description']}
        ''', unsafe_allow_html=True)

def run():
    name = st.sidebar.selectbox('select a dataset for qaqc', list(datasets.keys()), index=2)
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
        get_blogs()
    else:
        app()

if __name__ == "__main__":
    run()