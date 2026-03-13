# Insight-Airbnb

## Project Description
I built this interactive web app as a university project, where it ended up receiving a maximum score.
This project is an interactive Streamlit web application designed for exploring and analyzing Airbnb listing data across multiple cities The application provides a comprehensive platform for users to gain insights into city-wide rental statistics and discover personalized listing recommendations. This project was inspired by [inside-airbnb](https://insideairbnb.com/get-the-data/).


Key features of the application include:

* **Interactive Map Visualization:** A dynamic map (using `folium` and `streamlit_folium`) displays the geographical distribution of listings, allowing users to select individual properties.
* **City-wide and Listing-specific Statistics:** The app presents aggregated statistical data for the selected city, which switches to a detailed view of an individual listing when selected on the map.
* **Multi-City Support:** The application is built to load data and switch between different cities, provided the data is available for scraping.

## Tech Stack

The application is built primarily using Python and relies on the following key libraries:

 **Web Framework:** `streamlit` 
 **Data Analysis:** `pandas`, `numpy`, `polars` 
 **Machine Learning:** `scikit_learn` (for KNN model and preprocessing) 
 **Mapping/Geospatial:** `folium`, `streamlit_folium`, `geopandas` 
 **Web Scraping:** `beautifulsoup4`, `Requests` 



## Installation and Setup
You can use this project directly at [Insight-airbnb](https://insight-airbnb-1.streamlit.app/).

To run this project locally:

### Step 1: Clone the repository

```bash
git clone https://github.com/limlim12-blip/Insight-Airbnb.git
````
#### Optional Step: Get initial data

The application requires raw data for cities like Singapore, Bangkok, and Taipei to function correctly when offline. The data is expected to be organized in the `raw/<city>/<snapshot_date>` structure.

Run the following script to download and structure the initial datasets:

```bash
python src/Get_raw.py
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the application

Start the Streamlit application from the project root directory:

```bash
streamlit run src/app/main.py
```










