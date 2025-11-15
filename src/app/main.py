
import numpy as np
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
from datetime import datetime
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
from folium import plugins
from folium.plugins import MarkerCluster, HeatMap
import branca
import streamlit as st
from streamlit_folium import st_folium

#get date + set map

# st.write("heelowojf")

st.set_page_config(
    layout="wide",
    page_icon="🌏",
    initial_sidebar_state="collapsed",
)
hide_streamlit_style = """
    <style>
    header {
        visibility: hidden;
    }
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
with st.popover("Menu"):
    st.page_link("pages/map_smth.py", label="Map")
st.header("Singapore", divider=True)
CENTER_START = [1.330270, 103.851959]
m = folium.Map(
)
a = [[np.float64(1.158699), np.float64(103.605436)], [np.float64(1.470775), np.float64(104.088483)]]
m.fit_bounds(a)

folium.Marker([40.7128, -74.0060], popup="New York City").add_to(m)

st_folium(m, width="strech", height=500) 

# ! jupyter nbconvert --to script Untitled0.ipynb

# d1 = pd.read_csv("https://data.insideairbnb.com/taiwan/northern-taiwan/taipei/2025-06-29/data/listings.csv")
# d2 = pd.read_csv("https://data.insideairbnb.com/taiwan/northern-taiwan/taipei/2025-06-29/data/calendar.csv")
# d3 = pd.read_csv("https://data.insideairbnb.com/taiwan/northern-taiwan/taipei/2025-06-29/data/reviews.csv")
# d4 = pd.read_csv("https://data.insideairbnb.com/taiwan/northern-taiwan/taipei/2025-06-29/visualisations/listings.csv")
# d5 = pd.read_csv("https://data.insideairbnb.com/taiwan/northern-taiwan/taipei/2025-06-29/visualisations/reviews.csv")
# d6 = pd.read_csv("https://data.insideairbnb.com/taiwan/northern-taiwan/taipei/2025-06-29/visualisations/neighbourhoods.csv")
# gdf = gpd.read_file("https://data.insideairbnb.com/taiwan/northern-taiwan/taipei/2025-06-29/visualisations/neighbourhoods.geojson")
# data = d4[["latitude","longitude","price"]]
# data

# d4 = pd.read_csv("https://data.insideairbnb.com/taiwan/northern-taiwan/taipei/2025-06-29/visualisations/listings.csv")
# d5 = pd.read_csv("https://data.insideairbnb.com/taiwan/northern-taiwan/taipei/2025-06-29/data/listings.csv")
# d5.head()

# d4.head()