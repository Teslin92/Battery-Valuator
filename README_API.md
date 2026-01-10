# Battery Valuator API

REST API for battery material valuation calculations.

## Endpoints

- `GET /api/health` - Health check
- `GET /api/market-data?currency=USD` - Get live metal prices
- `POST /api/parse-coa` - Parse COA text
- `POST /api/calculate` - Calculate valuation
- `POST /api/validate-assays` - Validate assay ranges

## Documentation

See [LOVABLE_INTEGRATION.md](LOVABLE_INTEGRATION.md) for complete API documentation.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python api.py

# Test
curl http://localhost:5000/api/health
```

## Railway Deployment

This API is configured to run on Railway via `Procfile.api`.

**Start Command:** `gunicorn api:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

## Environment Variables

No environment variables required. All configuration is in the code with sensible defaults.

## CORS

CORS is enabled for all origins to allow frontend integration.
