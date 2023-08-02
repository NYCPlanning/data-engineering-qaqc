import pandas as pd
import streamlit as st


def get_data():

    url = f"https://edm-publishing.nyc3.cdn.digitaloceanspaces.com/db-checkbook/2023-08-01/historical_spend.csv"
    df = pd.read_csv(url)

    return df