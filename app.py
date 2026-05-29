import streamlit as st
import pandas as pd
from PIL import Image
from openai import OpenAI
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ABT-TRAC Marine AI",
    layout="wide"
)

# ---------------- STYLE ----------------
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

.stTextArea textarea {
    background-color: rgba(255,255,255,0.95);
    border: 2px solid #0D4F7C;
    border-radius: 12px;
    font-size: 17px;
}

.stDataFrame {
    background-color: rgba(255,255,255,0.95);
}

h1, h2, h3 {
    color: #1E2F4D;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGOS ----------------
abt_logo = Image.open("ABT TRAC Logo.jpg")
inov8v_logo = Image.open("Innov8v Marine Logo.png")

col1, col2 = st.columns([5, 1])

with col1:
    st.image(abt_logo, width=320)

with col2:
    st.image(inov8v_logo, width=120)

st.title("ABT-TRAC Marine AI Assistant")
st.write("Ask questions about boats, customers, sales orders, parts, invoices, and shipment history.")

# ---------------- DATA LOADING ----------------
@st.cache_data
def load_data():
    sales_orders = pd.read_excel("Sales Order Record.xlsx")
    line_items = pd.read_excel("Line Item for SOs.xlsx")
    invoices = pd.read_excel("INVs_AsOf_05.20.2026.xlsx")

    sales_orders["_source"] = "Sales Order Record"
    line_items["_source"] = "Line Item"
    invoices["_source"] = "Invoice / Ship Date"

    sales_orders["_search_text"] = (
        sales_orders
        .fillna("")
        .astype(str)
        .apply(lambda row: " ".join(row.values), axis=1)
        .str.lower()
    )

    line_items["_search_text"] = (
        line_items
        .fillna("")
        .astype(str)
        .apply(lambda row: " ".join(row.values), axis=1)
        .str.lower()
    )

    invoices["_search_text"] = (
        invoices
        .fillna("")
        .astype(str)
        .apply(lambda row: " ".join(row.values), axis=1)
        .str.lower()
    )

    return sales_orders, line_items, invoices


sales_orders, line_items, invoices = load_data()

# ---------------- SEARCH HELPERS ----------------
def extract_search_terms(question):
    question = str(question).lower()

    stop_words = {
        "what", "do", "we", "know", "about", "tell", "me", "show",
        "find", "for", "the", "a", "an", "of", "and", "or", "to",
        "history", "records", "record", "boat", "customer", "sales",
        "order", "so", "invoice", "part", "parts"
    }

    numbers = re.findall(r"\d+", question)

    words = re.findall(r"[a-zA-Z0-9\-]+", question)
    keywords = [
        word for word in words
        if word not in stop_words and len(word) >= 3
    ]

    terms = numbers + keywords

    seen = set()
    clean_terms = []

    for term in terms:
        if term not in seen:
            clean_terms.append(term)
            seen.add(term)

    return clean_terms


def search_df(df, question, max_rows=40):
    terms = extract_search_terms(question)

    if not terms:
        return df.head(0).drop(columns=["_search_text"], errors="ignore")

    results = pd.DataFrame()

    for term in terms:
        matches = df[
            df["_search_text"].str.contains(
                term,
                na=False,
                regex=False
            )
        ]
        results = pd.concat([results, matches])

    if len(results) == 0:
        fallback = str(question).lower().strip()
        results = df[
            df["_search_text"].str.contains(
                fallback,
                na=False,
                regex=False
            )
        ]

    results = results.drop_duplicates()

    return results.drop(
        columns=["_search_text"],
        errors="ignore"
    ).head(max_rows)


def compact_table_text(df, max_rows=20):
    if df.empty:
        return "No matching records found."

    return df.head(max_rows).to_string(index=False)


# ---------------- AI INTERFACE ----------------
st.header("Ask ABT Marine AI")

question = st.text_area(
    "Ask a question",
    placeholder="Example: What do we know about SO 31884? Or: What do we know about Odyssey?"
)

if st.button("Ask AI"):

    if not question.strip():
        st.warning("Enter a question first.")

    else:
        with st.spinner("Searching records and asking AI..."):

            extracted_terms = extract_search_terms(question)

            sales_matches = search_df(sales_orders, question, max_rows=40)
            line_matches = search_df(line_items, question, max_rows=60)
            invoice_matches = search_df(invoices, question, max_rows=40)

            context = f"""
USER QUESTION:
{question}

SEARCH TERMS USED:
{extracted_terms}

MATCHING SALES ORDER RECORDS:
{compact_table_text(sales_matches)}

MATCHING LINE ITEM RECORDS:
{compact_table_text(line_matches)}

MATCHING INVOICE / SHIP DATE RECORDS:
{compact_table_text(invoice_matches)}

IMPORTANT NOTES:
- Use only the provided records.
- The invoice spreadsheet includes sales order number and ship date / invoice date information.
- Treat invoice ship date as the closest available shipment date to the customer.
- Use sales order number to connect invoices back to sales order and line item history when possible.
- If information is missing or unclear, say so.
"""

            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are an internal ABT-TRAC / Inov8v Marine AI assistant.

Your job is to help sales and service users understand vessel, customer, part, sales order, invoice, and shipment history.

Use only the spreadsheet records provided in the prompt.
Do not invent facts.
If dates are available, organize the answer chronologically.
If a vessel appears multiple times, summarize the timeline.
If sales order, invoice, and ship date records connect, explain the relationship clearly.
Be concise, practical, and useful for a marine parts salesperson.
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

            st.caption(f"Search terms used: {', '.join(extracted_terms)}")

            st.subheader("Matching Sales Orders")
            st.dataframe(sales_matches, use_container_width=True)

            st.subheader("Matching Line Items")
            st.dataframe(line_matches, use_container_width=True)

            st.subheader("Matching Invoice / Ship Date Records")
            st.dataframe(invoice_matches, use_container_width=True)

st.markdown("---")
st.caption("AI answers are based on uploaded sales order, line item, and invoice spreadsheet records.")
