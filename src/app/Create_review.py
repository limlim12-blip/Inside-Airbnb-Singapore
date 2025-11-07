import pandas as pd
import streamlit as st

csv_reviews_path = "raw/singapore/2025-09-28/data/reviews.csv.gz"
def load_review():
    df= pd.read_csv(csv_reviews_path,low_memory=False)
    for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.replace("<br/>", '', regex=True)
    df_reviews = df[::-1].reset_index(drop=True)
    return df_reviews
