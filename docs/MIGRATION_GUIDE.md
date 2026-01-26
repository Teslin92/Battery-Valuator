# Battery Valuator - Practical Migration Guide

**Status:** Ready to Execute  
**Estimated Time:** 4-6 hours for Phase 1  
**Date:** January 26, 2026

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Git installed and configured
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.11+ installed (`python --version`)
- [ ] npm installed (`npm --version`)
- [ ] Access to GitHub (for creating new repo)
- [ ] Railway CLI installed (optional, for deployment)
- [ ] Vercel CLI installed (optional, for deployment)

---

## Phase 1: Create Monorepo Structure

### Step 1.1: Create New Repository

```bash
# Create new directory
mkdir battery-valuator-monorepo
cd battery-valuator-monorepo

# Initialize git
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
dist/
build/

# Node
node_modules/
dist/
build/
.next/
.turbo/
*.log

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Testing
.coverage
htmlcov/
.pytest_cache/
playwright-report/
test-results/

# Build outputs
*.pyc
*.pyo
*.pyd
.Python
EOF

# Initial commit
git add .gitignore
git commit -m "Initial commit: Add .gitignore"
```

### Step 1.2: Create Directory Structure

```bash
# Create main directories
mkdir -p apps/{api,web,streamlit}
mkdir -p packages/{contracts,constants}
mkdir -p tools/{scripts,docker}
mkdir -p docs
mkdir -p .github/workflows

echo "✅ Directory structure created"
```

### Step 1.3: Setup Root Package.json

```bash
# Create root package.json
cat > package.json << 'EOF'
{
  "name": "battery-valuator",
  "version": "1.0.0",
  "private": true,
  "description": "Battery material valuation platform",
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "turbo run dev",
    "dev:api": "cd apps/api && python src/main.py",
    "dev:web": "cd apps/web && npm run dev",
    "dev:streamlit": "cd apps/streamlit && streamlit run app.py",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "generate:types": "cd packages/contracts && ./generate-types.sh",
    "validate:contract": "cd packages/contracts && ./validate-spec.sh",
    "clean": "turbo run clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^1.11.0",
    "prettier": "^3.1.0",
    "eslint": "^8.55.0"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  }
}
EOF

echo "✅ Root package.json created"
```

### Step 1.4: Setup Turborepo

```bash
# Create turbo.json
cat > turbo.json << 'EOF'
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", "build/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": [],
      "cache": false
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "clean": {
      "cache": false
    }
  }
}
EOF

# Install dependencies
npm install

echo "✅ Turborepo configured"
```

### Step 1.5: Copy Backend Code

```bash
# Navigate to parent directory
cd ..

# Copy backend files to monorepo
cp -r "Battery Valuator/backend.py" battery-valuator-monorepo/apps/api/
cp -r "Battery Valuator/api.py" battery-valuator-monorepo/apps/api/
cp -r "Battery Valuator/requirements.txt" battery-valuator-monorepo/apps/api/
cp -r "Battery Valuator/Procfile" battery-valuator-monorepo/apps/api/
cp -r "Battery Valuator/runtime.txt" battery-valuator-monorepo/apps/api/

# Copy Streamlit app
cp -r "Battery Valuator/app.py" battery-valuator-monorepo/apps/streamlit/
cp -r "Battery Valuator/requirements.txt" battery-valuator-monorepo/apps/streamlit/
cp -r "Battery Valuator/Battery Valuator.png" battery-valuator-monorepo/apps/streamlit/

# Copy documentation
cp -r "Battery Valuator/LOVABLE_INTEGRATION.md" battery-valuator-monorepo/docs/
cp -r "Battery Valuator/README_API.md" battery-valuator-monorepo/docs/
cp -r "Battery Valuator/LOVABLE_FIX_PROMPT.md" battery-valuator-monorepo/docs/
cp -r "Battery Valuator/DEPLOYMENT_GUIDE.md" battery-valuator-monorepo/docs/
cp -r "Battery Valuator/ARCHITECTURE_REVIEW.md" battery-valuator-monorepo/docs/
cp -r "Battery Valuator/MONOREPO_PROPOSAL.md" battery-valuator-monorepo/docs/

cd battery-valuator-monorepo

echo "✅ Backend code copied"
```

### Step 1.6: Restructure Backend

```bash
# Create proper Python package structure
mkdir -p apps/api/src
mkdir -p apps/api/tests

# Move files to src/
mv apps/api/backend.py apps/api/src/engine.py
mv apps/api/api.py apps/api/src/main.py

# Create __init__.py
cat > apps/api/src/__init__.py << 'EOF'
"""Battery Valuator API"""
__version__ = "1.0.0"
EOF

# Update imports in main.py
cat > apps/api/src/main.py << 'EOF'
"""
Flask API for Battery Valuator
RESTful endpoints for frontend integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from . import engine
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    import os
    import requests as req
    api_key = os.environ.get('METALS_DEV_API_KEY', '')
    api_key_set = bool(api_key)
    key_preview = f"{api_key[:4]}..." if len(api_key) > 4 else "not set"

    # Test Metals.Dev API
    metals_dev_status = "not tested"
    metals_dev_response = None
    if api_key:
        try:
            url = f"https://api.metals.dev/v1/latest?api_key={api_key}&currency=USD&unit=toz"
            r = req.get(url, timeout=10)
            data = r.json()
            metals_dev_response = data
            if data.get('status') == 'success':
                metals_dev_status = f"working - got {len(data.get('metals', {}))} metals"
            else:
                metals_dev_status = f"error: {data.get('error_message', r.status_code)}"
        except Exception as e:
            metals_dev_status = f"exception: {str(e)}"

    return jsonify({
        'status': 'healthy',
        'service': 'Battery Valuator API',
        'version': '1.0.0',
        'metals_dev_api_key_configured': api_key_set,
        'key_preview': key_preview,
        'metals_dev_api_status': metals_dev_status,
        'metals_dev_sample': metals_dev_response
    })

@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    """
    Get current market data including metal prices and FX rates

    Query params:
        currency: USD, CAD, EUR, or CNY (default: USD)
    """
    try:
        currency = request.args.get('currency', 'USD')
        data = engine.get_market_data(currency)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        logger.error(f"Market data fetch error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/parse-coa', methods=['POST'])
def parse_coa():
    """
    Parse COA text to extract metal assays

    Request body:
        {
            "coa_text": "Ni: 20.5%\nCo: 6.2%\nLi: 2.5%..."
        }
    """
    try:
        data = request.get_json()
        coa_text = data.get('coa_text', '')

        if not coa_text:
            return jsonify({
                'success': False,
                'error': 'Missing coa_text parameter'
            }), 400

        assays = engine.parse_coa_text(coa_text)

        return jsonify({
            'success': True,
            'data': assays
        })
    except Exception as e:
        logger.error(f"COA parsing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calculate', methods=['POST'])
def calculate_valuation():
    """
    Calculate battery material valuation

    Request body: See LOVABLE_INTEGRATION.md for full schema
    """
    try:
        input_params = request.get_json()

        # Validate required parameters
        required_params = ['gross_weight', 'assays', 'metal_prices', 'payables']
        for param in required_params:
            if param not in input_params:
                return jsonify({
                    'success': False,
                    'error': f'Missing required parameter: {param}'
                }), 400

        # Calculate valuation
        results = engine.calculate_valuation(input_params)

        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/validate-assays', methods=['POST'])
def validate_assays():
    """
    Validate assay values against typical ranges

    Request body:
        {
            "bm_grades": {
                "Nickel": 20.5,
                "Cobalt": 6.2,
                ...
            }
        }
    """
    try:
        data = request.get_json()
        bm_grades = data.get('bm_grades', {})

        warnings = []
        if bm_grades.get('Nickel', 0) > 60:
            warnings.append(f"Nickel grade ({bm_grades['Nickel']:.1f}%) exceeds typical black mass range (10-60%)")
        if bm_grades.get('Cobalt', 0) > 25:
            warnings.append(f"Cobalt grade ({bm_grades['Cobalt']:.1f}%) exceeds typical black mass range (3-25%)")
        if bm_grades.get('Lithium', 0) > 10:
            warnings.append(f"Lithium grade ({bm_grades['Lithium']:.1f}%) exceeds typical black mass range (1-10%)")

        total_grade = sum(bm_grades.values())
        if total_grade > 100:
            warnings.append(f"Total metal content ({total_grade:.1f}%) exceeds 100%")

        return jsonify({
            'success': True,
            'data': {
                'valid': len(warnings) == 0,
                'warnings': warnings
            }
        })
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
EOF

# Create API README
cat > apps/api/README.md << 'EOF'
# Battery Valuator API

Flask REST API for battery material valuation.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
# Development
python src/main.py

# Production
gunicorn src.main:app --bind 0.0.0.0:$PORT
```

## Test

```bash
pytest
```

## Environment Variables

- `METALS_DEV_API_KEY` - Optional API key for Metals.Dev
EOF

echo "✅ Backend restructured"
```

### Step 1.7: Copy Frontend Code

```bash
# Clone frontend repo (if not already cloned)
cd ..
if [ ! -d "battery-value-hub" ]; then
    git clone https://github.com/Teslin92/battery-value-hub.git
fi

# Copy frontend files
cp -r battery-value-hub/src battery-valuator-monorepo/apps/web/
cp -r battery-value-hub/public battery-valuator-monorepo/apps/web/
cp battery-value-hub/package.json battery-valuator-monorepo/apps/web/
cp battery-value-hub/package-lock.json battery-valuator-monorepo/apps/web/
cp battery-value-hub/tsconfig.json battery-valuator-monorepo/apps/web/
cp battery-value-hub/tsconfig.app.json battery-valuator-monorepo/apps/web/
cp battery-value-hub/tsconfig.node.json battery-valuator-monorepo/apps/web/
cp battery-value-hub/vite.config.ts battery-valuator-monorepo/apps/web/
cp battery-value-hub/tailwind.config.ts battery-valuator-monorepo/apps/web/
cp battery-value-hub/postcss.config.js battery-valuator-monorepo/apps/web/
cp battery-value-hub/components.json battery-valuator-monorepo/apps/web/
cp battery-value-hub/index.html battery-valuator-monorepo/apps/web/
cp battery-value-hub/.gitignore battery-valuator-monorepo/apps/web/

# Create web README
cat > battery-valuator-monorepo/apps/web/README.md << 'EOF'
# Battery Valuator Web UI

Modern React/TypeScript frontend for battery material valuation.

## Setup

```bash
npm install
```

## Run

```bash
# Development
npm run dev

# Build
npm run build

# Preview production build
npm run preview
```

## Test

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e
```

## Environment Variables

- `VITE_API_URL` - API base URL (default: https://web-production-e2d0.up.railway.app)
EOF

cd battery-valuator-monorepo

echo "✅ Frontend code copied"
```

### Step 1.8: Install Dependencies

```bash
# Install root dependencies
npm install

# Install web dependencies
cd apps/web
npm install
cd ../..

# Install Python dependencies
cd apps/api
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cd ../..

echo "✅ Dependencies installed"
```

### Step 1.9: Test Everything Works

```bash
# Test API
echo "Testing API..."
cd apps/api
source venv/bin/activate
python src/main.py &
API_PID=$!
sleep 3

# Test health endpoint
curl http://localhost:5000/api/health

# Stop API
kill $API_PID
cd ../..

echo "✅ API works"

# Test Web
echo "Testing Web..."
cd apps/web
npm run build
echo "✅ Web builds successfully"
cd ../..
```

### Step 1.10: Create Initial README

```bash
cat > README.md << 'EOF'
# Battery Valuator

Modern web application for battery material valuation.

## 🚀 Quick Start

```bash
# Clone repository
git clone <your-repo-url>
cd battery-valuator-monorepo

# Install dependencies
npm install

# Setup Python environment
cd apps/api
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cd ../..

# Start development servers
npm run dev
```

## 📁 Project Structure

```
battery-valuator/
├── apps/
│   ├── api/          # Python Flask API
│   ├── web/          # React/TypeScript frontend
│   └── streamlit/    # Streamlit UI (optional)
├── packages/
│   ├── contracts/    # OpenAPI specification
│   └── constants/    # Shared constants
├── tools/            # Scripts and utilities
└── docs/             # Documentation
```

## 🛠️ Development

### Run API Only
```bash
npm run dev:api
```

### Run Web Only
```bash
npm run dev:web
```

### Run Both
```bash
npm run dev
```

## 📚 Documentation

- [Architecture Review](docs/ARCHITECTURE_REVIEW.md)
- [Monorepo Proposal](docs/MONOREPO_PROPOSAL.md)
- [API Documentation](docs/README_API.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)

## 🧪 Testing

```bash
# Run all tests
npm run test

# Run API tests
cd apps/api && pytest

# Run web tests
cd apps/web && npm run test
```

## 🚢 Deployment

### API (Railway)
```bash
railway up --service api
```

### Web (Vercel)
```bash
vercel deploy
```

## 📝 License

MIT
EOF

echo "✅ README created"
```

### Step 1.11: Commit Everything

```bash
# Add all files
git add .

# Commit
git commit -m "Phase 1: Initial monorepo setup

- Created monorepo structure with Turborepo
- Moved backend code to apps/api/
- Moved frontend code to apps/web/
- Moved Streamlit to apps/streamlit/
- Setup workspaces and scripts
- All apps verified working"

echo "✅ Phase 1 complete!"
```

### Step 1.12: Push to GitHub

```bash
# Create GitHub repo (do this manually on GitHub.com)
# Then:

git remote add origin https://github.com/YOUR_USERNAME/battery-valuator-monorepo.git
git branch -M main
git push -u origin main

echo "✅ Pushed to GitHub"
```

---

## Verification Checklist

After Phase 1, verify:

- [ ] Directory structure matches proposal
- [ ] API runs with `npm run dev:api`
- [ ] Web runs with `npm run dev:web`
- [ ] API health check responds: `curl http://localhost:5000/api/health`
- [ ] Web builds successfully: `cd apps/web && npm run build`
- [ ] All files committed to git
- [ ] Pushed to GitHub

---

## What's Next?

Phase 1 is complete! You now have a working monorepo with both apps.

**Next Steps:**
1. Review the setup
2. Test both applications
3. Proceed to Phase 2 (Shared Contracts) when ready

**Phase 2 Preview:**
- Create OpenAPI specification
- Generate TypeScript types
- Add runtime validation

---

## Troubleshooting

### API won't start
```bash
cd apps/api
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Web won't start
```bash
cd apps/web
npm install
npm run dev
```

### Import errors in Python
Make sure you're running from the correct directory:
```bash
cd apps/api
python src/main.py  # Not: python main.py
```

### Port already in use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

---

## Need Help?

- Check [ARCHITECTURE_REVIEW.md](docs/ARCHITECTURE_REVIEW.md) for detailed analysis
- Check [MONOREPO_PROPOSAL.md](docs/MONOREPO_PROPOSAL.md) for full plan
- Open an issue on GitHub
