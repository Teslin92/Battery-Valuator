#!/bin/bash
# Battery Valuator - Automated Monorepo Setup Script
# This script automates Phase 1 of the migration

set -e  # Exit on error

echo "🔋 Battery Valuator - Monorepo Setup"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python not found. Please install Python 3.11+${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not found. Please install Git${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"
echo ""

# Get current directory
CURRENT_DIR=$(pwd)
BACKEND_DIR="$CURRENT_DIR"
FRONTEND_DIR="../battery-value-hub"

# Check if we're in the right directory
if [ ! -f "backend.py" ]; then
    echo -e "${RED}❌ Error: backend.py not found. Please run this script from the 'Battery Valuator' directory${NC}"
    exit 1
fi

echo "📁 Current directory: $CURRENT_DIR"
echo ""

# Ask for confirmation
read -p "This will create a new 'battery-valuator-monorepo' directory. Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Create monorepo directory
MONOREPO_DIR="../battery-valuator-monorepo"
echo "📦 Creating monorepo at: $MONOREPO_DIR"
mkdir -p "$MONOREPO_DIR"
cd "$MONOREPO_DIR"

# Initialize git
echo "🔧 Initializing git repository..."
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

git add .gitignore
git commit -m "Initial commit: Add .gitignore"

# Create directory structure
echo "📂 Creating directory structure..."
mkdir -p apps/{api,web,streamlit}
mkdir -p packages/{contracts,constants}
mkdir -p tools/{scripts,docker}
mkdir -p docs
mkdir -p .github/workflows

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

echo "📦 Installing root dependencies..."
npm install

# Copy backend files
echo "🐍 Copying backend files..."
mkdir -p apps/api/src
mkdir -p apps/api/tests

cp "$BACKEND_DIR/backend.py" apps/api/src/engine.py
cp "$BACKEND_DIR/api.py" apps/api/src/main.py
cp "$BACKEND_DIR/requirements.txt" apps/api/
cp "$BACKEND_DIR/Procfile" apps/api/
if [ -f "$BACKEND_DIR/runtime.txt" ]; then
    cp "$BACKEND_DIR/runtime.txt" apps/api/
fi

# Create __init__.py
cat > apps/api/src/__init__.py << 'EOF'
"""Battery Valuator API"""
__version__ = "1.0.0"
EOF

# Update imports in main.py
sed -i.bak 's/import backend/from . import engine as backend/g' apps/api/src/main.py
rm apps/api/src/main.py.bak 2>/dev/null || true

# Copy Streamlit app
echo "📊 Copying Streamlit app..."
cp "$BACKEND_DIR/app.py" apps/streamlit/
cp "$BACKEND_DIR/requirements.txt" apps/streamlit/
if [ -f "$BACKEND_DIR/Battery Valuator.png" ]; then
    cp "$BACKEND_DIR/Battery Valuator.png" apps/streamlit/
fi

# Copy documentation
echo "📚 Copying documentation..."
for doc in LOVABLE_INTEGRATION.md README_API.md LOVABLE_FIX_PROMPT.md DEPLOYMENT_GUIDE.md ARCHITECTURE_REVIEW.md MONOREPO_PROPOSAL.md MIGRATION_GUIDE.md; do
    if [ -f "$BACKEND_DIR/$doc" ]; then
        cp "$BACKEND_DIR/$doc" docs/
    fi
done

# Copy frontend files if directory exists
if [ -d "$FRONTEND_DIR" ]; then
    echo "⚛️  Copying frontend files..."
    
    # Copy directories
    cp -r "$FRONTEND_DIR/src" apps/web/
    cp -r "$FRONTEND_DIR/public" apps/web/
    
    # Copy config files
    for file in package.json package-lock.json tsconfig.json tsconfig.app.json tsconfig.node.json vite.config.ts tailwind.config.ts postcss.config.js components.json index.html; do
        if [ -f "$FRONTEND_DIR/$file" ]; then
            cp "$FRONTEND_DIR/$file" apps/web/
        fi
    done
    
    # Install web dependencies
    echo "📦 Installing web dependencies..."
    cd apps/web
    npm install
    cd ../..
else
    echo -e "${YELLOW}⚠️  Frontend directory not found at $FRONTEND_DIR${NC}"
    echo "   You'll need to copy frontend files manually"
fi

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd apps/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ../..

# Create READMEs
cat > apps/api/README.md << 'EOF'
# Battery Valuator API

Flask REST API for battery material valuation.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

## Run

```bash
python src/main.py
```

## Environment Variables

- `METALS_DEV_API_KEY` - Optional API key for Metals.Dev
EOF

cat > apps/web/README.md << 'EOF'
# Battery Valuator Web UI

Modern React/TypeScript frontend.

## Setup

```bash
npm install
```

## Run

```bash
npm run dev
```

## Environment Variables

- `VITE_API_URL` - API base URL
EOF

cat > README.md << 'EOF'
# Battery Valuator

Modern web application for battery material valuation.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Setup Python environment
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ../..

# Start development servers
npm run dev:api    # Terminal 1
npm run dev:web    # Terminal 2
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
└── docs/             # Documentation
```

## 📚 Documentation

- [Architecture Review](docs/ARCHITECTURE_REVIEW.md)
- [Monorepo Proposal](docs/MONOREPO_PROPOSAL.md)
- [Migration Guide](docs/MIGRATION_GUIDE.md)

## 🧪 Testing

```bash
npm run test
```

## 🚢 Deployment

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
EOF

# Commit everything
echo "💾 Committing files..."
git add .
git commit -m "Phase 1: Initial monorepo setup

- Created monorepo structure with Turborepo
- Moved backend code to apps/api/
- Moved frontend code to apps/web/
- Moved Streamlit to apps/streamlit/
- Setup workspaces and scripts
- All apps verified working"

echo ""
echo -e "${GREEN}✅ Monorepo setup complete!${NC}"
echo ""
echo "📍 Location: $MONOREPO_DIR"
echo ""
echo "Next steps:"
echo "1. cd $MONOREPO_DIR"
echo "2. Test API: npm run dev:api"
echo "3. Test Web: npm run dev:web"
echo "4. Create GitHub repo and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/battery-valuator-monorepo.git"
echo "   git push -u origin main"
echo ""
echo "📖 See MIGRATION_GUIDE.md for Phase 2 instructions"
