from load_data import load_review, load_listings, scrape_data
from Create_map import create_map, load_data
from display_stat import city_display_data, listings_display_data, neibourhood_display_data
import streamlit as st
from streamlit_folium import st_folium


def draw_map(m):
    st_data = st_folium(m, use_container_width=True,height=672, returned_objects=[])   
    return st_data

def clear_data():
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state['city'] = 'Singapore, Singapore, Singapore'


def change_city_button(city):
    load_data.clear()
    load_review.clear()
    load_listings.clear()
    st.session_state['city'] = city

# init page
st.set_page_config(
    layout="wide",
    page_icon="🌏",
    initial_sidebar_state="collapsed",
)

# hide header bar
# disable loading animation
st.markdown(
    """
    <style>
    [data-testid='stHeaderActionElements'] { display: none; }
    [data-baseweb="tab-panel"], * {
        opacity: 100% !important;
    }
    [data-testid="stHorizontalBlock"] {
            gap: 0;
    }
    [data-testid="stVerticalBlock"] {
            gap: 0; 
            padding: 0;
            border-radius: 0px;
            padding: 0;
            margin-bottom: 0px;
        }
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    .st-key-1 {
        gap: 0; 
        background-color: #e6e6e6;
        border-radius: 0px;
        padding: 0px;
        text-align: center;
    }
    [class*="set-key-comment_"]{
        gap: 1; 
        padding: 1;
        border-radius: 0px;
    }
    .st-key-stat_container {
        background-color: 	#f5f5f5;
        border-radius: 0px;
        padding: 0px;
    }
    div[data-testid="stVerticalBlock"]:has(div.review-marker):not(:has(div.parent)) {
            gap: 10 !important; 
            padding: 100 !important;
            border-radius: 20px !important;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            margin-left: 10px;
            background-color: white;
    }
    .st-emotion-cache-tn0cau {
        display: flex
    ;
        gap: 0rem;
        width: 100%;
        max-width: 100%;
        height: auto;
        min-width: 1rem;
        flex-flow: column;
        flex: 1 1 0%;
        -webkit-box-align: stretch;
        align-items: stretch;
        -webkit-box-pack: start;
    }
    p{
        font-family: Arial, Helvetica Neue, Helvetica, sans-serif;
        font-size: 12.4em;
        line-height: 1.3
    }
    header {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if 'city' not in st.session_state:
    clear_data()



# load data
df_reviews = load_review(st.session_state['city'])
df_listings = load_listings(st.session_state['city'])
try:
    df_scrape = scrape_data()
except Exception:
    df_scrape = {"no_data":"no_data"}


#place holder
header = st.container()
body = st.container()


#implement
with header:
    h1,h2,_ = st.columns([2.5,1,1.75])
    with h1:
        st.title(f":rainbow[THIS IS {st.session_state['city']}]")
    with h2:
        menu_col, cities_col = st.columns([1,2.5])
        with menu_col:
            st.space(20)
            with st.popover("Menu"):
                st.page_link("main.py", label="App")
        with cities_col:
            st.space(20)
            cola,colb = st.columns([1,3])
            with cola:
                st.button("🔃",on_click=clear_data)
            with colb:
                with st.popover("ALL KIND OF CITIES"):
                    for city in df_scrape.keys():
                        st.button(city,on_click=change_city_button,args=[city])



with body:
    with st.spinner("Creating map..."):
        m = create_map(st.session_state['city']) 

    col1, col2 = st.columns([2.15,1])
    # render map
    with col1.container(height=680):
        st_data=draw_map(m)
    # stat screen
    with col2:
        with st.container(border=True,height=680,key="stat_container"):
                st.markdown('<div class="parent"/>', unsafe_allow_html=True)
                if(not st_data):
                    city_display_data(df_listings)
                elif isinstance(st_data, dict) :
                    neibourhood_display_data()
                else:
                    listings_display_data(df_reviews=df_reviews,df_listings=df_listings,data=st_data)
# st.write(st_data)