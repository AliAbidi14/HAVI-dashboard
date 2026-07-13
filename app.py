import os
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

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
        /* Keep the Rural-Urban card fully legible in dark mode. */
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

def percentile_text(value):
    if pd.isna(value):
        return "Not available"
    return f"{float(value):.1f}%"

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
        "NCHS_code", "NCHS_CODE", "nchs_code",
        "NCHS Urban-Rural Code", "NCHS_URBAN_RURAL_CODE", "nchs_urban_rural_code",
        "urban_rural_code", "URBAN_RURAL_CODE",
        "NCHS_2013_CODE", "nchs_2013_code", "NCHS_2023_CODE", "nchs_2023_code",
        "nchs_code_2013", "NCHS_code_2013", "nchs_code_2023", "NCHS_code_2023",
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
    if code in [1, 2, 3, 4]:
        return "Urban/Semi-Urban"
    if code in [5, 6]:
        return "Rural"
    return "Not available"

def is_urban_or_semiurban(row):
    return get_nchs_code(row) in [1, 2, 3, 4]

rural_specific_factors = [
    "Rural Health Clinic (RHC) Availability",
    "Critical Access Hospital Availability"
]

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
        data["HAVI Level"] = pd.qcut(
            data["HAVI Score"].rank(method="first"),
            q=4,
            labels=["Low Vulnerability", "Moderate Vulnerability", "High Vulnerability", "Very High Vulnerability"]
        ).astype(str)
    data["HAVI Level"] = data["HAVI Level"].apply(normalize_vulnerability_text)

    rank_col = coalesce_columns(
        data,
        ["HAVI_rank_national", "HAVI_national_rank", "HAVI Rank", "National Rank", "rank_national"],
        None
    )
    pct_col = coalesce_columns(
        data,
        ["HAVI_percentile_national", "HAVI_national_percentile", "HAVI Percentile", "National Percentile", "percentile_national"],
        None
    )

    if rank_col is not None:
        data["National Rank"] = pd.to_numeric(data[rank_col], errors="coerce")
    else:
        data["National Rank"] = data["HAVI Score"].rank(ascending=False, method="min")

    if pct_col is not None:
        data["National Percentile"] = pd.to_numeric(data[pct_col], errors="coerce")
    else:
        data["National Percentile"] = data["HAVI Score"].rank(pct=True, ascending=True).mul(100)

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

# -----------------------------
# Reference medians and means
# -----------------------------
havi_reference_vars = [
    "HAVI", "HAVI Score", "disease_burden_composite",
    "ACS_PCT_AGE_ABOVE65", "ACS_PCT_AGE_0_4", "ACS_PCT_DISABLE",
    "pers_povty_pct_23", "ACS_PCT_UNEMPLOY",
    "ACS_PCT_HU_NO_VEH", "ACS_PCT_PUBL_TRANSIT", "transport_vulnerability",
    "ACS_PCT_HH_NO_INTERNET", "ACS_PCT_RENTER_HU_COST_30PCT", "ACS_PCT_UNINSURED",
    "primary_care_providers_per_10k", "dentists_per_10k", "mental_health_providers_per_10k",
    "providers_per_10k", "beds_per_1000", "hospitals_per_100k", "clinics_per_100k",
    "critical_access_per_100k", "POS_FQHC_RATE", "rural_pct", "ACS_PCT_HH_LIMIT_ENGLISH",
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
    "poor_health_pct": "Poor or Fair Health",
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
    '<div class="havi-subtitle">HAVI is a county-level decision support tool that identifies communities where residents may experience greater challenges accessing healthcare. By combining healthcare resources, population health needs, and social and structural barriers, HAVI helps policymakers, healthcare organizations, researchers, and community leaders identify areas that may benefit from additional healthcare resources, planning, or targeted interventions.</div>',
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
#st.markdown("### Healthcare Access Vulnerability Index (HAVI)")
nchs_code = get_nchs_code(selected)
ru_group = rural_urban_group(nchs_code)
ru_detail = nchs_detail_label(nchs_code)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_metric("HAVI Score (1-100)", f"{float(selected['HAVI Score']):.1f}" if not pd.isna(selected["HAVI Score"]) else "Not available", havi_color)
with col2:
    render_metric("HAVI Level", normalize_vulnerability_text(selected["HAVI Level"]), havi_color, font_size=24)
with col3:
    render_metric("National Rank (Out of 3144)", rank_text(selected["National Rank"]), havi_color)
with col4:
    lower_than = (
        100 - float(selected["National Percentile"])
        if not pd.isna(selected["National Percentile"])
        else np.nan
    )

    render_metric(
        "National Percentile",
        f"{lower_than:.1f}%"
        if not pd.isna(lower_than)
        else "Not available",
        havi_color
    )
with col5:
    render_metric(
        "Rural-Urban Class",
        f"{ru_group}<br><span style='font-size:15px; font-weight:600; color:#64748b;'>{ru_detail}</span>",
        "#172554",
        font_size=22,
        css_class="force-dark-white"
    )

st.markdown(
    "Higher HAVI scores and rank indicate counties where residents may face greater barriers to accessing healthcare services relative to other U.S. counties."
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
    "rural_pct": "Rural Population (%)",
    "transport_vulnerability": "Transportation Vulnerability (Vehicle & Transit)",
    "POS_MEDIAN_DIST_CLINIC": "Median Distance to Nearest Clinic",
    "POS_MEDIAN_DIST_CLINIC_w": "Distance to Nearest Clinic",
    "primary_care_providers_per_10k": "Primary Care Provider Availability",
    "dentists_per_10k": "Dentist Availability",
    "mental_health_providers_per_10k": "Mental Health Provider Availability",
    "providers_per_10k": "Primary Care Provider Availability",
    "beds_per_1000": "Hospital Bed Capacity",
    "hospitals_per_100k": "Hospital Availability",
    "clinics_per_100k": "Rural Health Clinic (RHC) Availability",
    "critical_access_per_100k": "Critical Access Hospital Availability",
    "POS_FQHC_RATE": "FQHC Availability",
    "FQHC Access": "FQHC Availability",
    "Federally Qualified Health Centers": "FQHC Availability",
    "Hospitals": "Hospital Availability",

    # Backward-compatible display labels from older contribution files
    "Older Adults": "Older Adults (≥65 Years)",
    "Children Under 5": "Young Children (<5 Years)",
    "Disability": "Population with Disabilities",
    "Disease Burden": "Chronic Disease Burden",
    "Poverty": "Population Below Poverty Level",
    "Unemployment": "Unemployment Rate",
    "Housing Burden": "Housing Cost Burden",
    "No Internet": "Households Without Internet",
    "Limited English": "Language Access Barriers",
    "Limited English Proficiency": "Language Access Barriers",
    "Rural Population": "Rural Population (%)",
    "Transportation Access": "Transportation Access (Vehicle & Transit)",
    "Transportation Vulnerability": "Transportation Access (Vehicle & Transit)",
    "Distance to Clinic": "Distance to Nearest Clinic",
    "Provider Availability": "Primary Care Provider Availability",
    "Primary Care Providers": "Primary Care Provider Availability",
    "Primary Care Provider Availability": "Primary Care Provider Availability",
    "Dentists": "Dentist Availability",
    "Dentist Availability": "Dentist Availability",
    "Mental Health Providers": "Mental Health Provider Availability",
    "Mental Health Provider Availability": "Mental Health Provider Availability",
    "Hospital Beds": "Hospital Bed Capacity",
    "Hospital Access": "Hospital Availability",
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
    "Language Access Barriers": "ACS_PCT_HH_LIMIT_ENGLISH",
    "Limited English": "ACS_PCT_HH_LIMIT_ENGLISH",
    "Limited English Proficiency": "ACS_PCT_HH_LIMIT_ENGLISH",
    "Rural Population (%)": "rural_pct",
    "Rural Population": "rural_pct",
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
        "ACS_PCT_UNINSURED", "ACS_PCT_HH_LIMIT_ENGLISH", "rural_pct",
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
            "Engineered from no-vehicle access and public transit use.",
            f"No vehicle: {no_vehicle}; Public transit use: {transit}",
            f"No vehicle median: {no_vehicle_med}; Public transit median: {transit_med}",
            f"No vehicle mean: {no_vehicle_mean}; Public transit mean: {transit_mean}"
        )

    if clean_label in ["Disease Burden", "Chronic Disease Burden"]:
        county_value, median_value, mean_value = format_variable_value(
            clean_label, "disease_burden_composite", selected, NATIONAL_MEDIAN, NATIONAL_MEAN
        )
        return (
            "Composite disease burden variable. See Disease Burden Variables below for component outcomes.",
            county_value,
            median_value,
            mean_value
        )

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

# For Urban/Semi-Urban counties, RHC and CAH variables are not shown because
# they are rural-specific resources and are not applied to HAVI scoring for NCHS 1–4 counties.
if len(factor_df) > 0 and is_urban_or_semiurban(selected):
    factor_df = factor_df[~factor_df["Factor"].isin(rural_specific_factors)].copy()

st.markdown("## Factors Contributing to This County's HAVI Score")
#st.markdown(
#    "<div class='section-subtitle'>This chart shows how each HAVI factor contributes to the selected county's overall healthcare access vulnerability profile. Factors shown in red are associated with higher healthcare access vulnerability and increase the county's HAVI score, while factors shown in green are associated with lower healthcare access vulnerability and decrease the county's HAVI score. Longer bars indicate larger relative contributions within the HAVI model.</div>",
#    unsafe_allow_html=True
#)

if len(factor_df) > 0:
    factor_df["Direction"] = factor_df["Contribution (%)"].apply(
        lambda x: "Increases HAVI Profile (factors associated with higher healthcare access vulnerability for this county)" 
        if x > 0 
        else "Decreases HAVI Profile (factors associated with lower healthcare access vulnerability for this county)"
    )

    factor_df["Direction Short"] = factor_df["Contribution (%)"].apply(
        lambda x: "Associated with Higher Healthcare Access Vulnerability" if x > 0 else "Associated with Lower Healthcare Access Vulnerability"
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
            "Increases HAVI Profile (factors associated with higher healthcare access vulnerability for this county)": "#dc2626",
            "Decreases HAVI Profile (factors associated with lower healthcare access vulnerability for this county)": "#16a34a"
        },
        title="Factors Contributing to This County's HAVI Score"
    )

    fig.add_vline(x=0, line_width=2, line_color="#111827")

    fig.update_traces(
        textposition="outside",
        cliponaxis=True,
        textfont=dict(size=16, color="#475569"),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{customdata[0]}<br>"
            "Contribution to HAVI Profile: %{x:.1f}%<br>"
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
            title=dict(text="Relative Contribution to HAVI Profile (%)", font=dict(size=22, color="#111827")),
            tickfont=dict(size=14, color="#374151"),
            range=[-x_axis_limit, x_axis_limit],
            automargin=True,
            fixedrange=True
        ),
        legend_title_text="",
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5, font=dict(size=16))
    )
    #st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True
    }
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
        "definition": "Estimated total county population, shown for context but not interpreted as a standalone HAVI vulnerability driver."
    },
    "Households Without Vehicle": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_HU_NO_VEH",
        "source": "AHRQ SDOH 2025",
        "definition": "Percentage of households without access to a vehicle. This is one input used to construct the Transportation Vulnerability variable."
    },
    "Public Transit Use": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_PUBL_TRANSIT",
        "source": "AHRQ SDOH 2025",
        "definition": "Percentage of workers using public transportation. This is used with no-vehicle access to contextualize transportation barriers."
    },
    "Transportation Vulnerability (Vehicle & Transit)": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "transport_vulnerability",
        "source": "Engineered from AHRQ SDOH 2025",
        "definition": "Combines household no-vehicle burden and public transit use to estimate transportation-related access barriers."
    },
    "Distance to Nearest Clinic": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "POS_MEDIAN_DIST_CLINIC",
        "source": "AHRF 2025",
        "definition": "Median distance from residents to the nearest outpatient clinic."
    },
    "Primary Care Provider Availability": {
        "domain": "Healthcare Supply",
        "raw": "primary_care_providers_per_10k",
        "source": "AHRF 2025",
        "definition": "Number of primary care providers per 10,000 residents."
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
        "source": "AHRF 2025",
        "definition": "Number of mental health providers per 10,000 residents."
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
        "definition": "Number of hospitals per 100,000 residents."
    },
    "Rural Health Clinic (RHC) Availability": {
        "domain": "Healthcare Supply",
        "raw": "clinics_per_100k",
        "source": "AHRF 2025",
        "definition": "Number of Rural Health Clinics (RHC) per 100,000 residents."
    },
    "Critical Access Hospital Availability": {
        "domain": "Healthcare Supply",
        "raw": "critical_access_per_100k",
        "source": "AHRF 2025",
        "definition": "Number of Critical Access Hospitals per 100,000 residents."
    },
    "FQHC Availability": {
        "domain": "Healthcare Supply",
        "raw": "POS_FQHC_RATE",
        "source": "AHRF 2025",
        "definition": "Federally Qualified Health Centers per 100,000 residents. AHRQ's original per-1,000 rate is rescaled for dashboard display only."
    },
    "Older Adults (≥65 Years)": {
        "domain": "Healthcare Demand",
        "raw": "ACS_PCT_AGE_ABOVE65",
        "source": "AHRQ SDOH 2025",
        "definition": "Percentage of residents aged 65 years or older."
    },
    "Young Children (<5 Years)": {
        "domain": "Healthcare Demand",
        "raw": "ACS_PCT_AGE_0_4",
        "source": "AHRQ SDOH 2025",
        "definition": "Percentage of residents younger than 5 years."
    },
    "Population with Disabilities": {
        "domain": "Healthcare Demand",
        "raw": "ACS_PCT_DISABLE",
        "source": "AHRQ SDOH 2025",
        "definition": "Percentage of residents reporting a disability."
    },
    "Chronic Disease Burden": {
        "domain": "Healthcare Demand",
        "raw": "disease_burden_composite",
        "source": "CDC PLACES 2025",
        "definition": "Composite index summarizing county-level chronic disease burden across selected chronic conditions."
    },
    "Population Below Poverty Level": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "pers_povty_pct_23",
        "source": "AHRQ SDOH 2025",
        "definition": "Percentage of residents living below the federal poverty level."
    },
    "Unemployment Rate": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_UNEMPLOY",
        "source": "AHRQ SDOH 2025",
        "definition": "Percentage of the labor force that is unemployed."
    },
    "Housing Cost Burden": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_RENTER_HU_COST_30PCT",
        "source": "AHRQ SDOH 2025",
        "definition": "Percentage of renter households spending at least 30% of income on housing."
    },
    "Households Without Internet": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_HH_NO_INTERNET",
        "source": "AHRQ SDOH 2025",
        "definition": "Percentage of households without internet access."
    },
    "Uninsured Population": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_UNINSURED",
        "source": "AHRQ SDOH 2025",
        "definition": "Percentage of residents without health insurance coverage."
    },
    "Rural Population (%)": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "rural_pct",
        "source": "AHRF 2025",
        "definition": "Percentage of residents living in rural areas."
    },
    "Language Access Barriers": {
        "domain": "Social or Structural Determinant of Health",
        "raw": "ACS_PCT_HH_LIMIT_ENGLISH",
        "source": "AHRQ SDOH 2025",
        "definition": "Percentage of households with limited English-speaking ability."
    }
}

st.markdown(
    """
<span style="color:#16a34a;"><b>Green</b></span> bars represent factors associated with <b>lower healthcare access vulnerability</b> and a lower HAVI score, while <span style="color:#dc2626;"><b>red</b></span> bars represent factors associated with <b>higher healthcare access vulnerability</b> and a higher HAVI score. Longer bars indicate larger relative contributions within the HAVI model. These contributions represent standardized county-level model signals rather than evidence of direct causation and should be interpreted together with the county's raw values, national medians, national means used as HAVI reference values, and local context. <b>Rural Health Clinic (RHC) Availability</b> and <b>Critical Access Hospital Availability</b> are displayed only for rural-classified counties because these rural-specific resources are not applied to HAVI scoring for Urban/Semi-Urban counties.
""",
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
        "Moderate Vulnerability": "Moderate relative healthcare access vulnerability; continued monitoring and targeted local review may be appropriate.",
        "High Vulnerability": "Elevated healthcare access vulnerability; county may warrant focused access and disease-burden planning.",
        "Very High Vulnerability": "Highest relative healthcare access vulnerability; county may warrant urgent review for resource targeting and intervention planning."
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

# -----------------------------
# HAVI variables table
# -----------------------------
st.markdown("## HAVI Variables")
st.markdown(
    '<div class="section-subtitle">County values are shown alongside the median for a typical U.S. county and the national mean used as the HAVI standardization reference.</div>',
    unsafe_allow_html=True
)

variable_rows = []

def add_row(factor, county_value, median_value, mean_value):
    meta = factor_metadata.get(factor, {})
    variable_rows.append({
        "Factor": factor,
        "County Value": county_value,
        "Typical U.S. County (Median)": median_value,
        "U.S. Average (Mean - HAVI Reference)": mean_value,
        "Definition": meta.get("definition", "Shown for county context.")
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
   # ("Healthcare Access Vulnerability Index", "HAVI", lambda r, c: fmt_score(safe_get(r, c)), lambda c: fmt_score(NATIONAL_MEDIAN.get(c, np.nan)), lambda c: fmt_score(NATIONAL_MEAN.get(c, np.nan))),
    ("Older Adults (≥65 Years)", "ACS_PCT_AGE_ABOVE65", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Young Children (<5 Years)", "ACS_PCT_AGE_0_4", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Population with Disabilities", "ACS_PCT_DISABLE", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Chronic Disease Burden", "disease_burden_composite", lambda r, c: fmt_score(safe_get(r, c)), lambda c: fmt_score(NATIONAL_MEDIAN.get(c, np.nan)), lambda c: fmt_score(NATIONAL_MEAN.get(c, np.nan))),
    ("Population Below Poverty Level", "pers_povty_pct_23", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Unemployment Rate", "ACS_PCT_UNEMPLOY", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Households Without Vehicle", "ACS_PCT_HU_NO_VEH", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Public Transit Use", "ACS_PCT_PUBL_TRANSIT", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Households Without Internet", "ACS_PCT_HH_NO_INTERNET", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Housing Cost Burden", "ACS_PCT_RENTER_HU_COST_30PCT", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Uninsured Population", "ACS_PCT_UNINSURED", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Primary Care Provider Availability", "primary_care_providers_per_10k", lambda r, c: fmt_rate(safe_get(r, c), "providers per 10,000 residents"), lambda c: median_rate(c, "providers per 10,000 residents"), lambda c: mean_rate(c, "providers per 10,000 residents")),
    ("Dentist Availability", "dentists_per_10k", lambda r, c: fmt_rate(safe_get(r, c), "dentists per 10,000 residents"), lambda c: median_rate(c, "dentists per 10,000 residents"), lambda c: mean_rate(c, "dentists per 10,000 residents")),
    ("Mental Health Provider Availability", "mental_health_providers_per_10k", lambda r, c: fmt_rate(safe_get(r, c), "mental health providers per 10,000 residents"), lambda c: median_rate(c, "mental health providers per 10,000 residents"), lambda c: mean_rate(c, "mental health providers per 10,000 residents")),
    ("Hospital Bed Capacity", "beds_per_1000", lambda r, c: fmt_count_with_rate(r, "hosp_beds_23", c, "bed", "beds", "per 1,000 residents"), lambda c: median_rate(c, "beds per 1,000 residents"), lambda c: mean_rate(c, "beds per 1,000 residents")),
    ("Hospital Availability", "hospitals_per_100k", lambda r, c: fmt_count_with_rate(r, "hosp_23", c, "hospital", "hospitals", "per 100,000 residents"), lambda c: median_rate(c, "hospitals per 100,000 residents"), lambda c: mean_rate(c, "hospitals per 100,000 residents")),
    ("Rural Health Clinic (RHC) Availability", "clinics_per_100k", lambda r, c: fmt_count_with_rate(r, "rural_hlth_clincs_24", c, "rural health clinic", "rural health clinics", "per 100,000 residents"), lambda c: median_rate(c, "clinics per 100,000 residents"), lambda c: mean_rate(c, "clinics per 100,000 residents")),
    ("Critical Access Hospital Availability", "critical_access_per_100k", lambda r, c: fmt_count_with_rate(r, "critcl_access_hosp_23", c, "critical access hospital", "critical access hospitals", "per 100,000 residents"), lambda c: median_small_rate(c, "critical access hospitals per 100,000 residents"), lambda c: mean_small_rate(c, "critical access hospitals per 100,000 residents")),
    ("FQHC Availability", "POS_FQHC_RATE", lambda r, c: fmt_fqhc_per_100k(safe_get(r, c)), lambda c: fmt_fqhc_per_100k(NATIONAL_MEDIAN.get(c, np.nan)), lambda c: fmt_fqhc_per_100k(NATIONAL_MEAN.get(c, np.nan))),
    ("Rural Population (%)", "rural_pct", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
    ("Language Access Barriers", "ACS_PCT_HH_LIMIT_ENGLISH", lambda r, c: fmt_pct(safe_get(r, c)), median_pct, mean_pct),
]

for label, col, county_formatter, median_formatter, mean_formatter in access_rows:
    if is_urban_or_semiurban(selected) and label in rural_specific_factors:
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

- **HAVI variables** are shown as county values alongside the median for a typical U.S. county and the national mean used as the HAVI standardization reference. The **Definition** column provides additional context for interpreting each variable.

- **Transportation Vulnerability (Vehicle & Transit)** is an engineered HAVI variable that combines household no-vehicle burden with public transportation use to better represent transportation-related access barriers.

- **Chronic Disease Burden** is an engineered healthcare need variable that summarizes multiple CDC PLACES chronic disease measures into a single composite index. Individual disease measures are displayed separately below under **Disease Burden Variables**.

- **Rural-specific supply variables** — Rural Health Clinic Availability and Critical Access Hospital Availability — are displayed only for rural-classified counties because they are not applied to HAVI scoring for Urban/Semi-Urban counties.
"""
)
# -----------------------------
# Disease burden variables table
# -----------------------------
st.markdown("## Disease Burden Variables")
st.markdown(
    """
    These variables come from CDC PLACES health outcome estimates and describe the observed chronic disease burden for the selected county. They are shown here as direct county values with national county medians and means for comparison.
    """
)

if len(disease_cols) > 0:
    disease_table = pd.DataFrame({
        "Disease Burden Variable": [disease_var_map[c] for c in disease_cols],
        "County Value": [fmt_pct(safe_get(selected, c)) for c in disease_cols],
        "Typical U.S. County (Median)": [fmt_pct(DISEASE_MEDIAN.get(c, np.nan)) for c in disease_cols],
        "U.S. Average (Mean - HAVI Reference)": [fmt_pct(DISEASE_MEAN.get(c, np.nan)) for c in disease_cols]
    })
    st.dataframe(disease_table, use_container_width=True, hide_index=True)
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

HAVI does not measure healthcare access using a single factor. Instead, it combines healthcare availability, population healthcare need, and social or structural conditions that may increase the risk of unmet healthcare needs.

### What HAVI Measures

HAVI includes three domains:

- **Healthcare Supply (30%)** measures the availability of healthcare resources, including primary care providers, dentists, mental health providers, hospital beds, hospitals, and Federally Qualified Health Centers. Rural Health Clinics and Critical Access Hospitals are included only for rural-classified counties to better reflect rural healthcare infrastructure.

- **Healthcare Demand (30%)** measures expected healthcare need using the proportion of older adults, children under age 5, people with disabilities, and the county's overall chronic disease burden.

- **Social and Structural Vulnerability (40%)** measures conditions that may make healthcare more difficult to obtain, including poverty, unemployment, housing cost burden, lack of internet access, lack of health insurance, limited English proficiency, rurality, transportation barriers, and distance to the nearest clinic.

### Engineered Measures

- **Transportation Vulnerability** combines the percentage of households without a vehicle with public transit availability to better identify transportation-related barriers to healthcare.

- **Chronic Disease Burden** summarizes the prevalence of multiple chronic conditions reported in the CDC PLACES dataset. It is included within the Healthcare Demand domain because greater disease burden increases the need for healthcare services.

### How HAVI Is Calculated

Variables are standardized using national county-level distributions so that measures with different units can be compared on a common scale. Each variable is aligned so that higher values consistently represent greater healthcare access vulnerability.

Variables are averaged within their respective domains and combined using the following weights:

- **30% Healthcare Supply**
- **30% Healthcare Demand**
- **40% Social and Structural Vulnerability**

Final HAVI scores are rescaled to a **0–100 national scale**, where higher scores indicate greater relative healthcare access vulnerability compared with other U.S. counties.

### Data Sources

HAVI was developed using **publicly available county-level datasets** from multiple U.S. government agencies.

- **Area Health Resources Files (AHRF) 2024–2025** – healthcare workforce, hospitals, healthcare infrastructure, and selected demographic measures.
- **Agency for Healthcare Research and Quality (AHRQ) Social Determinants of Health Database 2025** – social determinants of health, healthcare access, and population characteristics.
- **Centers for Disease Control and Prevention (CDC) PLACES 2025** – county-level chronic disease prevalence estimates used to develop the Chronic Disease Burden measure.
- **National Center for Health Statistics (NCHS)** – urban-rural county classification used to account for differences in rural healthcare infrastructure.
- **HRSA Data Warehouse** – countywide Medically Underserved Area (MUA) designation and Index of Medical Underservice (IMU) scores used for HAVI validation.

All datasets are publicly available and contain county-level information for the United States. The underlying data used in HAVI reflect information available through **2023**.
""")

# -----------------------------
# Interpretation / use
# -----------------------------
st.markdown("## How to Use This Dashboard")

st.markdown(
    """
    HAVI is intended to support public health planning, community needs assessment, grant development, resource prioritization, and communication about county-level healthcare access vulnerability.

    **Higher HAVI scores** indicate counties where limited healthcare resources, greater healthcare need, and social or structural barriers may combine to create greater difficulty accessing timely care.

    **Lower HAVI scores** indicate comparatively lower healthcare access vulnerability.

    **Recommended use:** HAVI should be used as a screening and planning tool to identify counties that may benefit from closer review, additional local assessment, or targeted healthcare access interventions.

    **Important limitations:** HAVI describes relative county-level patterns and does not measure individual access to care. It should not be interpreted as a clinical tool, a definitive designation of medical underservice, or proof that any individual factor caused a county's outcomes. Results should be interpreted alongside local data, community knowledge, stakeholder input, and other established measures of healthcare access.
    """
)

st.info(
    """
    **Project Disclosure**

    HAVI was developed by **Ali Abidi** as an independent high school research project using publicly available data from multiple U.S. government agencies.

    The methodology was designed to support research, education, community health assessment, and public health planning. HAVI is intended to complement—not replace—local expertise, community assessment, and established public health resources. It should not be used as the sole basis for clinical, funding, policy, or resource-allocation decisions.
    """
)
