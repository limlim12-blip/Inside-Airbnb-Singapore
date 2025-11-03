import pandas as pd
import geopandas as gpd
import folium
import branca
from folium.plugins import HeatMap, MarkerCluster, Fullscreen, FastMarkerCluster
import streamlit as st

@st.cache_resource 
def load_data():
    _df = pd.read_csv("raw/singapore/2025-09-28/visualisations/listings.csv")
    _geojson_data = gpd.read_file("raw/singapore/2025-09-28/visualisations/neighbourhoods.geojson")
    _world_bounds = gpd.read_file("world.geojson")
    vignette_area_calc = _world_bounds.union_all() - _geojson_data.union_all()
    vignette_area = gpd.GeoDataFrame(geometry=[vignette_area_calc], crs=_world_bounds.crs)
    heatmap_data = _df[["latitude", "longitude", "price"]].dropna()
    price_min = _df['price'].quantile(0.05)
    price_max = _df['price'].quantile(0.95)
    gdf = gpd.GeoDataFrame(
        _df, 
        geometry=gpd.points_from_xy(_df.longitude, _df.latitude)
    )
    gdf.set_crs("EPSG:4326", inplace=True)
    data = _df[["latitude","longitude","price","host_name"]]
    colors_ylorrd = ['#FFFFE5', '#FEB24C', '#F03B20', '#BD0026']
    heat_gradient = {0.2: '#FFFFE5', 0.5: '#FEB24C', 0.8: '#F03B20', 1.0: '#BD0026'}
    colormap = branca.colormap.LinearColormap(
    colors=colors_ylorrd,
    vmin=price_min,
    vmax=price_max
    )
    colormap.caption = 'House Price'
    return _geojson_data, vignette_area, heatmap_data, data, heat_gradient, colormap, gdf

def style_function(feature):
    return {'fillColor': '#00000000', 'color': "#00000076", 'fillOpacity': 0.3, 'opacity': 1}
def highlight_function(feature):
    return {'fillColor': '#ff0000', 'color': 'green', 'weight': 5, 'opacity': 1, 'fillOpacity': 0.2}
def vignette_style(feature):
    return {'fillColor': '#FFFFFF', 'color': '#00000076', 'fillOpacity': 0.8, 'opacity': 1}




def create_map():
    
    _geojson_data, vignette_area, heatmap_data, data, heat_gradient, colormap,gdf = load_data()

    
    CENTER_START = [1.330270, 103.851959]
    
    m = folium.Map(location=CENTER_START, control_scale=True, zoom_start=11.75, zoomDelta=0.25, zoomSnap=0.25)
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap', control=False).add_to(m)


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
        name="Airbnb Density", control=True,options={'max_cluster_radius': 100}, disableClusteringAtZoom=18
    )
    
    # for lati, longi in zip(data.latitude, data.longitude):
    #     folium.Circle(  
    #         location=[lati, longi], radius=10, fill_color="#3388FF", fill=True,
    #         fill_opacity=1, weight=1, tooltip=[lati, longi], popup="Hi, I'm a marker"
    #     ).add_to(marker_cluster)
    # marker_cluster.add_to(m)
    # callback = """
    # function (row) {
    #     var popup = row[2];  // Use the HTML string from Python
    #     return L.marker(new L.LatLng(row[0], row[1])).bindPopup(popup);
    # }
    # """
    # coords = [
    #     [row.latitude, row.longitude, f"<b>{row.host_name}</b><br>Price: ${row.price}"]
    #     for row in data.itertuples(index=False)
    # ]
    # FastMarkerCluster(coords, callback=callback).add_to(m)
    folium.GeoJson(
        gdf,
        name="Listings (Circles)",
        marker=folium.Marker(radius=2, fill_color="#3388FF", fill=True, fill_opacity=1, weight=1, popup="Hi, I'm a marker"),
        tooltip=folium.GeoJsonTooltip(fields=['name'])
    ).add_to(marker_cluster)
    marker_cluster.add_to(m)


    folium.LayerControl(collapsed=False, position='bottomright').add_to(m)
    folium.plugins.Fullscreen(
        position="topright", title="Expand me", title_cancel="Exit me", force_separate_button=True
    ).add_to(m)
    
    return m