import streamlit as st
import pandas as pd
from PIL import Image
from openai import OpenAI
import re
from datetime import datetime

st.set_page_config(page_title="ABT-TRAC Marine AI", layout="wide")

GITHUB_BASE = "https://raw.githubusercontent.com/afellows8/abt-trac-parts-ai/main/"

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
st.write("Ask about boats, customers, service needs, upgrade opportunities, sales orders, parts, invoices, and shipment history.")

@st.cache_data
def load_data():
    sales_orders = pd.read_excel("Sales Order Record.xlsx")
    line_items = pd.read_excel("Line Item for SOs.xlsx")
    invoices = pd.read_excel("INVs_AsOf_05.20.2026.xlsx")
    seal_kits = pd.read_excel("actuator_seal_kits.xlsx")
    upgrades = pd.read_excel("Upgrades.xlsx")

    for df, source in [
        (sales_orders, "Sales Order Record"),
        (line_items, "Line Item"),
        (invoices, "Invoice / Ship Date"),
        (seal_kits, "Actuator Seal Kit List"),
        (upgrades, "Upgrade Opportunities")
    ]:
        df["_source"] = source
        df["_search_text"] = (
            df.fillna("")
            .astype(str)
            .apply(lambda row: " ".join(row.values), axis=1)
            .str.lower()
        )

    return sales_orders, line_items, invoices, seal_kits, upgrades

sales_orders, line_items, invoices, seal_kits, upgrades = load_data()

def find_cols(df, keywords):
    return [col for col in df.columns if any(k in str(col).lower() for k in keywords)]

def get_first_matching_col(df, keywords):
    cols = find_cols(df, keywords)
    return cols[0] if cols else None

def normalize_part(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.endswith(".0"):
        value = value[:-2]
    return value.upper().replace(" ", "").replace("-", "")

def extract_search_terms(question):
    question = str(question).lower()
    stop_words = {
        "what","do","we","know","about","tell","me","show","find","for",
        "the","a","an","of","and","or","to","history","records","record",
        "boat","customer","sales","order","so","invoice","part","parts",
        "needs","need","seal","kit","actuator","upgrade","service"
    }

    numbers = re.findall(r"\d+", question)
    words = re.findall(r"[a-zA-Z0-9\-]+", question)
    keywords = [w for w in words if w not in stop_words and len(w) >= 3]

    terms = numbers + keywords
    clean_terms = []
    seen = set()

    for term in terms:
        if term not in seen:
            clean_terms.append(term)
            seen.add(term)

    return clean_terms

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

def compact_table_text(df, max_rows=20):
    if df.empty:
        return "No matching records found."
    return df.head(max_rows).to_string(index=False)

def get_related_history(question, sales_matches):
    original_so_col = get_first_matching_col(
        sales_orders,
        ["original so", "orig so", "original sales order", "original order"]
    )

    so_cols_sales = find_cols(sales_orders, ["sales order", "so number", "order number", "so"])
    so_cols_line = find_cols(line_items, ["sales order", "so number", "order number", "so"])
    so_cols_inv = find_cols(invoices, ["sales order", "so number", "order number", "so"])

    original_sos = set(re.findall(r"\d+", str(question)))

    if original_so_col and not sales_matches.empty:
        original_sos.update(
            sales_matches[original_so_col].dropna().astype(str).str.strip().tolist()
        )

    original_sos = {x for x in original_sos if x and x.lower() != "nan"}

    related_sales = pd.DataFrame()

    if original_so_col and original_sos:
        related_sales = sales_orders[
            sales_orders[original_so_col].astype(str).str.strip().isin(original_sos)
        ]

    if related_sales.empty:
        related_sales = sales_matches.copy()

    related_sos = set(original_sos)

    for col in so_cols_sales:
        if col in related_sales.columns:
            related_sos.update(
                related_sales[col].dropna().astype(str).str.strip().tolist()
            )

    related_sos = {x for x in related_sos if x and x.lower() != "nan"}

    related_lines = pd.DataFrame()
    for col in so_cols_line:
        if col in line_items.columns:
            related_lines = pd.concat([
                related_lines,
                line_items[line_items[col].astype(str).str.strip().isin(related_sos)]
            ])

    related_invoices = pd.DataFrame()
    for col in so_cols_inv:
        if col in invoices.columns:
            related_invoices = pd.concat([
                related_invoices,
                invoices[invoices[col].astype(str).str.strip().isin(related_sos)]
            ])

    return (
        related_sales.drop_duplicates(),
        related_lines.drop_duplicates(),
        related_invoices.drop_duplicates(),
        related_sos
    )
def analyze_actuator_seal_service(question, sales_matches):

    today = pd.Timestamp(datetime.today().date())

    related_sales, related_lines, related_invoices, related_sos = get_related_history(
        question,
        sales_matches
    )

    part_cols = find_cols(line_items, ["part", "item", "sku", "number"])
    so_cols_line = find_cols(line_items, ["sales order", "so number", "order number", "so"])
    so_cols_inv = find_cols(invoices, ["sales order", "so number", "order number", "so"])
    date_cols_inv = find_cols(invoices, ["ship date", "shipdate", "invoice date", "date"])

    seal_part_col = get_first_matching_col(seal_kits, ["part", "item", "sku", "number"])

    if not seal_part_col:
        return "No part number column found in actuator_seal_kits.xlsx.", pd.DataFrame()

    seal_parts = set(seal_kits[seal_part_col].dropna().map(normalize_part))

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
        seal_invoice_rows = pd.concat([
            seal_invoice_rows,
            invoices[invoices[col].astype(str).str.strip().isin(seal_sos)]
        ])

    seal_invoice_rows = seal_invoice_rows.drop_duplicates()

    last_date = None

    for col in date_cols_inv:
        dates = pd.to_datetime(seal_invoice_rows[col], errors="coerce").dropna()
        if not dates.empty:
            candidate = dates.max()
            if last_date is None or candidate > last_date:
                last_date = candidate

    if seal_rows.empty:
        return (
            "No actuator seal kit purchase found in related history. Recommended service follow-up.",
            seal_rows
        )

    if last_date is None:
        return (
            "Actuator seal kit found, but no usable ship/invoice date found. Review manually.",
            seal_rows
        )

    years_since = round((today - last_date).days / 365.25, 1)

    if years_since >= 5:
        return (
            f"Last actuator seal kit shipment appears to be {last_date.date()}, about {years_since} years ago. Recommended service follow-up.",
            seal_rows
        )

    return (
        f"Last actuator seal kit shipment appears to be {last_date.date()}, about {years_since} years ago.",
        seal_rows
    )


def get_part_history_set(related_lines):
    part_cols = find_cols(line_items, ["part", "item", "sku", "number"])
    part_set = set()

    for col in part_cols:
        if col in related_lines.columns:
            values = related_lines[col].dropna().map(normalize_part).tolist()
            part_set.update([v for v in values if v])

    return part_set


def get_upgrade_links(row):
    links = []

    for col in upgrades.columns[9:11]:
        filename = row.get(col, "")
        if pd.notna(filename) and str(filename).strip():
            file_clean = str(filename).strip()
            url_file = file_clean.replace(" ", "%20")
            links.append((file_clean, GITHUB_BASE + url_file))

    return links


def analyze_upgrade_opportunities(question, sales_matches):
    related_sales, related_lines, related_invoices, related_sos = get_related_history(
        question,
        sales_matches
    )

    part_history = get_part_history_set(related_lines)

    opportunities = []

    for _, row in upgrades.iterrows():
        upgrade_name = str(row.iloc[0]).strip()

        if not upgrade_name or upgrade_name.lower() == "nan":
            continue

        must_not_have = normalize_part(row.iloc[1]) if len(row) > 1 else ""

        qualifying_parts = []

        for value in row.iloc[2:9]:
            part = normalize_part(value)
            if part:
                qualifying_parts.append(part)

        has_blocking_part = must_not_have in part_history if must_not_have else False

        if qualifying_parts:
            has_qualifying_part = any(part in part_history for part in qualifying_parts)
        else:
            has_qualifying_part = True

        if (not has_blocking_part) and has_qualifying_part:
            links = get_upgrade_links(row)

            opportunities.append({
                "Upgrade": upgrade_name,
                "Blocking Part Not Found": must_not_have,
                "Matching Existing Parts": ", ".join(
                    [p for p in qualifying_parts if p in part_history]
                ),
                "Literature": links
            })

    return opportunities


def opportunities_to_text(opportunities):
    if not opportunities:
        return "No applicable upgrade opportunities found."

    lines = []

    for opp in opportunities:
        lines.append(f"Upgrade: {opp['Upgrade']}")

        if opp["Matching Existing Parts"]:
            lines.append(f"Matching existing parts: {opp['Matching Existing Parts']}")

        if opp["Literature"]:
            literature_names = [name for name, url in opp["Literature"]]
            lines.append(f"Literature: {', '.join(literature_names)}")

        lines.append("")

    return "\n".join(lines)


st.header("Ask ABT Marine AI")

question = st.text_area(
    "Ask a question",
    placeholder="Example: What do we know about Odyssey? Does it need service or any upgrades?"
)

if st.button("Ask AI"):

    if not question.strip():
        st.warning("Enter a question first.")

    else:
        with st.spinner("Searching records, checking service needs, checking upgrade opportunities, and asking AI..."):

            extracted_terms = extract_search_terms(question)

            sales_matches = search_df(sales_orders, question, max_rows=50)
            line_matches = search_df(line_items, question, max_rows=75)
            invoice_matches = search_df(invoices, question, max_rows=50)

            service_message, seal_rows = analyze_actuator_seal_service(
                question,
                sales_matches
            )

            upgrade_opportunities = analyze_upgrade_opportunities(
                question,
                sales_matches
            )

            upgrade_text = opportunities_to_text(upgrade_opportunities)

            context = f"""
USER QUESTION:
{question}

SEARCH TERMS USED:
{extracted_terms}

RECOMMENDED SERVICE:
{service_message}

UPGRADE OPPORTUNITIES:
{upgrade_text}

MATCHING SALES ORDER RECORDS:
{compact_table_text(sales_matches)}

MATCHING LINE ITEM RECORDS:
{compact_table_text(line_matches)}

MATCHING INVOICE / SHIP DATE RECORDS:
{compact_table_text(invoice_matches)}

MATCHING ACTUATOR SEAL KIT ROWS:
{compact_table_text(seal_rows)}

IMPORTANT NOTES:
- Use only the provided records.
- Invoice ship date is the closest available shipment date to the customer.
- Recommended Service includes actuator seal kit follow-up.
- Upgrade opportunities come from Upgrades.xlsx.
- For upgrades, only mention applicable upgrade opportunities.
- Do not mention upgrade status categories.
- If literature files are available, mention them as supporting literature.
"""

            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are an internal ABT-TRAC / Inov8v Marine AI assistant.

Organize answers into:
1. Summary
2. Recommended Service
3. Upgrade Opportunities
4. Supporting Records

Use only the records provided.
Do not invent facts.
For Upgrade Opportunities, only list upgrades that are applicable.
Do not show internal eligibility/status logic.
Be concise and useful for a marine parts salesperson.
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

            st.subheader("Recommended Service")
            st.info(service_message)

            st.subheader("Upgrade Opportunities")

            if upgrade_opportunities:
                for opp in upgrade_opportunities:
                    st.markdown(f"### {opp['Upgrade']}")

                    if opp["Matching Existing Parts"]:
                        st.write(f"Relevant existing parts found: {opp['Matching Existing Parts']}")

                    if opp["Literature"]:
                        for name, url in opp["Literature"]:
                            st.markdown(f"- [{name}]({url})")
            else:
                st.write("No applicable upgrade opportunities found.")

            st.caption(f"Search terms used: {', '.join(extracted_terms)}")

            st.subheader("Matching Sales Orders")
            st.dataframe(sales_matches, use_container_width=True)

            st.subheader("Matching Line Items")
            st.dataframe(line_matches, use_container_width=True)

            st.subheader("Matching Invoice / Ship Date Records")
            st.dataframe(invoice_matches, use_container_width=True)

            st.subheader("Matching Actuator Seal Kit Rows")
            st.dataframe(seal_rows, use_container_width=True)

st.markdown("---")
st.caption("AI answers are based on uploaded sales order, line item, invoice, actuator seal kit, and upgrade opportunity records.")
