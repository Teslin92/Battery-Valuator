import streamlit as st
import re
import pandas as pd
import yfinance as yf

# --- 1. CONFIG & STOICHIOMETRY ---
st.set_page_config(page_title="Refinery Pro (Live)", layout="wide")
st.title("🏭 Integrated Refinery: Live Market Edition")

# Stoichiometry
FACTORS = {
    "Ni_to_Sulphate": 4.48, "Co_to_Sulphate": 4.77,   
    "Li_to_Carbonate": 5.32, "Li_to_Hydroxide": 6.05   
}

# --- 2. LIVE DATA ENGINE ---
# Added this decorator so the "Refresh" button actually works
@st.cache_data
def get_market_data(target_currency):
    """
    Fetches Live FX and Estimates Metal Prices.
    """
    data = {}
    
    # A. FX RATES (Real Live Data via Yahoo)
    try:
        if target_currency == "USD":
            fx = 1.0
        else:
            ticker = f"{target_currency}=X" 
            # Get data
            hist = yf.Ticker(ticker).history(period="1d")
            if not hist.empty:
                fx = hist['Close'].iloc[-1]
            else:
                fx = 1.0 # Fallback
    except:
        fx = 1.40 if target_currency == "CAD" else 1.0 # Fallback
    
    data['FX'] = fx

    # B. METAL PROXIES (Base prices in USD)
    base_prices_usd = {
        "Ni": 16500.00,  # LME Nickel Approx
        "Co": 33000.00,  # Fastmarkets Cobalt Approx
        "Li": 13500.00,  # China Carbonate Spot Approx
        "NiSO4": 3800.00, # Spot Sulphate
        "CoSO4": 6500.00, # Spot Sulphate
        "LCE": 14000.00,  # Carbonate Spot
        "LiOH": 15500.00  # Hydroxide Spot
    }
    
    # Convert to Target Currency and kg (LME is usually per Tonne)
    for key, price_usd_ton in base_prices_usd.items():
        price_per_kg = (price_usd_ton / 1000.0) * fx
        data[key] = price_per_kg

    return data

# --- 3. PARSER ---
def parse_coa_text(text):
    assays = {"Nickel": 0.0, "Cobalt": 0.0, "Lithium": 0.0, "Copper": 0.0, "Aluminum": 0.0, "Graphite": 0.0}
    text = text.lower().replace(",", "") 
    target_map = {
        "Nickel": ["ni", "nickel"], "Cobalt": ["co", "cobalt"], "Lithium": ["li", "lithium"],
        "Copper": ["cu", "copper"], "Aluminum": ["al", "aluminum"], "Graphite": ["graphite", "carbon", "c "]
    }
    for line in text.split('\n'):
        for metal, keywords in target_map.items():
            for kw in keywords:
                if re.search(rf"\b{kw}", line):
                    match = re.search(r"(\d+\.?\d*)", line.replace(kw, ""))
                    if match:
                        val = float(match.group(1))
                        if val > 100: assays[metal] = val / 10000.0 / 100.0
                        else: assays[metal] = val / 100.0
    return assays

# --- 4. SIDEBAR ---

# === GLOBAL SETTINGS ===
st.sidebar.header("1. Global Settings")
currency = st.sidebar.selectbox("Display Currency", ["CAD", "USD", "EUR", "CNY"])
market_data = get_market_data(currency)

# Show the Live Status
st.sidebar.caption(f"**Live FX:** 1 USD = {market_data['FX']:.4f} {currency}")
if st.sidebar.button("🔄 Refresh Market Data"):
    st.cache_data.clear()

# === UPSTREAM ===
st.sidebar.markdown("---")
st.sidebar.header("2. Feedstock (Buying)")

batch_name = st.sidebar.text_input("Batch ID", "Lot-2025-A")
total_weight_kg = st.sidebar.number_input(f"Total Weight (kg)", value=1000.0)

st.sidebar.caption(f"**Metal Prices ({currency}/kg)**")

c1, c2 = st.sidebar.columns(2)
# No min_value or max_value set. Type whatever you want.
ni_base = c1.number_input("Ni Price", value=float(f"{market_data['Ni']:.2f}"))
c2.caption(f"Live: {market_data['Ni']:.2f}")

c1, c2 = st.sidebar.columns(2)
co_base = c1.number_input("Co Price", value=float(f"{market_data['Co']:.2f}"))
c2.caption(f"Live: {market_data['Co']:.2f}")

c1, c2 = st.sidebar.columns(2)
li_base = c1.number_input("Li Price", value=float(f"{market_data['Li']:.2f}"))
c2.caption(f"Live: {market_data['Li']:.2f}")

st.sidebar.caption("**Payables (%)**")
c1, c2, c3 = st.sidebar.columns(3)
# These inputs take the number you type (e.g. 105) and divide by 100 for the math
ni_pay_feed = c1.number_input("Ni Pay", value=80.0) / 100
co_pay_feed = c2.number_input("Co Pay", value=75.0) / 100
li_pay_feed = c3.number_input("Li Pay", value=30.0) / 100

# === DOWNSTREAM ===
st.sidebar.markdown("---")
st.sidebar.header("3. Refining Strategy")
ni_product = st.sidebar.selectbox("Ni/Co Product", ["Sulphates (Battery Salt)", "MHP (Intermediate)"])
li_product = st.sidebar.selectbox("Li Product", ["Carbonate (LCE)", "Hydroxide (LiOH)"])

st.sidebar.subheader(f"Sales Pricing ({currency})")

# DYNAMIC PRICING INPUTS
price_ni_sulf = 0
price_co_sulf = 0
mhp_pay_ni = 0
mhp_pay_co = 0

if ni_product == "Sulphates (Battery Salt)":
    c1, c2 = st.sidebar.columns(2)
    price_ni_sulf = c1.number_input("NiSO4 Price", value=float(f"{market_data['NiSO4']:.2f}"))
    c2.caption(f"Ref: {market_data['NiSO4']:.2f}")

    c1, c2 = st.sidebar.columns(2)
    price_co_sulf = c1.number_input("CoSO4 Price", value=float(f"{market_data['CoSO4']:.2f}"))
    c2.caption(f"Ref: {market_data['CoSO4']:.2f}")
else:
    st.sidebar.info("MHP Pricing (Payable Basis)")
    c1, c2 = st.sidebar.columns(2)
    c1.number_input("Ni Ref", value=ni_base, disabled=True, label_visibility="collapsed")
    mhp_pay_ni = c2.number_input("MHP Ni Pay %", value=85.0) / 100
    
    c1, c2 = st.sidebar.columns(2)
    c1.number_input("Co Ref", value=co_base, disabled=True, label_visibility="collapsed")
    mhp_pay_co = c2.number_input("MHP Co Pay %", value=80.0) / 100

c1, c2 = st.sidebar.columns(2)
if li_product == "Carbonate (LCE)":
    price_li_salt = c1.number_input("LCE Price", value=float(f"{market_data['LCE']:.2f}"))
    c2.caption(f"Ref: {market_data['LCE']:.2f}")
else:
    price_li_salt = c1.number_input("LiOH Price", value=float(f"{market_data['LiOH']:.2f}"))
    c2.caption(f"Ref: {market_data['LiOH']:.2f}")

# OPEX
st.sidebar.markdown("---")
refining_opex = st.sidebar.number_input(f"Refining OPEX ({currency}/MT Feed)", value=1500.0)
rec_ni = st.sidebar.number_input("Ni Rec %", value=95.0) / 100
rec_co = st.sidebar.number_input("Co Rec %", value=95.0) / 100
rec_li = st.sidebar.number_input("Li Rec %", value=85.0) / 100

# --- 5. MAIN APP ---

# Header Metrics (Live Data)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Selected Currency", currency)
m2.metric("Exchange Rate", f"1 USD = {market_data['FX']:.3f} {currency}")
m3.metric("LME Nickel (Ref)", f"{market_data['Ni']:.2f} /kg")
m4.metric("LME Cobalt (Ref)", f"{market_data['Co']:.2f} /kg")

st.divider()

col_left, col_right = st.columns([1, 1])
with col_left:
    st.info("📋 **Paste Lab Results (CoA)**")
    default_text = "Ni: 22.5%\nCo: 7.2%\nLi: 3.5%\nAl: 4.1%\nCu: 1.5%\nGraphite: 25%"
    coa_text = st.text_area("Paste CoA:", height=150, value=default_text)

with col_right:
    st.success(f"🏭 **Refinery Configuration**")
    st.write(f"**Product Path:** {ni_product} + {li_product}")
    st.write(f"**Refining Cost:** ${refining_opex:,.0f} {currency} / Tonne")

if st.button("Run Integrated Model", type="primary"):
    assays = parse_coa_text(coa_text)
    
    # === STEP 1: UPSTREAM COST ===
    mass_ni = 1000 * assays["Nickel"]
    mass_co = 1000 * assays["Cobalt"]
    mass_li = 1000 * assays["Lithium"]
    
    cost_ni = mass_ni * ni_base * ni_pay_feed
    cost_co = mass_co * co_base * co_pay_feed
    cost_li = mass_li * li_base * li_pay_feed
    bm_cost = cost_ni + cost_co + cost_li
    
    # === STEP 2: DOWNSTREAM REVENUE ===
    revenue_items = []
    total_rev = 0
    
    # A. Nickel & Cobalt
    if ni_product == "Sulphates (Battery Salt)":
        qty_ni_sulf = mass_ni * rec_ni * FACTORS["Ni_to_Sulphate"]
        rev_ni = qty_ni_sulf * price_ni_sulf
        revenue_items.append(["Ni Sulphate", f"{qty_ni_sulf:.1f} kg", f"${rev_ni:,.2f}"])
        
        qty_co_sulf = mass_co * rec_co * FACTORS["Co_to_Sulphate"]
        rev_co = qty_co_sulf * price_co_sulf
        revenue_items.append(["Co Sulphate", f"{qty_co_sulf:.1f} kg", f"${rev_co:,.2f}"])
    else: # MHP
        contained_ni_mhp = mass_ni * rec_ni
        rev_ni = contained_ni_mhp * ni_base * mhp_pay_ni
        revenue_items.append(["MHP (Ni Content)", f"{contained_ni_mhp:.1f} kg (Ni)", f"${rev_ni:,.2f}"])
        
        contained_co_mhp = mass_co * rec_co
        rev_co = contained_co_mhp * co_base * mhp_pay_co
        revenue_items.append(["MHP (Co Content)", f"{contained_co_mhp:.1f} kg (Co)", f"${rev_co:,.2f}"])

    # B. Lithium
    if li_product == "Carbonate (LCE)":
        qty_li = mass_li * rec_li * FACTORS["Li_to_Carbonate"]
        rev_li = qty_li * price_li_salt
        revenue_items.append(["Li Carbonate", f"{qty_li:.1f} kg", f"${rev_li:,.2f}"])
    else: # Hydroxide
        qty_li = mass_li * rec_li * FACTORS["Li_to_Hydroxide"]
        rev_li = qty_li * price_li_salt
        revenue_items.append(["Li Hydroxide", f"{qty_li:.1f} kg", f"${rev_li:,.2f}"])

    total_rev = rev_ni + rev_co + rev_li
    net_profit = total_rev - bm_cost - refining_opex

    # === DISPLAY ===
    st.divider()
    
    # Financials
    st.subheader(f"💰 Economics ({currency} / MT)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("1. Revenue", f"${total_rev:,.0f}")
    c2.metric("2. Cost", f"${bm_cost:,.0f}", delta_color="inverse")
    c3.metric("3. OPEX", f"${refining_opex:,.0f}", delta_color="inverse")
    c4.metric("4. PROFIT", f"${net_profit:,.0f}", delta="Margin")
    
    st.divider()
    
    # Detailed Tables
    col_up, col_down = st.columns(2)
    with col_up:
        st.subheader("📉 Purchasing")
        cost_df = pd.DataFrame([
            ["Nickel", f"{mass_ni:.1f} kg", f"${cost_ni:,.2f}"],
            ["Cobalt", f"{mass_co:.1f} kg", f"${cost_co:,.2f}"],
            ["Lithium", f"{mass_li:.1f} kg", f"${cost_li:,.2f}"],
            ["**TOTAL**", "-", f"**${bm_cost:,.2f}**"]
        ], columns=["Metal", "Content", "Cost"])
        st.table(cost_df)
        
    with col_down:
        st.subheader("📈 Revenue")
        rev_df = pd.DataFrame(revenue_items, columns=["Product", "Volume", "Revenue"])
        rev_df.loc[len(rev_df)] = ["**TOTAL**", "-", f"**${total_rev:,.2f}**"]
        st.table(rev_df)
