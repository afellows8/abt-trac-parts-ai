import streamlit as st
import pandas as pd
from PIL import Image
from openai import OpenAI
import re
from datetime import datetime

st.set_page_config(page_title="ABT-TRAC Marine AI", layout="wide")

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
.stButton button * { color: white !important; }
.stTextArea textarea {
    background-color: rgba(255,255,255,0.95);
    border: 2px solid #0D4F7C;
    border-radius: 12px;
    font-size: 17px;
}
h1, h2, h3 {
    color: #1E2F4D;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

abt_logo = Image.open("ABT TRAC Logo.jpg")
inov8v_logo = Image.open("Innov8v Marine Logo.png")

col1, col2 = st.columns([5, 1])
with col1:
    st.image(abt_logo, width=320)
with col2:
    st.image(inov8v_logo, width=120)

st.title("ABT-TRAC Marine AI Assistant")
st.write("Ask about boats, customers, sales orders, parts, invoices, shipment history, and actuator seal kit opportunities.")

@st.cache_data
def load_data():
    sales_orders = pd.read_excel("Sales Order Record.xlsx")
    line_items = pd.read_excel("Line Item for SOs.xlsx")
    invoices = pd.read_excel("INVs_AsOf_05.20.2026.xlsx")
    seal_kits = pd.read_excel("actuator_seal_kits.xlsx")

    for df, source in [
        (sales_orders, "Sales Order Record"),
        (line_items, "Line Item"),
        (invoices, "Invoice / Ship Date"),
        (seal_kits, "Actuator Seal Kit List")
    ]:
        df["_source"] = source
        df["_search_text"] = (
            df.fillna("")
            .astype(str)
            .apply(lambda row: " ".join(row.values), axis=1)
            .str.lower()
        )

    return sales_orders, line_items, invoices, seal_kits

sales_orders, line_items, invoices, seal_kits = load_data()

def find_cols(df, keywords):
    cols = []
    for col in df.columns:
        c = str(col).lower()
        if any(k in c for k in keywords):
            cols.append(col)
    return cols

def extract_search_terms(question):
    question = str(question).lower()
    stop_words = {
        "what","do","we","know","about","tell","me","show","find","for",
        "the","a","an","of","and","or","to","history","records","record",
        "boat","customer","sales","order","so","invoice","part","parts",
        "needs","need","seal","kit","actuator"
    }

    numbers = re.findall(r"\d+", question)
    words = re.findall(r"[a-zA-Z0-9\-]+", question)

    keywords = [w for w in words if w not in stop_words and len(w) >= 3]

    terms = numbers + keywords
    clean = []
    seen = set()

    for term in terms:
        if term not in seen:
            clean.append(term)
            seen.add(term)

    return clean

def search_df(df, question, max_rows=50):
    terms = extract_search_terms(question)

    if not terms:
        return df.head(0).drop(columns=["_search_text"], errors="ignore")

    results = pd.DataFrame()

    for term in terms:
        matches = df[df["_search_text"].str.contains(term, na=False, regex=False)]
        results = pd.concat([results, matches])

    results = results.drop_duplicates()

    return results.drop(columns=["_search_text"], errors="ignore").head(max_rows)

def get_first_matching_col(df, keywords):
    cols = find_cols(df, keywords)
    return cols[0] if cols else None

def normalize_part(value):
    return str(value).strip().upper().replace(" ", "").replace("-", "")

def analyze_actuator_seal_opportunity(question, sales_matches):
    today = pd.Timestamp(datetime.today().date())

    original_so_col = get_first_matching_col(
        sales_orders,
        ["original so", "orig so", "original sales order", "original order"]
    )

    so_cols_sales = find_cols(sales_orders, ["sales order", "so number", "order number", "so"])
    so_cols_line = find_cols(line_items, ["sales order", "so number", "order number", "so"])
    so_cols_inv = find_cols(invoices, ["sales order", "so number", "order number", "so"])

    part_cols = find_cols(line_items, ["part", "item", "sku", "number"])
    date_cols_inv = find_cols(invoices, ["ship date", "shipdate", "invoice date", "date"])

    seal_part_col = get_first_matching_col(seal_kits, ["part", "item", "sku", "number"])

    if not seal_part_col:
        return {
            "status": "Could not analyze",
            "message": "No part number column found in actuator_seal_kits.xlsx.",
            "seal_rows": pd.DataFrame()
        }

    seal_parts = set(seal_kits[seal_part_col].dropna().map(normalize_part))

    if not seal_parts:
        return {
            "status": "Could not analyze",
            "message": "No seal kit part numbers found in actuator_seal_kits.xlsx.",
            "seal_rows": pd.DataFrame()
        }

    original_sos = set()

    if original_so_col and not sales_matches.empty:
        original_sos.update(
            sales_matches[original_so_col].dropna().astype(str).str.strip().tolist()
        )

    question_numbers = re.findall(r"\d+", question)
    original_sos.update(question_numbers)

    original_sos = {x for x in original_sos if x and x.lower() != "nan"}

    related_sales = pd.DataFrame()

    if original_sos and original_so_col:
        related_sales = sales_orders[
            sales_orders[original_so_col].astype(str).str.strip().isin(original_sos)
        ]

    if related_sales.empty:
        related_sales = sales_matches.copy()

    related_sos = set()

    for col in so_cols_sales:
        if col in related_sales.columns:
            related_sos.update(
                related_sales[col].dropna().astype(str).str.strip().tolist()
            )

    related_sos.update(original_sos)
    related_sos = {x for x in related_sos if x and x.lower() != "nan"}

    related_lines = pd.DataFrame()

    for col in so_cols_line:
        matches = line_items[line_items[col].astype(str).str.strip().isin(related_sos)]
        related_lines = pd.concat([related_lines, matches])

    related_lines = related_lines.drop_duplicates()

    seal_rows = pd.DataFrame()

    for col in part_cols:
        matches = related_lines[
            related_lines[col].map(normalize_part).isin(seal_parts)
        ]
        seal_rows = pd.concat([seal_rows, matches])

    seal_rows = seal_rows.drop_duplicates()

    seal_sos = set()

    for col in so_cols_line:
        if col in seal_rows.columns:
            seal_sos.update(
                seal_rows[col].dropna().astype(str).str.strip().tolist()
            )

    seal_invoice_rows = pd.DataFrame()

    for col in so_cols_inv:
        matches = invoices[invoices[col].astype(str).str.strip().isin(seal_sos)]
        seal_invoice_rows = pd.concat([seal_invoice_rows, matches])

    seal_invoice_rows = seal_invoice_rows.drop_duplicates()

    last_date = None

    for col in date_cols_inv:
        dates = pd.to_datetime(seal_invoice_rows[col], errors="coerce").dropna()
        if not dates.empty:
            candidate = dates.max()
            if last_date is None or candidate > last_date:
                last_date = candidate

    if seal_rows.empty:
        return {
            "status": "FLAG",
            "message": "No actuator seal kit purchase found for the related boat/original SO history. This may be a sales opportunity.",
            "seal_rows": seal_rows
        }

    if last_date is None:
        return {
            "status": "REVIEW",
            "message": "Actuator seal kit purchase found, but no usable invoice/ship date was found. Review manually.",
            "seal_rows": seal_rows
        }

    years_since = round((today - last_date).days / 365.25, 1)

    if years_since >= 5:
        status = "FLAG"
        message = f"Last actuator seal kit shipment appears to be {last_date.date()}, about {years_since} years ago. Flag this boat/order for actuator seal kit follow-up."
    else:
        status = "OK"
        message = f"Last actuator seal kit shipment appears to be {last_date.date()}, about {years_since} years ago. No 5-year flag yet."

    return {
        "status": status,
        "message": message,
        "seal_rows": seal_rows
    }

def compact_table_text(df, max_rows=20):
    if df.empty:
        return "No matching records found."
    return df.head(max_rows).to_string(index=False)

st.header("Ask ABT Marine AI")

question = st.text_area(
    "Ask a question",
    placeholder="Example: What do we know about Odyssey? Does it need an actuator seal kit follow-up?"
)

if st.button("Ask AI"):

    if not question.strip():
        st.warning("Enter a question first.")

    else:
        with st.spinner("Searching records, checking seal kit history, and asking AI..."):

            extracted_terms = extract_search_terms(question)

            sales_matches = search_df(sales_orders, question, max_rows=50)
            line_matches = search_df(line_items, question, max_rows=75)
            invoice_matches = search_df(invoices, question, max_rows=50)

            seal_analysis = analyze_actuator_seal_opportunity(question, sales_matches)

            context = f"""
USER QUESTION:
{question}

SEARCH TERMS USED:
{extracted_terms}

ACTUATOR SEAL KIT FLAG:
Status: {seal_analysis["status"]}
Message: {seal_analysis["message"]}

MATCHING SALES ORDER RECORDS:
{compact_table_text(sales_matches)}

MATCHING LINE ITEM RECORDS:
{compact_table_text(line_matches)}

MATCHING INVOICE / SHIP DATE RECORDS:
{compact_table_text(invoice_matches)}

MATCHING ACTUATOR SEAL KIT ROWS:
{compact_table_text(seal_analysis["seal_rows"])}

IMPORTANT NOTES:
- Use only the provided records.
- Invoice ship date is the closest available date to shipment to the customer.
- The actuator seal kit list comes from actuator_seal_kits.xlsx.
- If the last actuator seal kit shipment is 5+ years ago, flag it as a follow-up opportunity.
- If no actuator seal kit purchase is found, flag it as a possible opportunity.
"""

            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are an internal ABT-TRAC / Inov8v Marine AI assistant.

Help sales and service users understand vessel, customer, part, sales order, invoice, shipment, and actuator seal kit history.

Use only the spreadsheet records provided.
Do not invent facts.
If dates are available, organize chronologically.
Clearly identify actuator seal kit follow-up opportunities.
Be concise and practical for a marine parts salesperson.
"""
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.2
            )

            st.subheader("AI Answer")
            st.write(response.choices[0].message.content)

            if seal_analysis["status"] == "FLAG":
                st.error(seal_analysis["message"])
            elif seal_analysis["status"] == "REVIEW":
                st.warning(seal_analysis["message"])
            else:
                st.success(seal_analysis["message"])

            st.caption(f"Search terms used: {', '.join(extracted_terms)}")

            st.subheader("Matching Sales Orders")
            st.dataframe(sales_matches, use_container_width=True)

            st.subheader("Matching Line Items")
            st.dataframe(line_matches, use_container_width=True)

            st.subheader("Matching Invoice / Ship Date Records")
            st.dataframe(invoice_matches, use_container_width=True)

            st.subheader("Matching Actuator Seal Kit Rows")
            st.dataframe(seal_analysis["seal_rows"], use_container_width=True)

st.markdown("---")
st.caption("AI answers are based on uploaded sales order, line item, invoice, and actuator seal kit records.")
