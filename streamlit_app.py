# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title("My Parents New Healthy Diner")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit data
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to Pandas for Streamlit + lookups
pd_df = my_dataframe.to_pandas()

# Multiselect MUST use a list
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Get SEARCH_ON value
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Correct API call
        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(response.json(), use_container_width=True)

    # Insert order
    my_insert_stmt = (
        "INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
        f"VALUES ('{ingredients_string}', '{name_on_order}')"
    )

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered! ✅ {name_on_order}")
