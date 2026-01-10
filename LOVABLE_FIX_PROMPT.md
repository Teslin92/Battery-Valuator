# Lovable Fix: Pre-treatment Cost Bug

## Problem
The Vercel frontend is showing a **$300 pre-treatment cost** for "Black Mass (Processed)" material, which is incorrect. Black Mass is already processed material and should have **$0 pre-treatment costs**.

This causes the profit calculation to be $300 lower than the Streamlit reference app.

## Root Cause
The frontend is not implementing conditional logic for the `shredding_cost_per_ton` parameter based on material type.

Currently, the frontend is always sending:
```json
{
  "shredding_cost_per_ton": 300,
  ...
}
```

But it should send:
```json
{
  "shredding_cost_per_ton": 0,  // When material type is "Black Mass (Processed)"
  ...
}
```

## What Needs to Change

### 1. UI Changes (Material Type Dropdown)

When user selects **"Black Mass (Processed)"**:
- ✅ HIDE the "Mechanical/Shred Cost" input field
- ✅ HIDE the "Mechanical Recovery" slider
- ✅ The UI should show NO pre-treatment cost fields at all

When user selects **any other material type** (Cathode Foils, Cell Stacks, etc.):
- ✅ SHOW the "Mechanical/Shred Cost" input field (default: 300)
- ✅ SHOW the "Mechanical Recovery" slider (default: 95%)

### 2. API Request Logic

When building the request to `/api/calculate`, implement this logic:

```javascript
// Get the selected material type
const materialType = formData.materialType; // e.g., "Black Mass (Processed)"

// Build API request with conditional logic
const apiRequest = {
  currency: formData.currency,
  gross_weight: formData.grossWeight,
  feed_type: materialType,
  yield_pct: formData.yield / 100,

  // CONDITIONAL: Set mech_recovery based on material type
  mech_recovery: materialType === "Black Mass (Processed)"
    ? 1.0  // 100% for Black Mass
    : formData.mechRecovery / 100,  // User's input for other materials

  hydromet_recovery: formData.hydrometRecovery / 100,

  assays: {
    "Nickel": formData.niAssay / 100,
    "Cobalt": formData.coAssay / 100,
    "Lithium": formData.liAssay / 100,
    "Copper": formData.cuAssay / 100,
    "Aluminum": formData.alAssay / 100,
    "Manganese": formData.mnAssay / 100
  },

  assay_basis: formData.assayBasis,

  metal_prices: {
    "Ni": formData.niPrice,
    "Co": formData.coPrice,
    "Li": formData.liPrice,
    "Cu": formData.cuPrice,
    "Al": formData.alPrice,
    "Mn": formData.mnPrice
  },

  payables: {
    "Ni": formData.niPayable / 100,
    "Co": formData.coPayable / 100,
    "Li": formData.liPayable / 100,
    "Cu": formData.cuPayable / 100,
    "Al": formData.alPayable / 100,
    "Mn": formData.mnPayable / 100
  },

  // CONDITIONAL: Set shredding cost to 0 for Black Mass
  shredding_cost_per_ton: materialType === "Black Mass (Processed)"
    ? 0  // NO shredding cost for Black Mass
    : (formData.shreddingCost || 300),  // Use user's input or default 300

  elec_surcharge: formData.hasElectrolyte ? formData.elecSurcharge : 0,
  has_electrolyte: formData.hasElectrolyte,
  refining_opex_base: formData.refiningOpex,
  ni_product: formData.niProduct,
  li_product: formData.liProduct
};
```

### 3. Validation Test

After implementing, test with these exact values:

**Inputs:**
- Material Type: **Black Mass (Processed)**
- Gross Weight: 1000 kg
- Currency: CAD
- Ni assay: 20.5%
- Co assay: 6.2%
- Li assay: 2.5%
- Cu/Al/Mn assays: 0%
- Ni payable: 80%
- Co payable: 75%
- Li payable: 30%
- Ni product: MHP (Intermediate)
- Li product: Hydroxide (LiOH)
- Refining OPEX: 1500
- Hydromet Recovery: 95%

**Expected Results:**
- Total Revenue: **$6,290.77** CAD
- Material Cost: **$4,341.75** CAD
- Pre-treatment Cost: **$0.00** CAD (CRITICAL!)
- Refining Cost: **$1,500.00** CAD
- Total OPEX: **$1,500.00** CAD
- **Net Profit: $449.02** CAD

**If you see:**
- Total OPEX: $1,800.00 → BUG! Still adding $300 shredding cost
- Net Profit: $149.02 → BUG! $300 too low

## Reference Implementation

Check the Streamlit app logic in `app.py` lines 294-296:

```python
# B. Mechanical / Shredding Cost
shredding_cost_per_ton = 0.0
if feed_type != "Black Mass (Processed)":
    shredding_cost_per_ton = st.sidebar.number_input(f"Mechanical/Shred Cost ({currency}/MT)", value=300.0)
```

This means:
1. Default shredding cost is 0
2. Only show the input field if material is NOT Black Mass
3. For Black Mass, always use 0

## Summary

**The Fix (2 parts):**
1. **UI**: Hide shredding cost field when material type = "Black Mass (Processed)"
2. **API**: Always send `shredding_cost_per_ton: 0` when material type = "Black Mass (Processed)"

**Why it matters:**
- Black Mass is already shredded/processed material from battery recycling
- Charging for shredding it again makes no sense
- This is causing incorrect profit calculations

## Testing Checklist

After implementing, verify:
- [ ] Black Mass material type shows NO "Mechanical/Shred Cost" field
- [ ] Black Mass material type shows NO "Mechanical Recovery" field
- [ ] Cathode Foils material type SHOWS both fields
- [ ] API request for Black Mass has `shredding_cost_per_ton: 0`
- [ ] API request for Black Mass has `mech_recovery: 1.0`
- [ ] Total OPEX for Black Mass = Refining Cost only (no pre-treatment)
- [ ] Results match Streamlit app exactly with same inputs
