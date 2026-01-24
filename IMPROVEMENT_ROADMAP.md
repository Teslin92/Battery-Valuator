# Battery Valuator - Improvement Roadmap

## Strategic Direction: Layered Disclosure (Option B)

**Core Insight:** Two distinct user personas with different needs:

| | **OEMs** | **Traders/Recyclers** |
|---|----------|----------------------|
| **Primary need** | "What is my scrap worth?" | "How do I bid competitively?" |
| **Cares about** | Material value, recovery potential | Value + costs + sensitivities |
| **Doesn't need** | Processing costs | To *share* their cost data |
| **Output** | Simple valuation report | Bid document (hides margins) |

**Approach:** Start simple (serves OEMs), reveal complexity on demand (serves Traders), exportable reports that hide internal assumptions.

---

## Phase 1: Foundation (Priority)

### 1.1 LFP Chemistry Support ✅ IMPLEMENTED
**Problem:** Current tool is NMC-focused. LFP batteries (Li, Fe, P) show near-zero value because there's no Ni/Co.

**Changes Completed:**
- [x] Add Iron (Fe) to metal list in `backend.py`
- [x] Add Phosphorus (P) tracking (even if low value)
- [x] Add chemistry selector: "NMC" vs "LFP" vs "LCO" vs "NCA" + auto-detection
- [x] Adjust validation ranges for LFP (higher Li%, no Ni/Co expected)
- [x] LFP-specific product pathways:
  - Lithium recovery (same as NMC)
  - Iron phosphate (FePO4) recovery with stoichiometric factor
- [x] Update COA parser to recognize Fe, P patterns

**New API Endpoints:**
- `GET /api/chemistries` - List supported chemistries
- `POST /api/detect-chemistry` - Auto-detect from assays

**LFP Typical Composition:**
| Metal | LFP Range | NMC Range |
|-------|-----------|-----------|
| Li | 4-7% | 3-7% |
| Fe | 30-35% | 0-2% |
| P | 15-20% | 0% |
| Ni | 0% | 10-50% |
| Co | 0% | 3-20% |

### 1.2 Value View (Simple Mode) ✅ IMPLEMENTED
**For OEMs who just want to know "what's my scrap worth?"**

- [x] Simplified API mode showing only:
  - Material composition (from COA or manual entry)
  - Chemistry type (auto-detected)
  - Estimated recoverable value (total)
  - Recovery potential by metal
  - Value per tonne for comparison
- [x] Hide processing costs, OPEX, margins
- [x] Clean JSON output for frontend integration

**New API Endpoint:**
- `POST /api/value-view` - Simple valuation for OEMs

### 1.3 Bid Report Generator ✅ IMPLEMENTED
**For Traders who need to send quotes without revealing internals**

- [x] Configurable JSON report
- [x] Include/exclude options:
  - ✅ Material composition
  - ✅ Estimated recovery potential
  - ✅ Current market prices (optional toggle)
  - ✅ Transportation advisory (optional)
  - ✅ Offered price to seller
  - ❌ Processing costs (hidden by design)
  - ❌ Trader's margin (hidden by design)
  - ❌ Sensitivity analysis (hidden by design)
- [x] Company branding option
- [x] Reference number support
- [x] Date stamp and validity period

**New API Endpoint:**
- `POST /api/bid-report` - Generate shareable bid report

### 1.4 Fix Known Bug
- [ ] Black Mass shredding cost conditional logic (documented in LOVABLE_FIX_PROMPT.md)
  - **Note:** This is a frontend (Lovable) fix - backend already handles 0 cost correctly

---

## Phase 2: Transportation Advisory ✅ IMPLEMENTED

### 2.1 Route-Based Notifications
**Like travel advisories for battery materials**

Structure: Origin → Destination triggers relevant advisories

**Advisory Categories (all implemented):**
1. **Regulatory Classification**
   - Hazardous waste status
   - UN shipping classification (UN3480, UN3481, etc.)
   - Basel Convention implications

2. **Documentation Checklist**
   - Required permits with descriptions
   - Customs declarations
   - Environmental certificates
   - Insurance requirements
   - Marked as required/optional

3. **Route Restrictions**
   - OECD vs non-OECD restrictions (EU black mass = PROHIBITED)
   - Country-specific warnings
   - Port/carrier restrictions

4. **Cost Considerations**
   - Typical cost ranges by mode (truck, rail, sea)
   - Transit time estimates
   - Special handling notes

**New API Endpoints:**
- `POST /api/transport-advisory` - Get advisory for origin→destination
- `GET /api/transport-routes` - List all available routes

### 2.2 Implemented Routes
| Route | Status | Key Feature |
|-------|--------|-------------|
| Canada → USA | ✅ | EPA notification, RCRA manifest checklist |
| USA → Canada | ✅ | TDG regulations, ECCC permits |
| EU Internal | ✅ | ADR compliance, waste shipment notification |
| EU → Non-OECD | ✅ | **PROHIBITED** with alternatives listed |
| EU → OECD (non-EU) | ✅ | Prior Informed Consent procedure |
| Asia → North America | ✅ | IMDG code, SOC requirements |
| USA Internal | ✅ | DOT hazmat, state-specific rules |
| Canada Internal | ✅ | TDG requirements, provincial permits |

### 2.3 Data Structure
```python
TRANSPORT_ADVISORIES = {
    ("CA", "US"): {
        "classification": "Hazardous waste (may apply)",
        "checklist": [
            "EPA Consent for transboundary movement",
            "Manifest documentation",
            "Customs declaration (HS code 8549.31)",
            "Carrier hazmat certification",
        ],
        "warnings": [
            "Some US states have additional requirements",
            "Transit through certain ports may have restrictions",
        ],
        "estimated_cost_range": "$150-400/tonne (truck)",
        "transit_time": "3-7 days",
    },
    ("EU", "non-OECD"): {
        "classification": "PROHIBITED",
        "warnings": [
            "Black mass classified as hazardous waste under EU regulations",
            "Export to non-OECD countries prohibited under Basel Convention",
            "Violations subject to significant penalties",
        ],
    },
    # ... more routes
}
```

---

## Phase 3: Trader Power Features

### 3.1 Configurable Recovery Rates
- [ ] Per-metal recovery % inputs (currently fixed at 95%/85.5%)
- [ ] Preset profiles: "Conservative", "Typical", "Optimistic"
- [ ] Chemistry-specific defaults (LFP vs NMC)

### 3.2 Sensitivity Analysis
- [ ] Price sensitivity: ±10%, ±20% impact on value
- [ ] Recovery sensitivity: impact of yield changes
- [ ] Visual charts showing break-even points
- [ ] "What-if" scenarios

### 3.3 Historical Price Charts
- [ ] 30/90/365 day price trends
- [ ] Metal-by-metal breakdown
- [ ] Export price data

### 3.4 Saved Configurations
- [ ] Save/load bid templates
- [ ] Named configurations (e.g., "Q1 2025 Canada Pricing")
- [ ] Quick recall for repeat customers

---

## Phase 4: Polish & Reliability

### 4.1 Code Quality
- [ ] Unit tests for calculation engine
- [ ] Integration tests for API endpoints
- [ ] Deduplicate logic between `app.py` and `backend.py`
- [ ] Better error handling with user notifications

### 4.2 UX Improvements
- [ ] Loading states during API calls
- [ ] Form validation before calculation
- [ ] Calculation history
- [ ] Mobile responsiveness

---

## Technical Implementation Notes

### Adding LFP Support (Backend Changes)

**File: `backend.py`**

1. Update metal list:
```python
# Add to assays dict in parse_coa_text()
assays = {
    "Nickel": 0.0, "Cobalt": 0.0, "Lithium": 0.0,
    "Copper": 0.0, "Aluminum": 0.0, "Manganese": 0.0,
    "Iron": 0.0, "Phosphorus": 0.0  # NEW
}

# Add to target_map
"Iron": ["fe", "iron"],
"Phosphorus": ["p", "phosphorus", "phos"]
```

2. Add chemistry detection:
```python
def detect_chemistry(assays):
    """Auto-detect battery chemistry from assay profile."""
    ni = assays.get('Nickel', 0)
    co = assays.get('Cobalt', 0)
    fe = assays.get('Iron', 0)

    if fe > 0.20 and ni < 0.05 and co < 0.05:
        return "LFP"
    elif ni > 0.10 or co > 0.05:
        return "NMC"  # or NCM, NCA
    else:
        return "Unknown"
```

3. Add LFP-specific valuation:
```python
# LFP value is primarily from Lithium recovery
# Iron phosphate has some value but much lower than Ni/Co
LFP_FACTORS = {
    "Fe_recovery": 0.90,  # Iron recovery rate
    "FePO4_value_per_kg": 0.50,  # Much lower than battery metals
}
```

### Transportation Advisory (API Changes)

**New endpoint: `/api/transport-advisory`**
```python
@app.route('/api/transport-advisory', methods=['POST'])
def get_transport_advisory():
    origin = request.json.get('origin_country')  # e.g., "CA"
    destination = request.json.get('destination_country')  # e.g., "US"
    material_type = request.json.get('material_type')  # e.g., "black_mass"

    advisory = TRANSPORT_ADVISORIES.get((origin, destination), {})
    return jsonify(advisory)
```

---

## Questions to Resolve

1. **LFP Product Pathways:** What do recyclers actually produce from LFP?
   - Lithium carbonate/hydroxide (same as NMC)
   - Iron phosphate (FePO4) - is this sold?
   - Graphite recovery?

2. **Transportation Data Source:** Where to get authoritative info?
   - Basel Convention text
   - EPA/ECCC regulations
   - Industry associations (Battery Council International?)

3. **Report Branding:** Should traders be able to add their logo/company info?

4. **Offline Mode:** Should calculations work without API (using cached prices)?

---

## Deployment Notes

- **Backend:** Railway (auto-deploys on push)
- **Frontend:** Lovable/Vercel at https://batteryvaluator.vercel.app
- **Branch:** `claude/strategize-improvements-aDKgJ`
