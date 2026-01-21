"""
Battery Valuator Backend Logic
Pure calculation engine - no UI dependencies
"""

import os
import requests
import yfinance as yf
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metals.Dev API Key (get free key at https://metals.dev)
METALS_DEV_API_KEY = os.environ.get('METALS_DEV_API_KEY', '')

# Stoichiometry (Metal to Salt Conversion Factors)
# These factors convert pure metal mass to salt mass
# E.g., 1kg of Ni metal → 4.48kg of NiSO4·6H2O (including water of hydration)
FACTORS = {
    "Ni_to_Sulphate": 4.48,      # Ni → NiSO4·6H2O
    "Co_to_Sulphate": 4.77,      # Co → CoSO4·7H2O
    "Li_to_Carbonate": 5.32,     # Li → Li2CO3
    "Li_to_Hydroxide": 6.05      # Li → LiOH·H2O
}

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
        # Fetch latest prices (includes LME metals)
        url = f"https://api.metals.dev/v1/latest?api_key={METALS_DEV_API_KEY}&currency=USD&unit=toz"
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

        # Metals.Dev returns prices in USD per troy ounce
        # Convert to USD per tonne: 1 tonne = 32,150.7 troy ounces
        TOZ_PER_TONNE = 32150.7

        if 'lme_nickel' in metals:
            prices['Ni'] = metals['lme_nickel'] * TOZ_PER_TONNE
            logger.info(f"Nickel (Metals.Dev): ${prices['Ni']:.2f}/tonne")

        if 'lme_copper' in metals:
            prices['Cu'] = metals['lme_copper'] * TOZ_PER_TONNE
            logger.info(f"Copper (Metals.Dev): ${prices['Cu']:.2f}/tonne")

        if 'lme_aluminum' in metals:
            prices['Al'] = metals['lme_aluminum'] * TOZ_PER_TONNE
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

    Args:
        base_currency: Base currency code (USD)

    Returns:
        dict: Currency rates, or None if fetch fails
    """
    if not METALS_DEV_API_KEY:
        logger.warning("METALS_DEV_API_KEY not set, skipping currency fetch")
        return None

    try:
        # Use latest endpoint which includes currencies
        url = f"https://api.metals.dev/v1/latest?api_key={METALS_DEV_API_KEY}&currency=USD&unit=toz"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            logger.warning(f"Metals.Dev currencies API returned status {response.status_code}")
            return None

        data = response.json()
        if data.get('status') != 'success':
            logger.warning(f"Metals.Dev currencies error: {data.get('error_message', 'Unknown error')}")
            return None

        # The API returns rates as "how much 1 USD is worth in foreign currency"
        # But we need "how many target currency per 1 USD" for conversion
        # The rates are already in the format we need (1/rate gives us multiplier)
        currencies = data.get('currencies', {})

        # Convert to the format we need: CAD rate means 1 USD = X CAD
        # The API gives us rates where higher = stronger USD
        # We need to invert: if CAD = 0.72, then 1 USD = 1/0.72 = 1.38 CAD
        converted = {}
        for curr, rate in currencies.items():
            if rate > 0:
                converted[curr.lower()] = 1.0 / rate

        return converted

    except Exception as e:
        logger.error(f"Metals.Dev currencies fetch failed: {str(e)}")
        return None

def fetch_yfinance_prices():
    """
    Fallback: Fetch metal prices from yfinance futures.
    Only works for Copper and Aluminum.

    Returns:
        dict: Metal prices in USD per tonne, or None if fetch fails
    """
    try:
        prices = {}

        # Fetch Copper via futures
        try:
            cu_ticker = yf.Ticker("HG=F")  # Copper Futures
            cu_hist = cu_ticker.history(period="1d")
            if not cu_hist.empty:
                # Copper futures are in USD per pound, convert to USD per tonne
                cu_price_lb = cu_hist['Close'].iloc[-1]
                prices["Cu"] = cu_price_lb * 2204.62  # pounds to tonnes
                logger.info(f"Copper (yfinance): ${prices['Cu']:.2f}/tonne")
        except Exception as e:
            logger.warning(f"Copper price fetch failed: {str(e)}")

        # Fetch Aluminum via futures
        try:
            al_ticker = yf.Ticker("ALI=F")  # Aluminum Futures
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

    Args:
        target_currency: Target currency code (CAD, EUR, CNY)

    Returns:
        float: FX rate, or None if fetch fails
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

def get_market_data(target_currency="USD"):
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
            # Only update metals not already fetched from Metals.Dev
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
    import re

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

def calculate_valuation(input_params):
    """
    Main calculation engine for battery material valuation.

    Args:
        input_params: dict containing all input parameters

    Returns:
        dict: Complete valuation results including costs, revenue, profit, and product data
    """
    # Unpack input parameters
    currency = input_params.get('currency', 'USD')
    gross_weight = input_params['gross_weight']
    feed_type = input_params['feed_type']
    yield_pct = input_params['yield_pct']
    mech_recovery = input_params.get('mech_recovery', 1.0)
    hydromet_recovery = input_params.get('hydromet_recovery', 0.95)

    # Assays (as decimals)
    assays = input_params['assays']
    assay_basis = input_params.get('assay_basis', 'Final Powder')

    # Pricing
    metal_prices = input_params['metal_prices']  # in target currency per kg
    payables = input_params['payables']  # as decimals

    # Costs
    shredding_cost_per_ton = input_params.get('shredding_cost_per_ton', 0.0)
    elec_surcharge = input_params.get('elec_surcharge', 0.0)
    has_electrolyte = input_params.get('has_electrolyte', False)
    refining_opex_base = input_params.get('refining_opex_base', 1500.0)

    # Products
    ni_product = input_params.get('ni_product', 'Sulphates (Battery Salt)')
    li_product = input_params.get('li_product', 'Carbonate (LCE)')

    # Market data for salt prices
    market_data = get_market_data(currency)

    # Calculate net black mass weight
    net_bm_weight = gross_weight * yield_pct

    # 1. MASS BALANCE
    bm_grades = {}
    masses = {}

    if assay_basis == "Whole Battery":
        for metal in ['Nickel', 'Cobalt', 'Lithium', 'Copper', 'Aluminum', 'Manganese']:
            masses[metal] = (gross_weight * assays[metal]) * mech_recovery
            if net_bm_weight > 0:
                bm_grades[metal] = (masses[metal] / net_bm_weight) * 100
            else:
                bm_grades[metal] = 0.0
    else:
        for metal in ['Nickel', 'Cobalt', 'Lithium', 'Copper', 'Aluminum', 'Manganese']:
            masses[metal] = net_bm_weight * assays[metal]
            bm_grades[metal] = assays[metal] * 100

    # VALIDATION: Check for unrealistic assay values
    warnings = []
    if bm_grades['Nickel'] > 60:
        warnings.append(f"Nickel grade ({bm_grades['Nickel']:.1f}%) exceeds typical black mass range (10-60%)")
    if bm_grades['Cobalt'] > 25:
        warnings.append(f"Cobalt grade ({bm_grades['Cobalt']:.1f}%) exceeds typical black mass range (3-25%)")
    if bm_grades['Lithium'] > 10:
        warnings.append(f"Lithium grade ({bm_grades['Lithium']:.1f}%) exceeds typical black mass range (1-10%)")

    total_grade = sum(bm_grades.values())
    if total_grade > 100:
        warnings.append(f"Total metal content ({total_grade:.1f}%) exceeds 100%")

    # 2. COSTS
    costs = {}
    for metal in ['Nickel', 'Cobalt', 'Lithium', 'Copper', 'Aluminum', 'Manganese']:
        metal_key = metal  # Use full name for prices dict
        if metal == 'Nickel':
            price_key = 'Ni'
        elif metal == 'Cobalt':
            price_key = 'Co'
        elif metal == 'Lithium':
            price_key = 'Li'
        elif metal == 'Copper':
            price_key = 'Cu'
        elif metal == 'Aluminum':
            price_key = 'Al'
        elif metal == 'Manganese':
            price_key = 'Mn'

        costs[metal] = masses[metal] * metal_prices.get(price_key, 0.0) * payables.get(price_key, 0.0)

    material_cost = sum(costs.values())

    # Pre-treatment costs
    cost_shred = (gross_weight / 1000.0) * shredding_cost_per_ton
    cost_electrolyte = (gross_weight / 1000.0) * elec_surcharge if has_electrolyte else 0.0
    total_pre_treat = cost_shred + cost_electrolyte

    # Refining costs
    total_refining_cost = (net_bm_weight / 1000.0) * refining_opex_base
    total_opex = total_pre_treat + total_refining_cost

    # 3. REVENUE
    production_data = []

    # Recovery rates
    rec_ni = hydromet_recovery
    rec_co = hydromet_recovery
    rec_li = hydromet_recovery * 0.90

    # Salt prices
    price_ni_sulf = market_data['NiSO4']
    price_co_sulf = market_data['CoSO4']
    price_li_salt = market_data['LCE'] if li_product == "Carbonate (LCE)" else market_data['LiOH']
    mhp_pay_ni = 0.85
    mhp_pay_co = 0.80

    # Calculate revenues
    if ni_product == "Sulphates (Battery Salt)":
        qty_ni_prod = masses['Nickel'] * rec_ni * FACTORS["Ni_to_Sulphate"]
        rev_ni = qty_ni_prod * price_ni_sulf
        production_data.append({"Product": "Nickel Sulphate", "Mass (kg)": qty_ni_prod, "Revenue": rev_ni})

        qty_co_prod = masses['Cobalt'] * rec_co * FACTORS["Co_to_Sulphate"]
        rev_co = qty_co_prod * price_co_sulf
        production_data.append({"Product": "Cobalt Sulphate", "Mass (kg)": qty_co_prod, "Revenue": rev_co})
    else:
        qty_ni_prod = masses['Nickel'] * rec_ni
        rev_ni = qty_ni_prod * metal_prices['Ni'] * mhp_pay_ni
        production_data.append({"Product": "MHP (Ni Content)", "Mass (kg)": qty_ni_prod, "Revenue": rev_ni})

        qty_co_prod = masses['Cobalt'] * rec_co
        rev_co = qty_co_prod * metal_prices['Co'] * mhp_pay_co
        production_data.append({"Product": "MHP (Co Content)", "Mass (kg)": qty_co_prod, "Revenue": rev_co})

    factor_li = FACTORS["Li_to_Carbonate"] if li_product == "Carbonate (LCE)" else FACTORS["Li_to_Hydroxide"]
    qty_li_prod = masses['Lithium'] * rec_li * factor_li
    rev_li = qty_li_prod * price_li_salt
    production_data.append({"Product": li_product, "Mass (kg)": qty_li_prod, "Revenue": rev_li})

    total_rev = rev_ni + rev_co + rev_li
    net_profit = total_rev - material_cost - total_opex
    margin_pct = (net_profit / total_rev) * 100 if total_rev > 0 else 0

    # Return complete results
    return {
        'net_bm_weight': net_bm_weight,
        'bm_grades': bm_grades,
        'masses': masses,
        'costs': costs,
        'material_cost': material_cost,
        'total_pre_treat': total_pre_treat,
        'total_refining_cost': total_refining_cost,
        'total_opex': total_opex,
        'production_data': production_data,
        'total_revenue': total_rev,
        'net_profit': net_profit,
        'margin_pct': margin_pct,
        'warnings': warnings,
        'cost_breakdown': {
            'shredding': cost_shred,
            'electrolyte': cost_electrolyte,
            'refining': total_refining_cost
        }
    }
