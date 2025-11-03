from Create_map import create_map
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
from streamlit_option_menu import option_menu
import streamlit as st
from streamlit_folium import st_folium
def clear_all_caches():
    st.cache_data.clear()
    st.cache_resource.clear()

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
menu_col, refresh_col = st.columns([1.5,1])
with menu_col:
    with st.popover("Menu"):
        st.page_link("main.py", label="App")
with refresh_col:
    st.button("⟳", on_click=clear_all_caches)

with st.spinner("Creating map..."):
    m = create_map() 

col1, col2 = st.columns([1.5,1])
with col1.container():
    with st.spinner("Drawing map..."):
        st_data = st_folium(m, use_container_width=True, height=900)

with col2:
    st.write(st_data)