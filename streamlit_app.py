# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title("My Parents New Healthy Diner")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options
sp_df = session.table("smoothies.public.fruit_options") \
               .select(col("FRUIT_NAME"), col("SEARCH_ON"))

pd_df = sp_df.to_pandas()

# Multiselect must use a LIST
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

ingredients_string = ""

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.json(response.json())

    # Insert order
    if st.button("Submit Order"):
        session.sql(
            """
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES (%s, %s)
            """,
            params=[ingredients_string.strip(), name_on_order]
        ).collect()

        st.success(f"Your Smoothie is ordered! ✅ {name_on_order}")
