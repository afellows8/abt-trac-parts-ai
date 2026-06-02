import html
import re
from datetime import datetime

import pandas as pd
import streamlit as st
from openai import OpenAI
from PIL import Image

st.set_page_config(
    page_title="ABT-TRAC AI",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

GITHUB_BASE = "https://raw.githubusercontent.com/afellows8/abt-trac-parts-ai/main/"
BACKGROUND_IMAGE_URL = GITHUB_BASE + "Nordhavn%20N100%20Serenity.jpg"

# -----------------------------------------------------------------------------
# Visual design helpers
# -----------------------------------------------------------------------------

st.markdown(
    f"""
<style>
:root {{
    --abt-navy: #102B49;
    --abt-blue: #0D4F7C;
    --abt-sky: #2D8AB8;
    --abt-gold: #C7A349;
    --abt-ink: #17263B;
    --abt-muted: #627086;
    --abt-card: rgba(255,255,255,0.94);
    --abt-border: rgba(16,43,73,0.13);
}}

[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(120deg, rgba(8,25,43,0.84) 0%, rgba(13,79,124,0.60) 34%, rgba(255,255,255,0.82) 72%),
        url("{BACKGROUND_IMAGE_URL}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

.block-container {{
    padding-top: 1.2rem;
    padding-bottom: 2.5rem;
    max-width: 1220px;
}}

h1, h2, h3, h4 {{
    color: var(--abt-ink);
    letter-spacing: -0.02em;
}}

p, li, div {{
    color: var(--abt-ink);
}}

.hero-shell {{
    background: linear-gradient(135deg, rgba(255,255,255,0.97), rgba(245,250,253,0.90));
    border: 1px solid rgba(255,255,255,0.75);
    border-radius: 28px;
    padding: 28px 30px 24px 30px;
    box-shadow: 0 24px 80px rgba(6,22,38,0.22);
    margin-bottom: 20px;
}}

.hero-eyebrow {{
    color: var(--abt-blue);
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-size: 0.78rem;
    margin-bottom: 8px;
}}

.hero-title {{
    color: var(--abt-navy);
    font-size: 3.05rem;
    line-height: 0.98;
    font-weight: 900;
    margin: 0;
}}

.hero-subtitle {{
    color: var(--abt-muted);
    font-size: 1.08rem;
    line-height: 1.55;
    max-width: 720px;
    margin-top: 14px;
}}

.capability-card, .metric-card, .answer-card, .search-card, .record-card {{
    background: var(--abt-card);
    border: 1px solid var(--abt-border);
    border-radius: 22px;
    box-shadow: 0 16px 48px rgba(7,28,49,0.13);
}}

.capability-card {{
    padding: 18px 18px 16px 18px;
    min-height: 142px;
}}

.capability-icon {{
    width: 36px;
    height: 36px;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--abt-blue), var(--abt-sky));
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.08rem;
    font-weight: 900;
    margin-bottom: 12px;
}}

.capability-title {{
    font-weight: 850;
    color: var(--abt-navy);
    font-size: 1.02rem;
    margin-bottom: 6px;
}}

.capability-copy {{
    color: var(--abt-muted);
    font-size: 0.92rem;
    line-height: 1.42;
}}

.search-card {{
    padding: 22px 24px 24px 24px;
    margin-top: 18px;
}}

.search-label {{
    color: #102B49;
    font-weight: 900;
    font-size: 1.45rem;
    margin-bottom: 8px;
    text-shadow: 0px 1px 2px rgba(255,255,255,0.7);
}}

.search-help {{
    color: #FFFFFF;
    background: linear-gradient(135deg, #0D4F7C, #102B49);
    font-size: 1.14rem;
    font-weight: 900;
    margin-bottom: 16px;
    padding: 12px 16px;
    border-radius: 14px;
    box-shadow: 0 10px 26px rgba(7,28,49,0.18);
}}

.stTextArea textarea {{
    background-color: rgba(255,255,255,0.98) !important;
    border: 1.5px solid rgba(13,79,124,0.28) !important;
    border-radius: 18px !important;
    color: var(--abt-ink) !important;
    font-size: 1.02rem !important;
    line-height: 1.45 !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
}}

.stTextArea textarea:focus {{
    border-color: var(--abt-blue) !important;
    box-shadow: 0 0 0 4px rgba(13,79,124,0.10) !important;
}}

.stButton button {{
    width: 100%;
    background: linear-gradient(135deg, var(--abt-blue), var(--abt-navy)) !important;
    color: white !important;
    border-radius: 16px !important;
    border: 0 !important;
    padding: 0.78rem 1.15rem !important;
    font-weight: 850 !important;
    box-shadow: 0 12px 28px rgba(13,79,124,0.25);
}}

.stButton button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 16px 34px rgba(13,79,124,0.30);
}}

.stButton button * {{
    color: white !important;
}}

.metric-card {{
    padding: 17px 18px;
    border-left: 5px solid var(--abt-gold);
}}

.metric-value {{
    font-size: 2rem;
    line-height: 1;
    font-weight: 900;
    color: var(--abt-navy);
}}

.metric-label {{
    margin-top: 6px;
    color: var(--abt-muted);
    font-weight: 700;
    font-size: 0.88rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

.section-kicker {{
    color: var(--abt-blue);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.78rem;
    font-weight: 850;
    margin-top: 26px;
}}

.section-title {{
    color: var(--abt-navy);
    font-size: 1.55rem;
    font-weight: 900;
    margin-bottom: 10px;
}}

.answer-card {{
    padding: 24px 26px;
    border-top: 5px solid var(--abt-blue);
}}

.answer-card h1, .answer-card h2, .answer-card h3 {{
    color: var(--abt-navy);
}}

.service-card {{
    background: linear-gradient(135deg, rgba(199,163,73,0.18), rgba(255,255,255,0.94));
    border: 1px solid rgba(199,163,73,0.35);
    border-radius: 20px;
    padding: 18px 20px;
    box-shadow: 0 12px 36px rgba(7,28,49,0.10);
}}

.upgrade-card {{
    background: rgba(255,255,255,0.95);
    border: 1px solid rgba(13,79,124,0.18);
    border-radius: 20px;
    padding: 18px 20px;
    box-shadow: 0 12px 36px rgba(7,28,49,0.10);
    margin-bottom: 12px;
}}

.upgrade-title {{
    color: var(--abt-navy);
    font-size: 1.12rem;
    font-weight: 900;
    margin-bottom: 8px;
}}

.pill {{
    display: inline-block;
    background: rgba(13,79,124,0.10);
    color: var(--abt-blue);
    border: 1px solid rgba(13,79,124,0.14);
    border-radius: 999px;
    padding: 6px 10px;
    margin: 4px 5px 2px 0;
    font-size: 0.82rem;
    font-weight: 750;
}}

.lit-link a {{
    color: var(--abt-blue) !important;
    font-weight: 800;
    text-decoration: none;
}}

.small-muted {{
    color: var(--abt-muted);
    font-size: 0.88rem;
}}

div[data-testid="stExpander"] {{
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(16,43,73,0.12);
    border-radius: 18px;
}}

[data-testid="stDataFrame"] {{
    border-radius: 16px;
    overflow: hidden;
}}

.footer-note {{
    color: rgba(255,255,255,0.88);
    font-size: 0.86rem;
    text-align: center;
    padding: 14px 0 0 0;
}}
</style>
""",
    unsafe_allow_html=True,
)


def safe_text(value):
    return html.escape(str(value))


def markdown_card(title, body, icon="✓"):
    st.markdown(
        f"""
<div class="capability-card">
  <div class="capability-icon">{safe_text(icon)}</div>
  <div class="capability-title">{safe_text(title)}</div>
  <div class="capability-copy">{safe_text(body)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def metric_card(value, label):
    st.markdown(
        f"""
<div class="metric-card">
  <div class="metric-value">{safe_text(value)}</div>
  <div class="metric-label">{safe_text(label)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def section_header(kicker, title):
    st.markdown(
        f"""
<div class="section-kicker">{safe_text(kicker)}</div>
<div class="section-title">{safe_text(title)}</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
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
        (upgrades, "Upgrade Opportunities"),
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


# -----------------------------------------------------------------------------
# Business logic helpers
# -----------------------------------------------------------------------------

def find_cols(df, keywords):
    return [col for col in df.columns if any(k in str(col).lower() for k in keywords)]


def get_first_matching_col(df, keywords):
    cols = find_cols(df, keywords)
    return cols[0] if cols else None


def get_exact_col(df, desired_name):
    desired = str(desired_name).strip().lower()
    for col in df.columns:
        if str(col).strip().lower() == desired:
            return col
    return None


def get_part_number_col(df):
    exact = get_exact_col(df, "Part Number")
    if exact:
        return exact

    part_number_cols = [
        col for col in df.columns
        if "part number" in str(col).strip().lower()
    ]
    if part_number_cols:
        return part_number_cols[0]

    part_cols = [
        col for col in df.columns
        if "part" in str(col).strip().lower()
        and "description" not in str(col).strip().lower()
    ]
    return part_cols[0] if part_cols else None


def normalize_so(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.endswith(".0"):
        value = value[:-2]
    return value


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
        "what", "do", "we", "know", "about", "tell", "me", "show", "find", "for",
        "the", "a", "an", "of", "and", "or", "to", "history", "records", "record",
        "boat", "customer", "sales", "order", "so", "invoice", "part", "parts",
        "needs", "need", "seal", "kit", "actuator", "upgrade", "service",
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
        ["original so", "orig so", "original sales order", "original order"],
    )

    so_cols_sales = find_cols(sales_orders, ["sales order", "so number", "order number", "so"])
    so_cols_line = find_cols(line_items, ["sales order", "so number", "order number", "so"])
    so_cols_inv = find_cols(invoices, ["sales order", "so number", "order number", "so"])

    original_sos = {n for n in re.findall(r"\d+", str(question)) if len(n) >= 4}

    if original_so_col and not sales_matches.empty:
        original_sos.update(
            sales_matches[original_so_col].dropna().map(normalize_so).tolist()
        )

    original_sos = {x for x in original_sos if x and x.lower() != "nan"}

    related_sales = pd.DataFrame()

    if original_so_col and original_sos:
        related_sales = sales_orders[
            sales_orders[original_so_col].map(normalize_so).isin(original_sos)
        ]

    if related_sales.empty:
        related_sales = sales_matches.copy()

    related_sos = set(original_sos)

    for col in so_cols_sales:
        if col in related_sales.columns:
            related_sos.update(related_sales[col].dropna().map(normalize_so).tolist())

    related_sos = {x for x in related_sos if x and x.lower() != "nan"}

    related_lines = pd.DataFrame()
    for col in so_cols_line:
        if col in line_items.columns:
            related_lines = pd.concat([
                related_lines,
                line_items[line_items[col].map(normalize_so).isin(related_sos)],
            ])

    related_invoices = pd.DataFrame()
    for col in so_cols_inv:
        if col in invoices.columns:
            related_invoices = pd.concat([
                related_invoices,
                invoices[invoices[col].map(normalize_so).isin(related_sos)],
            ])

    return (
        related_sales.drop_duplicates(),
        related_lines.drop_duplicates(),
        related_invoices.drop_duplicates(),
        related_sos,
    )


def analyze_actuator_seal_service(question, sales_matches):
    today = pd.Timestamp(datetime.today().date())

    related_sales, related_lines, related_invoices, related_sos = get_related_history(
        question,
        sales_matches,
    )

    part_number_col = get_part_number_col(related_lines)
    so_cols_line = find_cols(line_items, ["sales order", "so number", "order number", "so"])
    so_cols_inv = find_cols(invoices, ["sales order", "so number", "order number", "so"])
    date_cols_inv = find_cols(invoices, ["ship date", "shipdate", "invoice date", "date"])

    seal_part_col = get_part_number_col(seal_kits)

    if not seal_part_col:
        return "No part number column found in actuator_seal_kits.xlsx.", pd.DataFrame()

    seal_parts = set(seal_kits[seal_part_col].dropna().map(normalize_part))

    seal_rows = pd.DataFrame()

    if part_number_col:
        seal_rows = related_lines[
            related_lines[part_number_col].map(normalize_part).isin(seal_parts)
        ].copy()

    seal_rows = seal_rows.drop_duplicates()

    seal_sos = set()

    for col in so_cols_line:
        if col in seal_rows.columns:
            seal_sos.update(seal_rows[col].dropna().map(normalize_so).tolist())

    seal_invoice_rows = pd.DataFrame()

    for col in so_cols_inv:
        seal_invoice_rows = pd.concat([
            seal_invoice_rows,
            invoices[invoices[col].map(normalize_so).isin(seal_sos)],
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
            seal_rows,
        )

    if last_date is None:
        return (
            "Actuator seal kit found, but no usable ship/invoice date found. Review manually.",
            seal_rows,
        )

    years_since = round((today - last_date).days / 365.25, 1)

    if years_since >= 5:
        return (
            f"Last actuator seal kit shipment appears to be {last_date.date()}, about {years_since} years ago. Recommended service follow-up.",
            seal_rows,
        )

    return (
        f"Last actuator seal kit shipment appears to be {last_date.date()}, about {years_since} years ago.",
        seal_rows,
    )


def get_part_history_set(related_lines):
    part_set = set()
    part_number_col = get_part_number_col(related_lines)

    if not part_number_col:
        return part_set

    values = related_lines[part_number_col].dropna().map(normalize_part).tolist()
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
        sales_matches,
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
        has_qualifying_part = any(part in part_history for part in qualifying_parts) if qualifying_parts else True

        if (not has_blocking_part) and has_qualifying_part:
            opportunities.append({
                "Upgrade": upgrade_name,
                "Matching Existing Parts": ", ".join([p for p in qualifying_parts if p in part_history]),
                "Literature": get_upgrade_links(row),
            })

    return opportunities


def opportunities_to_text(opportunities):
    if not opportunities:
        return "No applicable upgrade opportunities found."

    lines = []
    for opp in opportunities:
        lines.append(f"Upgrade: {opp['Upgrade']}")
        if opp["Literature"]:
            literature_names = [name for name, url in opp["Literature"]]
            lines.append(f"Literature: {', '.join(literature_names)}")
        lines.append("")
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Header / demo-ready UI
# -----------------------------------------------------------------------------

hero_left, hero_right = st.columns([4.5, 1.4], vertical_alignment="center")

with hero_left:
    st.markdown(
        """
<div class="hero-shell">
  <div class="hero-eyebrow">Internal Marine Sales Intelligence</div>
  <h1 class="hero-title">ABT-TRAC AI</h1>
  <div class="hero-subtitle">
    Search decades of vessel, parts, invoice, service, and upgrade history — then turn hidden records into actionable service and revenue opportunities.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

with hero_right:
    logo_col_a, logo_col_b = st.columns([4, 1])
    try:
        st.image(Image.open("ABT TRAC Logo.jpg"), width=210)
    except Exception:
        st.markdown("### ABT TRAC")
    try:
        st.image(Image.open("Innov8v Marine Logo.png"), width=120)
    except Exception:
        st.caption("Inov8v Marine")

cap1, cap2, cap3, cap4 = st.columns(4)
with cap1:
    markdown_card("Vessel History", "Connects related sales orders by original vessel history.", "⚓")
with cap2:
    markdown_card("Service Signals", "Flags actuator seal kit follow-up and service timing.", "🔧")
with cap3:
    markdown_card("Upgrade Paths", "Finds applicable upgrades without showing ineligible noise.", "↗")
with cap4:
    markdown_card("Sales Summary", "Generates concise, salesperson-ready customer notes.", "AI")

st.markdown('<div class="search-card">', unsafe_allow_html=True)
st.markdown('<div class="search-label">Search Vessel History, Service Opportunities, and Upgrade Recommendations</div>', unsafe_allow_html=True)
st.markdown('<div class="search-help">Ask ABT AI about a <b>Sales Order Number</b>, <b>Boat Name</b>, or <b>Hull Number</b>.</div>', unsafe_allow_html=True)

with st.form("ask_ai_form"):
    question = st.text_area(
        "Question",
        label_visibility="collapsed",
        placeholder="Ask ABT AI about a Sales Order Number, Boat Name, or Hull Number...",
        height=105,
    )
    ask_clicked = st.form_submit_button("Run Marine AI Analysis")

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# AI workflow and output
# -----------------------------------------------------------------------------

if ask_clicked:
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        with st.spinner("Analyzing vessel records, service history, invoice dates, and upgrade opportunities..."):
            extracted_terms = extract_search_terms(question)

            sales_matches = search_df(sales_orders, question, max_rows=50)
            line_matches = search_df(line_items, question, max_rows=75)
            invoice_matches = search_df(invoices, question, max_rows=50)

            related_sales, related_lines, related_invoices, related_sos = get_related_history(
                question,
                sales_matches,
            )

            sales_context = related_sales if not related_sales.empty else sales_matches
            line_context = related_lines if not related_lines.empty else line_matches
            invoice_context = related_invoices if not related_invoices.empty else invoice_matches

            service_message, seal_rows = analyze_actuator_seal_service(
                question,
                sales_matches,
            )

            upgrade_opportunities = analyze_upgrade_opportunities(question, sales_matches)
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
{compact_table_text(sales_context)}

MATCHING LINE ITEM RECORDS:
{compact_table_text(line_context)}

MATCHING INVOICE / SHIP DATE RECORDS:
{compact_table_text(invoice_context)}

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
""",
                    },
                    {"role": "user", "content": context},
                ],
                temperature=0.2,
            )

            ai_answer = response.choices[0].message.content

        section_header("Analysis Complete", "Marine AI Recommendation")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            metric_card(len(sales_context), "Sales Orders")
        with m2:
            metric_card(len(line_context), "Line Items")
        with m3:
            metric_card(len(invoice_context), "Invoice Records")
        with m4:
            metric_card(len(upgrade_opportunities), "Upgrade Opportunities")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="answer-card">', unsafe_allow_html=True)
        st.markdown(ai_answer)
        st.markdown('</div>', unsafe_allow_html=True)

        section_header("Recommended Service", "Service Follow-Up")
        st.markdown(
            f"""
<div class="service-card">
  <div class="upgrade-title">Actuator Seal Kit Review</div>
  <div>{safe_text(service_message)}</div>
</div>
""",
            unsafe_allow_html=True,
        )

        section_header("Revenue Opportunities", "Applicable Upgrades")
        if upgrade_opportunities:
            for opp in upgrade_opportunities:
                st.markdown(
                    f"""
<div class="upgrade-card">
  <div class="upgrade-title">{safe_text(opp['Upgrade'])}</div>
  <div class="small-muted">Supporting literature</div>
""",
                    unsafe_allow_html=True,
                )

                if opp["Literature"]:
                    for name, url in opp["Literature"]:
                        st.markdown(
                            f'<div class="lit-link">• <a href="{safe_text(url)}" target="_blank">{safe_text(name)}</a></div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("No literature file listed.")

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No applicable upgrade opportunities found.")

        section_header("Supporting Records", "Evidence Used by the AI")
        st.markdown(
            "".join([f'<span class="pill">{safe_text(term)}</span>' for term in extracted_terms])
            if extracted_terms else '<span class="pill">No search terms</span>',
            unsafe_allow_html=True,
        )

        with st.expander("Sales order records", expanded=False):
            st.dataframe(sales_context, use_container_width=True, hide_index=True)

        with st.expander("Line item records", expanded=False):
            st.dataframe(line_context, use_container_width=True, hide_index=True)

        with st.expander("Invoice / ship date records", expanded=False):
            st.dataframe(invoice_context, use_container_width=True, hide_index=True)

        with st.expander("Actuator seal kit rows", expanded=False):
            st.dataframe(seal_rows, use_container_width=True, hide_index=True)

st.markdown(
    '<div class="footer-note">AI answers are based on uploaded sales order, line item, invoice, actuator seal kit, and upgrade opportunity records.</div>',
    unsafe_allow_html=True,
)
