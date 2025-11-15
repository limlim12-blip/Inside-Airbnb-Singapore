import time
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import geopandas as gpd
from bs4 import BeautifulSoup
import requests
import pandas as pd
import polars as pl
url = "https://insideairbnb.com/get-the-data/"




@st.cache_data
def scrape_data():
	response = requests.get(url, timeout=20)
	all_content = response.content
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
	start_time = time.perf_counter()
	try:
		csv_reviews_path = scrape_data()[city][2]
	except Exception as e:
		st.error("error connection, wifi problem not code problem")
		if city == "Bangkok, Central Thailand, Thailand":
			csv_reviews_path = "raw/bangkok/2025-06-24/data/reviews.csv.gz"
		elif city == "Taipei, Northern Taiwan, Taiwan":
			csv_reviews_path = "raw/taipei/2025-06-29/data/reviews.csv.gz"
		else:
			csv_reviews_path = "raw/singapore/2025-09-28/data/reviews.csv.gz"
	pf= pl.scan_csv(
		csv_reviews_path,
	)
	pf = pf.with_columns(
		pl.col("comments").str.replace_all("<br/>", "\n"),
	)
	pf=pf.reverse()
	df = pf.collect().to_pandas()
	end_time = time.perf_counter()
	elapsed_time = end_time - start_time
	print(f"reviews executed in {elapsed_time:.4f} seconds.")
	return df
@st.cache_resource 
def load_listings(city):
	start_time = time.perf_counter()
	try:
		csv_listings_path = scrape_data()[city][0]
	except Exception as e:
		st.error("error connection, wifi problem not code problem")
		if city == "Bangkok, Central Thailand, Thailand":
			csv_listings_path = "raw/bangkok/2025-06-24/data/listings.csv.gz"
		elif city == "Taipei, Northern Taiwan, Taiwan":
			csv_listings_path = "raw/taipei/2025-06-29/data/listings.csv.gz"
		else:
			csv_listings_path = "raw/singapore/2025-09-28/data/listings.csv.gz"
	pf = pl.scan_csv(csv_listings_path, schema_overrides={"id": pl.String})
	df = pf.collect().to_pandas()
	end_time = time.perf_counter()
	elapsed_time = end_time - start_time
	print(f"listings executed in {elapsed_time:.4f} seconds.")
	return df



@st.cache_resource 
def load_geojson(city):
	start_time = time.perf_counter()
	try:
		geojson_data = gpd.read_file(scrape_data()[city][6])
		world_bounds = gpd.read_file("world.geojson")
	except Exception as e:
		st.error("error connection, wifi problem not code problem")
		world_bounds = gpd.read_file("world.geojson")
		st.error("error connection, wifi problem not code problem")
		if city == "Bangkok, Central Thailand, Thailand":
			geojson_data = "raw/bangkok/2025-06-24/visualisations/neibourhoods.geojson"
		elif city == "Taipei, Northern Taiwan, Taiwan":
			geojson_data = "raw/taipei/2025-06-29/visualisations/neibourhoods.geojson"
		else:
			geojson_data = "raw/singapore/2025-09-28/visualisations/neibourhoods.geojson"
	end_time = time.perf_counter()
	elapsed_time = end_time - start_time
	print(f"geojson executed in {elapsed_time:.4f} seconds.")
	return geojson_data, world_bounds 


def load_fig(listings):
	#fig1
	counts = list(listings['room_type'].value_counts())[::-1]
	room_type = listings['room_type'].unique()[::-1]
	bar_colors = ['red', 'green', 'blue', 'purple']
	fig1, ax1 = plt.subplots(figsize=(3, 4.5))
	fig1.patch.set_facecolor('#f5f5f5')
	ax1.set_facecolor("#f5f5f5")
	ax1.barh(room_type,counts,height=0.6,color=bar_colors)
	ax1.tick_params(axis='y', labelleft=False)
	ax1.set_xlabel("listings",fontdict={'family': 'serif', 'color': 'darkblue', 'size': 18}, labelpad=10)
	for i, room in enumerate(room_type):
		ax1.text(50, 
				i+0.5,            
				room,      
				ha='left',     
				va='center',   
				fontsize=17,
				fontweight= 400)
	plt.xticks(fontsize=12)
	ax1.spines['top'].set_visible(False)
	ax1.spines['right'].set_visible(False)
	#fig2

	# % of room_type
	room_type_counts = listings['room_type'].value_counts()
	room_type_counts=room_type_counts.rename(index={"Entire home/apt":"Entire homes/Apartments",})
  
  
  
	# top host table
	table_listings = listings[["host_name","room_type","host_total_listings_count"]]
	table_listings= pd.get_dummies(table_listings,columns=["room_type"], prefix='', prefix_sep='')
	table_listings = table_listings.groupby("host_name")
	top_host_table = table_listings.sum()
	top_host_table['host_total_listings_count'] = table_listings.count()['host_total_listings_count']
	top_host_table = top_host_table.sort_values(by='host_total_listings_count', ascending=False).head(100)
	top_host_table.rename(columns={"host_total_listings_count":"total_listings"},inplace=True)
	top_host_table.reset_index(inplace=True,col_level=0)
	# top_host_table = top_host_table.iloc[:, :0:-1]
	cols = top_host_table.columns.to_list()
	top_host_table = top_host_table[[cols[0]] + cols[1:][::-1]]

	return fig1, room_type_counts, top_host_table





