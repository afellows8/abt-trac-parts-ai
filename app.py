import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(
    page_title="ABT-TRAC Parts Sales AI",
    page_icon="⚓",
    layout="wide"
)

# LOGOS
abt_logo = Image.open("ABT TRAC Logo.jpg")
inov8v_logo = Image.open("Innov8v Marine Logo.png")

# LOAD DATA
@st.cache_data
def load_data():
    sales_orders = pd.read_excel("Sales Order Record.xlsx")
    line_items = pd.read_excel("Line Item for SOs.xlsx")
    return sales_orders, line_items

sales_orders, line_items = load_data()

# HEADER
col1, col2 = st.columns([6,1])

with col1:
    st.image(abt_logo, width=250)

with col2:
    st.image(inov8v_logo, width=120)

st.title("Parts & Boat Lookup Dashboard")

st.markdown("---")

# BOAT LOOKUP
st.header("Boat / Customer Lookup")

boat_search = st.text_input(
    "Search by boat name, customer, ship-to, or sales order"
)

if st.button("Search Boats"):

    search_term = boat_search.lower()

    matches = sales_orders[
        sales_orders.astype(str)
        .apply(lambda col: col.str.lower().str.contains(search_term, na=False))
        .any(axis=1)
    ]

    st.write(f"Found {len(matches)} matching records")

    st.dataframe(matches)

st.markdown("---")

# PART LOOKUP
st.header("Part Lookup")

part_search = st.text_input(
    "Search by part number or description"
)

if st.button("Search Parts"):

    search_term = part_search.lower()

    matches = line_items[
        line_items.astype(str)
        .apply(lambda col: col.str.lower().str.contains(search_term, na=False))
        .any(axis=1)
    ]

    st.write(f"Found {len(matches)} matching records")

    st.dataframe(matches)
