import pandas as pd
import streamlit as st
import geopandas as gpd
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
singapore_reviews_path = "raw/singapore/2025-09-28/data/reviews.csv.gz"
url = "https://insideairbnb.com/get-the-data/"
response = requests.get(url)
all_content = response.content

@st.cache_data
def scrape_data():
  soup = BeautifulSoup(all_content, 'lxml')
  all_cities_data = dict()
  cities = soup.find_all("h3")
  for city in cities:
    all_cities_data[city.get_text(strip=True)] = []
    table = city.find_next_sibling(class_=["data", "table", "table-hover", "table-striped"]).find_all("a")
    for link in table:
      all_cities_data[city.get_text(strip=True)].append(link["href"])
  return all_cities_data

@st.cache_resource 
def load_review(city):
    csv_reviews_path = scrape_data()[city][2]
    df= pd.read_csv(csv_reviews_path)
    df["comments"] = df["comments"].astype(str).str.replace("<br/>", '', regex=True)
    df_reviews = df.iloc[::-1].copy()
    return df_reviews
@st.cache_resource 
def load_listings(city):
    csv_listings_path = scrape_data()[city][3]
    df = pd.read_csv(csv_listings_path,low_memory=False, dtype= {"id":str})
    return df
@st.cache_resource 
def load_geojson(city):
    geojson_data = gpd.read_file(scrape_data()[city][6])
    world_bounds = gpd.read_file("world.geojson")
    return geojson_data, world_bounds 

