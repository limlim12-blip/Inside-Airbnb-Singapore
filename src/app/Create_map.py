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
    df['price'] = df['price'].round(2).astype('string')
    df.fillna({'price': 'unknown'}, inplace=True)
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
    return {'fillColor': "#FFFFFFFF", 'color': "#3511FF63", 'fillOpacity': 0.7, 'opacity': 1, 'weight': 1}


def create_map(city):
    start_time = time.perf_counter()
    geojson_data, vignette_area, heatmap_data, colormap,gdf = load_data(city)

    minx, miny, maxx, maxy = geojson_data.total_bounds
    bounds = [[miny-0.1, minx-0.1], [maxy+0.1, maxx+0.1]]
    # setup map
    m = folium.Map(
                    tiles="Cartodb Positron",
                    min_lat=miny-0.1,
                    min_lon=minx-0.1,
                    max_lat=maxy+0.1,
                    max_lon=maxx+0.1,
                    max_bounds=bounds,
                    zoomDelta=0, 
                    zoomSnap=0.25,
                    max_zoom=16,
                    zoom_control=False,
                    prefer_canvas=True,
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
        font-size: 0.7rem  !important;
    }
    .custom-tooltip {
        max-width: 300px !important;
        min-width: 150px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        background-color: white !important;
        border: 2px solid #ccc !important;
        padding: 8px !important;
        font-size: 13px !important;
    }
    </style>
    """
    m.get_root().header.add_child(folium.Element(css))

    marker = folium.FeatureGroup(name="marker")
    heatmap = folium.FeatureGroup(name="heatmap")
    bounds = folium.FeatureGroup(name="bounds")
    # heatmap + colormap
    HeatMap(data=heatmap_data, name='House Price', blur=23, radius=30, min_opacity=0.2).add_to(heatmap)
    colormap.add_to(m)

    # bounds 
    folium.GeoJson(
        vignette_area, style_function=vignette_style, name='Vignette Layer', control=False,overlay=False,
        on_each_feature= folium.JsCode(   
            """
                (feature, layer) => {
                    layer.on("click", (event) => {
                        Streamlit.setComponentValue(null);
                    });
                }
            """
        )
    ).add_to(bounds)
    folium.GeoJson(
        geojson_data, style_function=style_function, highlight_function=highlight_function,
        name='GeoJSON Layer', zoom_on_click=True, control=False,overlay=False,

        on_each_feature= folium.JsCode(   
        """
            (feature, layer) => {
                var label = '<b style="color: #2196F3;">Neighbourhood: </b>' + feature.properties.neighbourhood; 
                    layer.bindPopup(label);
                layer.on("click", (event) => {
                    Streamlit.setComponentValue({
                        Neighbourhood: feature.properties.neighbourhood,
                        // Be careful, on_each_feature binds only once.
                        // You need to extract the current location from
                        // the event.
                    });
                 });
            }
            
        """
        )

    ).add_to(bounds)
    

    # markers
    marker_cluster = MarkerCluster(
        name="Airbnb Density",options={'max_cluster_radius': 60,'spiderfyOnMaxZoom': True,'removeOutsideVisibleBounds': True}, disableClusteringAtZoom=17
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
                var label = `🏡 <b style="color: #2196F3;">${feature.properties.name}</b> by\
                                <b style="color: #2196F3;">${feature.properties.host_name}</b>\
                                <br>Price: $${feature.properties.price} <br>\
                                Number of reviews: ${feature.properties.number_of_reviews}`;
                layer.bindTooltip(label,{
                    direction: 'top', 
                    permanent: false, 
                    opacity: 1,
                    offset: [0,-20],
                    className: 'custom-tooltip',
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
    marker_cluster.add_to(marker)

    
    m.fit_bounds([[miny, minx], [maxy, maxx]])

    # plugins
    folium.LayerControl(collapsed=False, position='bottomright',draggable=True).add_to(m)
    Fullscreen(
        position="topright", title="Expand me", title_cancel="Exit me", force_separate_button=True
    ).add_to(m)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"create map executed in {elapsed_time:.4f} seconds.")
    fg = [heatmap, bounds, marker]
    return m, fg