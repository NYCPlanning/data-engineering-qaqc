import streamlit as st  # type: ignore
import pandas as pd
from src.cpdb.helpers import get_data
import plotly.express as px

def cpdb():
    st.title("Capital Projects DB QAQC")
    branch = st.sidebar.selectbox(
        "select a branch",
        ['main']
    )
    data = get_data(branch)

    st.header('Managing Agency Summary Stats')
    
    st.dataframe(data['magency'])

    # getting the 
    st.subheader('Top Ten Managing Agencies By Project Count or Commitment')
    sorter = st.selectbox('Sort Agencies Based On',
    options=('Total Projects', 'Total Commitment Amount'), index=0)
    if sorter == 'Total Projects':
        st.plotly_chart(
            px.bar(data['magency'].sort_values(by='totalcount', ascending=False).head(10), 
                x='magencyacro', 
                y=['totalcount', 'mapped'],
                barmode='group'
            )
        )
    else: 
        st.plotly_chart(
            px.bar(data['magency'].sort_values(by='totalcommit', ascending=False).head(10), 
                x='magencyacro', 
                y=['totalcommit', 'mappedcommit'],
                barmode='group'
            )
        )

    

    st.header("Sponsoring Agency Summary Stats")
    st.dataframe(data['sagency'])