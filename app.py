import os
import warnings
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

st.set_page_config(
    page_title="HAVI Dashboard",
    layout="wide"
)

st.markdown("""
<style>
.js-plotly-plot .plotly .cursor-crosshair {
    cursor: default !important;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# File paths - keep these files in the same folder as app.py
# -----------------------------
HAVI_MASTER_FILE = "HAVI_2_dashboard_master_county_file_v2.csv"
CONTRIB_LONG_FILE = "HAVI_2_county_factor_contributions_long_v1.csv"
HAVI_LOGO_FILE = "HAVI.png"

# Counties without published CDC PLACES 2025 estimates (values are model-based estimates)
PLACES_IMPUTED_STATES = {"Kentucky", "Pennsylvania"}
PLACES_IMPUTED_FIPS = {"48301"}  # Loving County, Texas

# -----------------------------
# Custom Styling
# -----------------------------
st.markdown(
    """
    <style>
    :root { color-scheme: light dark; }
    .main, [data-testid="stAppViewContainer"] { background-color: #f8fafc; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .havi-title {
        font-size: 44px; font-weight: 800; color: #172554; margin-bottom: 0px;
    }
    .havi-subtitle {
        font-size: 18px; color: #475569; margin-bottom: 24px;
    }
    .section-subtitle {
        font-size: 17px; color: #475569; margin-top: -8px; margin-bottom: 18px;
    }
    .sidebar-label {
        font-size: 15px; font-weight: bold; color: #172554; margin-top: 10px; margin-bottom: 6px;
    }
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 12px;
        text-align: center;
        height: 132px;
        min-height: 132px;
        max-height: 132px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    .metric-label {
        color: #475569;
        font-size: clamp(13px, 1.05vw, 17px);
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 8px;
        overflow-wrap: anywhere;
    }
    .metric-value {
        font-weight: 800;
        line-height: 1.08;
        overflow-wrap: anywhere;
        word-break: normal;
    }
    .interpret-card {
        background: white; border-left: 6px solid #172554; border-radius: 12px; padding: 16px 18px;
        border-top: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0;
        color: #334155; font-size: 17px;
    }
    .soft-card {
        background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 18px;
        color: #334155; font-size: 16px;
    }

    .havi-variable-table { width: 100%; border-collapse: collapse; margin-top: 10px; table-layout: fixed; }
    .havi-variable-table th {
        font-size: 16px; font-weight: 700; background-color: #f1f5f9; color: #172554;
        padding: 12px; border: 1px solid #e2e8f0; text-align: left; vertical-align: top;
        white-space: normal; word-wrap: break-word;
    }
    .havi-variable-table td {
        font-size: 14px; padding: 12px; border: 1px solid #e2e8f0; vertical-align: top;
        white-space: normal; word-wrap: break-word; line-height: 1.35;
    }
    .havi-variable-table tr:nth-child(even) { background-color: #fafafa; }
    .havi-variable-table th:nth-child(1), .havi-variable-table td:nth-child(1) { width: 18%; }
    .havi-variable-table th:nth-child(2), .havi-variable-table td:nth-child(2) { width: 16%; }
    .havi-variable-table th:nth-child(3), .havi-variable-table td:nth-child(3) { width: 18%; }
    .havi-variable-table th:nth-child(4), .havi-variable-table td:nth-child(4) { width: 20%; }
    .havi-variable-table th:nth-child(5), .havi-variable-table td:nth-child(5) { width: 28%; }
    .havi-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .havi-table th {
        font-size: 17px; font-weight: 700; background-color: #f1f5f9; color: #172554;
        padding: 12px; border: 1px solid #e2e8f0; text-align: left;
    }
    .havi-table td { font-size: 14px; padding: 12px; border: 1px solid #e2e8f0; }
    .havi-table tr:nth-child(even) { background-color: #fafafa; }

    /* Keep all summary cards equal-height and readable on narrower screens. */
    @media (max-width: 1200px) {
        .metric-card {
            height: 142px;
            min-height: 142px;
            max-height: 142px;
            padding: 14px 10px;
        }
        .metric-value { font-size: 22px !important; }
    }

    @media (max-width: 768px) {
        .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
        .havi-title { font-size: 32px; }
        .havi-subtitle, .section-subtitle { font-size: 15px; }
        .metric-card {
            height: 128px;
            min-height: 128px;
            max-height: 128px;
        }
        .metric-label { font-size: 14px; }
        .metric-value { font-size: 20px !important; }
    }

    /* Dark-mode support for the page, cards, tables, and embedded Plotly text. */
    @media (prefers-color-scheme: dark) {
        html, body, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #0f172a !important;
            color: #f8fafc !important;
        }
        .havi-title, .havi-subtitle, .section-subtitle, .sidebar-label,
        .metric-label, .interpret-card, .soft-card,
        .havi-variable-table td, .havi-table td,
        [data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"] {
            color: #f8fafc !important;
        }
        .metric-card, .interpret-card, .soft-card {
            background: #111827 !important;
            border-color: #334155 !important;
            box-shadow: none !important;
        }
        /* Keep the Urban-Rural card fully legible in dark mode. */
        .metric-card.force-dark-white .metric-value,
        .metric-card.force-dark-white .metric-value span {
            color: #ffffff !important;
        }
        .havi-variable-table th, .havi-table th {
            background-color: #1e293b !important;
            color: #f8fafc !important;
            border-color: #475569 !important;
        }
        .havi-variable-table td, .havi-table td {
            background-color: #111827 !important;
            border-color: #334155 !important;
        }
        .havi-variable-table tr:nth-child(even) td,
        .havi-table tr:nth-child(even) td {
            background-color: #172033 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #111827 !important;
        }
        [data-testid="stSidebar"] * { color: #f8fafc !important; }
        .js-plotly-plot .plotly text { fill: #f8fafc !important; }
        .js-plotly-plot .plotly .bg { fill: rgba(0,0,0,0) !important; }
        .js-plotly-plot .plotly .xgrid,
        .js-plotly-plot .plotly .ygrid { stroke: #334155 !important; }
        .js-plotly-plot .plotly .zerolinelayer path { stroke: #e2e8f0 !important; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Helper Functions
# -----------------------------
def clean_fips(series):
    return (
        series.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"[^0-9]", "", regex=True)
        .str.zfill(5)
    )

def coalesce_columns(df, candidates, output_name=None):
    for col in candidates:
        if col in df.columns:
            if output_name is not None and output_name != col:
                df[output_name] = df[col]
                return output_name
            return col
    return None

def safe_get(row, col):
    if col not in row.index:
        return np.nan
    return row[col]

def fmt_pct(value):
    if pd.isna(value):
        return "Not available"
    return f"{float(value):.1f}%"

def fmt_score(value):
    if pd.isna(value):
        return "Not available"
    return f"{float(value):.1f}"

def fmt_rate(value, label):
    if pd.isna(value):
        return "Not available"
    return f"{float(value):.1f} {label}"

def fmt_small_rate(value, label):
    if pd.isna(value):
        return "Not available"
    value = float(value)
    if value == 0:
        return f"0 {label}"
    return f"{value:.2f} {label}" if 0 < value < 1 else f"{value:.1f} {label}"

def fmt_fqhc_per_100k(value):
    """Display AHRQ POS_FQHC_RATE as FQHCs per 100,000 residents.
    AHRQ provides POS_FQHC_RATE per 1,000 residents, so multiply by 100
    only for dashboard display. This does not affect HAVI scoring.
    """
    if pd.isna(value):
        return "Not available"
    return fmt_small_rate(float(value) * 100, "FQHCs per 100,000 residents")

def fmt_count(value, singular, plural=None):
    if pd.isna(value):
        return "Not available"
    if plural is None:
        plural = singular + "s"
    value_int = int(round(float(value)))
    label = singular if value_int == 1 else plural
    return f"{value_int:,} {label}"

def fmt_count_with_rate(row, count_col, rate_col, singular, plural, rate_label):
    count_value = safe_get(row, count_col)
    rate_value = safe_get(row, rate_col)
    if pd.isna(count_value) and pd.isna(rate_value):
        return "Not available"
    count_text = fmt_count(count_value, singular, plural)
    if pd.isna(rate_value):
        return count_text
    return f"{count_text} ({float(rate_value):.1f} {rate_label})"

def rank_text(value):
    if pd.isna(value):
        return "Not available"
    return f"{int(round(float(value))):,}"

def normalize_vulnerability_text(value):
    if pd.isna(value):
        return "Not available"
    text = str(value).strip().replace("_", " ").replace("-", " ")
    text = " ".join(text.split())
    lower = text.lower()
    if "very" in lower and "high" in lower:
        return "Very High Vulnerability"
    if "moderate" in lower or "medium" in lower:
        return "Moderate Vulnerability"
    if "high" in lower:
        return "High Vulnerability"
    if "low" in lower:
        return "Low Vulnerability"
    return text

def render_metric(label, value, color="#172554", font_size=34, css_class=""):
    st.markdown(
        f"""
        <div class="metric-card {css_class}">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color}; font-size:{font_size}px;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def get_nchs_code(row):
    possible_cols = [
        "nchs_urban_rural_code", "NCHS_code", "NCHS_CODE", "nchs_code",
        "NCHS Urban-Rural Code", "NCHS_URBAN_RURAL_CODE",
        "urban_rural_code", "URBAN_RURAL_CODE",
        "NCHS_2023_CODE", "nchs_2023_code", "nchs_code_2023", "NCHS_code_2023",
        "URBRURAL", "urb_rural", "urban_rural",
        "NCHS_Urban_Rural_Classification_Code"
    ]

    for col in possible_cols:
        if col in row.index and not pd.isna(row[col]):
            try:
                return int(float(row[col]))
            except Exception:
                continue

    return None

def nchs_detail_label(code):
    labels = {
        1: "Large Central Metro",
        2: "Large Fringe Metro",
        3: "Medium Metro",
        4: "Small Metro",
        5: "Micropolitan",
        6: "Noncore"
    }
    return labels.get(code, "Not available")

def rural_urban_group(code):
    """HAVI urban-rural groups based on the 2023 NCHS Urban-Rural Classification Scheme:
    Urban/Suburban = metropolitan counties (codes 1-4);
    Semi-Rural/Rural = nonmetropolitan counties (codes 5-6)."""
    if code in [1, 2, 3, 4]:
        return "Urban/Suburban"
    if code in [5, 6]:
        return "Semi-Rural/Rural"
    return "Not available"

def is_urban_suburban(row):
    return get_nchs_code(row) in [1, 2, 3, 4]

rural_specific_factors = [
    "Rural Health Clinic (RHC) Availability",
    "Critical Access Hospital Availability"
]

def fmt_hospitals(row, rate_col):
    """Hospital count shown on the same basis as the HAVI indicator:
    all hospitals in Urban/Suburban counties; Critical Access Hospitals excluded in
    Semi-Rural/Rural counties because they are counted by their own indicator."""
    hosp = safe_get(row, "hosp_23")
    cah = safe_get(row, "critcl_access_hosp_23")
    rate = safe_get(row, rate_col)
    if is_urban_suburban(row):
        count, note = hosp, ""
    else:
        count = hosp - cah if not (pd.isna(hosp) or pd.isna(cah)) else np.nan
        note = " (excluding Critical Access Hospitals)"
    if pd.isna(count) and pd.isna(rate):
        return "Not available"
    text = fmt_count(count, "hospital", "hospitals") + note
    if not pd.isna(rate):
        text += f"; {float(rate):.1f} per 100,000 residents"
    return text

def fmt_nursing_home_beds(row, rate_col):
    snf = safe_get(row, "snf_beds_24")
    nf = safe_get(row, "nurs_fac_beds_24")
    count = np.nan if (pd.isna(snf) and pd.isna(nf)) else np.nansum([snf, nf])
    rate = safe_get(row, rate_col)
    if pd.isna(count) and pd.isna(rate):
        return "Not available"
    text = fmt_count(count, "bed", "beds")
    if not pd.isna(rate):
        text += f" ({float(rate):.1f} per 1,000 residents aged ≥65)"
    return text

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_havi():
    data = pd.read_csv(HAVI_MASTER_FILE, low_memory=False)

    fips_col = coalesce_columns(data, ["FIPS", "COUNTYFIPS", "county_fips", "GEOID", "LocationID"], "FIPS")
    if fips_col is None:
        st.error("No county FIPS column was identified in the master file.")
        st.stop()
    data["FIPS"] = clean_fips(data["FIPS"])

    state_col = coalesce_columns(data, ["State", "state", "STATE", "STATE_NAME", "state_name"], "State")
    county_col = coalesce_columns(data, ["County", "county", "COUNTY", "county_name", "County_Name", "County Name", "NAME"], "County")
    if state_col is None or county_col is None:
        st.error("State and county columns were not identified in the master file.")
        st.stop()

    data["State"] = data["State"].astype(str)
    data["County"] = data["County"].astype(str)

    score_col = coalesce_columns(
        data,
        ["HAVI", "HAVI_score", "HAVI Score", "HAVI_final"],
        "HAVI Score"
    )
    if score_col is None:
        st.error("No HAVI score column was found. Expected HAVI, HAVI_score, HAVI Score, or HAVI_final.")
        st.stop()
    data["HAVI Score"] = pd.to_numeric(data["HAVI Score"], errors="coerce")

    level_col = coalesce_columns(
        data,
        ["HAVI_level_final", "HAVI_level_jenks", "HAVI_level", "HAVI Level", "HAVI_category"],
        "HAVI Level"
    )
    if level_col is None:
        st.error(
            "Precomputed HAVI categories were not found in the master file. "
            "Provide the approved HAVI classifications instead of substituting quartiles."
        )
        st.stop()
    data["HAVI Level"] = data["HAVI Level"].apply(normalize_vulnerability_text)

    # Rank and standing are always computed here so that rank 1 = highest HAVI score.
    # (Rank columns stored in source files may use the opposite direction.)
    data = data.copy()
    n_scored = data["HAVI Score"].notna().sum()
    data["National Rank"] = data["HAVI Score"].rank(ascending=False, method="min")
    data["Pct Counties Lower"] = (n_scored - data["National Rank"]) / max(n_scored - 1, 1) * 100

    return data

@st.cache_data
def load_contrib_long():
    if not os.path.exists(CONTRIB_LONG_FILE):
        return None

    contrib = pd.read_csv(CONTRIB_LONG_FILE, low_memory=False)

    fips_col = coalesce_columns(contrib, ["FIPS", "COUNTYFIPS", "county_fips", "GEOID", "LocationID"], "FIPS")
    if fips_col is None:
        return None

    contrib["FIPS"] = clean_fips(contrib["FIPS"])

    factor_label_col = coalesce_columns(contrib, ["factor_label", "Factor", "factor", "variable", "Variable"], "factor_label")
    contrib_col = coalesce_columns(
        contrib,
        ["signed_pct_contribution", "Contribution (%)", "pct_contribution", "contribution_pct", "signed_contribution"],
        "signed_pct_contribution"
    )

    if factor_label_col is None or contrib_col is None:
        return None

    if "factor_variable" not in contrib.columns:
        contrib["factor_variable"] = np.nan

    contrib["signed_pct_contribution"] = pd.to_numeric(contrib["signed_pct_contribution"], errors="coerce")
    return contrib[["FIPS", "factor_variable", "factor_label", "signed_pct_contribution"]].copy()

try:
    df = load_havi()
except FileNotFoundError:
    st.error(f"Could not find {HAVI_MASTER_FILE}. Place it in the same folder as app.py.")
    st.stop()

contrib_long = load_contrib_long()
N_COUNTIES = int(df["HAVI Score"].notna().sum())

# -----------------------------
# Reference medians and means
# -----------------------------
havi_reference_vars = [
    "HAVI", "HAVI Score", "disease_burden_composite",
    "ACS_PCT_AGE_ABOVE65", "ACS_PCT_AGE_0_4", "ACS_PCT_DISABLE",
    "pers_povty_pct_23", "ACS_PCT_UNEMPLOY", "ACS_PCT_LT_HS",
    "ACS_PCT_HU_NO_VEH", "ACS_PCT_PUBL_TRANSIT", "transport_vulnerability",
    "ACS_PCT_HH_NO_INTERNET", "ACS_PCT_RENTER_HU_COST_30PCT", "ACS_PCT_UNINSURED",
    "primary_care_providers_per_10k", "dentists_per_10k", "mental_health_providers_per_10k",
    "providers_per_10k", "beds_per_1000", "hospitals_per_100k", "clinics_per_100k",
    "critical_access_per_100k", "POS_FQHC_RATE", "nursing_home_beds_per_1000_65plus",
    "rural_pct", "ACS_PCT_HH_LIMIT_ENGLISH",
    "POS_MEDIAN_DIST_CLINIC", "POS_MEDIAN_DIST_CLINIC_w"
]
havi_reference_vars = [c for c in havi_reference_vars if c in df.columns]
NATIONAL_MEDIAN = df[havi_reference_vars].median(numeric_only=True).to_dict()
NATIONAL_MEAN = df[havi_reference_vars].mean(numeric_only=True).to_dict()

disease_var_map = {
    "arthritis_pct": "Arthritis",
    "asthma_pct": "Current Asthma",
    "cancer_pct": "Cancer",
    "copd_pct": "COPD",
    "chd_pct": "Coronary Heart Disease",
    "depression_pct": "Depression",
    "diabetes_pct": "Diabetes",
    "hypertension_pct": "High Blood Pressure",
    "bphigh_pct": "High Blood Pressure",
    "obesity_pct": "Obesity",
    "stroke_pct": "Stroke"
}
disease_cols = [c for c in disease_var_map if c in df.columns]
DISEASE_MEDIAN = df[disease_cols].median(numeric_only=True).to_dict()
DISEASE_MEAN = df[disease_cols].mean(numeric_only=True).to_dict()

# -----------------------------
# Header and sidebar
# -----------------------------

st.markdown('<div class="havi-title">Healthcare Access Vulnerability Index (HAVI)</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="havi-subtitle">HAVI is a county-level screening tool that identifies communities where residents may face greater challenges accessing healthcare. It combines healthcare resources, population health needs, and social and structural barriers, and shows which conditions contribute most to each county\'s score. This dashboard is a research prototype intended to support further local assessment and planning.</div>',
    unsafe_allow_html=True
)

st.sidebar.title("HAVI Dashboard")
st.sidebar.markdown("Select a county to view its healthcare access vulnerability profile.")

st.sidebar.markdown('<div class="sidebar-label">Select State</div>', unsafe_allow_html=True)
state = st.sidebar.selectbox("Select State", sorted(df["State"].dropna().unique()), label_visibility="collapsed")

county_options = sorted(df[df["State"] == state]["County"].dropna().unique())
st.sidebar.markdown('<div class="sidebar-label">Select County</div>', unsafe_allow_html=True)
county = st.sidebar.selectbox("Select County", county_options, label_visibility="collapsed")

selected = df[(df["State"] == state) & (df["County"] == county)].iloc[0]
selected_fips = selected["FIPS"]

level_colors = {
    "Low Vulnerability": "#166534",
    "Moderate Vulnerability": "#ca8a04",
    "High Vulnerability": "#ea580c",
    "Very High Vulnerability": "#dc2626",
    "Low": "#166534",
    "Moderate": "#ca8a04",
    "High": "#ea580c",
    "Very High": "#dc2626"
}
havi_color = level_colors.get(str(selected["HAVI Level"]), "#172554")

# -----------------------------
# Top profile
# -----------------------------
st.markdown(f"## {county}, {state}")
nchs_code = get_nchs_code(selected)
ru_group = rural_urban_group(nchs_code)
ru_detail = nchs_detail_label(nchs_code)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_metric("HAVI Score (0–100)", f"{float(selected['HAVI Score']):.1f}" if not pd.isna(selected["HAVI Score"]) else "Not available", havi_color)
with col2:
    render_metric("HAVI Level", normalize_vulnerability_text(selected["HAVI Level"]), havi_color, font_size=24)
with col3:
    render_metric(f"National Rank (out of {N_COUNTIES:,})", rank_text(selected["National Rank"]), havi_color)
with col4:
    pct_lower = selected["Pct Counties Lower"]
    render_metric(
        "HAVI Higher Than",
        f"{pct_lower:.1f}%<br><span style='font-size:15px; font-weight:600; color:#64748b;'>of U.S. counties</span>"
        if not pd.isna(pct_lower) else "Not available",
        havi_color,
        font_size=30
    )
with col5:
    render_metric(
        "Urban–Rural Group (NCHS)",
        f"{ru_group}<br><span style='font-size:15px; font-weight:600; color:#64748b;'>{ru_detail}</span>",
        "#172554",
        font_size=22,
        css_class="force-dark-white"
    )

st.markdown(
    "Higher HAVI scores and smaller national rank numbers (rank 1 = highest score) indicate greater relative healthcare access vulnerability. "
    "Urban/Suburban = metropolitan counties (NCHS codes 1–4); Semi-Rural/Rural = nonmetropolitan counties (NCHS codes 5–6)."
)

# -----------------------------
# Contribution chart setup
# -----------------------------
factor_label_map = {
    "ACS_PCT_AGE_ABOVE65": "Older Adults (≥65 Years)",
    "ACS_PCT_AGE_0_4": "Young Children (<5 Years)",
    "ACS_PCT_DISABLE": "Population with Disabilities",
    "disease_burden_composite": "Chronic Disease Burden",
    "pers_povty_pct_23": "Population Below Poverty Level",
    "ACS_PCT_UNEMPLOY": "Unemployment Rate",
    "ACS_PCT_RENTER_HU_COST_30PCT": "Housing Cost Burden",
    "ACS_PCT_HH_NO_INTERNET": "Households Without Internet",
    "ACS_PCT_UNINSURED": "Uninsured Population",
    "ACS_PCT_HH_LIMIT_ENGLISH": "Language Access Barriers",
    "ACS_PCT_LT_HS": "Adults Without a High School Diploma",
    "rural_pct": "Rural Population (%)",
    "transport_vulnerability": "Transportation Vulnerability (Vehicle & Transit)",
    "POS_MEDIAN_DIST_CLINIC": "Distance to Nearest Clinic",
    "POS_MEDIAN_DIST_CLINIC_w": "Distance to Nearest Clinic",
    "primary_care_providers_per_10k": "Primary Care Provider Availability",
    "dentists_per_10k": "Dentist Availability",
    "mental_health_providers_per_10k": "Mental Health Provider Availability",
    "providers_per_10k": "Primary Care Provider Availability",
    "beds_per_1000": "Hospital Bed Capacity",
    "hospitals_per_100k": "Hospital Availability",
    "clinics_per_100k": "Rural Health Clinic (RHC) Availability",
    "critical_access_per_100k": "Critical Access Hospital Availability",
    "nursing_home_beds_per_1000_65plus": "Nursing Home Bed Capacity",
    "POS_FQHC_RATE": "FQHC Availability",
    "FQHC Access": "FQHC Availability",
    "Federally Qualified Health Centers": "FQHC Availability",
    "Hospitals": "Hospital Availability",

    # Display labels used in the contribution files
    "Older Adults": "Older Adults (≥65 Years)",
    "Children Under 5": "Young Children (<5 Years)",
    "Disability": "Population with Disabilities",
    "Disease Burden": "Chronic Disease Burden",
    "Poverty": "Population Below Poverty Level",
    "Unemployment": "Unemployment Rate",
    "Housing Burden": "Housing Cost Burden",
    "No Internet": "Households Without Internet",
    "Uninsured": "Uninsured Population",
    "Limited English": "Language Access Barriers",
    "Limited English Proficiency": "Language Access Barriers",
    "No High School Diploma": "Adults Without a High School Diploma",
    "Rural Population": "Rural Population (%)",
    "Transportation Access": "Transportation Vulnerability (Vehicle & Transit)",
    "Transportation Access (Vehicle & Transit)": "Transportation Vulnerability (Vehicle & Transit)",
    "Transportation Vulnerability": "Transportation Vulnerability (Vehicle & Transit)",
    "Distance to Clinic": "Distance to Nearest Clinic",
    "Median Distance to Nearest Clinic": "Distance to Nearest Clinic",
    "Provider Availability": "Primary Care Provider Availability",
    "Primary Care Providers": "Primary Care Provider Availability",
    "Primary Care Provider Availability": "Primary Care Provider Availability",
    "Dentists": "Dentist Availability",
    "Dentist Availability": "Dentist Availability",
    "Mental Health Providers": "Mental Health Provider Availability",
    "Mental Health Provider Availability": "Mental Health Provider Availability",
    "Hospital Beds": "Hospital Bed Capacity",
    "Hospital Access": "Hospital Availability",
    "Nursing Home Beds": "Nursing Home Bed Capacity",
    "Rural Health Clinics": "Rural Health Clinic (RHC) Availability",
    "Critical Access Hospitals": "Critical Access Hospital Availability"
}

label_to_col = {
    "Older Adults (≥65 Years)": "ACS_PCT_AGE_ABOVE65",
    "Older Adults": "ACS_PCT_AGE_ABOVE65",
    "Young Children (<5 Years)": "ACS_PCT_AGE_0_4",
    "Children Under 5": "ACS_PCT_AGE_0_4",
    "Population with Disabilities": "ACS_PCT_DISABLE",
    "Disability": "ACS_PCT_DISABLE",
    "Chronic Disease Burden": "disease_burden_composite",
    "Disease Burden": "disease_burden_composite",
    "Population Below Poverty Level": "pers_povty_pct_23",
    "Poverty": "pers_povty_pct_23",
    "Unemployment Rate": "ACS_PCT_UNEMPLOY",
    "Unemployment": "ACS_PCT_UNEMPLOY",
    "Housing Cost Burden": "ACS_PCT_RENTER_HU_COST_30PCT",
    "Housing Burden": "ACS_PCT_RENTER_HU_COST_30PCT",
    "Households Without Internet": "ACS_PCT_HH_NO_INTERNET",
    "No Internet": "ACS_PCT_HH_NO_INTERNET",
    "Uninsured Population": "ACS_PCT_UNINSURED",
    "Uninsured": "ACS_PCT_UNINSURED",
    "Language Access Barriers": "ACS_PCT_HH_LIMIT_ENGLISH",
    "Limited English": "ACS_PCT_HH_LIMIT_ENGLISH",
    "Limited English Proficiency": "ACS_PCT_HH_LIMIT_ENGLISH",
    "Adults Without a High School Diploma": "ACS_PCT_LT_HS",
    "No High School Diploma": "ACS_PCT_LT_HS",
    "Rural Population (%)": "rural_pct",
    "Rural Population": "rural_pct",
    "Transportation Vulnerability (Vehicle & Transit)": "transport_vulnerability",
    "Transportation Access (Vehicle & Transit)": "transport_vulnerability",
    "Transportation Access": "transport_vulnerability",
    "Distance to Nearest Clinic": "POS_MEDIAN_DIST_CLINIC",
    "Distance to Clinic": "POS_MEDIAN_DIST_CLINIC",
    "Primary Care Provider Availability": "primary_care_providers_per_10k",
    "Primary Care Providers": "primary_care_providers_per_10k",
    "Dentist Availability": "dentists_per_10k",
    "Dentists": "dentists_per_10k",
    "Mental Health Provider Availability": "mental_health_providers_per_10k",
    "Mental Health Providers": "mental_health_providers_per_10k",
    # Backward compatibility for older contribution files
    "Healthcare Provider Availability": "providers_per_10k",
    "Provider Availability": "providers_per_10k",
    "Hospital Bed Capacity": "beds_per_1000",
    "Hospital Beds": "beds_per_1000",
    "Hospital Availability": "hospitals_per_100k",
    "Hospitals": "hospitals_per_100k",
    "Hospital Access": "hospitals_per_100k",
    "Nursing Home Bed Capacity": "nursing_home_beds_per_1000_65plus",
    "Nursing Home Beds": "nursing_home_beds_per_1000_65plus",
    "Rural Health Clinic (RHC) Availability": "clinics_per_100k",
    "Rural Health Clinics": "clinics_per_100k",
    "Critical Access Hospital Availability": "critical_access_per_100k",
    "Critical Access Hospitals": "critical_access_per_100k",
    "FQHC Availability": "POS_FQHC_RATE",
    "FQHC Access": "POS_FQHC_RATE",
    "Federally Qualified Health Centers": "POS_FQHC_RATE"
}

def format_variable_value(label, col, row, median_dict, mean_dict):
    if col is None or col not in df.columns:
        return "Not available", "Not available", "Not available"

    value = safe_get(row, col)
    median = median_dict.get(col, np.nan)
    mean = mean_dict.get(col, np.nan)

    pct_cols = {
        "ACS_PCT_AGE_ABOVE65", "ACS_PCT_AGE_0_4", "ACS_PCT_DISABLE", "pers_povty_pct_23",
        "ACS_PCT_UNEMPLOY", "ACS_PCT_RENTER_HU_COST_30PCT", "ACS_PCT_HH_NO_INTERNET",
        "ACS_PCT_UNINSURED", "ACS_PCT_HH_LIMIT_ENGLISH", "ACS_PCT_LT_HS", "rural_pct",
        "ACS_PCT_HU_NO_VEH", "ACS_PCT_PUBL_TRANSIT"
    }

    if col in pct_cols:
        return fmt_pct(value), fmt_pct(median), fmt_pct(mean)
    if col == "disease_burden_composite":
        return fmt_score(value), fmt_score(median), fmt_score(mean)
    if col in ["POS_MEDIAN_DIST_CLINIC", "POS_MEDIAN_DIST_CLINIC_w"]:
        return fmt_rate(value, "miles"), fmt_rate(median, "miles"), fmt_rate(mean, "miles")
    if col in ["primary_care_providers_per_10k", "dentists_per_10k", "mental_health_providers_per_10k", "providers_per_10k"]:
        label_text = "providers per 10,000 residents"
        return fmt_rate(value, label_text), fmt_rate(median, label_text), fmt_rate(mean, label_text)
    if col == "beds_per_1000":
        label_text = "beds per 1,000 residents"
        return fmt_rate(value, label_text), fmt_rate(median, label_text), fmt_rate(mean, label_text)
    if col == "nursing_home_beds_per_1000_65plus":
        label_text = "beds per 1,000 residents aged ≥65"
        return fmt_rate(value, label_text), fmt_rate(median, label_text), fmt_rate(mean, label_text)
    if col in ["hospitals_per_100k", "clinics_per_100k", "critical_access_per_100k"]:
        label_text = "per 100,000 residents"
        return fmt_rate(value, label_text), fmt_rate(median, label_text), fmt_rate(mean, label_text)
    if col == "POS_FQHC_RATE":
        return fmt_fqhc_per_100k(value), fmt_fqhc_per_100k(median), fmt_fqhc_per_100k(mean)

    return fmt_score(value), fmt_score(median), fmt_score(mean)

def hover_details_for_factor(label):
    clean_label = str(label).strip()

    if clean_label in ["Transportation Vulnerability", "Transportation Vulnerability (Vehicle & Transit)"]:
        no_vehicle = fmt_pct(safe_get(selected, "ACS_PCT_HU_NO_VEH"))
        no_vehicle_med = fmt_pct(NATIONAL_MEDIAN.get("ACS_PCT_HU_NO_VEH", np.nan))
        no_vehicle_mean = fmt_pct(NATIONAL_MEAN.get("ACS_PCT_HU_NO_VEH", np.nan))
        transit = fmt_pct(safe_get(selected, "ACS_PCT_PUBL_TRANSIT"))
        transit_med = fmt_pct(NATIONAL_MEDIAN.get("ACS_PCT_PUBL_TRANSIT", np.nan))
        transit_mean = fmt_pct(NATIONAL_MEAN.get("ACS_PCT_PUBL_TRANSIT", np.nan))
        return (
            "Engineered proxy from no-vehicle households and public transit use.",
            f"No vehicle: {no_vehicle}; Public transit use: {transit}",
            f"No vehicle median: {no_vehicle_med}; Public transit median: {transit_med}",
            f"No vehicle mean: {no_vehicle_mean}; Public transit mean: {transit_mean}"
        )

    if clean_label in ["Disease Burden", "Chronic Disease Burden"]:
        county_value, median_value, mean_value = format_variable_value(
            clean_label, "disease_burden_composite", selected, NATIONAL_MEDIAN, NATIONAL_MEAN
        )
        return (
            "Composite of ten chronic conditions. See Disease Burden Variables below.",
            county_value,
            median_value,
            mean_value
        )

    if clean_label == "Hospital Availability" and not is_urban_suburban(selected):
        col = label_to_col.get(clean_label)
        county_value, median_value, mean_value = format_variable_value(
            clean_label, col, selected, NATIONAL_MEDIAN, NATIONAL_MEAN
        )
        return ("Excludes Critical Access Hospitals, which are counted separately.", county_value, median_value, mean_value)

    col = label_to_col.get(clean_label)
    county_value, median_value, mean_value = format_variable_value(
        clean_label, col, selected, NATIONAL_MEDIAN, NATIONAL_MEAN
    )
    return ("", county_value, median_value, mean_value)

# Preferred source: separate long contribution file used by the dashboard.
factor_rows = []

if contrib_long is not None:
    selected_contrib = contrib_long[contrib_long["FIPS"] == selected_fips].copy()

    for _, r in selected_contrib.iterrows():
        value = r["signed_pct_contribution"]
        if pd.isna(value):
            continue

        raw_factor_variable = str(r.get("factor_variable", "")).strip()
        raw_factor_label = str(r["factor_label"]).strip()
        base_factor_variable = raw_factor_variable.replace("_havi", "") if raw_factor_variable and raw_factor_variable != "nan" else raw_factor_variable
        label = factor_label_map.get(base_factor_variable, factor_label_map.get(raw_factor_label, raw_factor_label.replace("_", " ").title()))
        detail, county_value, median_value, mean_value = hover_details_for_factor(label)

        factor_rows.append({
            "Factor": label,
            "Contribution (%)": float(value),
            "County Value": county_value,
            "Typical U.S. County (Median)": median_value,
            "U.S. Average (Mean - HAVI Reference)": mean_value,
            "Details": detail
        })

# Backup source: wide contribution columns inside the master file, if present.
if len(factor_rows) == 0:
    contribution_cols = [c for c in df.columns if c.endswith("_signed_pct_contribution")]

    for col in contribution_cols:
        value = safe_get(selected, col)
        if pd.isna(value):
            continue

        raw_factor = col.replace("_signed_pct_contribution", "").replace("_havi", "")
        label = factor_label_map.get(raw_factor, raw_factor.replace("_", " ").title())
        detail, county_value, median_value, mean_value = hover_details_for_factor(label)

        factor_rows.append({
            "Factor": label,
            "Contribution (%)": float(value),
            "County Value": county_value,
            "Typical U.S. County (Median)": median_value,
            "U.S. Average (Mean - HAVI Reference)": mean_value,
            "Details": detail
        })

factor_df = pd.DataFrame(factor_rows)

# For Urban/Suburban (metropolitan, NCHS 1–4) counties, RHC and CAH indicators are not shown
# because these rural-specific resources are not scored for those counties.
if len(factor_df) > 0 and is_urban_suburban(selected):
    factor_df = factor_df[~factor_df["Factor"].isin(rural_specific_factors)].copy()

st.markdown("## Factors Contributing to This County's HAVI Score")

if len(factor_df) > 0:
    factor_df["Direction"] = factor_df["Contribution (%)"].apply(
        lambda x: "Increases HAVI Score (factors associated with higher healthcare access vulnerability for this county)"
        if x > 0
        else ("Decreases HAVI Score (factors associated with lower healthcare access vulnerability for this county)"
              if x < 0 else "No contribution to HAVI Score")
    )

    factor_df["Direction Short"] = factor_df["Contribution (%)"].apply(
        lambda x: (
            "Associated with Higher Healthcare Access Vulnerability" if x > 0
            else ("Associated with Lower Healthcare Access Vulnerability" if x < 0
                  else "No contribution within the HAVI model")
        )
    )

    factor_df["Label"] = factor_df["Contribution (%)"].apply(lambda x: f"{x:+.1f}%")

    # Order the chart so green/negative contributors appear at the top
    # and red/positive contributors appear below them.
    neg = (
        factor_df[factor_df["Contribution (%)"] < 0]
        .sort_values("Contribution (%)", ascending=True)
    )

    pos = (
        factor_df[factor_df["Contribution (%)"] >= 0]
        .sort_values("Contribution (%)", ascending=True)
    )

    factor_df = pd.concat([neg, pos], ignore_index=True)
    factor_order = factor_df["Factor"].tolist()

    # Add horizontal padding around the longest bar so outside value labels
    # remain inside the plotting region instead of spilling into factor names.
    max_abs_contribution = factor_df["Contribution (%)"].abs().max()
    if pd.isna(max_abs_contribution) or max_abs_contribution == 0:
        max_abs_contribution = 1.0
    x_axis_limit = float(max_abs_contribution) * 1.35

    fig = px.bar(
        factor_df,
        x="Contribution (%)",
        y="Factor",
        orientation="h",
        text="Label",
        color="Direction",
        custom_data=[
            "Direction Short",
            "County Value",
            "Typical U.S. County (Median)",
            "U.S. Average (Mean - HAVI Reference)",
            "Details"
        ],
        color_discrete_map={
            "Increases HAVI Score (factors associated with higher healthcare access vulnerability for this county)": "#dc2626",
            "Decreases HAVI Score (factors associated with lower healthcare access vulnerability for this county)": "#16a34a",
            "No contribution to HAVI Score": "#6b7280"
        },
    )

    fig.add_vline(x=0, line_width=2, line_color="#111827")

    fig.update_traces(
        textposition="outside",
        cliponaxis=True,
        textfont=dict(size=16, color="#475569"),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{customdata[0]}<br>"
            "Relative contribution share: %{x:.1f}%<br>"
            "County value: %{customdata[1]}<br>"
            "Typical U.S. county median: %{customdata[2]}<br>"
            "U.S. average mean (HAVI reference): %{customdata[3]}<br>"
            "%{customdata[4]}"
            "<extra></extra>"
        )
    )
    fig.update_layout(
        height=max(560, 34 * len(factor_df) + 160),
        yaxis_title="",
        margin=dict(l=30, r=55, t=70, b=100),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=18),
        yaxis=dict(
            categoryorder="array",
            categoryarray=factor_order[::-1],
            tickfont=dict(size=16, color="#111827"),
            automargin=True
        ),
        xaxis=dict(
            title=dict(text="Relative Contribution Share (%)", font=dict(size=22, color="#111827")),
            tickfont=dict(size=14, color="#374151"),
            range=[-x_axis_limit, x_axis_limit],
            automargin=True,
            fixedrange=True
        ),
        legend_title_text="",
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5, font=dict(size=16))
    )
    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": False,
            "responsive": True
        }
    )
    st.caption(
        "Terminology: 'Factors' on this chart means the indicators used in the HAVI "
        "framework, including composite indicators built from multiple data inputs. "
        "Percentages are relative contribution shares within the HAVI scoring model; "
        "they do not establish causal effects."
    )
else:
    st.info(f"No contribution data were found. Make sure {CONTRIB_LONG_FILE} is in the same folder as app.py, or that the master file contains columns ending in _signed_pct_contribution.")

# -----------------------------
# Factor metadata used in HAVI variables table
# -----------------------------
factor_metadata = {

    "Population": {
        "domain": "County Context",
        "raw": "popn_est_24",
        "source": "AHRF 2025",
        "definition": "Estimated total county population, shown for context; not a HAVI indicator."
    },
    "Households Without Vehicle": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_HU_NO_VEH",
        "source": "AHRQ SDOH 2023",
        "definition": "Percentage of households without access to a vehicle. One input to Transportation Vulnerability."
    },
    "Public Transit Use": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_PUBL_TRANSIT",
        "source": "AHRQ SDOH 2023",
        "definition": "Percentage of workers commuting by public transportation. One input to Transportation Vulnerability."
    },
    "Transportation Vulnerability (Vehicle & Transit)": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "transport_vulnerability",
        "source": "Engineered from AHRQ SDOH 2023",
        "definition": "Engineered proxy combining no-vehicle households with public transit use, which may partly offset lack of a vehicle. Higher values indicate greater transportation vulnerability."
    },
    "Distance to Nearest Clinic": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "POS_MEDIAN_DIST_CLINIC",
        "source": "AHRQ SDOH 2023",
        "definition": "Median distance from residents to the nearest FQHC or Rural Health Clinic."
    },
    "Primary Care Provider Availability": {
        "domain": "Healthcare Supply",
        "raw": "primary_care_providers_per_10k",
        "source": "AHRF 2025",
        "definition": "Primary care physicians, physician assistants, and nurse practitioners per 10,000 residents."
    },
    "Dentist Availability": {
        "domain": "Healthcare Supply",
        "raw": "dentists_per_10k",
        "source": "AHRF 2025",
        "definition": "Number of dentists per 10,000 residents."
    },
    "Mental Health Provider Availability": {
        "domain": "Healthcare Supply",
        "raw": "mental_health_providers_per_10k",
        "source": "AHRQ SDOH 2023",
        "definition": "All mental health providers (including psychiatrists, psychologists, licensed clinical social workers, counselors, and family therapists) per 10,000 residents."
    },
    "Hospital Bed Capacity": {
        "domain": "Healthcare Supply",
        "raw": "beds_per_1000",
        "source": "AHRF 2025",
        "definition": "Number of hospital beds per 1,000 residents."
    },
    "Hospital Availability": {
        "domain": "Healthcare Supply",
        "raw": "hospitals_per_100k",
        "source": "AHRF 2025",
        "definition": "Hospitals per 100,000 residents. In Semi-Rural/Rural counties, Critical Access Hospitals are excluded here because they are counted by their own indicator."
    },
    "Rural Health Clinic (RHC) Availability": {
        "domain": "Healthcare Supply",
        "raw": "clinics_per_100k",
        "source": "AHRF 2025",
        "definition": "Rural Health Clinics per 100,000 residents. Scored only for Semi-Rural/Rural counties."
    },
    "Critical Access Hospital Availability": {
        "domain": "Healthcare Supply",
        "raw": "critical_access_per_100k",
        "source": "AHRF 2025",
        "definition": "Critical Access Hospitals per 100,000 residents. Scored only for Semi-Rural/Rural counties."
    },
    "FQHC Availability": {
        "domain": "Healthcare Supply",
        "raw": "POS_FQHC_RATE",
        "source": "AHRQ SDOH 2023",
        "definition": "Federally Qualified Health Centers per 100,000 residents (AHRQ's per-1,000 rate rescaled for display only)."
    },
    "Nursing Home Bed Capacity": {
        "domain": "Healthcare Supply",
        "raw": "nursing_home_beds_per_1000_65plus",
        "source": "AHRF 2025",
        "definition": "Skilled nursing facility and nursing facility beds per 1,000 residents aged 65 years or older."
    },
    "Older Adults (≥65 Years)": {
        "domain": "Healthcare Demand",
        "raw": "ACS_PCT_AGE_ABOVE65",
        "source": "AHRQ SDOH 2023",
        "definition": "Percentage of residents aged 65 years or older."
    },
    "Young Children (<5 Years)": {
        "domain": "Healthcare Demand",
        "raw": "ACS_PCT_AGE_0_4",
        "source": "AHRQ SDOH 2023",
        "definition": "Percentage of residents younger than 5 years."
    },
    "Population with Disabilities": {
        "domain": "Healthcare Demand",
        "raw": "ACS_PCT_DISABLE",
        "source": "AHRQ SDOH 2023",
        "definition": "Percentage of residents reporting a disability."
    },
    "Chronic Disease Burden": {
        "domain": "Healthcare Demand",
        "raw": "disease_burden_composite",
        "source": "CDC PLACES 2025",
        "definition": "Average national percentile rank across ten chronic conditions (see Disease Burden Variables below)."
    },
    "Population Below Poverty Level": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "pers_povty_pct_23",
        "source": "AHRF 2025",
        "definition": "Percentage of residents living below the federal poverty level."
    },
    "Unemployment Rate": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_UNEMPLOY",
        "source": "AHRQ SDOH 2023",
        "definition": "Percentage of the labor force that is unemployed."
    },
    "Housing Cost Burden": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_RENTER_HU_COST_30PCT",
        "source": "AHRQ SDOH 2023",
        "definition": "Percentage of renter households spending at least 30% of income on housing."
    },
    "Households Without Internet": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_HH_NO_INTERNET",
        "source": "AHRQ SDOH 2023",
        "definition": "Percentage of households without internet access."
    },
    "Uninsured Population": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_UNINSURED",
        "source": "AHRQ SDOH 2023",
        "definition": "Percentage of residents without health insurance coverage."
    },
    "Adults Without a High School Diploma": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_LT_HS",
        "source": "AHRQ SDOH 2023",
        "definition": "Percentage of adults aged 25 years or older without a high school diploma."
    },
    "Rural Population (%)": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "rural_pct",
        "source": "AHRF 2025 (2020 Census)",
        "definition": "Percentage of residents living in rural areas."
    },
    "Language Access Barriers": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_HH_LIMIT_ENGLISH",
        "source": "AHRQ SDOH 2023",
        "definition": "Percentage of households with limited English-speaking ability."
    }
}

st.markdown(
    """
<span style="color:#16a34a;"><b>Green</b></span> bars represent factors that <b>lower this county's HAVI Score</b>, while <span style="color:#dc2626;"><b>red</b></span> bars represent factors that <b>raise this county's HAVI Score.</b> The percentage shown for each factor is its <b>relative contribution share</b>: its share of the total absolute contribution of all indicators to this county's HAVI score. It does <b>not</b> represent the percent difference between the county value and the national average or median. Contributions are calculated from each county's <b>standardized value relative to the national mean</b>, adjusted for factor direction and HAVI domain weighting. Because the four demand indicators share 25% of the weight, each carries more weight than an individual supply or social indicator, so demand factors appear more often as large contributors. These contributions reflect the HAVI scoring framework rather than evidence of direct causation and should be interpreted alongside the county's raw values, national reference values, and local context. <b>Rural Health Clinic (RHC) Availability</b> and <b>Critical Access Hospital Availability</b> are shown only for Semi-Rural/Rural counties because these rural-specific resources are not scored for Urban/Suburban counties.""",
    unsafe_allow_html=True
)

# -----------------------------
# HAVI level reference
# -----------------------------
st.markdown("## HAVI Category Reference")

def make_havi_level_table(data):
    ordered_levels = ["Low Vulnerability", "Moderate Vulnerability", "High Vulnerability", "Very High Vulnerability"]
    interpretations = {
        "Low Vulnerability": "Lower relative healthcare access vulnerability.",
        "Moderate Vulnerability": "Moderate relative healthcare access vulnerability.",
        "High Vulnerability": "Elevated relative healthcare access vulnerability; may warrant closer local review.",
        "Very High Vulnerability": "Highest relative healthcare access vulnerability; may warrant priority local review alongside other data."
    }
    colors = {
        "Low Vulnerability": "#166534",
        "Moderate Vulnerability": "#ca8a04",
        "High Vulnerability": "#ea580c",
        "Very High Vulnerability": "#dc2626"
    }
    temp = data[["HAVI Score", "HAVI Level"]].dropna().copy()
    total = len(temp)
    rows = []
    for level in ordered_levels:
        subset = temp[temp["HAVI Level"] == level]
        if len(subset) > 0:
            score_range = f"{subset['HAVI Score'].min():.1f}–{subset['HAVI Score'].max():.1f}"
            distribution = f"{len(subset):,} counties ({len(subset) / total * 100:.1f}%)" if total else "Not available"
        else:
            score_range = "Not available"
            distribution = "Not available"
        rows.append({
            "HAVI Level": f'<span style="color:{colors[level]}; font-weight:700;">{level}</span>',
            "HAVI Score Range": score_range,
            "National Distribution": distribution,
            "Interpretation": interpretations[level]
        })
    return pd.DataFrame(rows)

st.markdown(make_havi_level_table(df).to_html(classes="havi-table", index=False, escape=False), unsafe_allow_html=True)
st.caption(
    "Categories are based on Jenks natural breaks of the 0–100 HAVI score. They are descriptive groupings, "
    "not clinical or policy thresholds, and counties near a boundary may shift category under alternative "
    "weighting choices."
)

# -----------------------------
# HAVI variables table
# -----------------------------
st.markdown("## HAVI Measures and Supporting Data")
st.markdown(
    '<div class="section-subtitle">County values are shown alongside national county medians and means. The table also includes contextual inputs that are not separately counted as HAVI indicators.</div>',
    unsafe_allow_html=True
)

variable_rows = []

def add_row(factor, county_value, median_value, mean_value):
    meta = factor_metadata.get(factor, {})
    definition = meta.get("definition", "Shown for county context.")
    if meta.get("source"):
        definition = f"{definition} <i>Source: {meta['source']}.</i>"
    variable_rows.append({
        "Measure": factor,
        "County Value": county_value,
        "Typical U.S. County (Median)": median_value,
        "U.S. Average (Mean - HAVI Reference)": mean_value,
        "Definition": definition
    })

def median_pct(col):
    return fmt_pct(NATIONAL_MEDIAN.get(col, np.nan))

def mean_pct(col):
    return fmt_pct(NATIONAL_MEAN.get(col, np.nan))

def median_rate(col, label):
    return fmt_rate(NATIONAL_MEDIAN.get(col, np.nan), label)

def mean_rate(col, label):
    return fmt_rate(NATIONAL_MEAN.get(col, np.nan), label)

def median_small_rate(col, label):
    return fmt_small_rate(NATIONAL_MEDIAN.get(col, np.nan), label)

def mean_small_rate(col, label):
    return fmt_small_rate(NATIONAL_MEAN.get(col, np.nan), label)

if "popn_est_24" in df.columns:
    add_row(
        "Population",
        fmt_count(safe_get(selected, "popn_est_24"), "resident", "residents"),
        f"{int(df['popn_est_24'].median()):,} residents",
        f"{int(df['popn_est_24'].mean()):,} residents"
    )

access_rows = [
    ("Older Adults (≥65 Years)", "ACS_PCT_AGE_ABOVE65", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Young Children (<5 Years)", "ACS_PCT_AGE_0_4", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Population with Disabilities", "ACS_PCT_DISABLE", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Chronic Disease Burden", "disease_burden_composite", lambda r, c: fmt_score(safe_get(r, c)), lambda c: fmt_score(NATIONAL_MEDIAN.get(c, np.nan)), lambda c: fmt_score(NATIONAL_MEAN.get(c, np.nan))),
    ("Population Below Poverty Level", "pers_povty_pct_23", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Unemployment Rate", "ACS_PCT_UNEMPLOY", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Transportation Vulnerability (Vehicle & Transit)", "transport_vulnerability", lambda r, c: fmt_score(safe_get(r, c)), lambda c: fmt_score(NATIONAL_MEDIAN.get(c, np.nan)), lambda c: fmt_score(NATIONAL_MEAN.get(c, np.nan))),
    ("Households Without Vehicle", "ACS_PCT_HU_NO_VEH", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Public Transit Use", "ACS_PCT_PUBL_TRANSIT", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Households Without Internet", "ACS_PCT_HH_NO_INTERNET", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Housing Cost Burden", "ACS_PCT_RENTER_HU_COST_30PCT", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Uninsured Population", "ACS_PCT_UNINSURED", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Adults Without a High School Diploma", "ACS_PCT_LT_HS", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Primary Care Provider Availability", "primary_care_providers_per_10k", lambda r, c: fmt_rate(safe_get(r, c), "providers per 10,000 residents"), lambda c: median_rate(c, "providers per 10,000 residents"), lambda c: mean_rate(c, "providers per 10,000 residents")),
    ("Dentist Availability", "dentists_per_10k", lambda r, c: fmt_rate(safe_get(r, c), "dentists per 10,000 residents"), lambda c: median_rate(c, "dentists per 10,000 residents"), lambda c: mean_rate(c, "dentists per 10,000 residents")),
    ("Mental Health Provider Availability", "mental_health_providers_per_10k", lambda r, c: fmt_rate(safe_get(r, c), "mental health providers per 10,000 residents"), lambda c: median_rate(c, "mental health providers per 10,000 residents"), lambda c: mean_rate(c, "mental health providers per 10,000 residents")),
    ("Hospital Bed Capacity", "beds_per_1000", lambda r, c: fmt_count_with_rate(r, "hosp_beds_23", c, "bed", "beds", "per 1,000 residents"), lambda c: median_rate(c, "beds per 1,000 residents"), lambda c: mean_rate(c, "beds per 1,000 residents")),
    ("Hospital Availability", "hospitals_per_100k", lambda r, c: fmt_hospitals(r, c), lambda c: median_rate(c, "hospitals per 100,000 residents"), lambda c: mean_rate(c, "hospitals per 100,000 residents")),
    ("Rural Health Clinic (RHC) Availability", "clinics_per_100k", lambda r, c: fmt_count_with_rate(r, "rural_hlth_clincs_24", c, "rural health clinic", "rural health clinics", "per 100,000 residents"), lambda c: median_rate(c, "clinics per 100,000 residents"), lambda c: mean_rate(c, "clinics per 100,000 residents")),
    ("Critical Access Hospital Availability", "critical_access_per_100k", lambda r, c: fmt_count_with_rate(r, "critcl_access_hosp_23", c, "critical access hospital", "critical access hospitals", "per 100,000 residents"), lambda c: median_small_rate(c, "critical access hospitals per 100,000 residents"), lambda c: mean_small_rate(c, "critical access hospitals per 100,000 residents")),
    ("FQHC Availability", "POS_FQHC_RATE", lambda r, c: fmt_fqhc_per_100k(safe_get(r, c)), lambda c: fmt_fqhc_per_100k(NATIONAL_MEDIAN.get(c, np.nan)), lambda c: fmt_fqhc_per_100k(NATIONAL_MEAN.get(c, np.nan))),
    ("Nursing Home Bed Capacity", "nursing_home_beds_per_1000_65plus", lambda r, c: fmt_nursing_home_beds(r, c), lambda c: median_rate(c, "beds per 1,000 residents aged ≥65"), lambda c: mean_rate(c, "beds per 1,000 residents aged ≥65")),
    ("Rural Population (%)", "rural_pct", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Language Access Barriers", "ACS_PCT_HH_LIMIT_ENGLISH", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
]

for label, col, county_formatter, median_formatter, mean_formatter in access_rows:
    if is_urban_suburban(selected) and label in rural_specific_factors:
        continue

    if col in df.columns:
        add_row(label, county_formatter(selected, col), median_formatter(col), mean_formatter(col))

clinic_col = "POS_MEDIAN_DIST_CLINIC" if "POS_MEDIAN_DIST_CLINIC" in df.columns else "POS_MEDIAN_DIST_CLINIC_w" if "POS_MEDIAN_DIST_CLINIC_w" in df.columns else None
if clinic_col:
    add_row(
        "Distance to Nearest Clinic",
        fmt_rate(safe_get(selected, clinic_col), "miles"),
        median_rate(clinic_col, "miles"),
        mean_rate(clinic_col, "miles")
    )

variable_table = pd.DataFrame(variable_rows)
st.markdown(
    variable_table.to_html(classes="havi-variable-table", index=False, escape=False),
    unsafe_allow_html=True
)
st.markdown(
    """
**Interpretation Notes**

- **HAVI measures** are shown as county values alongside the median for a typical U.S. county and the national mean used as the HAVI standardization reference. The **Definition** column gives context and the data source for each measure.

- **Transportation Vulnerability (Vehicle & Transit)** is one engineered HAVI indicator. Household no-vehicle access and public transit use are shown separately for context, but are not counted as two independent HAVI indicators.

- **Chronic Disease Burden** is an engineered healthcare need indicator that summarizes ten CDC PLACES chronic disease measures into a single composite. Individual disease measures are displayed below under **Disease Burden Variables**.

- **Rural-specific supply indicators** (Rural Health Clinic and Critical Access Hospital Availability) are shown only for Semi-Rural/Rural counties because they are not scored for Urban/Suburban counties. In Semi-Rural/Rural counties, the hospital count excludes Critical Access Hospitals so that each hospital is counted once.

- **Connecticut** values for some facility and provider counts are estimates reallocated from the state's former counties to its nine planning regions. FQHC availability and distance to the nearest clinic are not available for the planning regions and were assigned the national median in HAVI scoring.
"""
)
# -----------------------------
# Disease burden variables table
# -----------------------------
st.markdown("## Disease Burden Variables")
st.markdown(
    """
    These variables come from CDC PLACES modeled health outcome estimates and describe estimated chronic disease prevalence for the selected county. They are shown here as direct county values with national county medians and means for comparison.
    """
)

if state in PLACES_IMPUTED_STATES or selected_fips in PLACES_IMPUTED_FIPS:
    st.warning(
        "CDC PLACES did not publish 2025 estimates for this county. The disease values shown here are "
        "model-based estimates developed for HAVI from county social and health characteristics."
    )

if len(disease_cols) > 0:
    disease_table = pd.DataFrame({
        "Disease Burden Variable": [disease_var_map[c] for c in disease_cols],
        "County Value": [fmt_pct(safe_get(selected, c)) for c in disease_cols],
        "Typical U.S. County (Median)": [fmt_pct(DISEASE_MEDIAN.get(c, np.nan)) for c in disease_cols],
        "U.S. Average (Mean - HAVI Reference)": [fmt_pct(DISEASE_MEAN.get(c, np.nan)) for c in disease_cols]
    })
    st.dataframe(disease_table, width="stretch", hide_index=True)
else:
    st.info("No disease burden variable columns were found in the master file.")

st.caption(
    "Disease burden variables are displayed for county context and HAVI interpretation. They should be interpreted alongside access vulnerability variables and local knowledge."
)

# -----------------------------
# Methodology
# -----------------------------
st.markdown("## HAVI Methodology")

st.markdown("""
The **Healthcare Access Vulnerability Index (HAVI)** is a county-level measure designed to identify communities where residents may face greater difficulty accessing timely healthcare.

HAVI does not measure healthcare access using a single factor. Instead, it combines **23 indicators** describing healthcare availability, population healthcare need, and social or structural conditions that may increase the risk of unmet healthcare needs.

### What HAVI Measures

HAVI includes three domains:

- **Healthcare Supply (25%; 9 indicators)** measures the availability of healthcare resources: primary care providers, mental health providers, dentists, hospital beds, hospitals, Federally Qualified Health Centers, nursing home beds, Rural Health Clinics, and Critical Access Hospitals. Rural Health Clinics and Critical Access Hospitals are scored only for Semi-Rural/Rural counties, and in those counties the hospital count excludes Critical Access Hospitals so that no hospital is counted twice.

- **Healthcare Demand (25%; 4 indicators)** measures expected healthcare need using the proportion of older adults, children under age 5, people with disabilities, and the county's overall chronic disease burden.

- **Social and Structural Vulnerability (50%; 10 indicators)** measures conditions that may make healthcare more difficult to obtain: poverty, unemployment, housing cost burden, lack of internet access, lack of health insurance, limited English proficiency, adults without a high school diploma, rurality, transportation barriers, and distance to the nearest clinic.

### Urban–Rural Groups

Counties are grouped using the 2023 National Center for Health Statistics (NCHS) Urban–Rural Classification Scheme: **Urban/Suburban** = metropolitan counties (codes 1–4: large central, large fringe, medium, and small metro); **Semi-Rural/Rural** = nonmetropolitan counties (codes 5–6: micropolitan and noncore).

### Engineered Measures

- **Transportation Vulnerability** is an engineered proxy combining the percentage of households without a vehicle with public transit use, which may partly offset the lack of a vehicle.

- **Chronic Disease Burden** is the average national percentile rank across ten chronic conditions from CDC PLACES. PLACES did not publish 2025 estimates for counties in Kentucky and Pennsylvania or for Loving County, Texas; for these 188 counties, disease values were estimated with regression models based on county characteristics.

### How HAVI Is Calculated

Indicators are capped at the 1st and 99th percentiles and standardized against the national county distribution so that measures with different units can be compared on a common scale. Each indicator is aligned so that higher values consistently represent greater healthcare access vulnerability.

Indicators are averaged within their domains and combined using the following weights:

- **25% Healthcare Supply**
- **25% Healthcare Demand**
- **50% Social and Structural Vulnerability**

The 50% weight for social and structural conditions is informed by the County Health Rankings & Roadmaps model; the weights are a conceptual choice rather than statistically derived. Final HAVI scores are rescaled to a **0–100 national scale**, where higher scores indicate greater relative healthcare access vulnerability compared with other U.S. counties.

### How HAVI Was Evaluated

- Counties designated as countywide **Medically Underserved Areas** had substantially higher HAVI scores than other counties.
- Higher HAVI scores were associated with **fewer dental visits, lower cancer and cholesterol screening, and more preventable hospitalizations** for acute conditions, including when comparing counties within the same state.
- County rankings stayed **very similar under alternative weighting choices**, although some counties near category boundaries changed category.

### Data Sources

HAVI was developed using **publicly available county-level datasets** from U.S. government agencies.

- **Area Health Resources Files (AHRF) 2025** – healthcare workforce, hospitals and other facilities, and selected demographic measures.
- **Agency for Healthcare Research and Quality (AHRQ) Community-Level Health Database (formerly the Social Determinants of Health Database), 2023 county file** – social determinants of health, mental health providers, FQHCs, distance to clinics, and population characteristics. Labeled "AHRQ SDOH 2023" in this dashboard.
- **Centers for Disease Control and Prevention (CDC) PLACES 2025** – county-level chronic disease prevalence estimates used for the Chronic Disease Burden indicator.
- **National Center for Health Statistics (NCHS) 2023 Urban–Rural Classification Scheme** – used to group counties and to apply rural-specific supply indicators.
- **HRSA Data Warehouse** – countywide Medically Underserved Area (MUA) designations and Index of Medical Underservice (IMU) scores, used only to evaluate HAVI.

The source variables have different reference years; HAVI is a cross-sectional snapshot, not a real-time measure.
""")

# -----------------------------
# Interpretation / use
# -----------------------------
st.markdown("## How to Use This Dashboard")

st.markdown(
    """
    HAVI is intended to support public health planning, community needs assessment, grant development, and communication about county-level healthcare access vulnerability.

    **Higher HAVI scores** indicate counties where limited healthcare resources, greater healthcare need, and social or structural barriers may combine to create greater difficulty accessing timely care.

    **Lower HAVI scores** indicate comparatively lower healthcare access vulnerability.

    **Recommended use:** HAVI should be used as a screening and planning tool to identify counties that may benefit from closer review and additional local assessment.

    **Important limitations:** HAVI describes relative county-level patterns and does not measure individual access to care or differences within a county. It should not be interpreted as a clinical tool, a definitive designation of medical underservice, or proof that any individual factor caused a county's outcomes. Results should be interpreted alongside local data, community knowledge, stakeholder input, and other established measures of healthcare access.
    """
)

st.info(
    """
    **Project Disclosure**

    HAVI was developed by **Ali Abidi** as an independent high school research project using publicly available data from multiple U.S. government agencies. This dashboard is a research prototype.

    The methodology was designed to support research, education, community health assessment, and public health planning. HAVI is intended to complement—not replace—local expertise, community assessment, and established public health resources. It should not be used as the sole basis for clinical, funding, policy, or resource-allocation decisions.
    """
)
