# Battery Valuator

Modern web application for battery material valuation with Python backend and React frontend.

## 🏗️ Structure

```
Battery Valuator/
├── backend.py              # Pure calculation engine
├── api.py                  # Flask REST API
├── app.py                  # Streamlit UI (optional)
├── frontend/               # React/TypeScript web UI
│   ├── src/
│   ├── public/
│   └── package.json
└── docs/                   # Documentation
```

## 🚀 Quick Start

### Backend (API)

```bash
# Install dependencies
pip install -r requirements.txt

# Run API
python api.py
```

API will be available at: http://localhost:5000

### Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:8080

## 📚 Documentation

- [Architecture Review](docs/ARCHITECTURE_REVIEW.md) - Complete technical analysis
- [API Documentation](docs/README_API.md) - API endpoints and usage
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Production deployment
- [Integration Guide](docs/LOVABLE_INTEGRATION.md) - Frontend-backend integration

## 🧪 Features

- **Live Market Data** - Real-time metal prices from Metals.Dev API
- **COA Text Parsing** - Extract assay values from Certificate of Analysis
- **Multi-Currency Support** - USD, CAD, EUR, CNY
- **Material Types** - Black Mass, Cathode Foils, Cell Stacks, Whole Cells, Modules, Battery Packs
- **Product Options** - Sulphates, MHP, Carbonate (LCE), Hydroxide (LiOH)
- **Validation** - Unrealistic grade warnings
- **PDF Export** - Export valuation results

## 🛠️ Technology Stack

### Backend
- Python 3.11
- Flask 3.1.0 (REST API)
- Streamlit 1.40.2 (Optional UI)
- pandas 2.2.3
- yfinance 0.2.50

### Frontend
- React 18.3
- TypeScript 5.8
- Vite 5.4
- TanStack Query 5.83
- Radix UI (shadcn/ui)
- Tailwind CSS 3.4
- Recharts 2.15

## 🚢 Deployment

### Backend (Railway)

The API is deployed to Railway from the repository root:

```bash
# Procfile.api
web: gunicorn api:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**Production URL:** https://web-production-e2d0.up.railway.app

### Frontend (Vercel)

The frontend is deployed to Vercel from the `frontend/` directory:

```bash
# vercel.json configuration included
vercel deploy
```

See [vercel-config.md](docs/vercel-config.md) for deployment instructions.

## 🔧 Environment Variables

### Backend
- `METALS_DEV_API_KEY` - Optional API key for Metals.Dev (falls back to yfinance if not set)

### Frontend
- `VITE_API_URL` - Backend API URL (default: https://web-production-e2d0.up.railway.app)

## 📖 API Endpoints

- `GET /api/health` - Health check
- `GET /api/market-data?currency=USD` - Get live metal prices
- `POST /api/parse-coa` - Parse COA text
- `POST /api/calculate` - Calculate valuation
- `POST /api/validate-assays` - Validate assay ranges

See [API Documentation](docs/README_API.md) for detailed endpoint specifications.

## 🧮 Calculation Engine

The core calculation logic handles:
- Mass balance calculations
- Stoichiometry conversions (metal to salt)
- Pre-treatment costs (shredding, electrolyte)
- Refining OPEX
- Product revenue (Sulphates, MHP, LCE, LiOH)
- Net profit and margin

## 🎯 Key Features

### Conditional Logic
- **Black Mass (Processed)** - No pre-treatment costs, 100% mechanical recovery
- **Other Materials** - Includes shredding costs and configurable recovery rates

### Market Data
- **Primary Source:** Metals.Dev API (LME prices)
- **Fallback:** yfinance (Copper, Aluminum futures)
- **Static Fallback:** Hardcoded prices if all APIs fail
- **Caching:** 15-minute cache for API responses

### Validation
- Grade range checking (Ni 10-60%, Co 3-25%, Li 1-10%)
- Total metal content validation
- Warning system for unrealistic values

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

MIT

## 🙏 Acknowledgments

- Metals.Dev for market data API
- Lovable for frontend scaffolding
- Railway for backend hosting
- Vercel for frontend hosting
