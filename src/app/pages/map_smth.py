from load_data import load_review, load_listings, scrape_data
from Create_map import create_map, load_data
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
import numpy as np


def clear_data():
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state['city'] = 'Singapore, Singapore, Singapore'
def change_city_button(city):
    st.session_state['city'] = city
    st.cache_data.clear()
    st.cache_resource.clear()
    load_data.clear()
    load_review.clear()
    load_listings.clear()
def neibourhood_display_data():
    with st.spinner("Comment loading........"):
        st.write("print some data about the neibor")
def listings_display_data(df_reviews,df_listings):
    with st.spinner("Comment loading........"):
        col1, col2 = st.columns([2,1])
        with col1.container(border=True):
            name = df_listings.loc[df_listings["id"] == st_data,'name']
            st.write(f"**{name.iloc[0]}**")
        with col2.container(border=True):
            st.metric(label="Total Reviews", value= df_listings.loc[df_listings["id"] == st_data, "number_of_reviews"].iloc[0])
            pass
        reviews = df_reviews[df_reviews["listing_id"] == int(st_data)]
        if reviews.empty:
            st.write("This listing has no comments.")
        else:
            for _, review in reviews.iterrows():
                with st.container(border=True):
                    name_col, date_col = st.columns([1, 2])
                    with name_col:
                        st.markdown(f"**{review['reviewer_name']}**")
                    with date_col:
                        st.caption(review['date'])
                    st.write(review["comments"])


# init page
st.set_page_config(
    layout="wide",
    page_icon="🌏",
    initial_sidebar_state="collapsed",
)

# hide header bar
hide_streamlit_style = """
    <style>
    header {
        visibility: hidden;
    }
    </style>
    """
# disable loading animation
st.markdown(
    """
    <style>
    [data-baseweb="tab-panel"], * {
        opacity: 100% !important;
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    }
    </style>
    """,
    unsafe_allow_html=True
)



if 'city' not in st.session_state:
    clear_data()


st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.header(f"THIS IS {st.session_state['city']}", divider= "rainbow")

# load data
df_reviews = load_review(st.session_state['city'])
df_listings = load_listings(st.session_state['city'])
df_scrape = scrape_data()


with st.spinner("Creating map..."):
    m = create_map() 

col1, col2 = st.columns([2.5,1])
# render map
with col1.container():
    menu_col, cities_col = st.columns([1,0.32])
    with menu_col:
        with st.popover("Menu"):
            st.page_link("main.py", label="App")
    with cities_col:
        cola,colb = st.columns([1,2])
        with cola:
            st.button("🔃",on_click=clear_data)

        with colb:
            with st.popover("ALL KIND OF CITIES"):
                for city in df_scrape.keys():
                    st.button(city,on_click=change_city_button,args=[city])
    st.write("")
    st_data = st_folium(m,key="map", use_container_width=True, height=500, returned_objects=[])

# stat screen
with col2:
    with st.container(border=True,height=560):
            if(not st_data):
                st.write("null")
            elif isinstance(st_data, dict) :
                neibourhood_display_data()
            else:
                listings_display_data(df_reviews=df_reviews,df_listings=df_listings)
st.write(st_data)