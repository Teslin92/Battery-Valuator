# Battery Valuator - Lovable Frontend Integration Guide

## Overview
The backend calculation logic has been separated into pure Python modules that you can call via REST API. Your Lovable frontend will make HTTP requests to get pricing data and calculate valuations.

## Backend Architecture

### Files Structure
```
backend.py      # Pure calculation engine (no UI dependencies)
api.py          # Flask REST API wrapper
app.py          # Original Streamlit app (still works independently)
```

## API Endpoints

### 1. Health Check
**GET** `/api/health`

Returns API status.

**Response:**
```json
{
  "status": "healthy",
  "service": "Battery Valuator API"
}
```

---

### 2. Get Market Data
**GET** `/api/market-data?currency=USD`

Fetches live metal prices and FX rates.

**Query Parameters:**
- `currency` (optional): USD, CAD, EUR, or CNY. Default: USD

**Response:**
```json
{
  "success": true,
  "data": {
    "FX": 1.0,
    "fx_fallback_used": false,
    "timestamp": "2025-01-09 15:30:00",
    "Ni": 16.5,
    "Co": 33.0,
    "Li": 13.5,
    "Cu": 9.2,
    "Al": 2.5,
    "Mn": 1.8,
    "NiSO4": 3.8,
    "CoSO4": 6.5,
    "LCE": 14.0,
    "LiOH": 15.5
  }
}
```

---

### 3. Parse COA Text
**POST** `/api/parse-coa`

Extracts metal percentages from pasted COA text.

**Request Body:**
```json
{
  "coa_text": "Ni: 20.5%\nCo: 6.2%\nLi: 2.5%\nCu: 3.5%\nAl: 1.2%\nMn: 4.8%"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "Nickel": 0.205,
    "Cobalt": 0.062,
    "Lithium": 0.025,
    "Copper": 0.035,
    "Aluminum": 0.012,
    "Manganese": 0.048
  }
}
```

---

### 4. Calculate Valuation (Main Endpoint)
**POST** `/api/calculate`

Performs complete valuation calculation.

**Request Body:**
```json
{
  "currency": "USD",
  "gross_weight": 1000,
  "feed_type": "Black Mass (Processed)",
  "yield_pct": 1.0,
  "mech_recovery": 0.95,
  "hydromet_recovery": 0.95,
  "assays": {
    "Nickel": 0.205,
    "Cobalt": 0.062,
    "Lithium": 0.025,
    "Copper": 0.035,
    "Aluminum": 0.012,
    "Manganese": 0.048
  },
  "assay_basis": "Final Powder",
  "metal_prices": {
    "Ni": 16.5,
    "Co": 33.0,
    "Li": 13.5,
    "Cu": 9.2,
    "Al": 2.5,
    "Mn": 1.8
  },
  "payables": {
    "Ni": 0.80,
    "Co": 0.75,
    "Li": 0.30,
    "Cu": 0.80,
    "Al": 0.70,
    "Mn": 0.60
  },
  "shredding_cost_per_ton": 300,
  "elec_surcharge": 150,
  "has_electrolyte": false,
  "refining_opex_base": 1500,
  "ni_product": "Sulphates (Battery Salt)",
  "li_product": "Carbonate (LCE)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "net_bm_weight": 1000.0,
    "bm_grades": {
      "Nickel": 20.5,
      "Cobalt": 6.2,
      "Lithium": 2.5,
      "Copper": 3.5,
      "Aluminum": 1.2,
      "Manganese": 4.8
    },
    "masses": {
      "Nickel": 205.0,
      "Cobalt": 62.0,
      "Lithium": 25.0,
      "Copper": 35.0,
      "Aluminum": 12.0,
      "Manganese": 48.0
    },
    "costs": {
      "Nickel": 2706.0,
      "Cobalt": 1534.5,
      "Lithium": 101.25,
      "Copper": 257.6,
      "Aluminum": 21.0,
      "Manganese": 51.84
    },
    "material_cost": 4672.19,
    "total_pre_treat": 0.0,
    "total_refining_cost": 1500.0,
    "total_opex": 1500.0,
    "production_data": [
      {
        "Product": "Nickel Sulphate",
        "Mass (kg)": 872.32,
        "Revenue": 3314.82
      },
      {
        "Product": "Cobalt Sulphate",
        "Mass (kg)": 281.08,
        "Revenue": 1827.02
      },
      {
        "Product": "Carbonate (LCE)",
        "Mass (kg)": 120.15,
        "Revenue": 1682.1
      }
    ],
    "total_revenue": 6823.94,
    "net_profit": 651.75,
    "margin_pct": 9.55,
    "warnings": [],
    "cost_breakdown": {
      "shredding": 0.0,
      "electrolyte": 0.0,
      "refining": 1500.0
    }
  }
}
```

---

### 5. Validate Assays
**POST** `/api/validate-assays`

Checks if assay values are within typical ranges.

**Request Body:**
```json
{
  "bm_grades": {
    "Nickel": 20.5,
    "Cobalt": 6.2,
    "Lithium": 2.5,
    "Copper": 3.5,
    "Aluminum": 1.2,
    "Manganese": 4.8
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "warnings": []
  }
}
```

---

## What to Tell Lovable

### Project Brief

**"I need you to create a modern, professional web frontend for a Battery Valuator application. The backend API is already built and running. Here's what I need:"**

### 1. Design Requirements

**Style:** Modern fintech/SaaS aesthetic
- Clean, minimalist design with lots of white space
- Rounded corners on cards and buttons
- Subtle shadows for depth
- Professional color scheme:
  - Primary: Deep green (#1B5E20) for profit/positive values
  - Accent: Shades of red (#B71C1C to #F44336) for costs
  - Background: Off-white (#FAFAFA)
  - Cards: Pure white (#FFFFFF) with subtle borders

**Typography:**
- Use Inter or similar modern sans-serif font
- Clear hierarchy with proper font weights

**Layout:**
- Responsive design (mobile-friendly)
- Left sidebar for inputs
- Main area for results and charts

---

### 2. Page Structure

#### **Global Settings Section**
- Currency selector (dropdown): USD, CAD, EUR, CNY
- Display current market data timestamp
- "Refresh Prices" button
- Warning indicator if using fallback prices

#### **Input Panel (Left Sidebar)**

**Section 1: Feedstock & Pre-treatment**
- Material Type (dropdown):
  - Black Mass (Processed)
  - Cathode Foils
  - Cell Stacks / Jelly Rolls
  - Whole Cells
  - Modules
  - Battery Packs
- Total Gross Weight (kg) - number input
- Black Mass Yield (%) - slider (10-100%)
- Mechanical Recovery (%) - slider (80-100%) - **HIDE if "Black Mass (Processed)"**
- Contains Electrolyte - checkbox
- Electrolyte Surcharge ($/MT) - number input - **SHOW ONLY if checkbox is true**
- Mechanical/Shred Cost ($/MT) - number input - **HIDE if "Black Mass (Processed)"** and **SET TO 0 in API request**
- Display calculated: **Recoverable Black Mass** in kg

**CRITICAL CONDITIONAL LOGIC:**
- When Material Type = "Black Mass (Processed)":
  - Hide "Mechanical Recovery" field (set to 100% / 1.0 in API)
  - Hide "Mechanical/Shred Cost" field
  - **ALWAYS send `shredding_cost_per_ton: 0` to the API**
  - Set `mech_recovery: 1.0` in API request

- When Material Type = anything else:
  - Show "Mechanical Recovery" field (default 95%)
  - Show "Mechanical/Shred Cost" field (default 300)
  - Send user's input values to the API

**Section 2: Pricing (Buying)**

*Primary Metals:*
- Ni Price ($/kg) - number input with live price shown next to it
- Co Price ($/kg) - number input with live price shown next to it
- Li Price ($/kg) - number input with live price shown next to it

*Secondary Metals:*
- Cu Price ($/kg) - number input with live price shown next to it
- Al Price ($/kg) - number input with live price shown next to it
- Mn Price ($/kg) - number input with live price shown next to it

*Payables (% of metal price paid):*
- Ni Payable (%) - slider (0-100%)
- Co Payable (%) - slider (0-100%)
- Li Payable (%) - slider (0-100%)
- Cu Payable (%) - slider (0-100%)
- Al Payable (%) - slider (0-100%)
- Mn Payable (%) - slider (0-100%)

**Section 3: Refining**
- Ni/Co Product (dropdown): "Sulphates (Battery Salt)", "MHP (Intermediate)"
- Li Product (dropdown): "Carbonate (LCE)", "Hydroxide (LiOH)"
- Refining OPEX ($/MT BM) - number input
- Refining Recovery (%) - slider (80-100%)

**Section 4: Lab Assay**
- Sample Source (radio): "Whole Battery" or "Final Powder"
- COA Text Area - large text input for pasting lab results
- "Parse COA" button - calls `/api/parse-coa` and auto-fills assay fields
- Manual assay inputs (if user wants to override):
  - Ni (%)
  - Co (%)
  - Li (%)
  - Cu (%)
  - Al (%)
  - Mn (%)
- **"RUN VALUATION"** button (primary, prominent)

---

#### **Results Panel (Main Area)**

**Summary Metrics Banner (Top)**
- Material: [feed type]
- Gross Weight: [value] kg
- Net Black Mass: [value] kg ([yield]% Yield)
- Recovery: Mech: [value]% | Hydro: [value]%

**Key Metrics (Large Cards)**
- **NET PROFIT** - Large, prominent display in green
  - Show margin % as delta/badge
- **Total Revenue** - Secondary card
- **Material Cost** - Secondary card in red
- **Total OPEX** - Secondary card in red

**Cost Breakdown Chart**
- Bar chart showing:
  - Material Cost (red)
  - Pre-Treatment (lighter red)
  - Refining (lightest red)
  - Profit (green)

**Product Schedule Table**
- Columns: Product | Mass (kg) | Revenue
- Rows for each product (Nickel Sulphate, Cobalt Sulphate, Li product)
- Total row at bottom

**Effective Grade Display**
- Show calculated black mass grades for all 6 metals
- Format: "Ni 20.5% | Co 6.2% | Li 2.5% | Cu 3.5% | Al 1.2% | Mn 4.8%"

**Warnings Section** (if any)
- Yellow warning box showing validation warnings
- e.g., "Nickel grade exceeds typical range"

---

### 3. User Flow

1. **On page load:**
   - Call `GET /api/market-data?currency=USD`
   - Populate all live price fields
   - Show timestamp

2. **When user changes currency:**
   - Call `GET /api/market-data?currency=[selected]`
   - Update all price fields

3. **When user clicks "Refresh Prices":**
   - Re-fetch market data
   - Update UI

4. **When user pastes COA text and clicks "Parse COA":**
   - Call `POST /api/parse-coa` with the text
   - Auto-populate assay percentage fields

5. **When user clicks "RUN VALUATION":**
   - Gather all input values
   - Format request body (convert percentages to decimals)
   - Call `POST /api/calculate`
   - Display results in main panel
   - Optionally call `POST /api/validate-assays` and show warnings

---

### 4. Data Format Notes

**Important conversions:**
- Assays: UI shows percentages (20.5%), API expects decimals (0.205)
- Payables: UI shows percentages (80%), API expects decimals (0.80)
- Yield: UI shows percentages (100%), API expects decimals (1.0)
- Recoveries: UI shows percentages (95%), API expects decimals (0.95)

**Feed type to yield defaults:**
```javascript
{
  "Black Mass (Processed)": 100,
  "Cathode Foils": 90,
  "Cell Stacks / Jelly Rolls": 70,
  "Whole Cells": 60,
  "Modules": 50,
  "Battery Packs": 40
}
```

**Default payables:**
- Ni: 80%
- Co: 75%
- Li: 30%
- Cu: 80%
- Al: 70%
- Mn: 60%

---

### 5. Example API Request Builder

```javascript
// Build request for /api/calculate
const buildCalculationRequest = (formData) => {
  return {
    currency: formData.currency,
    gross_weight: parseFloat(formData.grossWeight),
    feed_type: formData.feedType,
    yield_pct: formData.yieldPct / 100.0, // Convert % to decimal
    mech_recovery: formData.mechRecovery / 100.0,
    hydromet_recovery: formData.hydrometRecovery / 100.0,
    assays: {
      Nickel: formData.assays.ni / 100.0,
      Cobalt: formData.assays.co / 100.0,
      Lithium: formData.assays.li / 100.0,
      Copper: formData.assays.cu / 100.0,
      Aluminum: formData.assays.al / 100.0,
      Manganese: formData.assays.mn / 100.0
    },
    assay_basis: formData.assayBasis,
    metal_prices: {
      Ni: parseFloat(formData.prices.ni),
      Co: parseFloat(formData.prices.co),
      Li: parseFloat(formData.prices.li),
      Cu: parseFloat(formData.prices.cu),
      Al: parseFloat(formData.prices.al),
      Mn: parseFloat(formData.prices.mn)
    },
    payables: {
      Ni: formData.payables.ni / 100.0,
      Co: formData.payables.co / 100.0,
      Li: formData.payables.li / 100.0,
      Cu: formData.payables.cu / 100.0,
      Al: formData.payables.al / 100.0,
      Mn: formData.payables.mn / 100.0
    },
    shredding_cost_per_ton: parseFloat(formData.shreddingCost || 0),
    elec_surcharge: parseFloat(formData.elecSurcharge || 0),
    has_electrolyte: formData.hasElectrolyte,
    refining_opex_base: parseFloat(formData.refiningOpex),
    ni_product: formData.niProduct,
    li_product: formData.liProduct
  };
};
```

---

### 6. Nice-to-Have Features

- Loading states during API calls
- Error handling with user-friendly messages
- Form validation (e.g., gross weight must be > 0)
- Export results as PDF or CSV
- Save/load configurations (localStorage)
- Dark mode toggle
- Responsive mobile layout
- Tooltips explaining technical terms
- Animated number counters for profit/revenue
- Chart.js or Recharts for the cost breakdown visualization

---

### 7. Technical Stack Recommendations

**Framework:** React with TypeScript
**Styling:** Tailwind CSS or styled-components
**Charts:** Recharts or Chart.js
**HTTP Client:** axios or fetch
**State Management:** React Context or Zustand (for form state)
**Form Handling:** React Hook Form

---

## API Base URL

**Development:** `http://localhost:5000`
**Production (Railway):** `https://your-railway-api.railway.app`

You'll need to deploy the API separately on Railway and provide Lovable with that URL.

---

## Testing the API Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python api.py

# Test endpoint
curl http://localhost:5000/api/health
```

---

## Example COA Text Formats

The parser can handle various formats:

```
Ni: 20.5%
Co: 6.2%
Li: 2.5%
```

```
Nickel 2050
Cobalt 620
Lithium 250
```

```
Ni 0.205
Co 0.062
Li 0.025
```

---

## Questions for Lovable

If Lovable asks for clarifications, here are some suggested responses:

**Q: What should happen if the API is down?**
A: Show a friendly error message and allow users to manually input prices. Don't block the calculation.

**Q: Should we show all metals even if assay is 0%?**
A: Yes, show all 6 metals. Users might have trace amounts.

**Q: How should we format currency?**
A: Use locale formatting with 2 decimal places. Example: $12,345.67

**Q: Should sliders show exact values?**
A: Yes, display the current value next to or above the slider.

**Q: What's the primary user action?**
A: "RUN VALUATION" - make this button prominent and easy to find.

---

## Common Issues & Troubleshooting

### Issue: Profit differs from Streamlit app

**Symptom:** Vercel frontend shows different profit than Streamlit with same inputs.

**Cause:** Pre-treatment costs being applied incorrectly to Black Mass.

**Solution:** Ensure conditional logic is implemented correctly:
```javascript
// Pseudo-code for API request building
const materialType = form.materialType.value;
const apiRequest = {
  // ... other fields ...
  shredding_cost_per_ton: materialType === "Black Mass (Processed)" ? 0 : form.shreddingCost.value,
  mech_recovery: materialType === "Black Mass (Processed)" ? 1.0 : form.mechRecovery.value / 100,
  // ... rest of request ...
};
```

### Issue: Total OPEX is $300 higher than expected

**Cause:** Frontend is sending `shredding_cost_per_ton: 300` even when material type is "Black Mass (Processed)".

**Fix:** Black Mass should NEVER have shredding costs - it's already processed material.

### Validation Checklist

Before deploying, verify:
- [ ] Black Mass shows $0 pre-treatment costs
- [ ] Other materials (Cathode Foils, etc.) show correct shredding costs
- [ ] Electrolyte surcharge only applies when checkbox is checked
- [ ] Currency conversion applies to all prices
- [ ] Results match Streamlit app with identical inputs

---

## Backend Guarantees

✅ All calculations are tested and accurate
✅ Parser handles various COA formats
✅ Live pricing with automatic fallbacks
✅ Proper error handling and logging
✅ CORS enabled for cross-origin requests
✅ Validation for unrealistic assay values

Your frontend just needs to call these endpoints and display the results beautifully!
