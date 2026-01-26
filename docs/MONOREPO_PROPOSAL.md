# Battery Valuator - Monorepo Structure Proposal

**Date:** January 26, 2026  
**Status:** Proposed  
**Decision:** Combine repositories into monorepo

---

## Executive Summary

This document proposes a monorepo structure for the Battery Valuator project, combining the Python backend and React frontend into a single repository with shared contracts and constants.

**Key Benefits:**
- ✅ Single source of truth for API contracts
- ✅ Atomic deployments
- ✅ Shared tooling and CI/CD
- ✅ Easier refactoring across stack
- ✅ Better developer experience

---

## Proposed Directory Structure

```
battery-valuator/
│
├── apps/
│   ├── api/                           # Python Flask API
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                # Flask app (renamed from api.py)
│   │   │   ├── engine.py              # Calculation engine (renamed from backend.py)
│   │   │   ├── market_data.py         # Market data fetching (extracted)
│   │   │   ├── models.py              # Pydantic models
│   │   │   └── utils.py               # Utilities
│   │   ├── tests/
│   │   │   ├── test_engine.py
│   │   │   ├── test_market_data.py
│   │   │   └── test_api.py
│   │   ├── requirements.txt
│   │   ├── requirements-dev.txt
│   │   ├── Procfile
│   │   ├── .python-version
│   │   └── README.md
│   │
│   ├── web/                           # React/TypeScript frontend
│   │   ├── src/
│   │   │   ├── lib/
│   │   │   │   ├── api.ts
│   │   │   │   └── utils.ts
│   │   │   ├── hooks/
│   │   │   │   └── useBatteryValuator.ts
│   │   │   ├── components/
│   │   │   │   ├── ui/                # shadcn/ui components
│   │   │   │   └── valuator/
│   │   │   │       ├── GlobalSettings.tsx
│   │   │   │       ├── FeedstockSection.tsx
│   │   │   │       ├── PricingSection.tsx
│   │   │   │       ├── RefiningSection.tsx
│   │   │   │       ├── AssaySection.tsx
│   │   │   │       ├── ResultsPanel.tsx
│   │   │   │       ├── ProductTable.tsx
│   │   │   │       └── CostBreakdownChart.tsx
│   │   │   ├── pages/
│   │   │   │   ├── Index.tsx
│   │   │   │   └── NotFound.tsx
│   │   │   ├── types/
│   │   │   │   ├── api.generated.ts   # Generated from OpenAPI
│   │   │   │   └── battery.ts         # App-specific types
│   │   │   ├── App.tsx
│   │   │   ├── main.tsx
│   │   │   └── index.css
│   │   ├── public/
│   │   │   └── Battery Valuator.png
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   └── integration/
│   │   │       └── valuation.spec.ts
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.ts
│   │   ├── playwright.config.ts
│   │   └── README.md
│   │
│   └── streamlit/                     # Streamlit UI (optional, for internal use)
│       ├── app.py
│       ├── requirements.txt
│       ├── Procfile
│       └── README.md
│
├── packages/
│   ├── contracts/                     # Shared API contract
│   │   ├── openapi.yaml               # OpenAPI 3.0 specification
│   │   ├── schemas/
│   │   │   ├── calculation.yaml
│   │   │   ├── market-data.yaml
│   │   │   └── common.yaml
│   │   ├── generate-types.sh          # Generate TypeScript types
│   │   ├── validate-spec.sh           # Validate OpenAPI spec
│   │   ├── package.json
│   │   └── README.md
│   │
│   └── constants/                     # Shared constants (JSON)
│       ├── feed-types.json
│       ├── products.json
│       ├── stoichiometry.json
│       ├── default-payables.json
│       ├── metal-ranges.json
│       ├── package.json               # For TypeScript imports
│       └── README.md
│
├── tools/
│   ├── scripts/
│   │   ├── setup-dev.sh               # Setup development environment
│   │   ├── validate-contract.py       # Validate API matches OpenAPI spec
│   │   ├── generate-types.ts          # Generate TS types from OpenAPI
│   │   ├── sync-constants.py          # Validate constants are in sync
│   │   └── deploy.sh                  # Deployment script
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.web
│   │   └── docker-compose.yml
│   └── README.md
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                     # Main CI pipeline
│   │   ├── api-deploy.yml             # Deploy API to Railway
│   │   ├── web-deploy.yml             # Deploy web to Vercel
│   │   ├── integration-tests.yml      # E2E tests
│   │   └── contract-validation.yml    # Validate API contract
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── docs/
│   ├── API.md                         # API documentation
│   ├── ARCHITECTURE.md                # Architecture overview
│   ├── DEPLOYMENT.md                  # Deployment guide
│   ├── CONTRIBUTING.md                # Contribution guidelines
│   ├── DEVELOPMENT.md                 # Local development setup
│   └── MIGRATION.md                   # Migration guide from old structure
│
├── .gitignore
├── .editorconfig
├── .prettierrc
├── .eslintrc.json
├── turbo.json                         # Turborepo configuration
├── package.json                       # Root package.json (workspaces)
├── package-lock.json
├── README.md
└── LICENSE
```

---

## Detailed Package Descriptions

### 1. `apps/api/` - Python Flask API

**Purpose:** RESTful API for battery material valuation

**Key Files:**
- `src/main.py` - Flask application with routes
- `src/engine.py` - Pure calculation logic
- `src/market_data.py` - Market data fetching
- `src/models.py` - Pydantic models for validation

**Dependencies:**
- Flask 3.1.0
- Flask-CORS 5.0.0
- Pydantic 2.x (NEW - for validation)
- pandas 2.2.3
- yfinance 0.2.50
- requests 2.32.3
- gunicorn 23.0.0

**New Features:**
- Pydantic models for request/response validation
- Structured logging
- Health check with detailed diagnostics
- OpenAPI spec validation

**Deployment:**
- Railway (Python runtime)
- Command: `gunicorn src.main:app`

---

### 2. `apps/web/` - React Frontend

**Purpose:** Modern web UI for battery valuator

**Key Files:**
- `src/lib/api.ts` - API client with generated types
- `src/hooks/useBatteryValuator.ts` - Main state management
- `src/components/valuator/` - UI components
- `src/types/api.generated.ts` - Generated from OpenAPI

**Dependencies:**
- React 18.3
- TypeScript 5.8
- Vite 5.4
- TanStack Query 5.83
- Radix UI (shadcn/ui)
- Tailwind CSS 3.4
- Recharts 2.15
- Zod 3.25 (NEW - for runtime validation)

**New Features:**
- Runtime validation with Zod
- Generated TypeScript types from OpenAPI
- Integration tests with Playwright
- Error boundary components
- Loading states and skeletons

**Deployment:**
- Vercel (Node.js runtime)
- Command: `vite build`

---

### 3. `apps/streamlit/` - Streamlit UI (Optional)

**Purpose:** Internal/admin UI for power users

**Status:** Optional - can be deprecated once web UI is stable

**Use Cases:**
- Internal testing
- Admin operations
- Batch processing
- Data export

**Deployment:**
- Railway (Python runtime)
- Command: `streamlit run app.py`

---

### 4. `packages/contracts/` - API Contract

**Purpose:** Single source of truth for API specification

**Structure:**
```
contracts/
├── openapi.yaml              # Main OpenAPI spec
├── schemas/
│   ├── calculation.yaml      # Calculation request/response
│   ├── market-data.yaml      # Market data schemas
│   └── common.yaml           # Shared schemas
├── generate-types.sh         # Generate TypeScript types
├── validate-spec.sh          # Validate OpenAPI spec
└── README.md
```

**Key Features:**
- OpenAPI 3.0 specification
- Automatic TypeScript type generation
- Runtime validation schemas
- API documentation generation

**Example Schema:**
```yaml
# schemas/calculation.yaml
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
      default: USD
    gross_weight:
      type: number
      minimum: 0
      exclusiveMinimum: true
      description: Total weight of input material in kg
    feed_type:
      $ref: '#/components/schemas/FeedType'
    yield_pct:
      type: number
      minimum: 0
      maximum: 1
      description: Yield percentage as decimal (0.0-1.0)
    # ... rest of schema
```

**Tooling:**
- `openapi-typescript` - Generate TS types
- `openapi-python-client` - Generate Python client (optional)
- `swagger-ui-express` - API documentation UI

**Usage in Frontend:**
```typescript
import type { components } from '@battery-valuator/contracts';

type CalculationRequest = components['schemas']['CalculationRequest'];
type CalculationResponse = components['schemas']['CalculationResponse'];
```

**Usage in Backend:**
```python
from pydantic import BaseModel
# Import generated Pydantic models from OpenAPI spec
```

---

### 5. `packages/constants/` - Shared Constants

**Purpose:** Single source of truth for business logic constants

**Files:**

#### `feed-types.json`
```json
{
  "feedTypes": [
    {
      "id": "black_mass_processed",
      "label": "Black Mass (Processed)",
      "description": "Pre-processed black mass powder",
      "defaultYield": 100,
      "requiresShredding": false,
      "requiresMechanicalRecovery": false,
      "defaultMechRecovery": 100,
      "defaultShreddingCost": 0
    },
    {
      "id": "cathode_foils",
      "label": "Cathode Foils",
      "description": "Cathode foils from battery disassembly",
      "defaultYield": 90,
      "requiresShredding": true,
      "requiresMechanicalRecovery": true,
      "defaultMechRecovery": 95,
      "defaultShreddingCost": 300
    }
    // ... other feed types
  ]
}
```

#### `products.json`
```json
{
  "niProducts": [
    {
      "id": "sulphates",
      "label": "Sulphates (Battery Salt)",
      "description": "Battery-grade nickel sulphate",
      "conversionFactor": 4.48,
      "priceKey": "NiSO4"
    },
    {
      "id": "mhp",
      "label": "MHP (Intermediate)",
      "description": "Mixed hydroxide precipitate",
      "payableNi": 0.85,
      "payableCo": 0.80
    }
  ],
  "liProducts": [
    {
      "id": "carbonate",
      "label": "Carbonate (LCE)",
      "description": "Lithium carbonate equivalent",
      "conversionFactor": 5.32,
      "priceKey": "LCE"
    },
    {
      "id": "hydroxide",
      "label": "Hydroxide (LiOH)",
      "description": "Lithium hydroxide monohydrate",
      "conversionFactor": 6.05,
      "priceKey": "LiOH"
    }
  ]
}
```

#### `stoichiometry.json`
```json
{
  "conversionFactors": {
    "Ni_to_NiSO4_6H2O": 4.48,
    "Co_to_CoSO4_7H2O": 4.77,
    "Li_to_Li2CO3": 5.32,
    "Li_to_LiOH_H2O": 6.05
  },
  "molecularWeights": {
    "Ni": 58.69,
    "Co": 58.93,
    "Li": 6.94,
    "Cu": 63.55,
    "Al": 26.98,
    "Mn": 54.94
  }
}
```

#### `default-payables.json`
```json
{
  "payables": {
    "Ni": 0.80,
    "Co": 0.75,
    "Li": 0.30,
    "Cu": 0.80,
    "Al": 0.70,
    "Mn": 0.60
  }
}
```

#### `metal-ranges.json`
```json
{
  "typicalRanges": {
    "blackMass": {
      "Nickel": { "min": 10, "max": 60, "unit": "%" },
      "Cobalt": { "min": 3, "max": 25, "unit": "%" },
      "Lithium": { "min": 1, "max": 10, "unit": "%" },
      "Copper": { "min": 0, "max": 10, "unit": "%" },
      "Aluminum": { "min": 0, "max": 5, "unit": "%" },
      "Manganese": { "min": 0, "max": 15, "unit": "%" }
    }
  }
}
```

**Usage in Python:**
```python
import json
from pathlib import Path

CONSTANTS_DIR = Path(__file__).parent.parent.parent / "packages/constants"

def load_feed_types():
    with open(CONSTANTS_DIR / "feed-types.json") as f:
        return json.load(f)["feedTypes"]

FEED_TYPES = load_feed_types()

def get_default_yield(feed_type_label: str) -> float:
    for ft in FEED_TYPES:
        if ft["label"] == feed_type_label:
            return ft["defaultYield"] / 100.0
    return 1.0
```

**Usage in TypeScript:**
```typescript
import feedTypesData from '@battery-valuator/constants/feed-types.json';
import productsData from '@battery-valuator/constants/products.json';

export const FEED_TYPES = feedTypesData.feedTypes;
export const NI_PRODUCTS = productsData.niProducts;
export const LI_PRODUCTS = productsData.liProducts;

export function getDefaultYield(feedTypeLabel: string): number {
  const ft = FEED_TYPES.find(f => f.label === feedTypeLabel);
  return ft ? ft.defaultYield / 100 : 1.0;
}

export function requiresShredding(feedTypeLabel: string): boolean {
  const ft = FEED_TYPES.find(f => f.label === feedTypeLabel);
  return ft?.requiresShredding ?? true;
}
```

---

## Tooling & Infrastructure

### 1. Monorepo Management

**Tool:** Turborepo

**Why Turborepo:**
- Fast builds with caching
- Simple configuration
- Works well with mixed languages
- Good CI/CD integration

**Configuration (`turbo.json`):**
```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", "build/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": []
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

**Alternative:** Nx (more features, steeper learning curve)

### 2. Package Manager

**Tool:** npm workspaces

**Why npm:**
- Built into npm (no extra tools)
- Simple workspace configuration
- Good TypeScript support

**Root `package.json`:**
```json
{
  "name": "battery-valuator",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "dev:api": "cd apps/api && python src/main.py",
    "dev:web": "cd apps/web && npm run dev",
    "dev:streamlit": "cd apps/streamlit && streamlit run app.py",
    "generate:types": "cd packages/contracts && npm run generate",
    "validate:contract": "cd packages/contracts && npm run validate"
  },
  "devDependencies": {
    "turbo": "^1.11.0",
    "prettier": "^3.1.0",
    "eslint": "^8.55.0"
  }
}
```

### 3. Type Generation

**Tool:** `openapi-typescript`

**Setup:**
```bash
npm install -D openapi-typescript
```

**Script (`packages/contracts/generate-types.sh`):**
```bash
#!/bin/bash
set -e

echo "Generating TypeScript types from OpenAPI spec..."

npx openapi-typescript openapi.yaml \
  --output ../web/src/types/api.generated.ts \
  --path-params-as-types

echo "✅ Types generated successfully"
```

**Usage in CI:**
```yaml
# .github/workflows/ci.yml
- name: Generate types
  run: npm run generate:types
  
- name: Check for uncommitted changes
  run: |
    git diff --exit-code || (echo "Generated types are out of sync" && exit 1)
```

### 4. Validation

**Tool:** Custom Python script

**Script (`tools/scripts/validate-contract.py`):**
```python
#!/usr/bin/env python3
"""
Validate that the API implementation matches the OpenAPI spec.
"""
import yaml
import requests
from typing import Dict, Any

def load_openapi_spec() -> Dict[str, Any]:
    with open("packages/contracts/openapi.yaml") as f:
        return yaml.safe_load(f)

def test_endpoint(base_url: str, method: str, path: str, spec: Dict[str, Any]):
    """Test that endpoint matches spec"""
    # Make request
    response = requests.request(method, f"{base_url}{path}")
    
    # Validate response schema
    # ... validation logic ...
    
    print(f"✅ {method} {path} - OK")

def main():
    spec = load_openapi_spec()
    base_url = "http://localhost:5000"
    
    for path, methods in spec["paths"].items():
        for method, endpoint_spec in methods.items():
            test_endpoint(base_url, method.upper(), path, endpoint_spec)

if __name__ == "__main__":
    main()
```

### 5. Testing

**Unit Tests:**
- Python: `pytest`
- TypeScript: `vitest`

**Integration Tests:**
- Playwright for E2E tests

**Test Structure:**
```
apps/api/tests/
├── test_engine.py          # Pure calculation logic
├── test_market_data.py     # Market data fetching
└── test_api.py             # API endpoints

apps/web/tests/
├── unit/
│   ├── hooks.test.ts       # React hooks
│   └── utils.test.ts       # Utilities
└── integration/
    └── valuation.spec.ts   # E2E tests
```

**CI Configuration:**
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: cd apps/api && pip install -r requirements-dev.txt
      - run: cd apps/api && pytest

  test-web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: cd apps/web && npm run test

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: cd apps/api && pip install -r requirements.txt
      - run: cd apps/api && python src/main.py &
      - run: cd apps/web && npm run test:e2e
```

---

## Migration Plan

### Phase 1: Setup Monorepo (Week 1)

**Goal:** Create monorepo structure without breaking existing functionality

**Tasks:**
1. Create new repo `battery-valuator-monorepo`
2. Setup Turborepo configuration
3. Create directory structure
4. Move backend code to `apps/api/`
5. Move frontend code to `apps/web/`
6. Move Streamlit to `apps/streamlit/`
7. Setup root package.json with workspaces
8. Update import paths
9. Verify both apps run independently

**Commands:**
```bash
# Create new repo
git init battery-valuator-monorepo
cd battery-valuator-monorepo

# Setup Turborepo
npm init -y
npm install -D turbo

# Create structure
mkdir -p apps/{api,web,streamlit} packages/{contracts,constants} tools/{scripts,docker} docs

# Copy files (from old repos)
cp -r ../Battery\ Valuator/* apps/api/
cp -r ../battery-value-hub/* apps/web/

# Setup workspaces
# Edit package.json to add workspaces

# Test
npm run dev:api    # Should start Flask
npm run dev:web    # Should start Vite
```

**Validation:**
- ✅ Both apps start without errors
- ✅ API responds to health check
- ✅ Frontend loads and makes API calls
- ✅ No functionality changes

**Deliverables:**
- Working monorepo with both apps
- Updated README with setup instructions
- CI pipeline running tests

---

### Phase 2: Extract Shared Contracts (Week 2)

**Goal:** Create OpenAPI spec and generate TypeScript types

**Tasks:**
1. Create `packages/contracts/openapi.yaml`
2. Document all 5 API endpoints
3. Define all request/response schemas
4. Setup `openapi-typescript` tooling
5. Generate TypeScript types
6. Update frontend to use generated types
7. Add runtime validation with Zod
8. Update backend to validate against spec

**Example OpenAPI Spec:**
```yaml
# packages/contracts/openapi.yaml
openapi: 3.0.0
info:
  title: Battery Valuator API
  version: 1.0.0
  description: REST API for battery material valuation

servers:
  - url: https://web-production-e2d0.up.railway.app
    description: Production
  - url: http://localhost:5000
    description: Development

paths:
  /api/health:
    get:
      summary: Health check
      responses:
        '200':
          description: API is healthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'

  /api/market-data:
    get:
      summary: Get market data
      parameters:
        - name: currency
          in: query
          schema:
            $ref: '#/components/schemas/Currency'
      responses:
        '200':
          description: Market data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MarketDataResponse'

  /api/calculate:
    post:
      summary: Calculate valuation
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CalculationRequest'
      responses:
        '200':
          description: Calculation result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CalculationResponse'

components:
  schemas:
    Currency:
      type: string
      enum: [USD, CAD, EUR, CNY]
    
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
          $ref: '#/components/schemas/Currency'
        gross_weight:
          type: number
          minimum: 0
          exclusiveMinimum: true
        feed_type:
          $ref: '#/components/schemas/FeedType'
        # ... rest of schema
```

**Validation:**
- ✅ OpenAPI spec validates (no errors)
- ✅ TypeScript types generated successfully
- ✅ Frontend compiles with generated types
- ✅ Runtime validation catches invalid responses
- ✅ API matches spec (validated by script)

**Deliverables:**
- Complete OpenAPI specification
- Generated TypeScript types
- Runtime validation with Zod
- Validation script in CI

---

### Phase 3: Extract Shared Constants (Week 2)

**Goal:** Move all hardcoded constants to JSON files

**Tasks:**
1. Create `packages/constants/*.json` files
2. Extract feed types and defaults
3. Extract product types and conversion factors
4. Extract stoichiometry constants
5. Extract default payables
6. Extract metal validation ranges
7. Update backend to read from JSON
8. Update frontend to read from JSON
9. Remove all hardcoded constants

**Example Migration:**

**Before (Python):**
```python
# backend.py
FACTORS = {
    "Ni_to_Sulphate": 4.48,
    "Co_to_Sulphate": 4.77,
    # ...
}
```

**After (Python):**
```python
# apps/api/src/engine.py
import json
from pathlib import Path

CONSTANTS_DIR = Path(__file__).parent.parent.parent.parent / "packages/constants"

with open(CONSTANTS_DIR / "stoichiometry.json") as f:
    STOICH = json.load(f)
    FACTORS = STOICH["conversionFactors"]
```

**Before (TypeScript):**
```typescript
// useBatteryValuator.ts
const yields: Record<FeedType, number> = {
  'Black Mass (Processed)': 100,
  'Cathode Foils': 90,
  // ...
};
```

**After (TypeScript):**
```typescript
// useBatteryValuator.ts
import feedTypesData from '@battery-valuator/constants/feed-types.json';

const yields = Object.fromEntries(
  feedTypesData.feedTypes.map(ft => [ft.label, ft.defaultYield])
);
```

**Validation:**
- ✅ All constants moved to JSON
- ✅ No hardcoded values in code
- ✅ Backend reads from JSON successfully
- ✅ Frontend reads from JSON successfully
- ✅ Tests pass with new constants

**Deliverables:**
- 5 JSON files with all constants
- Updated backend code
- Updated frontend code
- Validation script to check sync

---

### Phase 4: Integration Testing (Week 3)

**Goal:** Add comprehensive E2E tests

**Tasks:**
1. Setup Playwright
2. Write integration tests for all material types
3. Write tests for all product combinations
4. Write tests for error cases
5. Write tests for validation warnings
6. Add tests to CI pipeline
7. Setup test coverage reporting

**Example Test:**
```typescript
// apps/web/tests/integration/valuation.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Battery Valuation', () => {
  test('calculates Black Mass correctly', async ({ page }) => {
    await page.goto('/');
    
    // Select Black Mass
    await page.selectOption('[data-testid="material-type"]', 'Black Mass (Processed)');
    
    // Verify shredding cost field is hidden
    await expect(page.locator('[data-testid="shredding-cost"]')).not.toBeVisible();
    
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
    
    // Verify pre-treatment cost is $0
    const preTreatCost = await page.textContent('[data-testid="pre-treat-cost"]');
    expect(preTreatCost).toContain('$0.00');
    
    // Verify profit is positive
    const profit = await page.textContent('[data-testid="net-profit"]');
    expect(profit).toMatch(/\$[\d,]+\.\d{2}/);
  });
  
  test('shows shredding cost for Cathode Foils', async ({ page }) => {
    await page.goto('/');
    
    // Select Cathode Foils
    await page.selectOption('[data-testid="material-type"]', 'Cathode Foils');
    
    // Verify shredding cost field is visible
    await expect(page.locator('[data-testid="shredding-cost"]')).toBeVisible();
    
    // Verify default value
    const shreddingCost = await page.inputValue('[data-testid="shredding-cost"]');
    expect(shreddingCost).toBe('300');
  });
  
  test('validates unrealistic assay values', async ({ page }) => {
    await page.goto('/');
    
    // Enter unrealistic Nickel value
    await page.fill('[data-testid="assay-ni"]', '80');
    
    // Run calculation
    await page.click('[data-testid="calculate-button"]');
    
    // Wait for results
    await page.waitForSelector('[data-testid="results-panel"]');
    
    // Verify warning is shown
    await expect(page.locator('[data-testid="warnings"]')).toContainText('Nickel grade');
  });
});
```

**Validation:**
- ✅ All tests pass
- ✅ Tests cover all material types
- ✅ Tests cover all edge cases
- ✅ Tests run in CI
- ✅ Coverage > 80%

**Deliverables:**
- 20+ integration tests
- CI pipeline with test reporting
- Coverage report

---

### Phase 5: Deployment (Week 4)

**Goal:** Deploy monorepo to production

**Tasks:**
1. Update Railway config for monorepo
2. Update Vercel config for monorepo
3. Setup GitHub Actions for monorepo
4. Deploy to staging environment
5. Run smoke tests
6. Deploy to production
7. Monitor for errors

**Railway Configuration:**
```toml
# railway.toml (for API)
[build]
builder = "NIXPACKS"
buildCommand = "cd apps/api && pip install -r requirements.txt"

[deploy]
startCommand = "cd apps/api && gunicorn src.main:app --bind 0.0.0.0:$PORT"
healthcheckPath = "/api/health"
```

**Vercel Configuration:**
```json
{
  "buildCommand": "cd apps/web && npm run build",
  "outputDirectory": "apps/web/dist",
  "installCommand": "npm install",
  "framework": "vite"
}
```

**GitHub Actions:**
```yaml
# .github/workflows/deploy-api.yml
name: Deploy API

on:
  push:
    branches: [main]
    paths:
      - 'apps/api/**'
      - 'packages/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          # Railway CLI deployment
          railway up --service api
```

**Validation:**
- ✅ API deploys successfully
- ✅ Frontend deploys successfully
- ✅ Health checks pass
- ✅ Integration tests pass against production
- ✅ No errors in logs

**Deliverables:**
- Production deployment
- Monitoring dashboard
- Rollback procedure

---

### Phase 6: Documentation (Week 4)

**Goal:** Complete documentation for monorepo

**Tasks:**
1. Update main README.md
2. Write ARCHITECTURE.md
3. Write CONTRIBUTING.md
4. Write DEVELOPMENT.md
5. Write DEPLOYMENT.md
6. Write MIGRATION.md
7. Generate API docs from OpenAPI
8. Create developer onboarding guide

**Documentation Structure:**

#### `README.md`
```markdown
# Battery Valuator

Modern web application for battery material valuation.

## Quick Start

```bash
# Clone repo
git clone https://github.com/your-org/battery-valuator-monorepo.git
cd battery-valuator-monorepo

# Install dependencies
npm install
cd apps/api && pip install -r requirements.txt && cd ../..

# Start development servers
npm run dev
```

## Project Structure

- `apps/api/` - Python Flask API
- `apps/web/` - React frontend
- `packages/contracts/` - OpenAPI specification
- `packages/constants/` - Shared constants

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Development](docs/DEVELOPMENT.md)
- [Deployment](docs/DEPLOYMENT.md)
- [API Reference](docs/API.md)
- [Contributing](docs/CONTRIBUTING.md)
```

**Validation:**
- ✅ All documentation complete
- ✅ Setup instructions work
- ✅ API docs generated
- ✅ Developer can onboard in < 1 hour

**Deliverables:**
- Complete documentation
- API reference site
- Developer onboarding guide

---

## Development Workflow

### Local Development

**Setup:**
```bash
# Clone repo
git clone https://github.com/your-org/battery-valuator-monorepo.git
cd battery-valuator-monorepo

# Install Node dependencies
npm install

# Install Python dependencies
cd apps/api
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cd ../..

# Generate types
npm run generate:types
```

**Start Development Servers:**
```bash
# Terminal 1: Start API
npm run dev:api

# Terminal 2: Start Web
npm run dev:web

# Or start both with Turborepo
npm run dev
```

**Run Tests:**
```bash
# Run all tests
npm run test

# Run API tests only
cd apps/api && pytest

# Run web tests only
cd apps/web && npm run test

# Run integration tests
cd apps/web && npm run test:e2e
```

### Making Changes

**1. Update API Contract:**
```bash
# Edit OpenAPI spec
vim packages/contracts/openapi.yaml

# Regenerate types
npm run generate:types

# Update backend implementation
vim apps/api/src/main.py

# Update frontend to use new types
vim apps/web/src/lib/api.ts

# Run tests
npm run test
```

**2. Add New Feed Type:**
```bash
# Edit constants
vim packages/constants/feed-types.json

# Add new entry:
{
  "id": "battery_modules_shredded",
  "label": "Battery Modules (Shredded)",
  "defaultYield": 55,
  "requiresShredding": false,
  "defaultMechRecovery": 100,
  "defaultShreddingCost": 0
}

# Backend automatically picks up new type (reads from JSON)
# Frontend automatically picks up new type (reads from JSON)

# Add tests
vim apps/web/tests/integration/valuation.spec.ts

# Run tests
npm run test
```

**3. Update Stoichiometry:**
```bash
# Edit constants
vim packages/constants/stoichiometry.json

# Update conversion factor
{
  "conversionFactors": {
    "Ni_to_NiSO4_6H2O": 4.50  # Changed from 4.48
  }
}

# Backend and frontend automatically use new value

# Run tests to verify
npm run test
```

### Pull Request Workflow

1. Create feature branch
2. Make changes
3. Run tests locally
4. Commit changes
5. Push to GitHub
6. Create PR
7. CI runs tests
8. Code review
9. Merge to main
10. Auto-deploy to production

**PR Checks:**
- ✅ All tests pass
- ✅ Types are in sync
- ✅ Linting passes
- ✅ No console errors
- ✅ Integration tests pass

---

## Deployment Strategy

### Current Setup (Separate Deploys)

**API:**
- Platform: Railway
- Runtime: Python 3.11
- Command: `gunicorn src.main:app`
- URL: `https://web-production-e2d0.up.railway.app`

**Web:**
- Platform: Vercel
- Runtime: Node.js 18
- Command: `vite build`
- URL: `https://battery-valuator.vercel.app`

**Pros:**
- ✅ Simple setup
- ✅ Separate scaling
- ✅ Independent deploys

**Cons:**
- ❌ Manual coordination
- ❌ Can't deploy atomically
- ❌ Two separate logs

### Future: Docker Compose (Optional)

**Setup:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: tools/docker/Dockerfile.api
    ports:
      - "5000:5000"
    environment:
      - METALS_DEV_API_KEY=${METALS_DEV_API_KEY}
    volumes:
      - ./apps/api:/app
      - ./packages:/packages
  
  web:
    build:
      context: .
      dockerfile: tools/docker/Dockerfile.web
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://api:5000
    volumes:
      - ./apps/web:/app
    depends_on:
      - api
```

**Pros:**
- ✅ Single deployment
- ✅ Consistent environments
- ✅ Easy local development

**Cons:**
- ❌ More complex setup
- ❌ Single point of failure

---

## Monitoring & Observability

### Metrics to Track

**API:**
- Request count by endpoint
- Response time (p50, p95, p99)
- Error rate
- Market data fetch success rate
- Cache hit rate

**Web:**
- Page load time
- Time to interactive
- API call success rate
- User engagement (calculations per session)

### Logging

**API:**
```python
import logging
import structlog

logger = structlog.get_logger()

@app.route('/api/calculate', methods=['POST'])
def calculate_valuation():
    logger.info("calculation_started", 
                feed_type=data['feed_type'],
                gross_weight=data['gross_weight'])
    
    # ... calculation ...
    
    logger.info("calculation_completed",
                net_profit=result['net_profit'],
                duration_ms=duration)
```

**Web:**
```typescript
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
});

// Track calculation events
Sentry.addBreadcrumb({
  category: 'calculation',
  message: 'Valuation calculated',
  data: { feedType, grossWeight, profit },
});
```

---

## Security Considerations

### API Security

1. **Rate Limiting**
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(app, key_func=get_remote_address)
   
   @app.route('/api/calculate')
   @limiter.limit("10 per minute")
   def calculate_valuation():
       # ...
   ```

2. **Input Validation**
   - Use Pydantic for all inputs
   - Validate ranges (weight > 0, percentages 0-100)
   - Sanitize COA text input

3. **CORS Configuration**
   ```python
   CORS(app, origins=[
       "https://battery-valuator.vercel.app",
       "http://localhost:3000"  # Development only
   ])
   ```

### Frontend Security

1. **Environment Variables**
   - Never commit API keys
   - Use `.env.local` for secrets
   - Validate all env vars at build time

2. **Content Security Policy**
   ```typescript
   // vite.config.ts
   export default defineConfig({
     server: {
       headers: {
         'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'"
       }
     }
   });
   ```

---

## Cost Estimation

### Current Costs

**Railway (API):**
- Hobby Plan: $5/month
- Includes 500 hours runtime
- Sufficient for current usage

**Vercel (Web):**
- Hobby Plan: Free
- 100GB bandwidth/month
- Sufficient for current usage

**Metals.Dev API:**
- Free tier: 100 requests/month
- With caching: ~200 requests/month needed
- Cost: $0

**Total:** ~$5/month

### Future Costs (with Growth)

**At 1,000 users:**
- Railway Pro: $20/month
- Vercel Pro: $20/month
- Redis (Upstash): $10/month
- Metals.Dev: $10/month
- **Total:** ~$60/month

**At 10,000 users:**
- Railway Scale: $50/month
- Vercel Team: $50/month
- Redis: $30/month
- Metals.Dev: $50/month
- **Total:** ~$180/month

---

## Success Metrics

### Technical Metrics

- ✅ Build time < 5 minutes
- ✅ Test coverage > 80%
- ✅ API response time < 500ms (p95)
- ✅ Frontend load time < 2s
- ✅ Zero runtime type errors
- ✅ 99.9% uptime

### Developer Experience

- ✅ Onboarding time < 1 hour
- ✅ Local setup < 10 minutes
- ✅ Hot reload < 1 second
- ✅ Type errors caught at compile time
- ✅ Clear error messages

### Business Metrics

- ✅ Calculation accuracy 100%
- ✅ User satisfaction > 90%
- ✅ Support tickets < 5/month
- ✅ Feature velocity: 2 features/month

---

## Conclusion

This monorepo structure provides:

1. **Single Source of Truth**
   - OpenAPI spec for API contract
   - JSON files for business logic
   - Generated types for type safety

2. **Developer Experience**
   - Fast local development
   - Clear project structure
   - Comprehensive documentation
   - Automated tooling

3. **Maintainability**
   - Easy to refactor
   - Atomic changes
   - Comprehensive tests
   - Clear ownership

4. **Scalability**
   - Separate deployment targets
   - Independent scaling
   - Monitoring and observability

**Next Steps:**
1. Review and approve this proposal
2. Create new monorepo
3. Follow migration plan
4. Deploy to production

---

**Questions or Feedback?**

Please open an issue or reach out to the team.
