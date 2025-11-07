from Create_review import load_review
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
st.markdown(
    """
    <style>
    [data-baseweb="tab-panel"], * {
        opacity: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

df_reviews = load_review()
with st.spinner("Creating map..."):
    m = create_map() 

col1, col2 = st.columns([2,1])
with col1.container():
    menu_col, refresh_col = st.columns([2,0.1])
    with menu_col:
        with st.popover("Menu"):
            st.page_link("main.py", label="App")
    with refresh_col:
        st.button("⟳", on_click=clear_all_caches)
    st.write("")
    st_data = st_folium(m, use_container_width=True, height=500, returned_objects=[])

# with col2:
#     st.header("data")
#     with st.container(border=True,height=500):
#             if(not st_data["last_active_drawing"]):
#                 st.write("null")
#             elif("id" in st_data["last_active_drawing"]["properties"]):
#                 with st.spinner("Comment loading........"):
#                     have_0_review=True
#                     for i, review in df_reviews.iterrows():
#                         if(int(st_data["last_active_drawing"]["properties"]["id"])==review["listing_id"]):
#                             have_0_review = False
#                             with st.container(border=True):
#                                 name_col,date_col=st.columns([1,2])
#                                 with name_col:
#                                     st.markdown(f"**{review['reviewer_name']}**")
#                                 with date_col:
#                                     st.caption(review['date'])
#                                 st.write(review["comments"])
#                     if(have_0_review):
#                         st.write("0 cmt")
st.write(st_data)