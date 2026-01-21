import streamlit as st
import re
import os
import pandas as pd
import yfinance as yf
import altair as alt
import requests
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metals.Dev API Key (get free key at https://metals.dev)
METALS_DEV_API_KEY = os.environ.get('METALS_DEV_API_KEY', '')

# --- 1. CONFIG & DESIGN ---
st.set_page_config(page_title="Battery Valuator", page_icon="🔋", layout="wide")

# OPTION 1: MODERN FINTECH DESIGN (Clean, Rounded, Floating Cards)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Background */
    .stApp {
        background-color: #FAFAFA; /* Slightly off-white */
        color: #1a1a1a;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E5E5;
    }

    /* Cards (Metrics) - The "Floating" Look */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #F0F0F0;
    }
    
    /* Green Metric Text */
    [data-testid="stMetricValue"] {
        color: #1B5E20 !important;
        font-weight: 700;
    }

    /* Buttons - Soft & Round */
    div.stButton > button {
        background-color: #1B5E20;
        color: white;
        border-radius: 25px; /* Pill shape */
        padding: 0.5rem 2rem;
        border: none;
        box-shadow: 0 4px 14px 0 rgba(27, 94, 32, 0.39);
        transition: transform 0.2s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        background-color: #2E7D32;
    }

    /* Inputs - Cleaner Borders */
    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #E0E0E0;
    }
    </style>
    """, unsafe_allow_html=True)

# HEADER WITH LOGO
col_logo, col_title = st.columns([2, 5]) 

with col_logo:
    try:
        st.image("Battery Valuator.png", width=350)
    except:
        st.markdown("# 🔋") 

with col_title:
    st.title("Battery Valuator")
    st.caption("Accurate Battery Material Valuations")

# Stoichiometry (Metal to Salt Conversion Factors)
# These factors convert pure metal mass to salt mass
# E.g., 1kg of Ni metal → 4.48kg of NiSO4·6H2O (including water of hydration)
FACTORS = {
    "Ni_to_Sulphate": 4.48,      # Ni → NiSO4·6H2O
    "Co_to_Sulphate": 4.77,      # Co → CoSO4·7H2O
    "Li_to_Carbonate": 5.32,     # Li → Li2CO3
    "Li_to_Hydroxide": 6.05      # Li → LiOH·H2O
}

# --- 2. LIVE DATA ENGINE ---
def fetch_metals_dev_prices():
    """
    Fetch LME metal prices from Metals.Dev API.

    Returns:
        dict: Metal prices in USD per tonne, or None if fetch fails
    """
    if not METALS_DEV_API_KEY:
        logger.warning("METALS_DEV_API_KEY not set, skipping Metals.Dev fetch")
        return None

    try:
        url = f"https://api.metals.dev/v1/metal/authority?api_key={METALS_DEV_API_KEY}&authority=lme"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            logger.warning(f"Metals.Dev API returned status {response.status_code}")
            return None

        data = response.json()
        if data.get('status') != 'success':
            logger.warning(f"Metals.Dev API error: {data.get('error_message', 'Unknown error')}")
            return None

        prices = {}
        metals = data.get('metals', {})

        if 'lme_nickel' in metals:
            prices['Ni'] = metals['lme_nickel']
            logger.info(f"Nickel (Metals.Dev): ${prices['Ni']:.2f}/tonne")

        if 'lme_copper' in metals:
            prices['Cu'] = metals['lme_copper']
            logger.info(f"Copper (Metals.Dev): ${prices['Cu']:.2f}/tonne")

        if 'lme_aluminum' in metals:
            prices['Al'] = metals['lme_aluminum']
            logger.info(f"Aluminum (Metals.Dev): ${prices['Al']:.2f}/tonne")

        return prices if prices else None

    except requests.exceptions.Timeout:
        logger.warning("Metals.Dev API request timed out")
        return None
    except Exception as e:
        logger.error(f"Metals.Dev API fetch failed: {str(e)}")
        return None

def fetch_metals_dev_currencies(base_currency="USD"):
    """
    Fetch currency exchange rates from Metals.Dev API.
    """
    if not METALS_DEV_API_KEY:
        return None

    try:
        url = f"https://api.metals.dev/v1/currencies?api_key={METALS_DEV_API_KEY}&base={base_currency}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()
        if data.get('status') != 'success':
            return None

        return data.get('currencies', {})

    except Exception as e:
        logger.error(f"Metals.Dev currencies fetch failed: {str(e)}")
        return None

def fetch_yfinance_prices():
    """
    Fallback: Fetch metal prices from yfinance futures.
    Only works for Copper and Aluminum.
    """
    try:
        prices = {}

        # Fetch Copper via futures
        try:
            cu_ticker = yf.Ticker("HG=F")
            cu_hist = cu_ticker.history(period="1d")
            if not cu_hist.empty:
                cu_price_lb = cu_hist['Close'].iloc[-1]
                prices["Cu"] = cu_price_lb * 2204.62
                logger.info(f"Copper (yfinance): ${prices['Cu']:.2f}/tonne")
        except Exception as e:
            logger.warning(f"Copper price fetch failed: {str(e)}")

        # Fetch Aluminum via futures
        try:
            al_ticker = yf.Ticker("ALI=F")
            al_hist = al_ticker.history(period="1d")
            if not al_hist.empty:
                prices["Al"] = al_hist['Close'].iloc[-1]
                logger.info(f"Aluminum (yfinance): ${prices['Al']:.2f}/tonne")
        except Exception as e:
            logger.warning(f"Aluminum price fetch failed: {str(e)}")

        return prices if prices else None

    except Exception as e:
        logger.error(f"yfinance metal price fetch failed: {str(e)}")
        return None

def fetch_yfinance_fx(target_currency):
    """
    Fallback: Fetch FX rate from yfinance.
    """
    if target_currency == "USD":
        return 1.0

    try:
        ticker = f"{target_currency}=X"
        hist = yf.Ticker(ticker).history(period="1d")
        if not hist.empty:
            rate = hist['Close'].iloc[-1]
            logger.info(f"FX rate (yfinance): 1 USD = {rate:.4f} {target_currency}")
            return rate
    except Exception as e:
        logger.warning(f"yfinance FX fetch failed: {str(e)}")

    return None

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_market_data(target_currency):
    """
    Fetch current market data including FX rates and metal prices.

    Priority order:
    1. Metals.Dev API (best source for LME prices + FX)
    2. yfinance (fallback for Cu, Al futures + FX)
    3. Static fallback prices

    Args:
        target_currency: Target currency code (USD, CAD, EUR, CNY)

    Returns:
        dict: Market data including FX rate and metal prices per kg
    """
    data = {}
    fx_fallback_used = False
    price_source = "fallback"

    # Static fallback rates (approximate, as of Jan 2025)
    fallback_fx_rates = {"CAD": 1.40, "EUR": 0.92, "CNY": 7.25, "USD": 1.0}

    # A. CURRENCY CONVERSION
    fx = None

    # Try Metals.Dev first for FX rates
    if METALS_DEV_API_KEY:
        currencies = fetch_metals_dev_currencies("USD")
        if currencies and target_currency.lower() in currencies:
            fx = currencies[target_currency.lower()]
            logger.info(f"FX rate (Metals.Dev): 1 USD = {fx:.4f} {target_currency}")

    # Fallback to yfinance for FX
    if fx is None and target_currency != "USD":
        fx = fetch_yfinance_fx(target_currency)

    # Final fallback to static rates
    if fx is None:
        fx = fallback_fx_rates.get(target_currency, 1.0)
        fx_fallback_used = True
        if target_currency != "USD":
            logger.warning(f"Using fallback FX rate for {target_currency}: {fx}")

    data['FX'] = fx
    data['fx_fallback_used'] = fx_fallback_used
    data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # B. METAL PRICES (Base prices in USD per tonne)
    # Fallback prices (used if all live fetches fail)
    base_prices_usd = {
        "Ni": 16500.00,   # LME Nickel 3-month ($/tonne)
        "Co": 33000.00,   # Fastmarkets Cobalt Standard Grade ($/tonne)
        "Li": 13500.00,   # China Lithium Carbonate Spot ($/tonne)
        "Cu": 9200.00,    # LME Copper 3-month ($/tonne)
        "Al": 2500.00,    # LME Aluminum 3-month ($/tonne)
        "Mn": 1800.00,    # Manganese Metal 99.7% ($/tonne)
        "NiSO4": 3800.00, # Battery-grade Nickel Sulphate ($/tonne)
        "CoSO4": 6500.00, # Battery-grade Cobalt Sulphate ($/tonne)
        "LCE": 14000.00,  # Lithium Carbonate Equivalent ($/tonne)
        "LiOH": 15500.00  # Lithium Hydroxide Monohydrate ($/tonne)
    }

    # Try Metals.Dev first (best source for Ni, Cu, Al)
    metals_dev_prices = fetch_metals_dev_prices()
    if metals_dev_prices:
        base_prices_usd.update(metals_dev_prices)
        price_source = "metals.dev"
        logger.info(f"Using {len(metals_dev_prices)} prices from Metals.Dev")

    # Fallback to yfinance for Cu and Al if not already fetched
    if 'Cu' not in (metals_dev_prices or {}) or 'Al' not in (metals_dev_prices or {}):
        yfinance_prices = fetch_yfinance_prices()
        if yfinance_prices:
            for metal, price in yfinance_prices.items():
                if metal not in (metals_dev_prices or {}):
                    base_prices_usd[metal] = price
                    if price_source == "fallback":
                        price_source = "yfinance"
            logger.info(f"Using {len(yfinance_prices)} prices from yfinance")

    data['price_source'] = price_source

    # Convert from $/tonne to $/kg in target currency
    for key, price_usd_ton in base_prices_usd.items():
        price_per_kg = (price_usd_ton / 1000.0) * fx
        data[key] = price_per_kg

    return data

# --- 3. PARSER ---
def parse_coa_text(text):
    """
    Parse certificate of analysis (COA) text to extract metal assay values.

    Handles various input formats:
    - Percentages (e.g., "Ni: 20.5%")
    - Basis points (e.g., "Ni 2050" → 20.5%)
    - Decimal notation (e.g., "Ni 0.205" → 20.5%)

    Args:
        text: Raw text from COA (email, PDF, etc.)

    Returns:
        dict: Metal assays as decimals (e.g., 0.205 for 20.5%)
    """
    assays = {"Nickel": 0.0, "Cobalt": 0.0, "Lithium": 0.0, "Copper": 0.0, "Aluminum": 0.0, "Manganese": 0.0}
    text = text.lower().replace(",", "")

    target_map = {
        "Nickel": ["ni", "nickel"],
        "Cobalt": ["co", "cobalt"],
        "Lithium": ["li", "lithium"],
        "Copper": ["cu", "copper"],
        "Aluminum": ["al", "aluminum", "aluminium"],
        "Manganese": ["mn", "manganese"]
    }

    for line in text.split('\n'):
        for metal, keywords in target_map.items():
            for kw in keywords:
                if re.search(rf"\b{kw}", line):
                    match = re.search(r"(\d+\.?\d*)", line.replace(kw, ""))
                    if match:
                        val = float(match.group(1))
                        # Handle basis points (e.g., 2050 → 20.5%)
                        if val > 100:
                            assays[metal] = val / 10000.0
                        # Handle percentages (e.g., 20.5 → 20.5%)
                        else:
                            assays[metal] = val / 100.0
                        logger.info(f"Parsed {metal}: {assays[metal]*100:.2f}%")

    return assays

# --- 4. SIDEBAR ---
with st.sidebar:
    try:
        st.image("Battery Valuator.png", width=400)
    except FileNotFoundError:
        st.write("## Battery Valuator")
        logger.warning("Logo image not found")

# === GLOBAL SETTINGS ===
st.sidebar.header("Global Settings")
currency = st.sidebar.selectbox("Currency", ["CAD", "USD", "EUR", "CNY"])
market_data = get_market_data(currency)

# Display pricing timestamp and warnings
if market_data.get('fx_fallback_used', False):
    st.sidebar.warning("⚠️ Using fallback prices - market data unavailable")

st.sidebar.caption(f"📅 Prices as of: {market_data.get('timestamp', 'Unknown')}")

if st.sidebar.button("🔄 Refresh Prices"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

# === SECTION 1: FEEDSTOCK & PRE-TREATMENT ===
st.sidebar.header("1. Feedstock & Pre-treatment")

feed_type = st.sidebar.selectbox("Material Type", 
    ["Black Mass (Processed)", "Cathode Foils", "Cell Stacks / Jelly Rolls", "Whole Cells", "Modules", "Battery Packs"])

# A. Electrolyte Logic
has_electrolyte = st.sidebar.checkbox("⚠️ Contains Electrolyte", value=False)
elec_surcharge = 0.0
if has_electrolyte:
    elec_surcharge = st.sidebar.number_input(f"Surcharge ({currency}/MT)", value=150.0, step=10.0)

# B. Mechanical / Shredding Cost
shredding_cost_per_ton = 0.0
if feed_type != "Black Mass (Processed)":
    shredding_cost_per_ton = st.sidebar.number_input(f"Mechanical/Shred Cost ({currency}/MT)", value=300.0)

# C. Yields & Mechanical Recovery
defaults = {
    "Black Mass (Processed)": 100, "Cathode Foils": 90,
    "Cell Stacks / Jelly Rolls": 70, "Whole Cells": 60,
    "Modules": 50, "Battery Packs": 40
}

yield_pct = st.sidebar.slider(f"Black Mass Yield (%)", min_value=10, max_value=100, value=defaults[feed_type]) / 100.0

# Mechanical Recovery Slider (Shredding Efficiency)
mech_recovery = 1.0 
if feed_type != "Black Mass (Processed)":
    mech_recovery = st.sidebar.slider("Mechanical Recovery (%)", min_value=80, max_value=100, value=95) / 100.0

gross_weight = st.sidebar.number_input(f"Total Gross Weight (kg)", value=1000.0, min_value=0.0, step=100.0)

# Validate gross weight
if gross_weight <= 0:
    st.sidebar.error("⚠️ Gross weight must be greater than 0")

net_bm_weight = gross_weight * yield_pct
st.sidebar.caption(f"📉 **Recoverable Black Mass:** {net_bm_weight:,.1f} kg")

# === SECTION 2: PRICING (Buying) ===
st.sidebar.markdown("---")
st.sidebar.header("2. Pricing (Buying)")

st.sidebar.caption(f"**Primary Metal Prices ({currency}/kg)**")
c1, c2 = st.sidebar.columns(2)
ni_base = c1.number_input("Ni Price", value=float(f"{market_data['Ni']:.2f}"), min_value=0.0, step=1.0)
c2.caption(f"Live: {market_data['Ni']:.2f}")

c1, c2 = st.sidebar.columns(2)
co_base = c1.number_input("Co Price", value=float(f"{market_data['Co']:.2f}"), min_value=0.0, step=1.0)
c2.caption(f"Live: {market_data['Co']:.2f}")

c1, c2 = st.sidebar.columns(2)
li_base = c1.number_input("Li Price", value=float(f"{market_data['Li']:.2f}"), min_value=0.0, step=1.0)
c2.caption(f"Live: {market_data['Li']:.2f}")

st.sidebar.caption(f"**Secondary Metal Prices ({currency}/kg)**")
c1, c2 = st.sidebar.columns(2)
cu_base = c1.number_input("Cu Price", value=float(f"{market_data['Cu']:.2f}"), min_value=0.0, step=0.5)
c2.caption(f"Live: {market_data['Cu']:.2f}")

c1, c2 = st.sidebar.columns(2)
al_base = c1.number_input("Al Price", value=float(f"{market_data['Al']:.2f}"), min_value=0.0, step=0.1)
c2.caption(f"Live: {market_data['Al']:.2f}")

c1, c2 = st.sidebar.columns(2)
mn_base = c1.number_input("Mn Price", value=float(f"{market_data['Mn']:.2f}"), min_value=0.0, step=0.1)
c2.caption(f"Live: {market_data['Mn']:.2f}")

st.sidebar.caption("**Payables (%)**")
c1, c2, c3 = st.sidebar.columns(3)
ni_pay_feed = c1.number_input("Ni Payable", value=80.0, min_value=0.0, max_value=100.0, step=5.0) / 100
co_pay_feed = c2.number_input("Co Payable", value=75.0, min_value=0.0, max_value=100.0, step=5.0) / 100
li_pay_feed = c3.number_input("Li Payable", value=30.0, min_value=0.0, max_value=100.0, step=5.0) / 100

c1, c2, c3 = st.sidebar.columns(3)
cu_pay_feed = c1.number_input("Cu Payable", value=80.0, min_value=0.0, max_value=100.0, step=5.0) / 100
al_pay_feed = c2.number_input("Al Payable", value=70.0, min_value=0.0, max_value=100.0, step=5.0) / 100
mn_pay_feed = c3.number_input("Mn Payable", value=60.0, min_value=0.0, max_value=100.0, step=5.0) / 100

# === SECTION 3: REFINING (Post-Treatment) ===
st.sidebar.markdown("---")
st.sidebar.header("3. Refining (Hydromet)")

ni_product = st.sidebar.selectbox("Ni/Co Product", ["Sulphates (Battery Salt)", "MHP (Intermediate)"])
li_product = st.sidebar.selectbox("Li Product", ["Carbonate (LCE)", "Hydroxide (LiOH)"])
refining_opex_base = st.sidebar.number_input(f"Refining OPEX ({currency}/MT BM)", value=1500.0, min_value=0.0, step=100.0)

# Hydromet Recovery Slider
hydromet_recovery = st.sidebar.slider("Refining Recovery (%)", min_value=80, max_value=100, value=95) / 100.0
st.sidebar.caption("Cost applied to Net Black Mass Weight only.")

# Market Prices & Recoveries (Hidden Vars)
price_ni_sulf = market_data['NiSO4']
price_co_sulf = market_data['CoSO4']
price_li_salt = market_data['LCE'] if li_product == "Carbonate (LCE)" else market_data['LiOH']
mhp_pay_ni = 0.85
mhp_pay_co = 0.80

rec_ni = hydromet_recovery
rec_co = hydromet_recovery
rec_li = hydromet_recovery * 0.90 

# --- 5. MAIN APP (DASHBOARD LAYOUT) ---

# A. THE "TICKER" HEADER
st.markdown("---")
with st.container():
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"**MATERIAL:** \n{feed_type}")
    c2.markdown(f"**GROSS WEIGHT:** \n{gross_weight:,.0f} kg")
    c3.markdown(f"**NET BLACK MASS:** \n{net_bm_weight:,.0f} kg ({yield_pct*100:.0f}% Yield)")
    c4.markdown(f"**RECOVERY:** \nMech: {mech_recovery*100:.0f}% | Hydro: {hydromet_recovery*100:.0f}%")
st.markdown("---")

# B. THE WORKSPACE (3 Columns)
col_input, col_metrics, col_chart = st.columns([1, 1.2, 1.5])

with col_input:
    st.markdown("### 1. Lab Assay")
    assay_basis = st.radio(
        "Sample Source", 
        ["Whole Battery", "Final Powder"],
        horizontal=False,
        help="Select 'Whole Battery' to trigger Enrichment Math. Select 'Final Powder' if your numbers are already from the Black Mass."
    )
    
    default_text = "Ni: 20.5%\nCo: 6.2%\nLi: 2.5%\nCu: 3.5%\nAl: 1.2%\nMn: 4.8%"
    coa_text = st.text_area("Paste Results", height=200, value=default_text, help="Paste text from email/PDF")
    
    calc_btn = st.button("RUN VALUATION ➤", type="primary")

# LOGIC BLOCK
if calc_btn:
    assays = parse_coa_text(coa_text)

    # VALIDATION: Check if assay values were successfully parsed
    if all(v == 0.0 for v in assays.values()):
        st.error("⚠️ Could not parse assay values. Please check input format.")
        st.stop()

    # 1. MASS BALANCE
    bm_ni_grade, bm_co_grade, bm_li_grade = 0.0, 0.0, 0.0
    bm_cu_grade, bm_al_grade, bm_mn_grade = 0.0, 0.0, 0.0

    if assay_basis == "Whole Battery":
        mass_ni = (gross_weight * assays["Nickel"]) * mech_recovery
        mass_co = (gross_weight * assays["Cobalt"]) * mech_recovery
        mass_li = (gross_weight * assays["Lithium"]) * mech_recovery
        mass_cu = (gross_weight * assays["Copper"]) * mech_recovery
        mass_al = (gross_weight * assays["Aluminum"]) * mech_recovery
        mass_mn = (gross_weight * assays["Manganese"]) * mech_recovery

        if net_bm_weight > 0:
            bm_ni_grade = (mass_ni / net_bm_weight) * 100
            bm_co_grade = (mass_co / net_bm_weight) * 100
            bm_li_grade = (mass_li / net_bm_weight) * 100
            bm_cu_grade = (mass_cu / net_bm_weight) * 100
            bm_al_grade = (mass_al / net_bm_weight) * 100
            bm_mn_grade = (mass_mn / net_bm_weight) * 100
    else:
        mass_ni = net_bm_weight * assays["Nickel"]
        mass_co = net_bm_weight * assays["Cobalt"]
        mass_li = net_bm_weight * assays["Lithium"]
        mass_cu = net_bm_weight * assays["Copper"]
        mass_al = net_bm_weight * assays["Aluminum"]
        mass_mn = net_bm_weight * assays["Manganese"]
        bm_ni_grade = assays["Nickel"] * 100
        bm_co_grade = assays["Cobalt"] * 100
        bm_li_grade = assays["Lithium"] * 100
        bm_cu_grade = assays["Copper"] * 100
        bm_al_grade = assays["Aluminum"] * 100
        bm_mn_grade = assays["Manganese"] * 100

    # VALIDATION: Check for unrealistic assay values in black mass
    # Typical black mass ranges: Ni (10-60%), Co (3-25%), Li (1-10%)
    warnings = []
    if bm_ni_grade > 60:
        warnings.append(f"Nickel grade ({bm_ni_grade:.1f}%) exceeds typical black mass range (10-60%)")
    if bm_co_grade > 25:
        warnings.append(f"Cobalt grade ({bm_co_grade:.1f}%) exceeds typical black mass range (3-25%)")
    if bm_li_grade > 10:
        warnings.append(f"Lithium grade ({bm_li_grade:.1f}%) exceeds typical black mass range (1-10%)")
    if bm_ni_grade + bm_co_grade + bm_li_grade > 100:
        warnings.append(f"Total metal content ({bm_ni_grade + bm_co_grade + bm_li_grade:.1f}%) exceeds 100%")

    if warnings:
        st.warning("⚠️ **Unusual assay values detected - please verify input:**\n\n" + "\n\n".join([f"• {w}" for w in warnings]))

    # 2. COSTS
    cost_ni = mass_ni * ni_base * ni_pay_feed
    cost_co = mass_co * co_base * co_pay_feed
    cost_li = mass_li * li_base * li_pay_feed
    cost_cu = mass_cu * cu_base * cu_pay_feed
    cost_al = mass_al * al_base * al_pay_feed
    cost_mn = mass_mn * mn_base * mn_pay_feed
    material_cost = cost_ni + cost_co + cost_li + cost_cu + cost_al + cost_mn
    
    # PRE-CALCULATIONS (Pulled from top section)
    cost_shred = (gross_weight / 1000.0) * shredding_cost_per_ton
    cost_electrolyte = 0
    if has_electrolyte:
        cost_electrolyte = (gross_weight / 1000.0) * elec_surcharge
    total_pre_treat = cost_shred + cost_electrolyte
    
    total_refining_cost = (net_bm_weight / 1000.0) * refining_opex_base
    total_opex = total_pre_treat + total_refining_cost
    
    # 3. REVENUE
    production_data = [] 
    if ni_product == "Sulphates (Battery Salt)":
        qty_ni_prod = mass_ni * rec_ni * FACTORS["Ni_to_Sulphate"]
        rev_ni = qty_ni_prod * price_ni_sulf
        production_data.append(["Nickel Sulphate", qty_ni_prod, rev_ni])
        qty_co_prod = mass_co * rec_co * FACTORS["Co_to_Sulphate"]
        rev_co = qty_co_prod * price_co_sulf
        production_data.append(["Cobalt Sulphate", qty_co_prod, rev_co])
    else: 
        qty_ni_prod = mass_ni * rec_ni
        rev_ni = qty_ni_prod * ni_base * mhp_pay_ni
        production_data.append(["MHP (Ni Content)", qty_ni_prod, rev_ni])
        qty_co_prod = mass_co * rec_co
        rev_co = qty_co_prod * co_base * mhp_pay_co
        production_data.append(["MHP (Co Content)", qty_co_prod, rev_co])

    factor_li = FACTORS["Li_to_Carbonate"] if li_product == "Carbonate (LCE)" else FACTORS["Li_to_Hydroxide"]
    qty_li_prod = mass_li * rec_li * factor_li
    rev_li = qty_li_prod * price_li_salt
    production_data.append([li_product, qty_li_prod, rev_li])
    
    total_rev = rev_ni + rev_co + rev_li
    net_profit = total_rev - material_cost - total_opex
    margin_pct = (net_profit / total_rev) * 100 if total_rev > 0 else 0

    # === DISPLAY: METRICS COLUMN ===
    with col_metrics:
        st.markdown("### 2. Valuation")
        st.metric("PROFIT", f"${net_profit:,.0f}", delta=f"{margin_pct:.1f}% Margin")
        st.write("") 
        st.metric("Total Revenue", f"${total_rev:,.0f}")
        st.metric("Material Cost", f"${material_cost:,.0f}", delta_color="inverse")
        st.metric("Total OPEX", f"${total_opex:,.0f}", delta_color="inverse")

    # === DISPLAY: CHART COLUMN ===
    with col_chart:
        st.markdown("### 3. Financial Split")
        chart_data = pd.DataFrame({
            "Category": ["Material", "Pre-Treat", "Refining", "PROFIT"],
            "Amount": [material_cost, total_pre_treat, total_refining_cost, net_profit],
            "Color": ["#B71C1C", "#D32F2F", "#F44336", "#1B5E20"] 
        })
        
        # Clean Chart Design
        c = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X('Category', sort=None, axis=alt.Axis(labelAngle=0, title=None)), 
            y=alt.Y('Amount', axis=alt.Axis(grid=False, format='$,.0f')), 
            color=alt.Color('Color', scale=None), 
            tooltip=['Category', alt.Tooltip('Amount', format='$,.0f')]
        ).properties(height=300).configure_view(strokeWidth=0)
        
        st.altair_chart(c, use_container_width=True)
        
    # === C. BOTTOM TABLE ===
    st.markdown("### 4. Product Schedule")
    prod_df = pd.DataFrame(production_data, columns=["Product", "Mass (kg)", "Revenue"])
    total_mass_prod = prod_df["Mass (kg)"].sum()
    new_row = {"Product": "TOTAL", "Mass (kg)": total_mass_prod, "Revenue": total_rev}
    prod_df = pd.concat([prod_df, pd.DataFrame([new_row])], ignore_index=True)
    
    st.dataframe(prod_df.style.format({"Mass (kg)": "{:,.0f}", "Revenue": "${:,.0f}"}), use_container_width=True, hide_index=True)
    
    st.caption(f"ℹ️ Effective Grade: Ni {bm_ni_grade:.1f}% | Co {bm_co_grade:.1f}% | Li {bm_li_grade:.1f}% | Cu {bm_cu_grade:.1f}% | Al {bm_al_grade:.1f}% | Mn {bm_mn_grade:.1f}%")

else:
    # Placeholder when app first loads
    with col_metrics:
        st.info("👈 Enter Assay & Click RUN")