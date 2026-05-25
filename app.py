
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="ABT-TRAC Parts Sales AI",
    page_icon="⚓",
    layout="wide"
)

abt_logo = Image.open("Assets/ABT TRAC Logo.jpg")
inov8v_logo = Image.open("Assets/Innov8v Marine Logo.png")

st.markdown("""
<style>
.stApp {
    background-color: #f7f9fb;
}

h1, h2, h3 {
    color: #062B45;
}

section[data-testid="stSidebar"] {
    background-color: #062B45;
}

section[data-testid="stSidebar"] * {
    color: white;
}

.stButton > button {
    background-color: #0077B6;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 0.5rem 1rem;
}

.stButton > button:hover {
    background-color: #00B4D8;
    color: white;
}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])

with col1:
    st.image(abt_logo, width=350)
    st.markdown("## Parts & Boat Lookup Dashboard")
    st.caption("Search parts, sales orders, and vessel/customer history")

with col2:
    st.image(inov8v_logo, width=120)

st.divider()

# BOAT LOOKUP FIRST

st.subheader("Boat / Customer Lookup")

boat_search = st.text_input(
    "Search by boat name, customer, ship-to, or sales order"
)

if st.button("Search Boats"):
    st.info(f"Searching boats/customers for: {boat_search}")

st.divider()

# PART LOOKUP SECOND

st.subheader("Part Lookup")

part_search = st.text_input(
    "Search by part number, description, or keyword"
)

if st.button("Search Parts"):
    st.info(f"Searching parts for: {part_search}")

st.divider()

st.subheader("Current Focus")

st.write(
    "This version is focused on boat/customer lookup and parts lookup."
)
