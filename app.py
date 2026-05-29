import streamlit as st
import pandas as pd
from PIL import Image
from openai import OpenAI

st.set_page_config(
    page_title="ABT-TRAC Marine AI",
    layout="wide"
)

# ---------- STYLE ----------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-image: linear-gradient(rgba(255,255,255,0.82), rgba(255,255,255,0.82)),
    url("https://raw.githubusercontent.com/afellows8/abt-trac-parts-ai/main/Nordhavn%20N100%20Serenity.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.stButton button {
    background-color: #0D4F7C !important;
    color: white !important;
    border-radius: 12px;
    padding: 12px 24px;
    border: none;
    font-weight: bold;
}

.stButton button * {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- LOGOS ----------
abt_logo = Image.open("ABT TRAC Logo.jpg")
inov8v_logo = Image.open("Innov8v Marine Logo.png")

col1, col2 = st.columns([5, 1])
with col1:
    st.image(abt_logo, width=320)
with col2:
    st.image(inov8v_logo, width=120)

st.title("ABT-TRAC Marine AI Assistant")
st.write("Ask about boats, customers, sales orders, parts, invoices, and shipment history.")

# ---------- LOAD DATA FAST ----------
@st.cache_data
def load_data():
    sales_orders = pd.read_excel("Sales Order Record.xlsx")
    line_items = pd.read_excel("Line Item for SOs.xlsx")
    invoices = pd.read_excel("INVs_AsOf_05.20.2026.xlsx")

    sales_orders["_source"] = "Sales Order Record"
    line_items["_source"] = "Line Item"
    invoices["_source"] = "Invoice / Ship Date"

    sales_orders["_search_text"] = @st.cache_data def load_data():     sales_orders = pd.read_excel("Sales Order Record.xlsx")     line_items = pd.read_excel("Line Item for SOs.xlsx")     invoices = pd.read_excel("INVs_AsOf_05.20.2026.xlsx")      sales_orders["_source"] = "Sales Order Record"     line_items["_source"] = "Line Item"     invoices["_source"] = "Invoice / Ship Date"      sales_orders["_search_text"] = sales_orders.fillna("").astype(str).apply(lambda row: " ".join(row.values), axis=1).str.lower()     line_items["_search_text"] = line_items.fillna("").astype(str).apply(lambda row: " ".join(row.values), axis=1).str.lower()     invoices["_search_text"] = invoices.fillna("").astype(str).apply(lambda row: " ".join(row.values), axis=1).str.lower()      return sales_orders, line_items, invoices.str.lower()
    line_items["_search_text"] = line_items.astype(str).agg(" ".join, axis=1).str.lower()
    invoices["_search_text"] = invoices.astype(str).agg(" ".join, axis=1).str.lower()

    return sales_orders, line_items, invoices

sales_orders, line_items, invoices = load_data()

# ---------- HELPERS ----------
def search_df(df, query, max_rows=40):
    query = query.lower().strip()
    if not query:
        return df.head(0)

    results = df[df["_search_text"].str.contains(query, na=False, regex=False)]
    return results.drop(columns=["_search_text"], errors="ignore").head(max_rows)

def compact_table_text(df, max_rows=20):
    if df.empty:
        return "No matching records found."
    return df.head(max_rows).to_string(index=False)

# ---------- AI SECTION ----------
st.header("Ask ABT Marine AI")

question = st.text_area(
    "Ask a question",
    placeholder="Example: What do we know about Odyssey? Build a timeline using sales orders, line items, and invoice ship dates."
)

if st.button("Ask AI"):

    if not question.strip():
        st.warning("Enter a question first.")

    else:
        with st.spinner("Searching records and asking AI..."):

            sales_matches = search_df(sales_orders, question, max_rows=40)
            line_matches = search_df(line_items, question, max_rows=60)
            invoice_matches = search_df(invoices, question, max_rows=40)

            context = f"""
USER QUESTION:
{question}

MATCHING SALES ORDER RECORDS:
{compact_table_text(sales_matches)}

MATCHING LINE ITEM RECORDS:
{compact_table_text(line_matches)}

MATCHING INVOICE / SHIP DATE RECORDS:
{compact_table_text(invoice_matches)}

NOTES:
- Invoice file columns include sales order number and invoice date.
- Treat invoice date as the closest available shipment date.
- Use sales order number to connect invoice records back to sales/order history when possible.
"""

            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are an internal ABT-TRAC / Inov8v Marine AI assistant.
Answer using only the provided spreadsheet records.
Focus on boats, customers, parts, sales orders, invoices, ship dates, and vessel timeline.
If records are incomplete, say what is missing.
Be concise but useful for a marine parts salesperson.
"""
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.2
            )

            answer = response.choices[0].message.content

            st.subheader("AI Answer")
            st.write(answer)

            st.subheader("Matching Sales Orders")
            st.dataframe(sales_matches, use_container_width=True)

            st.subheader("Matching Line Items")
            st.dataframe(line_matches, use_container_width=True)

            st.subheader("Matching Invoice / Ship Date Records")
            st.dataframe(invoice_matches, use_container_width=True)

st.markdown("---")
st.caption("AI answers are based on uploaded sales order, line item, and invoice spreadsheet records.")
