import time
from load_data import load_listings, load_geojson
import pandas as pd
import geopandas as gpd
import folium
import branca
from folium.plugins import HeatMap, MarkerCluster, Fullscreen, FastMarkerCluster
import streamlit as st
@st.cache_resource
def load_data(city):
    # get listings.csv singapore
    start_time = time.perf_counter()
    df = load_listings(city)
    
    # get singapore bounds
    geojson_data, world_bounds = load_geojson(city)
    vignette_area = world_bounds.union_all() - geojson_data.union_all()

    # heatmap
    heatmap_data = df[["latitude", "longitude", "price"]].dropna()
    heatmap_data['price'] = heatmap_data['price'].replace({'\$': '', ',': ''}, regex=True)
    heatmap_data['price'] = pd.to_numeric(heatmap_data['price'], errors='coerce')
    price_min = heatmap_data['price'].quantile(0.02)
    price_max = heatmap_data['price'].quantile(0.98)
    if len(heatmap_data['price']) == 0:
        price_min = 0
        price_max = 100

    # colormap 
    colors = ["blue",  "cyan",  "lime",  "yellow", "red"]
    colormap = branca.colormap.LinearColormap(
    colors=colors,
    vmin=price_min,
    vmax=price_max,
    )
    colormap.caption = 'House Price'

    # markers data
    gdf = gpd.GeoDataFrame(
        df[["id", "host_id", "name", "host_name", "neighbourhood", 'room_type', "price", "number_of_reviews"]], 
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
    )
    gdf.set_crs("EPSG:4326", inplace=True)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"load map data executed in {elapsed_time:.4f} seconds.")
    return geojson_data, vignette_area, heatmap_data, colormap, gdf

#style func
def style_function(feature):
    return {'fillColor': "#00000000", 'color': "#3511FF63", 'fillOpacity': 0.3, 'opacity': 1, 'weight': 1}
def highlight_function(feature):
    return {'fillColor': '#ff0000', 'color': 'green', 'weight': 4, 'opacity': 1, 'fillOpacity': 0.1}
def vignette_style(feature):
    return {'fillColor': "#FFFFFF83", 'color': "#FF118876", 'fillOpacity': 0.6, 'opacity': 1, 'weight': 1}




def create_map(city):
    
    start_time = time.perf_counter()
    geojson_data, vignette_area, heatmap_data, colormap,gdf = load_data(city)

    minx, miny, maxx, maxy = geojson_data.total_bounds
    bounds = [[miny, minx], [maxy, maxx]]
    # setup map
    CENTER_START = [1.330270, 103.851959]
    m = folium.Map(
                    control_scale=True, 
                    zoom_start=11, 
                    min_lat=miny,
                    min_lon=minx,
                    max_lat=maxy,
                    max_lon=maxx,
                    max_bounds=bounds,
                    zoomDelta=0, 
                    zoomSnap=0.25,
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
    .leaflet-control-layers-expanded {
        width: 130px !important; 
        font-size: 0.75rem  !important;
    }
    </style>
    """
    m.get_root().header.add_child(folium.Element(css))


    # heatmap + colormap
    HeatMap(data=heatmap_data, name='House Price', blur=20, radius=25, min_opacity=0.2).add_to(m)
    colormap.add_to(m)

    # bounds 
    folium.GeoJson(
        vignette_area, style_function=vignette_style, name='Vignette Layer', control=False,overlay=False,
    ).add_to(m)
    folium.GeoJson(
        geojson_data, style_function=style_function, highlight_function=highlight_function,
        name='GeoJSON Layer', zoom_on_click=True, control=False,overlay=False,

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

    url = "https://leafletjs.com/examples/custom-icons/{}".format
    icon_image = url("leaf-red.png")
    house_type_color = {"Entire home/apt":url("leaf-red.png"), "Private room":url("leaf-red.png"), "Shared room":url("leaf-red.png") }
    shadow_image = url("leaf-shadow.png")
    folium.GeoJson(
        gdf,
        name="Listings",
        marker=folium.Marker(icon = folium.CustomIcon(
            icon_image,
            icon_size=(19, 48),       
            icon_anchor=(11, 47),     
            shadow_image=shadow_image,
            shadow_size=(25, 32),     
            shadow_anchor=(2, 31),     
            popup_anchor=(-2, -38),   
        )),
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

    
    m.fit_bounds([[miny, minx], [maxy, maxx]])

    # plugins
    folium.LayerControl(collapsed=False, position='bottomright',draggable=True).add_to(m)
    Fullscreen(
        position="topright", title="Expand me", title_cancel="Exit me", force_separate_button=True
    ).add_to(m)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"draw map executed in {elapsed_time:.4f} seconds.")
    return m