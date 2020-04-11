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
    css = '''
        .blog-card {
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transition: 0.3s;
        width: 100%;
        height: 100%;
        margin-bottom: 30px;
        }

        .blog-card:hover {
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
        }

        .blog-card img {
            max-height: 200px;
            overflow: hidden;
            object-fit: cover;
        }

        .container {
        padding: 2px 16px;
        }
    '''
    for i in result: 
        st.markdown(f'''
        <style>
        {css}
        </style>
        <div class="blog-card">
        <img src="{i['image']}" alt="Avatar" style="width:100%;">
            <div class="container">
                <a href="{i['link']}"><h4><b>{i['title']}</b></h4></a>
                <p>{i['description']}</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)

def run():
    name = st.sidebar.selectbox('select a dataset for qaqc', list(datasets.keys()), index=0)
    app = datasets[name]
    if name == '-':
        st.sidebar.success("Select a dataset above.")
        st.markdown('''
        <h1><img style='height:10%; width:10%; float:left; vertical-align: baseline; padding: 5px;'
        src="https://raw.githubusercontent.com/NYCPlanning/logo/master/dcp_logo_772.png">
        Data Engineering</h1>
        ''', unsafe_allow_html=True)
        
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