import pandas as pd
import geopandas as gpd
import folium
import branca
from folium.plugins import HeatMap, MarkerCluster, Fullscreen, FastMarkerCluster
import streamlit as st

@st.cache_resource 
def load_data():
    df = pd.read_csv("raw/singapore/2025-09-28/visualisations/listings.csv",dtype={"id": str},low_memory=False)
    geojson_data = gpd.read_file("raw/singapore/2025-09-28/visualisations/neighbourhoods.geojson",low_memory=False)
    world_bounds = gpd.read_file("world.geojson",low_memory=False)
    vignette_area = world_bounds.union_all() - geojson_data.union_all()
    heatmap_data = df[["latitude", "longitude", "price"]].dropna()
    price_min = df['price'].quantile(0.05)
    price_max = df['price'].quantile(0.95)
    gdf = gpd.GeoDataFrame(
        df[["id", "host_id", "name", "host_name", "neighbourhood", 'room_type', "price"]], 
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
    )
    gdf.set_crs("EPSG:4326", inplace=True)
    data = df[["latitude","longitude","price","host_name"]]
    colors = ['#f7fcf5', '#c7e9c0', '#74c476', '#238b45', '#00441b']
    heat_gradient = {0.2:'#f7fcf5',0.4: '#c7e9c0', 0.6:'#74c476', 0.8:'#238b45',1.0: '#00441b'}
    colormap = branca.colormap.LinearColormap(
    colors=colors,
    vmin=price_min,
    vmax=price_max
    )
    colormap.caption = 'House Price'
    colormap.width = 350
    colormap.top = '90%'
    colormap.left = '1%'
    return geojson_data, vignette_area, heatmap_data, data, heat_gradient, colormap, gdf

def style_function(feature):
    return {'fillColor': '#00000000', 'color': "#322E2E76", 'fillOpacity': 0.3, 'opacity': 1, 'weight': 2}
def highlight_function(feature):
    return {'fillColor': '#ff0000', 'color': 'green', 'weight': 5, 'opacity': 1, 'fillOpacity': 0.2}
def vignette_style(feature):
    return {'fillColor': '#FFFFFF', 'color': "#3B353576", 'fillOpacity': 0.8, 'opacity': 1, 'weight': 2}



def create_map():
    
    _geojson_data, vignette_area, heatmap_data, data, heat_gradient, colormap,gdf = load_data()

    
    CENTER_START = [1.330270, 103.851959]
    m = folium.Map(location=CENTER_START,
                    tiles="OpenStreetMap", 
                    control_scale=True, 
                    zoom_start=11, 
                    zoomDelta=0.25, 
                    zoomSnap=0.25,
                    # max_lat = 1.47,
                    # min_lat = 1.15,
                    # min_lon = 103.63,
                    # max_lon = 104.1,
                    zoom_control=False,
                    prefer_canvas=True
                )

    folium.GeoJson(
        vignette_area, style_function=vignette_style, name='Vignette Layer', control=False
    ).add_to(m)
    folium.GeoJson(
        _geojson_data, style_function=style_function, highlight_function=highlight_function,
        name='GeoJSON Layer', zoom_on_click=True, control=False
    ).add_to(m)
    HeatMap(data=heatmap_data, name='House Price', gradient=heat_gradient, blur=15, radius=30, min_opacity=0.2).add_to(m)
    colormap.add_to(m)
    marker_cluster = MarkerCluster(
        name="Airbnb Density", control=True,options={'max_cluster_radius': 60}, disableClusteringAtZoom=18
    )
    
    # for lati, longi in zip(data.latitude, data.longitude):
    #     folium.Circle(  
    #         location=[lati, longi], radius=10, fill_color="#3388FF", fill=True,
    #         fill_opacity=1, weight=1, tooltip=[lati, longi], popup="Hi, I'm a marker"
    #     ).add_to(marker_cluster)
    # marker_cluster.add_to(m)
    # # coords = [
    # #     [row.latitude, row.longitude, f"<b>{row.host_name}</b><br>Price: ${row.price}"]
    #     for row in data.itertuples(index=False)
    # ]
    # FastMarkerCluster(coords, callback=callback).add_to(m)
    css = """
    <style>
    .leaflet-container {
	font-size: 0.55rem  !important;
    </style>
	}
    
    """
    m.get_root().header.add_child(folium.Element(css))
    on_each_feature = folium.JsCode(
    """
    (feature, layer) => {
        layer.bindTooltip(feature.properties.name);
        layer.on("click", (event) => {
            Streamlit.setComponentValue(
                feature.properties.id,
                // Be careful, on_each_feature binds only once.
                // You need to extract the current location from
                // the event.
            );
        });

    }
"""
    )
    folium.GeoJson(
        gdf,
        name="Listings",
        marker=folium.Marker(icon=folium.Icon(icon='star')),
        tooltip=folium.GeoJsonTooltip(fields=["name","price"]),
        popup=folium.GeoJsonPopup(fields=["name"]),
        on_each_feature=on_each_feature

    ).add_to(marker_cluster)
    marker_cluster.add_to(m)


    folium.LayerControl(collapsed=True, position='bottomright').add_to(m)
    folium.plugins.Fullscreen(
        position="topright", title="Expand me", title_cancel="Exit me", force_separate_button=True
    ).add_to(m)
    
    return m