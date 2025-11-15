from load_data import load_fig
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
def city_display_data(listings):
    fig,room_type_counts,top_host_table = load_fig(listings=listings)
    with st.container(border=True,key='1', horizontal_alignment="left",height=100):
        col1, col2 = st.columns([1,1])
        with col1:
            citi = st.session_state['city'].split(',')
            st.title(f":rainbow[{citi[0]}]")
        with col2:
            number = f"{len(listings):,} listings "
            st.title(f":rainbow[{number}]")
    st.space()
    with st.container(height=570,border=False):
        _,aligncenter,_=st.columns([1.5,17,1])
        with aligncenter:
            st.header("**Room Type**",divider="rainbow")
            st.space("small")
            c1, c2, c3 = st.columns([155.2,120,130],gap= None)
            with c1:
                st.space("small")
                st.write("Airbnb hosts can list entire homes/apartments, private, shared rooms, and more recently hotel rooms. \n\n Depending on the room type and activity, a residential airbnb listing could be more like a hotel, disruptive for neighbours, taking away housing, and illegal.")
            with c2:
                st.space("small")
                st.pyplot(fig)
            with c3:
                st.space("small")
                with stylable_container(
                        key=f"dynamic_button_1",
                        css_styles=["""
                        h1{
                            text-align: right;
                            font-family: Lato, sans-serif;
                            font-size: 25px;
                            font-weight: 800;
                            line-height: 1em;
                            padding-bottom: 5;
                            padding-top: 2;
                            float: right;
                            margin-top: 3px;
                            text-align: right;
                            width: 130px;
                        }
                        """,
                        """
                        p{
                            font-family: Arial, Helvetica Neue, Helvetica, sans-serif;
                            text-align: right;
                            font-size: .8em;
                            line-height: 1.3
                        }
                        """]
                    ):
                        st.title(f"{round(room_type_counts.iloc[0]/len(listings)*100,1)}%")
                        st.space("small")
                        st.write(f"{room_type_counts.index[0]}")
                        st.space("small")

                for type, counts in room_type_counts.items():
                    with stylable_container(
                        key=f"dynamic_button_{type}",
                        css_styles=["""
                        h2{
                            text-align: right;
                            font-family: Lato, sans-serif;
                            font-size: 15.5px;
                            font-weight: 800;
                            line-height: 1em;
                            padding-bottom: 5;
                            padding-top: 2;
                            float: right;
                            margin-top: 3px;
                            text-align: right;
                            width: 130px;
                        }
                        """,
                        """
                        p{
                            text-align: right;
                            padding-right: 0em;
                            font-size: 10.25px;
                        }
                        """]
                    ):
                        st.header(f"**{counts} ({round(counts/len(listings)*100,1)}%)**")
                        st.space("small")
                        st.write(f"{str(type)}")
                        st.space("small")
            st.header("Activity",divider="rainbow")
            c1,c2 = st.columns([1.7,1],gap="large")
            with c1:
                st.space("small")
                st.write("""The minimum stay, price and number of  
                            reviews have been used to estimate the 
                            number of **nights booked** and the **income** for  
                            each listing, for the last 12 months. """)
                st.space("small")
                st.write("""
                            Is the home, apartment or room rented
                            frequently and displacing units of housing and 
                            residents?  Does the income from Airbnb 
                            incentivise short-term rentals vs long-term housing?""")
            with c2:
                pass
            st.header("Short-Term Rentals",divider="rainbow")
            c1,c2 = st.columns([1.7,1],gap="large")
            with c1: 
                st.space("small")
                st.write("""Some Airbnb hosts have multiple listings.""")

                st.space("small")
                st.write("""A host may list separate rooms in the same
                            apartment, or multiple apartments or homes
                            available in their entirity.""")
        
                st.space("small")
                st.write("""Hosts with multiple listings are more likely to
                            be running a business, are unlikely to be living
                            in the property, and in violation of most short 
                            term rental laws designed to protect
                            residential housing.""")
                st.space("small")
            st.header("Listings per Host",divider="rainbow")
            c1,c2 = st.columns([1.7,1],gap="large")
            with c1: 
                st.space("small")
                st.write("""Some Airbnb hosts have multiple listings.""")

                st.space("small")
                st.write("""A host may list separate rooms in the same 
                            apartment, or multiple apartments or homes
                            available in their entirity.""")
        
                st.space("small")
                st.write("""Hosts with multiple listings are more likely to be running a business, are unlikely to be living in the property, and in violation of most short term rental laws designed to protect residential housing.  """)
                st.space("small")
            st.header("Top Hosts",divider="rainbow")
            def col_pretty(col):
                if col.name == 'total_listings' or col.name == "host_name":
                    return ["font-weight: bold"] * len(col)
                return [''] * len(col)
            def row_pretty(row):
                if (int(row.name) % 2) :
                    return ['background-color: lightgray; color: black'] * len(row)
                else:
                    return ['background-color: white; color: black'] * len(row)

            st.write(top_host_table.style\
                                    .apply(col_pretty, axis=0).hide(axis="index")\
                                    .apply(row_pretty, axis=1).to_html(), unsafe_allow_html=True)






def neibourhood_display_data():
    with st.spinner("Comment loading........"):
        st.write("print some data about the neibor")





def listings_display_data(df_reviews,df_listings,data):
    with st.spinner("Comment loading........"):
        col1, col2 = st.columns([2,1])
        with col1.container(border=True):
            name = df_listings.loc[df_listings["id"] == data,'name']
            st.write(f"**{name.iloc[0]}**")
        with col2.container(border=True):
            if(df_listings.loc[df_listings["id"] == data, "number_of_reviews"] is not None):
                st.metric(label="Total Reviews", value=df_listings.loc[df_listings["id"] == data, "number_of_reviews"].iloc[0])
            else:
                st.metric(label="Total Reviews", value=0)

        reviews = df_reviews[df_reviews["listing_id"] == int(data)]
        if reviews.empty:
            st.write("This listing has no comments.")
        else:
            for _, review in reviews.iterrows():
                with st.container(border=True, width= 440):
                    st.markdown(f":rainbow[**{review['reviewer_name']}**]")
                    st.caption(f":red[{review['date']}]")
                    st.write(review["comments"])
                    st.markdown('<div class="review-marker"/>', unsafe_allow_html=True)
