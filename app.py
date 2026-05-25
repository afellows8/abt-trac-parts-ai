import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(
    page_title="ABT-TRAC Parts Sales AI",
    layout="wide"
)

hero_image = "Nordhavn N100 Serenity.jpg"

st.markdown(
       """
    <style>

    .stApp {
        background: linear-gradient(
            rgba(5, 20, 35, 0.55),
            rgba(5, 20, 35, 0.55)
        ),
        url("https://raw.githubusercontent.com/afellows8/abt-trac-parts-ai/main/Nordhavn%20N100%20Serenity.jpg");

        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    .block-container {
        background-color: rgba(255,255,255,0.82);
        padding: 2rem;
        border-radius: 20px;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #0B3D5C;
        font-weight: 700;
    }

    p, label {
        color: #1A1A1A;
        font-weight: 500;
    }

    div[data-baseweb="input"] {
        background-color: rgba(255,255,255,0.96);
        border-radius: 14px;
        border: 2px solid #0B3D5C;
        padding: 6px;
    }

    input {
        color: #000000 !important;
        font-size: 18px !important;
    }

    .stButton button {
        background-color: #0B3D5C;
        color: white;
        border-radius: 14px;
        font-weight: bold;
        border: none;
        padding: 12px 24px;
        transition: 0.3s;
    }

    .stButton button:hover {
        background-color: #145A86;
        color: white;
    }

    hr {
        border-top: 1px solid rgba(255,255,255,0.3);
    }

    </style>
    """,
    unsafe_allow_html=True
)

abt_logo = Image.open("ABT TRAC Logo.jpg")
innov8v_logo = Image.open("Innov8v Marine Logo.png")

st.image("Nordhavn N100 Serenity.jpg", use_container_width=True)

col1, col2 = st.columns([6,1])

with col1:
    st.image(abt_logo, width=350)

with col2:
    st.image(innov8v_logo, width=120)

st.title("ABT-TRAC Parts Sales AI")

st.markdown("### Boat / Customer Lookup")

@st.cache_data
def load_data():
    sales_orders = pd.read_excel("Sales Order Record.xlsx")
    line_items = pd.read_excel("Line Item for SOs.xlsx")
    return sales_orders, line_items

sales_orders, line_items = load_data()

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

        if len(boat_results) > 0:

            st.success(f"Found {len(boat_results)} matching records")

            st.dataframe(
                boat_results,
                use_container_width=True
            )

        else:
            st.warning("No matching boats/customers found")

st.markdown("---")

st.markdown("### Part Lookup")

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

        if len(part_results) > 0:

            st.success(f"Found {len(part_results)} matching parts")

            st.dataframe(
                part_results,
                use_container_width=True
            )

        else:
            st.warning("No matching parts found")

st.markdown("---")

st.markdown(
    "### Current Focus\n"
    "- Boat / Customer search\n"
    "- Parts lookup\n"
    "- ABT-TRAC branded interface\n"
    "- Fast internal sales support"
)
