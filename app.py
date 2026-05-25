import streamlit as st
import pandas as pd
from PIL import Image

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ABT-TRAC Parts Sales AI",
    layout="wide"
)

# ---------------- LOAD LOGOS ----------------
abt_logo = Image.open("ABT TRAC Logo.jpg")
inov8v_logo = Image.open("Innov8v Marine Logo.png")

# ---------------- CUSTOM STYLING ----------------
st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background-image: linear-gradient(
        rgba(255,255,255,0.82),
        rgba(255,255,255,0.82)
    ),
    url("https://raw.githubusercontent.com/afellows8/abt-trac-parts-ai/main/Nordhavn%20N100%20Serenity.jpg");

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Main title */
h1 {
    color: #1E2F4D;
    font-size: 52px !important;
    font-weight: 800;
}

/* Section headers */
h2, h3 {
    color: #1E2F4D;
    font-weight: 700;
}

/* Search boxes */
.stTextInput input {
    background-color: rgba(255,255,255,0.92);
    border-radius: 14px;
    border: 2px solid #0D4F7C;
    padding: 14px;
    font-size: 18px;
}

/* Buttons */
.stButton button {
    background-color: #0D4F7C;
    color: white !important;
    border-radius: 12px;
    padding: 12px 24px;
    font-size: 18px;
    font-weight: bold;
    border: none;
}

/* Force button text white */
.stButton button p {
    color: white !important;
}

.stButton button span {
    color: white !important;
}

/* Hover effect */
.stButton button:hover {
    background-color: #1478B5;
    color: white !important;
}

/* Results boxes */
.stDataFrame, .stTable {
    background-color: rgba(255,255,255,0.92);
    border-radius: 10px;
    padding: 10px;
}

/* Info boxes */
[data-testid="stMarkdownContainer"] {
    color: #1E2F4D;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TOP LOGOS ----------------
col1, col2 = st.columns([5, 1])

with col1:
    st.image(abt_logo, width=320)

with col2:
    st.image(inov8v_logo, width=120)

# ---------------- TITLE ----------------
st.title("ABT-TRAC Parts Sales AI")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    sales_orders = pd.read_excel("Sales Order Record.xlsx")
    line_items = pd.read_excel("Line Item for SOs.xlsx")
    return sales_orders, line_items

sales_orders, line_items = load_data()

# ---------------- BOAT SEARCH ----------------
st.header("Boat / Customer Lookup")

boat_search = st.text_input(
    "Search by boat name, customer, ship-to, or sales order"
)

if st.button("Search Boats"):

    if boat_search:

        boat_results = sales_orders[
            sales_orders.astype(str)
            .apply(lambda row: row.str.contains(
                boat_search,
                case=False,
                na=False
            ).any(), axis=1)
        ]

        st.write(f"### Results for: {boat_search}")

        if len(boat_results) > 0:
            st.dataframe(boat_results, use_container_width=True)
        else:
            st.warning("No matching boats/customers found.")

# ---------------- PART SEARCH ----------------
st.header("Part Lookup")

part_search = st.text_input(
    "Search by part number, description, or keyword"
)

if st.button("Search Parts"):

    if part_search:

        part_results = line_items[
            line_items.astype(str)
            .apply(lambda row: row.str.contains(
                part_search,
                case=False,
                na=False
            ).any(), axis=1)
        ]

        st.write(f"### Results for: {part_search}")

        if len(part_results) > 0:
            st.dataframe(part_results, use_container_width=True)
        else:
            st.warning("No matching parts found.")

# ---------------- FOOTER ----------------
st.markdown("---")

st.markdown("""
### Current Focus

- Boat / Customer search  
- Parts lookup  
- ABT-TRAC branded interface  
- Streamlined sales support tools  
""")
