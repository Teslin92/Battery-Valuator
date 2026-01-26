# Battery Valuator - Complete Architecture Review

**Date:** January 26, 2026  
**Reviewer:** AI Code Analysis  
**Scope:** Python backend + Lovable React frontend

---

## Executive Summary

### Current State
- **Two separate repositories** with different tech stacks
- **Backend:** Python (Flask API + Streamlit UI) in local repo
- **Frontend:** React/TypeScript (Lovable) in GitHub repo
- **Integration:** REST API contract with documented endpoints
- **Deployment:** Backend on Railway, Frontend on Lovable/Vercel

### Key Findings
✅ **Strengths:**
- Clean separation of calculation engine from UI
- Well-documented API contract
- Both UIs functional and deployed
- Proper CORS and error handling

⚠️ **Critical Issues:**
1. **Known bug:** Pre-treatment cost incorrectly applied to Black Mass (documented in LOVABLE_FIX_PROMPT.md)
2. **Type duplication:** Metal names, feed types, products defined in 3+ places
3. **No shared contract:** Frontend types manually maintained, prone to drift
4. **Deployment complexity:** Two separate deploy pipelines
5. **Testing gaps:** No integration tests between API and frontend

### Recommendation
**YES - Combine into a monorepo** with clear boundaries and shared contracts.

---

## Part 1: Backend Analysis

### Architecture Overview

```
backend.py (509 lines)
├── Pure calculation engine
├── No UI dependencies
├── Market data fetching (Metals.Dev + yfinance fallbacks)
├── COA text parsing
└── Valuation calculation logic

api.py (227 lines)
├── Flask REST wrapper
├── 5 endpoints
├── CORS enabled
└── Error handling

app.py (664 lines)
├── Streamlit UI
├── Direct import of backend.py
├── Duplicate logic for UI state
└── Independent deployment
```

### Code Quality Assessment

#### ✅ Strengths

1. **Clean Separation**
   - `backend.py` is pure Python with zero UI dependencies
   - Can be imported by both Streamlit and Flask
   - Calculation logic is reusable

2. **Robust Data Fetching**
   - Multi-tier fallback: Metals.Dev → yfinance → static prices
   - 15-minute caching for API responses
   - Proper timeout handling

3. **Flexible COA Parser**
   - Handles percentages, basis points, decimals
   - Regex-based extraction
   - Works with various formats

4. **Validation**
   - Grade range checking (Ni 10-60%, Co 3-25%, Li 1-10%)
   - Total metal content validation
   - Warning system for unrealistic values

#### ⚠️ Issues & Risks

1. **Type Safety (HIGH SEVERITY)**
   ```python
   # No type hints in backend.py
   def calculate_valuation(input_params):  # What shape is this dict?
       assays = input_params['assays']  # What keys are required?
   ```
   - No Pydantic models or dataclasses
   - Easy to pass wrong data structure
   - Runtime errors instead of validation errors

2. **Magic Strings Everywhere (MEDIUM SEVERITY)**
   ```python
   # In backend.py
   feed_type = input_params['feed_type']  # String matching
   if feed_type == "Black Mass (Processed)":  # Typo = silent bug
   
   # In api.py
   ni_product = input_params.get('ni_product', 'Sulphates (Battery Salt)')
   
   # In app.py
   feed_type = st.sidebar.selectbox("Material Type", 
       ["Black Mass (Processed)", "Cathode Foils", ...])
   ```
   - Feed types defined in 3 places
   - Product names defined in 3 places
   - No single source of truth

3. **Duplicate Constants (MEDIUM SEVERITY)**
   ```python
   # backend.py
   FACTORS = {
       "Ni_to_Sulphate": 4.48,
       "Co_to_Sulphate": 4.77,
       ...
   }
   
   # app.py (lines 75-80)
   FACTORS = {
       "Ni_to_Sulphate": 4.48,
       "Co_to_Sulphate": 4.77,
       ...
   }
   ```
   - Stoichiometry factors duplicated
   - If one changes, other must be updated manually

4. **Inconsistent Naming (LOW SEVERITY)**
   ```python
   # API uses full names
   assays = {"Nickel": 0.205, "Cobalt": 0.062, ...}
   
   # But prices use abbreviations
   metal_prices = {"Ni": 16.5, "Co": 33.0, ...}
   
   # And payables also use abbreviations
   payables = {"Ni": 0.80, "Co": 0.75, ...}
   ```
   - Inconsistent key naming
   - Requires mapping logic in multiple places

5. **Market Data Caching (LOW SEVERITY)**
   ```python
   # backend.py uses module-level cache
   _metals_dev_cache = {
       'data': None,
       'timestamp': None,
       'ttl_minutes': 15
   }
   ```
   - Works for single-process deployment
   - Won't work across multiple workers/instances
   - Should use Redis or similar for production

6. **Error Handling Inconsistency**
   ```python
   # api.py returns different error formats
   return jsonify({'success': False, 'error': str(e)}), 500
   
   # vs
   return jsonify({'success': False, 'error': 'Missing coa_text parameter'}), 400
   ```
   - No standardized error response shape
   - Frontend must handle multiple formats

### API Contract Analysis

#### Endpoint: `POST /api/calculate`

**Request Shape:**
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
  "shredding_cost_per_ton": 0,
  "elec_surcharge": 0,
  "has_electrolyte": false,
  "refining_opex_base": 1500,
  "ni_product": "Sulphates (Battery Salt)",
  "li_product": "Carbonate (LCE)"
}
```

**Issues:**
- ❌ No validation on required fields (crashes if missing)
- ❌ No range validation (can send negative weights)
- ❌ Inconsistent naming (assays use full names, prices use abbreviations)
- ❌ No OpenAPI spec

### Streamlit App Analysis

**Purpose:** Standalone UI for internal use

**Overlap with Lovable Frontend:**
- 100% feature parity
- Same calculation logic (via backend.py import)
- Different UX/design

**Recommendation:**
- Keep for internal/admin use
- Deprecate once Lovable frontend is stable
- Or maintain as "power user" tool with advanced features

---

## Part 2: Frontend Analysis

### Architecture Overview

```
src/
├── lib/
│   ├── api.ts (API client)
│   └── utils.ts (utilities)
├── hooks/
│   └── useBatteryValuator.ts (main state hook)
├── components/
│   └── valuator/
│       ├── GlobalSettings.tsx
│       ├── FeedstockSection.tsx
│       ├── PricingSection.tsx
│       ├── RefiningSection.tsx
│       ├── AssaySection.tsx
│       ├── ResultsPanel.tsx
│       ├── ProductTable.tsx
│       └── CostBreakdownChart.tsx
├── pages/
│   └── Index.tsx (main page)
└── types/
    └── battery.ts (TypeScript types)
```

### Code Quality Assessment

#### ✅ Strengths

1. **Modern Tech Stack**
   - React 18 + TypeScript
   - TanStack Query for data fetching
   - shadcn/ui components (Radix UI primitives)
   - Tailwind CSS for styling
   - Recharts for visualization

2. **Good Component Architecture**
   - Clear separation of concerns
   - Reusable UI components
   - Custom hook for business logic
   - Type-safe props

3. **Proper State Management**
   ```typescript
   // useBatteryValuator.ts
   const [formData, setFormData] = useState<FormData>(initialFormData);
   const [result, setResult] = useState<CalculationResult | null>(null);
   
   // TanStack Query for server state
   const { data: marketData, isLoading, refetch } = useQuery({
     queryKey: ['marketData', formData.currency],
     queryFn: () => fetchMarketData(formData.currency),
     staleTime: 5 * 60 * 1000,
   });
   ```

4. **Conditional Logic Implementation**
   ```typescript
   // useBatteryValuator.ts lines 164-171
   const updateFeedType = useCallback((feedType: FeedType) => {
     const isBlackMass = feedType === 'Black Mass (Processed)';
     setFormData(prev => ({
       ...prev,
       feedType,
       yieldPct: yields[feedType],
       shreddingCost: isBlackMass ? 0 : 300,  // ✅ Correct!
     }));
   }, []);
   ```

5. **API Request Builder**
   ```typescript
   // useBatteryValuator.ts lines 185-217
   const handleCalculate = useCallback(() => {
     const request = {
       // ... all fields ...
       shredding_cost_per_ton: formData.feedType === 'Black Mass (Processed)' 
         ? 0 
         : formData.shreddingCost,  // ✅ Correct conditional!
     };
     calcMutation.mutate(request);
   }, [formData, calcMutation]);
   ```

#### ⚠️ Issues & Risks

1. **Type Duplication (HIGH SEVERITY)**
   ```typescript
   // src/types/battery.ts (inferred from usage)
   export type FeedType = 
     | 'Black Mass (Processed)'
     | 'Cathode Foils'
     | 'Cell Stacks / Jelly Rolls'
     | 'Whole Cells'
     | 'Modules'
     | 'Battery Packs';
   
   export type NiProduct = 
     | 'Sulphates (Battery Salt)'
     | 'MHP (Intermediate)';
   
   export type LiProduct = 
     | 'Carbonate (LCE)'
     | 'Hydroxide (LiOH)';
   ```
   - These types are MANUALLY maintained
   - Must match backend string literals exactly
   - No validation that they're in sync
   - If backend adds new feed type, frontend breaks silently

2. **No Runtime Validation (MEDIUM SEVERITY)**
   ```typescript
   // src/lib/api.ts
   export const calculateValuation = async (request: CalculationRequest) => {
     const response = await api.post<CalculateResponse>('/api/calculate', request);
     return response.data;  // Assumes response matches CalculateResponse
   };
   ```
   - No Zod/Yup validation
   - Trusts API response shape
   - Runtime errors if API changes

3. **Hardcoded Constants (MEDIUM SEVERITY)**
   ```typescript
   // useBatteryValuator.ts lines 164-171
   const yields: Record<FeedType, number> = {
     'Black Mass (Processed)': 100,
     'Cathode Foils': 90,
     'Cell Stacks / Jelly Rolls': 70,
     'Whole Cells': 60,
     'Modules': 50,
     'Battery Packs': 40,
   };
   ```
   - Duplicates backend logic
   - If backend changes defaults, frontend is out of sync

4. **API Base URL Management**
   ```typescript
   // src/lib/api.ts
   const API_BASE_URL = import.meta.env.VITE_API_URL 
     || 'https://web-production-e2d0.up.railway.app';
   ```
   - Hardcoded fallback URL
   - No environment-specific config
   - Should use proper env vars

5. **Error Handling (LOW SEVERITY)**
   ```typescript
   // src/lib/api.ts
   export const fetchMarketData = async (currency: Currency) => {
     try {
       const response = await api.get(`/api/market-data?currency=${currency}`);
       return response.data;
     } catch (error) {
       console.error('Failed to fetch market data:', error);
       throw error;  // Re-throws without context
     }
   };
   ```
   - Generic error messages
   - No user-friendly error handling
   - Should provide actionable feedback

6. **Missing Features**
   - ❌ No PDF export (mentioned in Index.tsx but uses html2canvas/jsPDF client-side)
   - ❌ No save/load configurations
   - ❌ No dark mode (mentioned in integration docs)
   - ❌ No mobile optimization testing

### UI/UX Analysis

#### ✅ Good Practices

1. **Loading States**
   ```typescript
   {isLoadingMarket && <Spinner />}
   {isCalculating && <Button disabled>Calculating...</Button>}
   ```

2. **Conditional Rendering**
   ```typescript
   // FeedstockSection.tsx
   {!isBlackMass && (
     <div>
       <label>Mechanical Recovery</label>
       <Slider ... />
     </div>
   )}
   ```

3. **Live Price Display**
   ```typescript
   // PricingSection.tsx
   <Input value={formData.prices.ni} />
   <span>Live: ${marketData.Ni.toFixed(2)}</span>
   ```

#### ⚠️ Issues

1. **No Form Validation**
   - Can submit with 0 or negative weights
   - No min/max constraints on inputs
   - Should use React Hook Form with Zod

2. **Inconsistent Formatting**
   ```typescript
   // Multiple currency formatting implementations
   const symbol = currency === 'EUR' ? '€' : currency === 'CNY' ? '¥' : '$';
   ```
   - Should use `Intl.NumberFormat`

3. **Accessibility**
   - No ARIA labels on sliders
   - No keyboard navigation testing
   - No screen reader testing

---

## Part 3: Integration Analysis

### Known Bug: Pre-treatment Cost

**Status:** DOCUMENTED in LOVABLE_FIX_PROMPT.md

**Issue:** Frontend was initially sending `shredding_cost_per_ton: 300` for Black Mass

**Current Status:** ✅ FIXED in frontend code
```typescript
// useBatteryValuator.ts line 211
shredding_cost_per_ton: formData.feedType === 'Black Mass (Processed)' ? 0 : formData.shreddingCost,
```

**Verification Needed:**
- Test with exact inputs from LOVABLE_FIX_PROMPT.md
- Confirm Total OPEX = $1,500 (not $1,800)
- Confirm Net Profit = $449.02 CAD

### API Contract Drift Risk

**Scenario:** Backend adds new feed type "Battery Modules (Shredded)"

**What Happens:**
1. Backend: Add to validation logic ✅
2. API: No changes needed ✅
3. Frontend: Type error ❌ (FeedType union doesn't include it)
4. UI: Dropdown doesn't show new option ❌
5. Users: Can't select new material type ❌

**Solution:** Shared contract package (see Part 4)

### Deployment Complexity

**Current:**
```
Developer makes change
  ↓
Backend: git push → Railway deploy (Python)
Frontend: git push → Lovable/Vercel deploy (Node.js)
  ↓
Two separate pipelines
Two separate logs
Two separate rollback procedures
```

**Issues:**
- Can't deploy atomically
- Backend deploy can break frontend
- No integration testing in CI
- Manual coordination required

---

## Part 4: Monorepo Recommendation

### Why Monorepo?

✅ **Benefits:**
1. **Single source of truth** for types and constants
2. **Atomic deploys** - backend + frontend together
3. **Shared tooling** - linting, testing, CI/CD
4. **Easier refactoring** - change API contract, update frontend in same PR
5. **Better developer experience** - one repo to clone, one set of commands

❌ **Drawbacks:**
1. **Build complexity** - need proper tooling (Turborepo/Nx)
2. **Different runtimes** - Python + Node.js in same repo
3. **Larger repo size** - more to clone/sync
4. **Learning curve** - team needs to understand monorepo patterns

### Proposed Structure

```
battery-valuator/
├── apps/
│   ├── api/                    # Flask API (Python)
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── api.py          # Flask routes
│   │   │   ├── engine.py       # Calculation logic (renamed from backend.py)
│   │   │   └── market_data.py  # Market data fetching
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   ├── Procfile
│   │   └── README.md
│   │
│   ├── web/                    # React frontend (TypeScript)
│   │   ├── src/
│   │   │   ├── lib/
│   │   │   ├── hooks/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   └── types/          # Generated from contracts
│   │   ├── public/
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── README.md
│   │
│   └── streamlit/              # Streamlit UI (Python) - OPTIONAL
│       ├── app.py
│       ├── requirements.txt
│       └── README.md
│
├── packages/
│   ├── contracts/              # Shared API contract
│   │   ├── openapi.yaml        # OpenAPI 3.0 spec
│   │   ├── generate-types.sh   # Script to generate TS types
│   │   └── README.md
│   │
│   └── constants/              # Shared constants (Python + TS)
│       ├── feed_types.json     # Feed types and defaults
│       ├── products.json       # Product types
│       ├── stoichiometry.json  # Conversion factors
│       └── README.md
│
├── tools/
│   ├── scripts/
│   │   ├── validate-contract.py    # Validate API matches spec
│   │   └── generate-types.ts       # Generate TS from OpenAPI
│   └── docker/
│       ├── Dockerfile.api
│       └── Dockerfile.web
│
├── .github/
│   └── workflows/
│       ├── api-deploy.yml
│       ├── web-deploy.yml
│       └── integration-tests.yml
│
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
│
├── turbo.json                  # Turborepo config
├── package.json                # Root package.json
├── .gitignore
└── README.md
```

### Key Design Decisions

#### 1. Shared Contracts Package

**`packages/contracts/openapi.yaml`**
```yaml
openapi: 3.0.0
info:
  title: Battery Valuator API
  version: 1.0.0

components:
  schemas:
    FeedType:
      type: string
      enum:
        - Black Mass (Processed)
        - Cathode Foils
        - Cell Stacks / Jelly Rolls
        - Whole Cells
        - Modules
        - Battery Packs
    
    CalculationRequest:
      type: object
      required:
        - gross_weight
        - assays
        - metal_prices
        - payables
      properties:
        currency:
          type: string
          enum: [USD, CAD, EUR, CNY]
        gross_weight:
          type: number
          minimum: 0
        feed_type:
          $ref: '#/components/schemas/FeedType'
        # ... rest of schema
```

**Benefits:**
- Single source of truth
- Generate TypeScript types automatically
- Validate API responses at runtime
- Generate API documentation automatically

**Tooling:**
- `openapi-typescript` - Generate TS types from OpenAPI
- `openapi-python-client` - Generate Python client (optional)
- `swagger-ui` - API documentation UI

#### 2. Shared Constants Package

**`packages/constants/feed_types.json`**
```json
{
  "feedTypes": [
    {
      "id": "black_mass_processed",
      "label": "Black Mass (Processed)",
      "defaultYield": 100,
      "requiresShredding": false,
      "defaultMechRecovery": 100
    },
    {
      "id": "cathode_foils",
      "label": "Cathode Foils",
      "defaultYield": 90,
      "requiresShredding": true,
      "defaultMechRecovery": 95
    }
  ]
}
```

**Usage in Python:**
```python
import json
from pathlib import Path

FEED_TYPES = json.loads(
    (Path(__file__).parent.parent / "packages/constants/feed_types.json").read_text()
)

def get_default_yield(feed_type_label: str) -> float:
    for ft in FEED_TYPES["feedTypes"]:
        if ft["label"] == feed_type_label:
            return ft["defaultYield"] / 100.0
    return 1.0
```

**Usage in TypeScript:**
```typescript
import feedTypesData from '@battery-valuator/constants/feed_types.json';

export const FEED_TYPES = feedTypesData.feedTypes;

export function getDefaultYield(feedTypeLabel: string): number {
  const ft = FEED_TYPES.find(f => f.label === feedTypeLabel);
  return ft ? ft.defaultYield / 100 : 1.0;
}
```

#### 3. Deployment Strategy

**Option A: Separate Deploys (Current)**
- Keep Railway for API
- Keep Vercel/Lovable for frontend
- Monorepo just for development

**Option B: Docker Compose**
- Single docker-compose.yml
- Deploy to Railway/Render/Fly.io
- Easier local development

**Option C: Kubernetes (Overkill)**
- Separate pods for API and web
- Only if scaling to 1000s of users

**Recommendation:** Option A initially, migrate to B if needed

---

## Part 5: Migration Plan

### Phase 1: Setup Monorepo (Week 1)

**Tasks:**
1. Create new repo `battery-valuator-monorepo`
2. Setup Turborepo/Nx
3. Move backend code to `apps/api/`
4. Move frontend code to `apps/web/`
5. Setup root package.json with workspaces
6. Verify both apps still run independently

**Validation:**
- `npm run dev:api` starts Flask
- `npm run dev:web` starts Vite
- No functionality changes

### Phase 2: Extract Shared Contracts (Week 2)

**Tasks:**
1. Create `packages/contracts/openapi.yaml`
2. Document all API endpoints in OpenAPI format
3. Setup `openapi-typescript` to generate types
4. Update frontend to use generated types
5. Add runtime validation with Zod

**Validation:**
- Frontend types match API exactly
- API changes trigger type errors in frontend
- Runtime validation catches malformed responses

### Phase 3: Extract Shared Constants (Week 2)

**Tasks:**
1. Create `packages/constants/*.json` files
2. Extract feed types, products, stoichiometry
3. Update backend to read from JSON
4. Update frontend to read from JSON
5. Remove hardcoded constants

**Validation:**
- Add new feed type in JSON → works in both backend and frontend
- Change stoichiometry factor → updates everywhere

### Phase 4: Integration Testing (Week 3)

**Tasks:**
1. Setup Playwright for E2E tests
2. Write integration tests:
   - Market data fetch
   - COA parsing
   - Full valuation calculation
   - All material types
   - All product combinations
3. Add to CI/CD pipeline

**Validation:**
- All tests pass
- Tests catch API contract violations
- Tests run on every PR

### Phase 5: Deployment (Week 4)

**Tasks:**
1. Update Railway config for monorepo
2. Update Vercel config for monorepo
3. Setup GitHub Actions for monorepo
4. Deploy to staging
5. Run smoke tests
6. Deploy to production

**Validation:**
- Both apps deploy successfully
- No downtime
- All features work

### Phase 6: Documentation (Week 4)

**Tasks:**
1. Update README.md
2. Write ARCHITECTURE.md
3. Write CONTRIBUTING.md
4. Document API with Swagger UI
5. Create developer onboarding guide

---

## Part 6: Detailed Technical Recommendations

### 1. Add Type Safety to Backend

**Before:**
```python
def calculate_valuation(input_params):
    assays = input_params['assays']
    # ...
```

**After:**
```python
from pydantic import BaseModel, Field
from typing import Literal

class Assays(BaseModel):
    Nickel: float = Field(ge=0, le=1)
    Cobalt: float = Field(ge=0, le=1)
    Lithium: float = Field(ge=0, le=1)
    Copper: float = Field(ge=0, le=1)
    Aluminum: float = Field(ge=0, le=1)
    Manganese: float = Field(ge=0, le=1)

class CalculationRequest(BaseModel):
    currency: Literal["USD", "CAD", "EUR", "CNY"] = "USD"
    gross_weight: float = Field(gt=0)
    feed_type: str
    yield_pct: float = Field(ge=0, le=1)
    assays: Assays
    # ... rest of fields

def calculate_valuation(input_params: CalculationRequest) -> CalculationResult:
    # Type-safe!
```

### 2. Generate TypeScript Types from OpenAPI

**Setup:**
```bash
npm install -D openapi-typescript
```

**Script:**
```json
{
  "scripts": {
    "generate-types": "openapi-typescript packages/contracts/openapi.yaml -o apps/web/src/types/api.generated.ts"
  }
}
```

**Usage:**
```typescript
import type { components } from '@/types/api.generated';

type CalculationRequest = components['schemas']['CalculationRequest'];
type CalculationResponse = components['schemas']['CalculationResponse'];
```

### 3. Add Runtime Validation

**Frontend:**
```typescript
import { z } from 'zod';

const CalculationResponseSchema = z.object({
  success: z.boolean(),
  data: z.object({
    net_bm_weight: z.number(),
    material_cost: z.number(),
    total_revenue: z.number(),
    net_profit: z.number(),
    // ... rest of schema
  }),
});

export const calculateValuation = async (request: CalculationRequest) => {
  const response = await api.post('/api/calculate', request);
  return CalculationResponseSchema.parse(response.data);  // Validates!
};
```

### 4. Standardize Error Responses

**Backend:**
```python
from flask import jsonify
from typing import Dict, Any

def error_response(message: str, code: int = 400, details: Dict[str, Any] = None) -> tuple:
    return jsonify({
        'success': False,
        'error': {
            'message': message,
            'code': code,
            'details': details or {}
        }
    }), code

@app.route('/api/calculate', methods=['POST'])
def calculate_valuation():
    try:
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        # Validate with Pydantic
        req = CalculationRequest(**data)
        result = backend.calculate_valuation(req.dict())
        
        return jsonify({'success': True, 'data': result})
    
    except ValidationError as e:
        return error_response('Validation failed', 400, {'errors': e.errors()})
    
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return error_response('Internal server error', 500)
```

### 5. Improve Market Data Caching

**Current:** Module-level dict (doesn't work with multiple workers)

**Better:** Redis cache
```python
import redis
import json
from datetime import timedelta

redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))

def get_market_data(currency: str):
    cache_key = f"market_data:{currency}"
    
    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Fetch fresh data
    data = fetch_fresh_market_data(currency)
    
    # Cache for 15 minutes
    redis_client.setex(cache_key, timedelta(minutes=15), json.dumps(data))
    
    return data
```

### 6. Add Integration Tests

**Example:**
```typescript
// apps/web/tests/integration/valuation.spec.ts
import { test, expect } from '@playwright/test';

test('calculates black mass valuation correctly', async ({ page }) => {
  await page.goto('/');
  
  // Select material type
  await page.selectOption('[data-testid="material-type"]', 'Black Mass (Processed)');
  
  // Enter weight
  await page.fill('[data-testid="gross-weight"]', '1000');
  
  // Enter assays
  await page.fill('[data-testid="assay-ni"]', '20.5');
  await page.fill('[data-testid="assay-co"]', '6.2');
  await page.fill('[data-testid="assay-li"]', '2.5');
  
  // Run calculation
  await page.click('[data-testid="calculate-button"]');
  
  // Wait for results
  await page.waitForSelector('[data-testid="results-panel"]');
  
  // Verify no pre-treatment cost for black mass
  const preTreatCost = await page.textContent('[data-testid="pre-treat-cost"]');
  expect(preTreatCost).toContain('$0.00');
  
  // Verify profit is calculated
  const profit = await page.textContent('[data-testid="net-profit"]');
  expect(profit).not.toContain('$0.00');
});
```

---

## Part 7: Risk Assessment

### High Priority Risks

1. **Type Drift Between Backend and Frontend**
   - **Likelihood:** High
   - **Impact:** High (silent bugs, incorrect calculations)
   - **Mitigation:** Shared OpenAPI contract + generated types

2. **Breaking Changes in API**
   - **Likelihood:** Medium
   - **Impact:** High (frontend breaks)
   - **Mitigation:** Versioned API, integration tests

3. **Market Data API Failures**
   - **Likelihood:** Medium
   - **Impact:** Medium (fallback prices used)
   - **Mitigation:** Already has fallback system, add monitoring

### Medium Priority Risks

4. **Deployment Coordination**
   - **Likelihood:** Medium
   - **Impact:** Medium (temporary inconsistency)
   - **Mitigation:** Monorepo + atomic deploys

5. **Cache Invalidation Issues**
   - **Likelihood:** Low
   - **Impact:** Medium (stale prices)
   - **Mitigation:** Move to Redis, add TTL monitoring

### Low Priority Risks

6. **Performance at Scale**
   - **Likelihood:** Low
   - **Impact:** Low (current usage is low)
   - **Mitigation:** Add monitoring, optimize if needed

---

## Part 8: Conclusion

### Should They Be Combined?

**YES - Strongly Recommended**

**Reasons:**
1. ✅ Eliminates type duplication and drift
2. ✅ Enables atomic deploys
3. ✅ Simplifies developer workflow
4. ✅ Enables shared tooling and testing
5. ✅ Reduces maintenance burden

**Recommended Structure:**
- Monorepo with clear app boundaries
- Shared contracts package (OpenAPI)
- Shared constants package (JSON)
- Separate deployment targets (Railway + Vercel)
- Comprehensive integration tests

### Next Steps

**Immediate (This Week):**
1. Create monorepo structure
2. Move code without changes
3. Verify everything still works

**Short Term (Next 2 Weeks):**
1. Extract shared contracts
2. Generate TypeScript types
3. Add runtime validation

**Medium Term (Next Month):**
1. Add integration tests
2. Setup CI/CD for monorepo
3. Deploy to production

**Long Term (Next Quarter):**
1. Deprecate Streamlit app (optional)
2. Add advanced features
3. Optimize performance

---

## Appendix A: File Inventory

### Backend Files
- `backend.py` (509 lines) - Calculation engine
- `api.py` (227 lines) - Flask API
- `app.py` (664 lines) - Streamlit UI
- `requirements.txt` - Python dependencies
- `Procfile` - Streamlit deployment
- `Procfile.api` - Flask deployment
- `LOVABLE_INTEGRATION.md` - API documentation
- `README_API.md` - API overview
- `LOVABLE_FIX_PROMPT.md` - Known bug documentation
- `DEPLOYMENT_GUIDE.md` - Deployment instructions

### Frontend Files
- `src/lib/api.ts` - API client
- `src/hooks/useBatteryValuator.ts` - Main state hook
- `src/components/valuator/*.tsx` - UI components (8 files)
- `src/pages/Index.tsx` - Main page
- `package.json` - Dependencies
- `vite.config.ts` - Build config

### Total Lines of Code
- Backend: ~1,400 lines Python
- Frontend: ~2,000 lines TypeScript
- Total: ~3,400 lines

---

## Appendix B: Technology Stack

### Backend
- **Language:** Python 3.11
- **Framework:** Flask 3.1.0
- **Data:** pandas 2.2.3
- **Market Data:** yfinance 0.2.50, requests 2.32.3
- **Server:** gunicorn 23.0.0
- **UI:** streamlit 1.40.2 (optional)

### Frontend
- **Language:** TypeScript 5.8
- **Framework:** React 18.3
- **Build:** Vite 5.4
- **UI Library:** Radix UI (via shadcn/ui)
- **Styling:** Tailwind CSS 3.4
- **Data Fetching:** TanStack Query 5.83
- **Charts:** Recharts 2.15
- **HTTP:** axios 1.13

### Deployment
- **Backend:** Railway (Python runtime)
- **Frontend:** Lovable/Vercel (Node.js runtime)
- **Database:** None (stateless)
- **Cache:** In-memory (should be Redis)

---

## Appendix C: API Endpoint Summary

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| GET | `/api/health` | Health check | ✅ Working |
| GET | `/api/market-data` | Fetch live prices | ✅ Working |
| POST | `/api/parse-coa` | Parse COA text | ✅ Working |
| POST | `/api/calculate` | Main calculation | ✅ Working |
| POST | `/api/validate-assays` | Validate ranges | ✅ Working |

---

## Appendix D: Type Definitions Needed

### Shared Types (to be extracted)

```typescript
// Feed Types
type FeedType = 
  | 'Black Mass (Processed)'
  | 'Cathode Foils'
  | 'Cell Stacks / Jelly Rolls'
  | 'Whole Cells'
  | 'Modules'
  | 'Battery Packs';

// Product Types
type NiProduct = 'Sulphates (Battery Salt)' | 'MHP (Intermediate)';
type LiProduct = 'Carbonate (LCE)' | 'Hydroxide (LiOH)';

// Currency
type Currency = 'USD' | 'CAD' | 'EUR' | 'CNY';

// Assay Basis
type AssayBasis = 'Final Powder' | 'Whole Battery';

// Metal Names (full)
type MetalName = 'Nickel' | 'Cobalt' | 'Lithium' | 'Copper' | 'Aluminum' | 'Manganese';

// Metal Symbols (abbreviated)
type MetalSymbol = 'Ni' | 'Co' | 'Li' | 'Cu' | 'Al' | 'Mn';

// Assays (full names, decimals)
interface Assays {
  Nickel: number;
  Cobalt: number;
  Lithium: number;
  Copper: number;
  Aluminum: number;
  Manganese: number;
}

// Prices (symbols, per kg)
interface MetalPrices {
  Ni: number;
  Co: number;
  Li: number;
  Cu: number;
  Al: number;
  Mn: number;
}

// Payables (symbols, decimals)
interface Payables {
  Ni: number;
  Co: number;
  Li: number;
  Cu: number;
  Al: number;
  Mn: number;
}
```

---

**End of Review**
