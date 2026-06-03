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
    --abt-ink: #0A1A2F;
    --abt-muted: #5D6B7A;
    --abt-card: #FFFFFF;
    --abt-border: rgba(16,43,73,0.14);
}}

[data-testid="stAppViewContainer"] {{
    background: #F5F7FA;
}}

[data-testid="stHeader"] {{
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(8px);
}}

.block-container {{
    padding-top: 1.0rem;
    padding-bottom: 2.5rem;
    max-width: 1220px;
}}

h1, h2, h3, h4, p, li, div {{
    color: var(--abt-ink);
}}

.hero-shell {{
    position: relative;
    overflow: hidden;
    min-height: 275px;
    border-radius: 30px;
    padding: 32px 34px;
    margin-bottom: 18px;
    background:
        linear-gradient(90deg, rgba(7,26,47,0.92) 0%, rgba(16,43,73,0.82) 42%, rgba(16,43,73,0.25) 100%),
        url("{BACKGROUND_IMAGE_URL}");
    background-size: cover;
    background-position: center;
    box-shadow: 0 24px 80px rgba(7,28,49,0.22);
    border: 1px solid rgba(255,255,255,0.45);
}}

.hero-eyebrow {{
    color: #D8EAF5;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-size: 0.78rem;
    margin-bottom: 10px;
}}

.hero-title {{
    color: #FFFFFF;
    font-size: 3.25rem;
    line-height: 0.98;
    font-weight: 950;
    margin: 0;
    text-shadow: 0 3px 16px rgba(0,0,0,0.35);
}}

.hero-subtitle {{
    color: rgba(255,255,255,0.94);
    font-size: 1.13rem;
    line-height: 1.55;
    max-width: 720px;
    margin-top: 14px;
    font-weight: 550;
}}

.hero-badge-row {{
    margin-top: 20px;
}}
.hero-badge {{
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.22);
    color: #FFFFFF;
    border-radius: 999px;
    padding: 7px 12px;
    margin: 0 8px 8px 0;
    font-size: 0.86rem;
    font-weight: 800;
}}

.logo-card {{
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(16,43,73,0.14);
    border-radius: 22px;
    padding: 16px;
    box-shadow: 0 12px 36px rgba(7,28,49,0.12);
}}

.search-card, .dashboard-card, .answer-card, .timeline-box, .service-card, .upgrade-card, .profile-tile, .metric-card, .panel-note, div[data-testid="stExpander"] {{
    background: #FFFFFF !important;
    border: 1px solid var(--abt-border) !important;
    border-radius: 22px !important;
    box-shadow: 0 14px 42px rgba(7,28,49,0.10) !important;
}}

.search-card {{
    padding: 22px 24px 24px 24px;
    margin: 12px 0 16px 0;
}}

.search-label {{
    color: var(--abt-navy);
    font-weight: 950;
    font-size: 1.35rem;
    margin-bottom: 8px;
}}

.search-help {{
    color: #FFFFFF !important;
    background: linear-gradient(135deg, var(--abt-blue), var(--abt-navy));
    font-size: 1.02rem;
    font-weight: 850;
    margin-bottom: 16px;
    padding: 11px 15px;
    border-radius: 14px;
}}
.search-help, .search-help *, .search-help b {{
    color: #FFFFFF !important;
}}

.stTextArea textarea {{
    background-color: #FFFFFF !important;
    border: 1.5px solid rgba(13,79,124,0.26) !important;
    border-radius: 16px !important;
    color: var(--abt-ink) !important;
    font-size: 1.02rem !important;
    line-height: 1.45 !important;
}}

.stButton button {{
    width: 100%;
    background: linear-gradient(135deg, var(--abt-blue), var(--abt-navy)) !important;
    color: #FFFFFF !important;
    border-radius: 15px !important;
    border: 0 !important;
    padding: 0.78rem 1.15rem !important;
    font-weight: 900 !important;
    box-shadow: 0 10px 26px rgba(13,79,124,0.22);
}}
.stButton button *, .stButton button p, .stButton button span {{
    color: #FFFFFF !important;
}}

.section-kicker {{
    color: var(--abt-blue);
    text-transform: uppercase;
    letter-spacing: 0.13em;
    font-size: 0.78rem;
    font-weight: 950;
    margin-top: 22px;
}}
.section-title {{
    color: var(--abt-navy);
    font-size: 1.50rem;
    font-weight: 950;
    margin-bottom: 10px;
}}

.metric-card {{
    padding: 17px 18px;
    border-left: 5px solid var(--abt-gold) !important;
}}
.metric-value {{
    font-size: 1.9rem;
    line-height: 1;
    font-weight: 950;
    color: var(--abt-navy);
}}
.metric-label {{
    margin-top: 6px;
    color: var(--abt-muted);
    font-weight: 850;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

.profile-grid {{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 12px;
}}
.profile-tile {{
    padding: 15px 16px;
}}
.profile-label {{
    color: var(--abt-muted);
    font-size: 0.76rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}}
.profile-value {{
    color: var(--abt-navy);
    font-size: 1.12rem;
    font-weight: 950;
    margin-top: 4px;
    line-height: 1.2;
}}

.ai-answer-html {{
    background: #FFFFFF;
    border: 1px solid var(--abt-border);
    border-top: 5px solid var(--abt-blue);
    border-radius: 22px;
    box-shadow: 0 14px 42px rgba(7,28,49,0.10);
    padding: 24px 28px;
}}
.ai-answer-html, .ai-answer-html * {{
    color: var(--abt-ink) !important;
}}
.ai-answer-html h1, .ai-answer-html h2, .ai-answer-html h3, .ai-answer-html strong {{
    color: var(--abt-navy) !important;
}}

.timeline-box {{
    padding: 16px 18px;
    margin-bottom: 10px;
}}
.timeline-item {{
    border-left: 4px solid var(--abt-blue);
    padding: 7px 0 12px 14px;
    margin-left: 5px;
}}
.timeline-date {{
    color: var(--abt-blue);
    font-weight: 950;
    font-size: 0.9rem;
}}
.timeline-title {{
    color: var(--abt-navy);
    font-weight: 950;
}}
.timeline-copy {{
    color: var(--abt-muted);
    font-size: 0.9rem;
}}

.service-card, .upgrade-card, .dashboard-card, .panel-note {{
    padding: 18px 20px;
    margin-bottom: 12px;
}}
.upgrade-title {{
    color: var(--abt-navy);
    font-size: 1.12rem;
    font-weight: 950;
    margin-bottom: 8px;
}}
.small-muted {{
    color: var(--abt-muted);
    font-size: 0.88rem;
}}

.pill {{
    display: inline-block;
    background: rgba(13,79,124,0.09);
    color: var(--abt-blue);
    border: 1px solid rgba(13,79,124,0.15);
    border-radius: 999px;
    padding: 6px 10px;
    margin: 4px 5px 2px 0;
    font-size: 0.82rem;
    font-weight: 850;
}}

.footer-note {{
    color: var(--abt-muted);
    background: #FFFFFF;
    border: 1px solid var(--abt-border);
    border-radius: 14px;
    font-size: 0.86rem;
    text-align: center;
    padding: 12px;
    margin-top: 16px;
}}

/* Selectbox labels are dark now because the page is clean white */
div[data-testid="stSelectbox"] label,
div[data-testid="stSelectbox"] label *,
.stSelectbox label,
.stSelectbox label * {{
    color: var(--abt-navy) !important;
    font-weight: 950 !important;
    font-size: 1rem !important;
}}
.stSelectbox > div > div {{
    background-color: #FFFFFF !important;
    color: var(--abt-ink) !important;
}}

button[data-baseweb="tab"] {{
    background: #FFFFFF !important;
    border: 1px solid rgba(16,43,73,0.18) !important;
    border-radius: 14px !important;
    margin-right: 8px !important;
    padding: 10px 14px !important;
    color: var(--abt-navy) !important;
    font-weight: 950 !important;
    box-shadow: 0 8px 22px rgba(7,28,49,0.08);
}}
button[data-baseweb="tab"] * {{
    color: var(--abt-navy) !important;
    font-weight: 950 !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    background: linear-gradient(135deg, var(--abt-blue), var(--abt-navy)) !important;
    color: #FFFFFF !important;
    border-color: transparent !important;
}}
button[data-baseweb="tab"][aria-selected="true"] * {{
    color: #FFFFFF !important;
}}

[data-testid="stDataFrame"] {{
    border-radius: 16px;
    overflow: hidden;
    background: #FFFFFF !important;
}}

.nav-caption, .capability-card:empty, .dashboard-card:empty, .search-card:empty, .record-card:empty {{
    display: none !important;
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


DEMO_HIDDEN_COLUMN_NAMES = {"order name"}
DEMO_HIDDEN_COLUMN_KEYWORDS = ["contact", "email", "phone", "person"]


def is_demo_hidden_column(col):
    """Hide columns that can expose individual people in demo outputs."""
    col_text = str(col).strip().lower()
    if col_text in DEMO_HIDDEN_COLUMN_NAMES:
        return True
    return any(keyword in col_text for keyword in DEMO_HIDDEN_COLUMN_KEYWORDS)


def demo_safe_df(df):
    """Return a copy of a dataframe with sensitive demo columns removed."""
    if df is None or getattr(df, "empty", True):
        return pd.DataFrame() if df is None else df.copy()

    safe = df.copy()
    drop_cols = [col for col in safe.columns if is_demo_hidden_column(col)]
    if drop_cols:
        safe = safe.drop(columns=drop_cols, errors="ignore")
    return safe.drop(columns=["_search_text"], errors="ignore")


def compact_table_text(df, max_rows=20):
    if df.empty:
        return "No matching records found."
    return demo_safe_df(df).head(max_rows).to_string(index=False)


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


def looks_like_hull_or_project(value):
    text = str(value).strip().upper()
    if not text or text == "NAN":
        return True
    if re.fullmatch(r"[A-Z]?\d{2,3}[- ]?\d{1,4}", text):
        return True
    if re.search(r"\b\d{2,3}[- ]\d{1,4}\b", text):
        return True
    if re.fullmatch(r"\d+", text):
        return True
    if text.startswith("FLEMING ") and re.search(r"\d", text):
        return True
    if text.startswith("HULL") or "HULL" in text:
        return True
    return False


def get_known_vessel_names(sales_context):
    """Demo-safe vessel labels: pull ONLY from Hull Project / column C.

    This intentionally does NOT read Order Name / column D because that field can
    contain customer, contact, company, or personal names. Unlike the older
    filter, this keeps Hull Project values even when they contain model numbers
    like HAMPTON E 700-27, because those are safe vessel/project labels.
    """
    hull_col = get_exact_col(sales_context, "Hull Project")
    if not hull_col or sales_context.empty:
        return "No vessel names found"

    names = []
    seen = set()
    for value in sales_context[hull_col].dropna().astype(str).str.strip():
        if not value or value.lower() == "nan":
            continue
        key = value.upper()
        if key not in seen:
            names.append(value)
            seen.add(key)

    if not names:
        return "No vessel names found"
    return ", ".join(names[:4])

def build_boat_profile(sales_context, line_context, invoice_context, upgrade_opportunities, service_message):
    original_so_col = get_first_matching_col(sales_orders, ["original so", "orig so", "original sales order", "original order"])
    sales_order_col = get_first_matching_col(sales_orders, ["sales order", "so number", "order number", "so"])

    # Demo-safe: use only Hull Project for the visible boat/hull label.
    # Do not fall back to Order Name because it may contain customer/person names.
    boat_name = get_first_value(sales_context, ["Hull Project"])
    original_so = get_first_value(sales_context, [original_so_col] if original_so_col else [])

    if original_so == "Not found":
        original_so = get_first_value(sales_context, [sales_order_col] if sales_order_col else [])

    service_count = 1 if "recommended" in str(service_message).lower() else 0
    upgrade_count = len(upgrade_opportunities)
    if service_count > 0 or upgrade_count >= 2:
        opportunity_level = "High"
    elif upgrade_count == 1:
        opportunity_level = "Medium"
    else:
        opportunity_level = "Low"

    return {
        "Boat / Hull": boat_name,
        "Original Sales Order": original_so,
        "Related Sales Orders": len(sales_context),
        "Line Items": len(line_context),
        "Known Vessel Names": get_known_vessel_names(sales_context),
        "Service Signals": service_count,
        "Upgrade Opportunities": upgrade_count,
        "Opportunity Level": opportunity_level,
    }


def render_boat_profile(profile):
    boat = safe_text(profile.get("Boat / Hull", "Not found"))
    original_so = safe_text(profile.get("Original Sales Order", "Not found"))
    related_sos = safe_text(profile.get("Related Sales Orders", 0))
    upgrade_opps = safe_text(profile.get("Upgrade Opportunities", 0))
    line_items_count = safe_text(profile.get("Line Items", 0))
    known_names = safe_text(profile.get("Known Vessel Names", "No vessel names found"))
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
  <div class="profile-tile"><div class="profile-label">Known Vessel Names</div><div class="profile-value">{known_names}</div></div>
  <div class="profile-tile"><div class="profile-label">Service Signals</div><div class="profile-value">{service_signals}</div></div>
  <div class="profile-tile"><div class="profile-label">Opportunity Level</div><div class="profile-value">{safe_text(profile.get("Opportunity Level", "Unknown"))}</div></div>
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


def render_vessel_timeline(events, line_context=None):
    if not events:
        st.info("No timeline events found for this search.")
        return

    line_context = line_context if line_context is not None else pd.DataFrame()
    line_so_col = get_first_matching_col(line_context, ["sales order", "so number", "order number", "so"]) if not line_context.empty else None
    part_col = get_part_number_col(line_context) if not line_context.empty else None
    desc_col = get_first_matching_col(line_context, ["description", "item description", "part description", "desc"]) if not line_context.empty else None
    qty_col = get_first_matching_col(line_context, ["qty", "quantity"]) if not line_context.empty else None

    st.markdown('<div class="timeline-box">', unsafe_allow_html=True)

    for event in events:
        so_raw = str(event.get("date", "")).replace("SO", "").strip()
        title = safe_text(event.get("title", ""))
        copy = safe_text(event.get("copy", ""))
        label = f"SO {safe_text(so_raw)} — {title}" if so_raw else title

        with st.expander(label, expanded=False):
            st.markdown(f"**{title}**")
            if copy:
                st.write(copy)

            if line_so_col and part_col and so_raw:
                so_lines = line_context[line_context[line_so_col].map(normalize_so) == so_raw].copy()

                if so_lines.empty:
                    st.caption("No line item detail found for this sales order.")
                else:
                    display_cols = []
                    for col in [part_col, desc_col, qty_col]:
                        if col and col in so_lines.columns and col not in display_cols:
                            display_cols.append(col)

                    if display_cols:
                        st.dataframe(
                            so_lines[display_cols].drop_duplicates().head(50),
                            use_container_width=True,
                            hide_index=True,
                        )
                    else:
                        st.dataframe(so_lines.head(50), use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)


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

st.markdown(
    """
<div class="hero-shell">
  <div class="hero-eyebrow">Internal Marine Sales Intelligence</div>
  <h1 class="hero-title">ABT-TRAC AI</h1>
  <div class="hero-subtitle">
    AI-powered marine service, upgrade, AIS, and sales intelligence for ABT-TRAC / Inov8v Marine.
  </div>
  <div class="hero-badge-row">
    <span class="hero-badge">Vessel History</span>
    <span class="hero-badge">Service Signals</span>
    <span class="hero-badge">Upgrade Paths</span>
    <span class="hero-badge">AI Sales Agent</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

logo_a, logo_b, logo_c = st.columns([1.4, 1, 5])
with logo_a:
    try:
        st.image(Image.open("ABT TRAC Logo.jpg"), width=220)
    except Exception:
        st.markdown("### ABT TRAC")
with logo_b:
    try:
        st.image(Image.open("Innov8v Marine Logo.png"), width=120)
    except Exception:
        st.caption("Inov8v Marine")

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


# Fleet-wide dashboard is intentionally placed below the individual vessel analysis.
# It becomes more useful after the demo audience sees one boat analysis first.

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



def get_agent_priority(data):
    service_message = str(data.get("service_message", "")).lower()
    upgrade_count = len(data.get("upgrade_opportunities", []))
    service_signal = "recommended" in service_message or "follow-up" in service_message

    if service_signal and upgrade_count >= 1:
        return "High", "Service follow-up and upgrade opportunity both identified."
    if upgrade_count >= 2:
        return "High", "Multiple upgrade opportunities identified."
    if service_signal or upgrade_count == 1:
        return "Medium", "One clear follow-up opportunity identified."
    return "Low", "No immediate service or upgrade opportunity identified from the current records."


def build_agent_evidence(data):
    evidence = []
    service_message = str(data.get("service_message", ""))
    if service_message:
        evidence.append(f"Service signal: {service_message}")

    upgrades_found = data.get("upgrade_opportunities", [])
    if upgrades_found:
        for opp in upgrades_found:
            upgrade_name = opp.get("Upgrade", "Upgrade opportunity")
            matching_parts = opp.get("Matching Existing Parts", "")
            if matching_parts:
                evidence.append(f"{upgrade_name}: qualifying part history found: {matching_parts}")
            else:
                evidence.append(f"{upgrade_name}: applicable based on current upgrade rules.")
            lit = opp.get("Literature", [])
            if lit:
                evidence.append(f"{upgrade_name}: supporting literature available: {', '.join([name for name, url in lit])}")
    else:
        evidence.append("No applicable upgrade opportunities were found for this vessel search.")

    profile = data.get("boat_profile", {})
    evidence.append(f"Related sales orders reviewed: {profile.get('Related Sales Orders', len(data.get('sales_context', [])))}")
    evidence.append(f"Line items reviewed: {profile.get('Line Items', len(data.get('line_context', [])))}")
    return evidence


def build_next_best_actions(data):
    actions = []
    upgrades_found = data.get("upgrade_opportunities", [])
    service_message = str(data.get("service_message", ""))

    if "recommended" in service_message.lower() or "follow-up" in service_message.lower():
        actions.append("Ask the customer or dealer whether actuator seal kits have been serviced recently.")
        actions.append("Offer a preventive service review before the next operating season.")

    for opp in upgrades_found[:4]:
        upgrade_name = opp.get("Upgrade", "upgrade opportunity")
        actions.append(f"Send supporting literature for {upgrade_name}.")
        actions.append(f"Ask whether the vessel owner would like to review the benefits of {upgrade_name}.")

    if not actions:
        actions.append("Use this search as an account-history summary and ask whether there are current service issues or planned refit work.")

    actions.append("Document the follow-up in CRM or Cetec notes after customer contact.")
    return actions[:8]


def render_agent_bullets(items):
    if not items:
        st.info("No agent items generated.")
        return
    st.markdown("<div class='ai-answer-html'><ul>" + "".join([f"<li>{safe_text(item)}</li>" for item in items]) + "</ul></div>", unsafe_allow_html=True)


def build_agent_context(data, agent_task):
    return f"""
CURRENT BOAT PROFILE:
{data.get('boat_profile', {})}

OPPORTUNITY PRIORITY:
{get_agent_priority(data)}

NEXT BEST ACTIONS:
{build_next_best_actions(data)}

EVIDENCE:
{build_agent_evidence(data)}

SERVICE MESSAGE:
{data.get('service_message', '')}

UPGRADE OPPORTUNITIES:
{opportunities_to_text(data.get('upgrade_opportunities', []))}

AI SUMMARY:
{data.get('ai_answer', '')}

AGENT TASK:
{agent_task}
"""


def render_ai_agent_tab(data):
    section_header("AI Agent", "Sales Follow-Up Assistant")

    priority, reason = get_agent_priority(data)
    a1, a2, a3 = st.columns(3)
    with a1:
        metric_card(priority, "Opportunity Priority")
    with a2:
        metric_card(len(data.get("upgrade_opportunities", [])), "Upgrade Paths")
    with a3:
        service_flag = "Yes" if "recommended" in str(data.get("service_message", "")).lower() or "follow-up" in str(data.get("service_message", "")).lower() else "No"
        metric_card(service_flag, "Service Follow-Up")

    st.markdown(
        f"""
<div class="service-card">
  <div class="upgrade-title">Agent Priority Rationale</div>
  <div>{safe_text(reason)}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### Next Best Actions")
    render_agent_bullets(build_next_best_actions(data))

    st.markdown("### Why the Agent Recommends This")
    render_agent_bullets(build_agent_evidence(data))

    st.markdown("### Generate AI Sales Material")
    agent_task = st.selectbox(
        "Choose what the AI agent should create",
        [
            "Draft a concise customer follow-up email",
            "Create a sales call script",
            "Summarize the opportunity for a sales manager",
            "Write an upgrade explanation in plain English",
            "Create a prioritized follow-up plan",
        ],
        key="agent_task_selector",
    )

    custom_instruction = st.text_area(
        "Optional custom instruction",
        placeholder="Example: Make it shorter and focused on the Hydraulic to DC upgrade.",
        height=80,
        key="agent_custom_instruction",
    )

    if st.button("Run AI Sales Agent", key="run_ai_sales_agent"):
        with st.spinner("AI Agent is generating sales guidance..."):
            full_task = agent_task
            if custom_instruction.strip():
                full_task += "\nAdditional instruction: " + custom_instruction.strip()

            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            agent_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are an ABT-TRAC sales enablement AI agent.
Use only the provided records and recommendations.
Do not invent prices, dates, or installed equipment.
Be concise, practical, and sales-focused.
When drafting customer-facing material, keep it professional and avoid sounding too aggressive.
""",
                    },
                    {"role": "user", "content": build_agent_context(data, full_task)},
                ],
                temperature=0.25,
            )
            st.markdown(
                f"""
<div class="ai-answer-html">
{simple_markdown_to_html(agent_response.choices[0].message.content)}
</div>
""",
                unsafe_allow_html=True,
            )


def infer_ais_region_from_records(data):
    """Prototype AIS-style inference using existing records only; no live AIS API."""
    text_parts = []
    for key in ["sales_context", "line_context", "invoice_context"]:
        df = data.get(key)
        if df is not None and not getattr(df, "empty", True):
            text_parts.append(" ".join(df.fillna("").astype(str).head(30).values.flatten().tolist()).lower())
    text = " ".join(text_parts)

    region_rules = [
        ("Pacific Northwest", ["seattle", "everett", "washington", "wa", "anacortes", "bellingham", "tacoma", "port angeles"]),
        ("Florida / Southeast", ["florida", "fl", "fort lauderdale", "miami", "stuart", "west palm", "palm beach"]),
        ("California / West Coast", ["california", "ca", "san diego", "los angeles", "newport", "san francisco"]),
        ("Northeast", ["new york", "rhode island", "massachusetts", "maine", "connecticut", "boston"]),
        ("International", ["taiwan", "hong kong", "australia", "canada", "korea", "netherlands", "china", "japan"]),
    ]
    for region, keywords in region_rules:
        if any(k in text for k in keywords):
            return region
    return "Unknown / not enough location data"


def get_latest_activity_date(data):
    invoice_context = data.get("invoice_context", pd.DataFrame())
    sales_context = data.get("sales_context", pd.DataFrame())
    candidates = []

    for df in [invoice_context, sales_context]:
        if df is None or df.empty:
            continue
        date_cols = find_cols(df, ["ship date", "shipdate", "invoice date", "date", "created", "order date"])
        for col in date_cols:
            dates = pd.to_datetime(df[col], errors="coerce").dropna()
            if not dates.empty:
                candidates.append(dates.max())

    if not candidates:
        return None
    return max(candidates)


def build_ais_intelligence(data):
    """V1 AIS Intelligence: inferred from business records, ready for future live AIS API."""
    latest_date = get_latest_activity_date(data)
    today = pd.Timestamp(datetime.today().date())

    if latest_date is None:
        activity_status = "Unknown"
        days_since = "Not available"
        sales_timing = "Use account history first; AIS API integration would improve timing."
    else:
        days = int((today - pd.Timestamp(latest_date).normalize()).days)
        days_since = f"{days} days since latest record"
        if days <= 365:
            activity_status = "Recently Active"
            sales_timing = "Good candidate for near-term outreach. Recent account activity suggests the vessel/customer is still engaged."
        elif days <= 365 * 3:
            activity_status = "Moderately Active"
            sales_timing = "Good candidate for planned service or refit outreach."
        else:
            activity_status = "Dormant / Older Records"
            sales_timing = "Use a softer reactivation message and verify current vessel ownership before heavy sales follow-up."

    region = infer_ais_region_from_records(data)
    upgrades = data.get("upgrade_opportunities", [])
    service_message = str(data.get("service_message", ""))
    service_flag = "recommended" in service_message.lower() or "follow-up" in service_message.lower()

    if upgrades and service_flag:
        sales_angle = "Bundle upgrade review with preventive service discussion."
    elif upgrades:
        sales_angle = "Lead with upgrade education and supporting literature."
    elif service_flag:
        sales_angle = "Lead with maintenance/service reliability."
    else:
        sales_angle = "Use as relationship intelligence; ask about current operating plans."

    return {
        "Last Known Status": activity_status,
        "Estimated Operating Region": region,
        "Latest Record": str(latest_date.date()) if latest_date is not None else "Not found",
        "Activity Signal": days_since,
        "Likely Operating Pattern": "Prototype inference from sales/invoice history; live AIS would validate movement and location.",
        "Recommended Sales Timing": sales_timing,
        "Recommended Sales Angle": sales_angle,
        "Future AIS Upgrade": "Connect vessel name/MMSI to a live AIS provider to confirm last position, movement frequency, and operating region.",
    }


def render_ais_intelligence_tab(data):
    section_header("AIS Intelligence", "Prototype Vessel Activity Layer")
    ais = build_ais_intelligence(data)

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card(ais["Last Known Status"], "Activity Status")
    with c2:
        metric_card(ais["Estimated Operating Region"], "Estimated Region")
    with c3:
        metric_card(ais["Latest Record"], "Latest Record")

    st.markdown(
        f"""
<div class="service-card">
  <div class="upgrade-title">AIS Intelligence V1</div>
  <div><strong>Activity Signal:</strong> {safe_text(ais['Activity Signal'])}</div>
  <div><strong>Likely Operating Pattern:</strong> {safe_text(ais['Likely Operating Pattern'])}</div>
  <div><strong>Recommended Sales Timing:</strong> {safe_text(ais['Recommended Sales Timing'])}</div>
  <div><strong>Recommended Sales Angle:</strong> {safe_text(ais['Recommended Sales Angle'])}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### Future Live AIS Integration")
    st.markdown(
        f"""
<div class="ai-answer-html">
<ul>
  <li>{safe_text(ais['Future AIS Upgrade'])}</li>
  <li>Use vessel activity to prioritize outreach before service season or refit windows.</li>
  <li>Combine ERP history + upgrade rules + AIS movement to rank real-world sales opportunities.</li>
</ul>
</div>
""",
        unsafe_allow_html=True,
    )

def render_latest_analysis():
    data = st.session_state.latest_analysis

    if not data:
        st.markdown(
            '<div class="panel-note">Run a Marine AI Analysis to load the Boat Profile, AI Summary, Vessel History, Service Signals, and Upgrade Paths.</div>',
            unsafe_allow_html=True,
        )
        return

    section_header("Analysis Complete", "Boat Profile")
    render_boat_profile(data.get("boat_profile", {}))

    section_header("Analysis Complete", "Marine AI Dashboard")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card(len(data["sales_context"]), "Sales Orders")
    with m2:
        metric_card(len(data["line_context"]), "Line Items")
    with m3:
        metric_card(len(data["invoice_context"]), "Invoice Records")
    with m4:
        metric_card(len(data["upgrade_opportunities"]), "Upgrade Opportunities")

    summary_tab, vessel_tab, service_tab, upgrade_tab, ais_tab, records_tab, agent_tab = st.tabs([
        "AI Summary",
        "⚓ Vessel History",
        "🔧 Service Signals",
        "↗ Upgrade Paths",
        "AIS Intelligence",
        "Supporting Records",
        "AI Agent",
    ])

    with summary_tab:
        section_header("Sales Summary", "AI Recommendation")
        st.markdown(
            f"""
<div class="ai-answer-html">
{simple_markdown_to_html(data["ai_answer"])}
</div>
""",
            unsafe_allow_html=True,
        )

    with vessel_tab:
        section_header("Vessel History", "Vessel Timeline")
        render_vessel_timeline(data.get("vessel_timeline", []), data.get("line_context", pd.DataFrame()))

    with service_tab:
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

    with upgrade_tab:
        section_header("Upgrade Paths", "Applicable Upgrades")
        render_upgrade_cards(data["upgrade_opportunities"])

    with ais_tab:
        render_ais_intelligence_tab(data)

    with records_tab:
        section_header("Supporting Records", "Evidence Used by the AI")
        st.markdown(
            "".join([f'<span class="pill">{safe_text(term)}</span>' for term in data["extracted_terms"]])
            if data["extracted_terms"] else '<span class="pill">No search terms</span>',
            unsafe_allow_html=True,
        )
        with st.expander("Sales order records", expanded=True):
            st.dataframe(demo_safe_df(data["sales_context"]), use_container_width=True, hide_index=True)
        with st.expander("Line item records", expanded=False):
            st.dataframe(demo_safe_df(data["line_context"]), use_container_width=True, hide_index=True)
        with st.expander("Invoice / ship date records", expanded=False):
            st.dataframe(demo_safe_df(data["invoice_context"]), use_container_width=True, hide_index=True)

    with agent_tab:
        render_ai_agent_tab(data)


render_latest_analysis()

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
        st.dataframe(demo_safe_df(dashboard_df), use_container_width=True, hide_index=True)
        st.download_button(
            "Download Opportunity List as CSV",
            demo_safe_df(dashboard_df).to_csv(index=False),
            file_name="abt_trac_upgrade_opportunities.csv",
            mime="text/csv",
        )






st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="footer-note">AI answers are based on uploaded records. Demo view hides Order Name/contact-style fields from visible outputs.</div>',
    unsafe_allow_html=True,
)
