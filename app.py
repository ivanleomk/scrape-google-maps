import streamlit as st
import pandas as pd
from pydantic import BaseModel
from typing import List

df = pd.read_csv("./locations.csv")

category_set = set()
parsed_categories = [
    [j.strip() for j in i[1:-1].replace("'", "").split(",")]
    for i in df["categories"].to_list()
]
for cat_list in parsed_categories:
    for cat in cat_list:
        category_set.add(cat)


st.title("Location Filter")

# Filter by title
title_filter = st.sidebar.text_input("Search by title")
filtered_df = df[df["title"].str.contains(title_filter, case=False)]

# Filter by categories
unique_categories = list(category_set)
selected_categories = st.sidebar.multiselect("Filter by categories", unique_categories)
filtered_df = filtered_df[
    filtered_df["categories"].apply(
        lambda x: any(category in x for category in selected_categories)
        or len(selected_categories) == 0
    )
]


# Filter by number of reviews
min_reviews, max_reviews = st.sidebar.slider(
    "Filter by number of reviews",
    int(df["number_of_reviews"].min()),
    int(df["number_of_reviews"].max()),
    (0, int(df["number_of_reviews"].max())),
)
filtered_df = filtered_df[
    (filtered_df["number_of_reviews"] >= min_reviews)
    & (filtered_df["number_of_reviews"] <= max_reviews)
]


# view_df = filtered_df[["title", "number_of_reviews", "categories"]]
# Display the filtered DataFrame
st.write(filtered_df[["title", "number_of_reviews", "rating", "user_review"]])
