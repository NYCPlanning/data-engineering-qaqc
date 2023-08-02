import streamlit as st
import pandas as pd
from helpers import get_data


def checkbook():

    print('started load')

    data = get_data()
    agency = st.selectbox('Agency Selection: ',
            ('SCA', 'DOE', 'Parks'))

    agency_data = data[data['agency'] == agency]
    grouped_by_category = agency_data.groupby('final_category', as_index = False).sum()

    st.bar_chart(grouped_by_category, x = 'final_category', y = 'check_amount')
    return 

checkbook()