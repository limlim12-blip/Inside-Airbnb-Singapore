from load_data import load_listings, load_geojson
import pandas as pd
import geopandas as gpd
import folium
import branca
from folium.plugins import HeatMap, MarkerCluster, Fullscreen, FastMarkerCluster
import streamlit as st
import numpy as np

if 'city' not in st.session_state:
    st.session_state['city'] = 'Singapore, Singapore, Singapore'
@st.cache_resource
def load_data():
    # get listings.csv singapore
    df = load_listings(st.session_state['city'])
    
    # get singapore bounds
    geojson_data, world_bounds = load_geojson(st.session_state['city'])
    vignette_area = world_bounds.union_all() - geojson_data.union_all()

    # heatmap
    heatmap_data = df[["latitude", "longitude", "price"]].dropna()
    price_min = heatmap_data['price'].quantile(0.05)
    price_max = heatmap_data['price'].quantile(0.95)
    if len(heatmap_data['price']) == 0:
        price_min = 0
        price_max = 100



    # markers data
    gdf = gpd.GeoDataFrame(
        df[["id", "host_id", "name", "host_name", "neighbourhood", 'room_type', "price", "number_of_reviews"]].fillna(0), 
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
    )
    gdf.set_crs("EPSG:4326", inplace=True)

    # colormap 
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
    return geojson_data, vignette_area, heatmap_data,heat_gradient, colormap, gdf

#style func
def style_function(feature):
    return {'fillColor': '#00000000', 'color': "#322E2E76", 'fillOpacity': 0.3, 'opacity': 1, 'weight': 2}
def highlight_function(feature):
    return {'fillColor': '#ff0000', 'color': 'green', 'weight': 5, 'opacity': 1, 'fillOpacity': 0.1}
def vignette_style(feature):
    return {'fillColor': '#FFFFFF', 'color': "#3B353576", 'fillOpacity': 0.8, 'opacity': 1, 'weight': 2}



def create_map():
    
    geojson_data, vignette_area, heatmap_data, heat_gradient, colormap,gdf = load_data()

    
    # setup map
    CENTER_START = [1.330270, 103.851959]
    m = folium.Map(location=CENTER_START,
                    control_scale=True, 
                    zoom_start=11, 
                    zoomDelta=0.25, 
                    zoomSnap=0.25,
                    max_bounds=True,
                    max_zoom=16,
                    zoom_control=False,
                    prefer_canvas=True
                )
    css = """
    <style>
    .leaflet-container {
	font-size: 0.55rem  !important;
	}
    .leaflet-tooltip {
        color: #222;
        border: 2px solid #ddd;
        border-radius: 10px; 
        font-size: 1.2em;
	}
    </style>
    """
    m.get_root().header.add_child(folium.Element(css))


    # heatmap + colormap
    HeatMap(data=heatmap_data, name='House Price', gradient=heat_gradient, blur=15, radius=30, min_opacity=0.2).add_to(m)
    colormap.add_to(m)

    # bounds 
    folium.GeoJson(
        vignette_area, style_function=vignette_style, name='Vignette Layer', control=False
    ).add_to(m)
    folium.GeoJson(
        geojson_data, style_function=style_function, highlight_function=highlight_function,
        name='GeoJSON Layer', zoom_on_click=True, control=False,
        on_each_feature= folium.JsCode(   
        """
            (feature, layer) => {
                layer.bindPopup("Neighbourhood: " + feature.properties.neighbourhood + "<br>" + "Group: " + feature.properties.neighbourhood_group);
            layer.on("click", (event) => {
                Streamlit.setComponentValue({
                    Neibourhood: feature.properties.neighbourhood,
                    Neibourhood_group: feature.properties.neighbourhood_group,
                    // Be careful, on_each_feature binds only once.
                    // You need to extract the current location from
                    // the event.
                });
            });
            }
        """
        )

    ).add_to(m)
    

    # markers
    marker_cluster = MarkerCluster(
        name="Airbnb Density",options={'max_cluster_radius': 65,'spiderfyOnMaxZoom': True,'removeOutsideVisibleBounds': True}, disableClusteringAtZoom=17
    )
    
    #! biết đâu cần dùng`
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

    folium.GeoJson(
        gdf,
        name="Listings",
        marker=folium.Marker(icon=folium.Icon(icon='star')),
        #! code lấy từ streamlit-folium
        on_each_feature= folium.JsCode(          
        """
            (feature, layer) => {
                label = String('Name: ' + feature.properties.name + '<br>' + 'Price: ' + feature.properties.price + '<br>' + 'Number  of reviews: ' + feature.properties.number_of_reviews)
                layer.bindTooltip(label,{
                    direction: 'top', 
                    permanent: false, 
                    opacity: 1,
                    offset: [0,-20] 
                });
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

    ).add_to(marker_cluster)
    marker_cluster.add_to(m)


    # plugins
    folium.LayerControl(collapsed=True, position='bottomright').add_to(m)
    Fullscreen(
        position="topright", title="Expand me", title_cancel="Exit me", force_separate_button=True
    ).add_to(m)
    minx, miny, maxx, maxy = geojson_data.total_bounds
    m.fit_bounds([[miny, minx], [maxy, maxx]])
    
    return m