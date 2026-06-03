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
    --abt-card: rgba(255,255,255,0.97);
    --abt-border: rgba(16,43,73,0.13);
}}

[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(120deg, rgba(0,0,0,0.16), rgba(0,0,0,0.16)),
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
    background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(245,250,253,0.94));
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
    color: #233B58;
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
    background: rgba(255,255,255,0.98);
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
    color: #233B58;
    font-size: 0.92rem;
    line-height: 1.42;
}}

.search-card {{
    padding: 22px 24px 24px 24px;
    margin-top: 18px;
    background: rgba(255,255,255,0.97);
}}

.search-label {{
    color: #081A2F;
    font-weight: 900;
    font-size: 1.45rem;
    margin-bottom: 8px;
    text-shadow: 0px 1px 2px rgba(255,255,255,0.7);
}}

.search-help {{
    color: #FFFFFF !important;
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

.nav-caption {{
    background: rgba(255,255,255,0.98);
    border: 1px solid rgba(16,43,73,0.12);
    border-radius: 0 0 18px 18px;
    padding: 8px 12px 12px 12px;
    margin-top: -8px;
    margin-bottom: 8px;
    min-height: 54px;
    color: #233B58;
    font-size: 0.90rem;
    line-height: 1.32;
    box-shadow: 0 14px 34px rgba(7,28,49,0.10);
}}

.panel-note {{
    background: rgba(255,255,255,0.98);
    border: 1px solid rgba(16,43,73,0.12);
    border-radius: 18px;
    padding: 16px 18px;
    margin-top: 12px;
    color: #102B49;
    font-weight: 800;
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
    color: #102B49;
    font-weight: 800;
    font-size: 0.88rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

.section-kicker {{
    color: #0D4F7C;
    background: rgba(255,255,255,0.97);
    border: 1px solid rgba(16,43,73,0.12);
    border-bottom: 0;
    border-radius: 18px 18px 0 0;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.78rem;
    font-weight: 900;
    margin-top: 26px;
    padding: 14px 18px 4px 18px;
}}

.section-title {{
    color: #081A2F;
    background: rgba(255,255,255,0.97);
    border: 1px solid rgba(16,43,73,0.12);
    border-top: 0;
    border-radius: 0 0 18px 18px;
    font-size: 1.55rem;
    font-weight: 900;
    margin-bottom: 10px;
    padding: 0 18px 14px 18px;
    box-shadow: 0 12px 32px rgba(7,28,49,0.10);
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
    color: #233B58;
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
    color: #102B49;
    background: rgba(255,255,255,0.86);
    border-radius: 14px;
    font-size: 0.86rem;
    text-align: center;
    padding: 12px;
    margin-top: 16px;
}}

.profile-grid {{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 12px;
}}
.profile-tile {{
    background: rgba(255,255,255,0.98);
    border: 1px solid rgba(16,43,73,0.12);
    border-radius: 18px;
    padding: 14px 16px;
    box-shadow: 0 12px 32px rgba(7,28,49,0.10);
}}
.profile-label {{
    color: #233B58;
    font-size: 0.78rem;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}}
.profile-value {{
    color: var(--abt-navy);
    font-size: 1.2rem;
    font-weight: 900;
    margin-top: 4px;
}}
.timeline-box {{
    background: rgba(255,255,255,0.98);
    border: 1px solid rgba(16,43,73,0.12);
    border-radius: 20px;
    padding: 16px 18px;
    box-shadow: 0 12px 32px rgba(7,28,49,0.10);
    margin-bottom: 10px;
}}
.timeline-item {{
    border-left: 4px solid var(--abt-blue);
    padding: 6px 0 10px 14px;
    margin-left: 5px;
}}
.timeline-date {{
    color: #102B49;
    font-weight: 900;
    font-size: 0.9rem;
}}
.timeline-title {{
    color: var(--abt-navy);
    font-weight: 900;
}}
.timeline-copy {{
    color: #233B58;
    font-size: 0.9rem;
}}
.dashboard-card {{
    background: rgba(255,255,255,0.98);
    border: 1px solid rgba(16,43,73,0.12);
    border-radius: 22px;
    padding: 18px 20px;
    box-shadow: 0 16px 48px rgba(7,28,49,0.13);
    margin: 18px 0;
}}

/* Readability hardening for demo screens */
.stMarkdown, .stMarkdown p, .stMarkdown li, .stCaptionContainer, label, .stSelectbox label, .stTextInput label {{
    color: #081A2F !important;
}}
div[data-testid="stMarkdownContainer"] p {{
    color: #102B49;
}}


/* Final readability fix: keep generated output on clean white surfaces */
.generated-output-card, .ai-answer-html, .opportunity-dashboard-shell {{
    background: rgba(255,255,255,0.985);
    border: 1px solid rgba(16,43,73,0.14);
    border-radius: 22px;
    box-shadow: 0 16px 48px rgba(7,28,49,0.14);
    color: #071A2F !important;
}}
.ai-answer-html {{
    padding: 24px 28px;
    border-top: 5px solid #0D4F7C;
}}
.ai-answer-html, .ai-answer-html * {{
    color: #071A2F !important;
}}
.ai-answer-html h1, .ai-answer-html h2, .ai-answer-html h3, .ai-answer-html strong {{
    color: #061B31 !important;
}}
.timeline-box, .service-card, .upgrade-card, .profile-tile, .dashboard-card, .answer-card {{
    background: rgba(255,255,255,0.985) !important;
    color: #071A2F !important;
}}
.timeline-box *, .service-card *, .upgrade-card *, .profile-tile *, .dashboard-card *, .answer-card * {{
    color: #071A2F !important;
}}
.stMarkdown, .stMarkdown *, div[data-testid="stMarkdownContainer"], div[data-testid="stMarkdownContainer"] *,
.stCaptionContainer, .stCaptionContainer *, label, .stSelectbox label, .stTextArea label, .stTextInput label {{
    color: #071A2F !important;
}}
div[data-testid="stExpander"] {{
    background: rgba(255,255,255,0.985) !important;
}}
div[data-testid="stExpander"] * {{
    color: #071A2F !important;
}}
.stSelectbox > div > div {{
    background-color: rgba(255,255,255,0.98) !important;
    color: #071A2F !important;
}}
[data-testid="stDataFrame"] {{
    background: rgba(255,255,255,0.99) !important;
}}

.search-help, .search-help *, .search-help b {{
    color: #FFFFFF !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 10px;
    background: rgba(255,255,255,0.92);
    border-radius: 18px;
    padding: 10px;
    box-shadow: 0 14px 34px rgba(7,28,49,0.16);
}}

.stTabs [data-baseweb="tab"] {{
    background: linear-gradient(135deg, #0D4F7C, #102B49);
    color: #FFFFFF !important;
    border-radius: 14px;
    padding: 10px 16px;
    font-weight: 900;
}}

.stTabs [data-baseweb="tab"] * {{
    color: #FFFFFF !important;
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, #2D8AB8, #0D4F7C) !important;
}}

.agent-card {{
    background: rgba(255,255,255,0.985);
    border: 1px solid rgba(16,43,73,0.14);
    border-radius: 22px;
    box-shadow: 0 16px 48px rgba(7,28,49,0.14);
    padding: 22px 24px;
    color: #071A2F !important;
}}

.agent-card, .agent-card * {{
    color: #071A2F !important;
}}

</style>
""",
    unsafe_allow_html=True,
)


def safe_text(value):
    return html.escape(str(value))


def simple_markdown_to_html(markdown_text):
    """Small markdown renderer for the AI answer so it stays inside a readable white card."""
    lines = str(markdown_text).splitlines()
    html_lines = []
    in_ul = False
    in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            html_lines.append("</ul>")
            in_ul = False
        if in_ol:
            html_lines.append("</ol>")
            in_ol = False

    for raw in lines:
        line = raw.strip()
        if not line:
            close_lists()
            html_lines.append("<br>")
            continue

        escaped = safe_text(line)
        escaped = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", escaped)

        if re.match(r"^#{1,3}\s+", line):
            close_lists()
            level = min(line.count("#", 0, line.find(" ")), 3)
            content = safe_text(line[level:].strip())
            html_lines.append(f"<h{level}>{content}</h{level}>")
        elif re.match(r"^\d+\.\s+", line):
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            if not in_ol:
                html_lines.append("<ol>")
                in_ol = True
            item = re.sub(r"^\d+\.\s+", "", escaped)
            html_lines.append(f"<li>{item}</li>")
        elif line.startswith("- ") or line.startswith("• "):
            if in_ol:
                html_lines.append("</ol>")
                in_ol = False
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            item = escaped[2:].strip()
            html_lines.append(f"<li>{item}</li>")
        else:
            close_lists()
            html_lines.append(f"<p>{escaped}</p>")

    close_lists()
    return "\n".join(html_lines)


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


def get_first_value(df, possible_cols):
    for col in possible_cols:
        if col and col in df.columns:
            vals = df[col].dropna().astype(str).str.strip()
            vals = vals[vals.str.lower() != "nan"]
            if not vals.empty:
                return vals.iloc[0]
    return "Not found"


def build_boat_profile(sales_context, line_context, invoice_context, upgrade_opportunities, service_message):
    original_so_col = get_first_matching_col(sales_orders, ["original so", "orig so", "original sales order", "original order"])
    sales_order_col = get_first_matching_col(sales_orders, ["sales order", "so number", "order number", "so"])

    boat_name = get_first_value(sales_context, ["Hull Project", "Order Name", "Boat Name", "Vessel Name", "Hull Number"])
    original_so = get_first_value(sales_context, [original_so_col] if original_so_col else [])

    if original_so == "Not found":
        original_so = get_first_value(sales_context, [sales_order_col] if sales_order_col else [])

    service_count = 1 if "recommended" in str(service_message).lower() else 0

    return {
        "Boat / Hull": boat_name,
        "Original Sales Order": original_so,
        "Related Sales Orders": len(sales_context),
        "Line Items": len(line_context),
        "Invoice Records": len(invoice_context),
        "Service Signals": service_count,
        "Upgrade Opportunities": len(upgrade_opportunities),
    }


def render_boat_profile(profile):
    boat = safe_text(profile.get("Boat / Hull", "Not found"))
    original_so = safe_text(profile.get("Original Sales Order", "Not found"))
    related_sos = safe_text(profile.get("Related Sales Orders", 0))
    upgrade_opps = safe_text(profile.get("Upgrade Opportunities", 0))
    line_items_count = safe_text(profile.get("Line Items", 0))
    invoices_count = safe_text(profile.get("Invoice Records", 0))
    service_signals = safe_text(profile.get("Service Signals", 0))
    st.markdown(
        f"""
<div class="profile-grid">
  <div class="profile-tile"><div class="profile-label">Boat / Hull</div><div class="profile-value">{boat}</div></div>
  <div class="profile-tile"><div class="profile-label">Original SO</div><div class="profile-value">{original_so}</div></div>
  <div class="profile-tile"><div class="profile-label">Related SOs</div><div class="profile-value">{related_sos}</div></div>
  <div class="profile-tile"><div class="profile-label">Upgrade Opps</div><div class="profile-value">{upgrade_opps}</div></div>
</div>
<div class="profile-grid">
  <div class="profile-tile"><div class="profile-label">Line Items</div><div class="profile-value">{line_items_count}</div></div>
  <div class="profile-tile"><div class="profile-label">Invoices</div><div class="profile-value">{invoices_count}</div></div>
  <div class="profile-tile"><div class="profile-label">Service Signals</div><div class="profile-value">{service_signals}</div></div>
  <div class="profile-tile"><div class="profile-label">Status</div><div class="profile-value">Ready</div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def build_vessel_timeline(sales_context, invoice_context, seal_rows, upgrade_opportunities):
    events = []

    sales_order_col = get_first_matching_col(sales_context, ["sales order", "so number", "order number", "so"])
    original_so_col = get_first_matching_col(sales_context, ["original so", "orig so", "original sales order", "original order"])
    type_col = get_first_matching_col(sales_context, ["type of sale", "sale type", "type"])

    if sales_order_col and not sales_context.empty:
        for _, row in sales_context.head(12).iterrows():
            so = normalize_so(row.get(sales_order_col, ""))
            orig = normalize_so(row.get(original_so_col, "")) if original_so_col else ""
            sale_type = str(row.get(type_col, "Sales order")) if type_col else "Sales order"
            label = "Original sale" if so and orig and so == orig else "Related sales order"
            events.append({"sort": 1, "date": f"SO {so}", "title": label, "copy": sale_type})

    date_cols_inv = find_cols(invoice_context, ["ship date", "shipdate", "invoice date", "date"])
    so_cols_inv = find_cols(invoice_context, ["sales order", "so number", "order number", "so"])
    if date_cols_inv and not invoice_context.empty:
        date_col = date_cols_inv[0]
        so_col = so_cols_inv[0] if so_cols_inv else None
        temp = invoice_context.copy()
        temp["_timeline_date"] = pd.to_datetime(temp[date_col], errors="coerce")
        temp = temp.dropna(subset=["_timeline_date"]).sort_values("_timeline_date").tail(8)
        for _, row in temp.iterrows():
            so = normalize_so(row.get(so_col, "")) if so_col else ""
            events.append({
                "sort": row["_timeline_date"],
                "date": str(row["_timeline_date"].date()),
                "title": "Invoice / shipment",
                "copy": f"Shipment or invoice record linked to SO {so}" if so else "Shipment or invoice record",
            })

    if seal_rows is not None and not seal_rows.empty:
        events.append({
            "sort": 9998,
            "date": "Service",
            "title": "Actuator seal kit history found",
            "copy": f"{len(seal_rows)} matching seal kit line item(s) found in related history.",
        })

    for opp in upgrade_opportunities:
        events.append({
            "sort": 9999,
            "date": "Opportunity",
            "title": opp.get("Upgrade", "Upgrade Opportunity"),
            "copy": "Eligible based on current boat history and upgrade rules.",
        })

    def sort_key(event):
        v = event.get("sort", 0)
        if isinstance(v, pd.Timestamp):
            return v.value
        try:
            return int(v)
        except Exception:
            return 0

    return sorted(events, key=sort_key)[:18]


def render_vessel_timeline(events):
    if not events:
        st.info("No timeline events found for this search.")
        return

    items = []
    for event in events:
        date = safe_text(event.get("date", ""))
        title = safe_text(event.get("title", ""))
        copy = safe_text(event.get("copy", ""))
        items.append(
            f"""
<div class="timeline-item">
  <div class="timeline-date">{date}</div>
  <div class="timeline-title">{title}</div>
  <div class="timeline-copy">{copy}</div>
</div>
"""
        )

    st.markdown(
        f"""
<div class="timeline-box">
{''.join(items)}
</div>
""",
        unsafe_allow_html=True,
    )


def evaluate_upgrade_for_part_history(row, part_history):
    upgrade_name = str(row.iloc[0]).strip()
    if not upgrade_name or upgrade_name.lower() == "nan":
        return None

    must_not_have = normalize_part(row.iloc[1]) if len(row) > 1 else ""
    qualifying_parts = [normalize_part(v) for v in row.iloc[2:9] if normalize_part(v)]

    has_blocking_part = must_not_have in part_history if must_not_have else False
    matching_parts = [p for p in qualifying_parts if p in part_history]
    has_qualifying_part = bool(matching_parts) if qualifying_parts else True

    if (not has_blocking_part) and has_qualifying_part:
        return {
            "Upgrade": upgrade_name,
            "Missing Installed Part": must_not_have,
            "Matching Existing Parts": ", ".join(matching_parts),
            "Literature": get_upgrade_links(row),
        }
    return None


@st.cache_data(show_spinner=False)
def build_customer_opportunity_dashboard(selected_upgrade="All Upgrade Types"):
    original_so_col = get_first_matching_col(sales_orders, ["original so", "orig so", "original sales order", "original order"])
    sales_order_col = get_first_matching_col(sales_orders, ["sales order", "so number", "order number", "so"])
    line_so_col = get_first_matching_col(line_items, ["sales order", "so number", "order number", "so"])
    part_col = get_part_number_col(line_items)

    if not original_so_col or not sales_order_col or not line_so_col or not part_col:
        return pd.DataFrame()

    rows = []
    temp_sales = sales_orders.dropna(subset=[original_so_col]).copy()
    temp_sales["_orig_norm"] = temp_sales[original_so_col].map(normalize_so)

    for original_so, sales_group in temp_sales.groupby("_orig_norm"):
        if not original_so or str(original_so).lower() == "nan":
            continue

        related_sos = set(sales_group[sales_order_col].dropna().map(normalize_so).tolist())
        if not related_sos:
            continue

        related_lines = line_items[line_items[line_so_col].map(normalize_so).isin(related_sos)]
        if related_lines.empty:
            continue

        part_history = set(related_lines[part_col].dropna().map(normalize_part).tolist())
        if not part_history:
            continue

        boat_name = get_first_value(sales_group, ["Hull Project", "Order Name", "Boat Name", "Vessel Name", "Hull Number"])

        for _, upgrade_row in upgrades.iterrows():
            result = evaluate_upgrade_for_part_history(upgrade_row, part_history)
            if not result:
                continue
            if selected_upgrade != "All Upgrade Types" and result["Upgrade"] != selected_upgrade:
                continue

            lit_names = ", ".join([name for name, url in result["Literature"]])
            rows.append({
                "Original Sales Order": original_so,
                "Boat / Hull": boat_name,
                "Upgrade Type": result["Upgrade"],
                "Related Sales Orders": len(related_sos),
                "Matching Existing Parts": result["Matching Existing Parts"],
                "Literature": lit_names,
            })

    return pd.DataFrame(rows).drop_duplicates()





def run_sales_agent(agent_request, data):
    """Use the latest analysis context to produce next-step sales guidance."""
    upgrade_lines = []
    for opp in data.get("upgrade_opportunities", []):
        literature = ", ".join([name for name, url in opp.get("Literature", [])])
        upgrade_lines.append(
            f"- {opp.get('Upgrade','Upgrade')}; literature: {literature or 'none listed'}"
        )

    profile = data.get("boat_profile", {})
    context = f"""
BOAT PROFILE:
{profile}

SERVICE SIGNAL:
{data.get('service_message', 'No service signal available')}

UPGRADE OPPORTUNITIES:
{chr(10).join(upgrade_lines) if upgrade_lines else 'No applicable upgrades found.'}

AI SUMMARY:
{data.get('ai_answer', '')}

USER REQUEST TO AGENT:
{agent_request}
"""

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are an ABT-TRAC internal sales agent. Your job is to turn vessel history,
service signals, and upgrade eligibility into a practical salesperson action plan.
Use only the provided context. Do not invent prices, customer commitments, or facts.
Organize the answer into:
1. Priority
2. Recommended Next Action
3. Talking Points
4. Evidence From Records
5. Follow-Up Email Draft
Keep it concise and useful for a marine sales manager.
""",
            },
            {"role": "user", "content": context},
        ],
        temperature=0.25,
    )
    return response.choices[0].message.content

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------

if "latest_analysis" not in st.session_state:
    st.session_state.latest_analysis = None

if "active_panel" not in st.session_state:
    st.session_state.active_panel = "summary"

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

nav1, nav2, nav3, nav4 = st.columns(4)
with nav1:
    if st.button("⚓ Vessel History", key="btn_vessel_history"):
        st.session_state.active_panel = "vessel"
    st.markdown('<div class="nav-caption">Sales orders, line items, invoices, and related vessel records.</div>', unsafe_allow_html=True)
with nav2:
    if st.button("🔧 Service Signals", key="btn_service_signals"):
        st.session_state.active_panel = "service"
    st.markdown('<div class="nav-caption">Actuator seal kit timing and service follow-up opportunities.</div>', unsafe_allow_html=True)
with nav3:
    if st.button("↗ Upgrade Paths", key="btn_upgrade_paths"):
        st.session_state.active_panel = "upgrades"
    st.markdown('<div class="nav-caption">Applicable upgrades and supporting literature links.</div>', unsafe_allow_html=True)
with nav4:
    if st.button("AI Sales Summary", key="btn_sales_summary"):
        st.session_state.active_panel = "summary"
    st.markdown('<div class="nav-caption">Concise AI-generated summary for sales follow-up.</div>', unsafe_allow_html=True)

section_header("Customer Opportunity Dashboard", "Find Eligible Original Sales Orders by Upgrade Type")
st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
upgrade_names = [str(x).strip() for x in upgrades.iloc[:, 0].dropna().tolist() if str(x).strip()]
upgrade_filter = st.selectbox("Upgrade type", ["All Upgrade Types"] + upgrade_names, index=0)
scan_clicked = st.button("Scan Customer Base for Eligible Upgrade Opportunities", key="scan_customer_base")

if scan_clicked or "opportunity_dashboard" in st.session_state:
    if scan_clicked:
        with st.spinner("Scanning original sales orders and line item history..."):
            st.session_state.opportunity_dashboard = build_customer_opportunity_dashboard(upgrade_filter)
            st.session_state.opportunity_dashboard_filter = upgrade_filter

    dashboard_df = st.session_state.get("opportunity_dashboard", pd.DataFrame())
    dashboard_filter = st.session_state.get("opportunity_dashboard_filter", upgrade_filter)
    st.caption(f"Showing eligible original sales orders for: {dashboard_filter}")

    if dashboard_df.empty:
        st.info("No eligible opportunities found for this upgrade type.")
    else:
        d1, d2, d3 = st.columns(3)
        with d1:
            metric_card(len(dashboard_df), "Eligible Records")
        with d2:
            metric_card(dashboard_df["Original Sales Order"].nunique(), "Original SOs")
        with d3:
            metric_card(dashboard_df["Upgrade Type"].nunique(), "Upgrade Types")
        st.dataframe(dashboard_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Opportunity List as CSV",
            dashboard_df.to_csv(index=False),
            file_name="abt_trac_upgrade_opportunities.csv",
            mime="text/csv",
        )

st.markdown('</div>', unsafe_allow_html=True)

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

            boat_profile = build_boat_profile(
                sales_context,
                line_context,
                invoice_context,
                upgrade_opportunities,
                service_message,
            )
            vessel_timeline = build_vessel_timeline(
                sales_context,
                invoice_context,
                seal_rows,
                upgrade_opportunities,
            )

            st.session_state.latest_analysis = {
                "ai_answer": ai_answer,
                "extracted_terms": extracted_terms,
                "sales_context": sales_context,
                "line_context": line_context,
                "invoice_context": invoice_context,
                "service_message": service_message,
                "seal_rows": seal_rows,
                "upgrade_opportunities": upgrade_opportunities,
                "boat_profile": boat_profile,
                "vessel_timeline": vessel_timeline,
            }
            st.session_state.active_panel = "summary"


def render_upgrade_cards(upgrade_opportunities):
    if upgrade_opportunities:
        for opp in upgrade_opportunities:
            st.markdown(
                f"""
<div class="upgrade-card">
  <div class="upgrade-title">{safe_text(opp['Upgrade'])}</div>
  <div class="small-muted">Clickable supporting literature</div>
""",
                unsafe_allow_html=True,
            )

            if opp.get("Matching Existing Parts"):
                st.caption(f"Relevant existing parts found: {opp['Matching Existing Parts']}")

            if opp["Literature"]:
                cols = st.columns(min(len(opp["Literature"]), 3))
                for i, (name, url) in enumerate(opp["Literature"]):
                    with cols[i % len(cols)]:
                        st.link_button(name, url, use_container_width=True)
            else:
                st.caption("No literature file listed.")

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No applicable upgrade opportunities found.")


def render_latest_analysis():
    data = st.session_state.latest_analysis

    if not data:
        st.markdown(
            '<div class="panel-note">Run a Marine AI Analysis, then use the tabs to review AI Summary, Vessel History, Service Signals, Upgrade Paths, Supporting Records, and the AI Agent.</div>',
            unsafe_allow_html=True,
        )
        return

    section_header("Analysis Complete", "Boat Profile")
    render_boat_profile(data.get("boat_profile", {}))

    section_header("Analysis Complete", "Marine AI Workspace")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card(len(data["sales_context"]), "Sales Orders")
    with m2:
        metric_card(len(data["line_context"]), "Line Items")
    with m3:
        metric_card(len(data["invoice_context"]), "Invoice Records")
    with m4:
        metric_card(len(data["upgrade_opportunities"]), "Upgrade Opportunities")

    tab_summary, tab_vessel, tab_service, tab_upgrades, tab_records, tab_agent = st.tabs([
        "AI Summary",
        "⚓ Vessel History",
        "🔧 Service Signals",
        "↗ Upgrade Paths",
        "Supporting Records",
        "AI Agent",
    ])

    with tab_summary:
        section_header("Sales Summary", "AI Recommendation")
        st.markdown(
            f"""
<div class="ai-answer-html">
{simple_markdown_to_html(data["ai_answer"])}
</div>
""",
            unsafe_allow_html=True,
        )

    with tab_vessel:
        section_header("Vessel History", "Vessel Timeline")
        render_vessel_timeline(data.get("vessel_timeline", []))

    with tab_service:
        section_header("Service Signals", "Recommended Service")
        st.markdown(
            f"""
<div class="service-card">
  <div class="upgrade-title">Actuator Seal Kit Review</div>
  <div>{safe_text(data['service_message'])}</div>
</div>
""",
            unsafe_allow_html=True,
        )
        with st.expander("Actuator seal kit rows", expanded=True):
            st.dataframe(data["seal_rows"], use_container_width=True, hide_index=True)

    with tab_upgrades:
        section_header("Upgrade Paths", "Applicable Upgrades")
        render_upgrade_cards(data["upgrade_opportunities"])

    with tab_records:
        section_header("Supporting Records", "Evidence Used by the AI")
        st.markdown(
            "".join([f'<span class="pill">{safe_text(term)}</span>' for term in data["extracted_terms"]])
            if data["extracted_terms"] else '<span class="pill">No search terms</span>',
            unsafe_allow_html=True,
        )
        with st.expander("Sales order records", expanded=True):
            st.dataframe(data["sales_context"], use_container_width=True, hide_index=True)
        with st.expander("Line item records", expanded=False):
            st.dataframe(data["line_context"], use_container_width=True, hide_index=True)
        with st.expander("Invoice / ship date records", expanded=False):
            st.dataframe(data["invoice_context"], use_container_width=True, hide_index=True)

    with tab_agent:
        section_header("AI Agent", "Sales Follow-Up Planner")
        st.markdown(
            '<div class="agent-card"><b>Ask the agent for a next-step sales plan, call notes, or follow-up email based on the current vessel analysis.</b></div>',
            unsafe_allow_html=True,
        )
        agent_request = st.text_area(
            "Agent request",
            value="Create a concise sales follow-up plan for this vessel.",
            height=100,
            key="agent_request_box",
        )
        if st.button("Run AI Agent", key="run_ai_agent_button"):
            with st.spinner("Building sales action plan..."):
                agent_answer = run_sales_agent(agent_request, data)
            st.markdown(
                f"""
<div class="ai-answer-html">
{simple_markdown_to_html(agent_answer)}
</div>
""",
                unsafe_allow_html=True,
            )


render_latest_analysis()

st.markdown(
    '<div class="footer-note">AI answers are based on uploaded sales order, line item, invoice, actuator seal kit, and upgrade opportunity records.</div>',
    unsafe_allow_html=True,
)
