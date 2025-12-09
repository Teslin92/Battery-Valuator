import streamlit as st
import re
import pandas as pd
import yfinance as yf
import altair as alt

# --- 1. CONFIG & DESIGN ---
st.set_page_config(page_title="Battery Valuator", page_icon="🔋", layout="wide")

# FORCE LIGHT THEME & DARK GREEN ACCENTS
st.markdown("""
    <style>
    /* 1. Main Background: White */
    .stApp {
        background-color: #FFFFFF;
        color: #333333; /* Dark Grey Text */
    }
    
    /* 2. Sidebar Background: Very Light Grey */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FA;
    }
    
    /* 3. Primary Buttons: Dark Green */
    div.stButton > button {
        background-color: #1B5E20; /* Dark Forest Green */
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #2E7D32; /* Slightly lighter on hover */
        color: white;
    }

    /* 4. Metrics & Highlights: Dark Green */
    [data-testid="stMetricValue"] {
        color: #1B5E20;
    }
    
    /* 5. Headings */
    h1, h2, h3 {
        color: #1B5E20; /* Headlines in Green */
    }
    </style>
    """, unsafe_allow_html=True)

# HEADER WITH LOGO
col_logo, col_title = st.columns([2, 5]) 

with col_logo:
    # Ensure "Battery Valuator.png" is in the same folder
    try:
        st.image("Battery Valuator.png", width=350)
    except:
        # Fallback if image is missing
        st.markdown("# 🔋") 

with col_title:
    st.title("Battery Valuator")
    st.caption("Accurate Battery Material Valuations")

# Stoichiometry (Metal to Salt Conversion Factors)
FACTORS = {
    "Ni_to_Sulphate": 4.48, "Co_to_Sulphate": 4.77,   
    "Li_to_Carbonate": 5.32, "Li_to_Hydroxide": 6.05   
}

# --- 2. LIVE DATA ENGINE ---
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
        # Fallback constants if API fails
        fx = 1.40 if target_currency == "CAD" else 1.0 
    
    data['FX'] = fx

    # B. METAL PROXIES (Base prices in USD)
    # Ideally, connect this to Fastmarkets or SMM API in production
    base_prices_usd = {
        "Ni": 16500.00,   # LME Nickel Approx
        "Co": 33000.00,   # Fastmarkets Cobalt Approx
        "Li": 13500.00,   # China Carbonate Spot Approx
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
    assays = {"Nickel": 0.0, "Cobalt": 0.0, "Lithium": 0.0}
    text = text.lower().replace(",", "") 
    target_map = {
        "Nickel": ["ni", "nickel"], 
        "Cobalt": ["co", "cobalt"], 
        "Lithium": ["li", "lithium"]
    }
    for line in text.split('\n'):
        for metal, keywords in target_map.items():
            for kw in keywords:
                if re.search(rf"\b{kw}", line):
                    # Find numbers
                    match = re.search(r"(\d+\.?\d*)", line.replace(kw, ""))
                    if match:
                        val = float(match.group(1))
                        # Handle percentages: if user enters 22.5, we treat as 22.5% (0.225)
                        if val > 100: assays[metal] = val / 10000.0 / 100.0
                        else: assays[metal] = val / 100.0
    return assays

# --- 4. SIDEBAR ---
with st.sidebar:
    try:
        st.image("Battery Valuator.png", width=400) 
    except:
        st.write("## Battery Valuator")

# === GLOBAL SETTINGS ===
st.sidebar.header("Global Settings")
currency = st.sidebar.selectbox("Currency", ["CAD", "USD", "EUR", "CNY"])
market_data = get_market_data(currency)
if st.sidebar.button("🔄 Refresh Prices"):
    st.cache_data.clear()

st.sidebar.markdown("---")

# === SECTION 1: FEEDSTOCK & PRE-TREATMENT ===
st.sidebar.header("1. Feedstock & Pre-treatment")

feed_type = st.sidebar.selectbox("Material Type", 
    ["Black Mass (Processed)", "Cathode Foils", "Cell Stacks / Jelly Rolls", "Whole Cells", "Modules", "Battery Packs"])

# A. Electrolyte Logic (Adjustable Cost)
has_electrolyte = st.sidebar.checkbox("⚠️ Contains Electrolyte", value=False)
elec_surcharge = 0.0

if has_electrolyte:
    elec_surcharge = st.sidebar.number_input(
        f"Safety & Drying Cost ({currency}/MT)", 
        value=150.0, 
        step=10.0,
        help="Cost for thermal treatment and hazardous handling (Class 9)."
    )

# B. Mechanical / Shredding Cost
# This cost only exists if we need to turn cells into black mass
shredding_cost_per_ton = 0.0
if feed_type != "Black Mass (Processed)":
    shredding_cost_per_ton = st.sidebar.number_input(f"Mechanical/Shred Cost ({currency}/MT)", value=300.0, help="Cost to shred and separate plastics/foils.")

# C. Yields
defaults = {
    "Black Mass (Processed)": 100, "Cathode Foils": 90,
    "Cell Stacks / Jelly Rolls": 70, "Whole Cells": 60,
    "Modules": 50, "Battery Packs": 40
}

yield_pct = st.sidebar.slider(
    f"Black Mass Yield (%)", 
    min_value=10, max_value=100, 
    value=defaults[feed_type],
    help="Weight of Black Mass recovered after shredding."
) / 100.0

gross_weight = st.sidebar.number_input(f"Total Gross Weight (kg)", value=1000.0)
net_bm_weight = gross_weight * yield_pct
st.sidebar.caption(f"📉 **Recoverable Black Mass:** {net_bm_weight:,.1f} kg")

# === SECTION 2: PRICING (Buying) ===
st.sidebar.markdown("---")
st.sidebar.header("2. Pricing (Buying)")

st.sidebar.caption(f"**Metal Prices ({currency}/kg)**")
c1, c2 = st.sidebar.columns(2)
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
ni_pay_feed = c1.number_input("Ni Payable", value=80.0) / 100
co_pay_feed = c2.number_input("Co Payable", value=75.0) / 100
li_pay_feed = c3.number_input("Li Payable", value=30.0) / 100

# === SECTION 3: REFINING (Post-Treatment) ===
st.sidebar.markdown("---")
st.sidebar.header("3. Refining (Hydromet)")

ni_product = st.sidebar.selectbox("Ni/Co Product", ["Sulphates (Battery Salt)", "MHP (Intermediate)"])
li_product = st.sidebar.selectbox("Li Product", ["Carbonate (LCE)", "Hydroxide (LiOH)"])

refining_opex_base = st.sidebar.number_input(f"Refining OPEX ({currency}/MT BM)", value=1500.0)
st.sidebar.caption("Cost applied to Net Black Mass Weight only.")

# Market Prices & Recoveries (Hidden Vars for cleaner UI)
price_ni_sulf = market_data['NiSO4']
price_co_sulf = market_data['CoSO4']
price_li_salt = market_data['LCE'] if li_product == "Carbonate (LCE)" else market_data['LiOH']
mhp_pay_ni = 0.85
mhp_pay_co = 0.80
rec_ni = 0.95
rec_co = 0.95
rec_li = 0.85

# --- 5. MAIN APP ---

st.subheader(f"Feedstock: {feed_type}")

# === PRE-CALCULATIONS ===
# 1. Shredding Cost (Applied to Gross)
cost_shred = (gross_weight / 1000.0) * shredding_cost_per_ton

# 2. Electrolyte Cost (Applied to Gross)
cost_electrolyte = 0
if has_electrolyte:
    cost_electrolyte = (gross_weight / 1000.0) * elec_surcharge

total_pre_treat = cost_shred + cost_electrolyte

# === UI SECTION ===
col_left, col_right = st.columns([1, 1])

with col_left:
    st.info("📋 **Assay Input (Lab Results)**")
    
    # RENAMED FOR CLARITY
    assay_basis = st.radio(
        "Where did you take this sample?", 
        ["Whole Battery (Diluted Grade)", "Final Powder (Concentrated Grade)"],
        horizontal=True,
        help="Select 'Whole Battery' to trigger Enrichment Math. Select 'Final Powder' if your numbers are already from the Black Mass."
    )
    
    default_text = "Ni: 20.5%\nCo: 6.2%\nLi: 2.5%"
    coa_text = st.text_area("Paste Lab Results", height=150, value=default_text)

with col_right:
    st.success(f"**Process Configuration**")
    
    # 1. Physical Inputs
    st.markdown(f"**Feedstock:** {gross_weight:,.0f} kg (Gross)")
    st.markdown(f"**Yield:** {yield_pct*100:.0f}% → **{net_bm_weight:,.0f} kg (Net BM)**")
    
    st.divider()
    
    # 2. Pre-Treatment
    if has_electrolyte:
        st.write(f"⚠️ **Electrolyte:** ${elec_surcharge:,.0f} / ton surcharge")
    
    if feed_type != "Black Mass (Processed)":
        st.write(f"⚙️ **Shredding:** ${shredding_cost_per_ton:,.0f} / ton")
    else:
        st.write(f"⚙️ **Shredding:** Included / None")

    # 3. Post-Treatment
    st.markdown(f"🧪 **Refining:** ${refining_opex_base:,.0f} / ton (BM)")
    st.caption(f"Target: {ni_product} & {li_product}")

if st.button("Calculate Value", type="primary"):
    assays = parse_coa_text(coa_text)
    
    # === 1. MASS BALANCE & ENRICHMENT ===
    
    # Initialize variables
    bm_ni_grade = 0.0
    bm_co_grade = 0.0
    bm_li_grade = 0.0
    
    # LOGIC CHECK:
    # If "Whole Battery", we keep Metal Mass constant, but Weight drops -> Grade GOES UP.
    if assay_basis == "Whole Battery (Diluted Grade)":
        mass_ni = gross_weight * assays["Nickel"]
        mass_co = gross_weight * assays["Cobalt"]
        mass_li = gross_weight * assays["Lithium"]
        
        if net_bm_weight > 0:
            bm_ni_grade = (mass_ni / net_bm_weight) * 100
            bm_co_grade = (mass_co / net_bm_weight) * 100
            bm_li_grade = (mass_li / net_bm_weight) * 100
            
    # If "Final Powder", the user gave us the final grade. Grade stays SAME.
    else:
        mass_ni = net_bm_weight * assays["Nickel"]
        mass_co = net_bm_weight * assays["Cobalt"]
        mass_li = net_bm_weight * assays["Lithium"]
        
        bm_ni_grade = assays["Nickel"] * 100
        bm_co_grade = assays["Cobalt"] * 100
        bm_li_grade = assays["Lithium"] * 100

    # === 2. COSTS ===
    cost_ni = mass_ni * ni_base * ni_pay_feed
    cost_co = mass_co * co_base * co_pay_feed
    cost_li = mass_li * li_base * li_pay_feed
    material_cost = cost_ni + cost_co + cost_li
    
    total_refining_cost = (net_bm_weight / 1000.0) * refining_opex_base
    total_opex = total_pre_treat + total_refining_cost
    
    # === 3. REVENUE & PRODUCTION SCHEDULE ===
    
    production_data = [] # Stores [Product Name, Mass (kg), Revenue ($)]
    
    # Ni/Co Revenue
    if ni_product == "Sulphates (Battery Salt)":
        qty_ni_prod = mass_ni * rec_ni * FACTORS["Ni_to_Sulphate"]
        rev_ni = qty_ni_prod * price_ni_sulf
        production_data.append(["Nickel Sulphate", qty_ni_prod, rev_ni])
        
        qty_co_prod = mass_co * rec_co * FACTORS["Co_to_Sulphate"]
        rev_co = qty_co_prod * price_co_sulf
        production_data.append(["Cobalt Sulphate", qty_co_prod, rev_co])
    else: 
        # MHP (Intermediate)
        qty_ni_prod = mass_ni * rec_ni
        rev_ni = qty_ni_prod * ni_base * mhp_pay_ni
        production_data.append(["MHP (Ni Content)", qty_ni_prod, rev_ni])
        
        qty_co_prod = mass_co * rec_co
        rev_co = qty_co_prod * co_base * mhp_pay_co
        production_data.append(["MHP (Co Content)", qty_co_prod, rev_co])
        
    # Li Revenue
    factor_li = FACTORS["Li_to_Carbonate"] if li_product == "Carbonate (LCE)" else FACTORS["Li_to_Hydroxide"]
    qty_li_prod = mass_li * rec_li * factor_li
    rev_li = qty_li_prod * price_li_salt
    production_data.append([li_product, qty_li_prod, rev_li])
    
    total_rev = rev_ni + rev_co + rev_li
    net_profit = total_rev - material_cost - total_opex

    # === DISPLAY METRICS ===
    st.divider()
    
    st.caption(f"ℹ️ **Effective Black Mass Grade:** Ni {bm_ni_grade:.1f}% | Co {bm_co_grade:.1f}% | Li {bm_li_grade:.1f}%")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Revenue", f"${total_rev:,.0f}")
    c2.metric("Feedstock Cost", f"${material_cost:,.0f}", delta_color="inverse")
    c3.metric("Total OPEX", f"${total_opex:,.0f}", help="Shredding + Electrolyte + Refining", delta_color="inverse")
    
    margin_pct = (net_profit / total_rev) * 100 if total_rev > 0 else 0
    c4.metric("Net Profit", f"${net_profit:,.0f}", delta=f"{margin_pct:.1f}% Margin")

    st.write("---")
    
    # === NEW DETAILED OUTPUT SECTION ===
    
    # THIS WAS THE MISSING LINE:
    col_prod, col_chart = st.columns([1, 2])
    
    with col_prod:
        st.subheader("Products")
        # Create a nice table showing what you actually produced
        prod_df = pd.DataFrame(production_data, columns=["Product Stream", "Output Mass (kg)", "Est. Revenue"])
        
        # Add a total row
        total_mass_prod = prod_df["Output Mass (kg)"].sum()
        new_row = {"Product Stream": "TOTAL", "Output Mass (kg)": total_mass_prod, "Est. Revenue": total_rev}
        prod_df = pd.concat([prod_df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Format the numbers
        st.dataframe(
            prod_df.style.format({
                "Output Mass (kg)": "{:,.0f}",
                "Est. Revenue": "${:,.0f}"
            }),
            use_container_width=True,
            hide_index=True
        )

    with col_chart:
        st.subheader("Financial Split")
        
        # 1. Prepare Data with a specific "Color" column
        chart_data = pd.DataFrame({
            "Category": ["Feedstock Cost", "Pre-Treatment", "Refining", "Net Profit"],
            "Amount": [material_cost, total_pre_treat, total_refining_cost, net_profit],
            "Color": ["#FF5252", "#FF5252", "#FF5252", "#00D668"] # Red for costs, Green for profit
        })
        
        # 2. Build Chart using Altair (enables custom colors)
        c = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Category', sort=None), 
            y='Amount',
            color=alt.Color('Color', scale=None), 
            tooltip=['Category', 'Amount']
        )
        
        st.altair_chart(c, use_container_width=True)
