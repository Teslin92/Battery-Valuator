# Railway Configuration for Monorepo

## Current Setup (Before Monorepo)

Your API is currently deployed from the root of your repository.

## New Setup (After Monorepo)

Your API will be in `apps/api/` subdirectory.

---

## Option 1: Railway Dashboard Configuration

1. Go to your Railway project dashboard
2. Click on your service
3. Go to **Settings** → **Build & Deploy**
4. Update the following:

### Build Settings:
- **Root Directory:** `apps/api`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn src.main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

### Environment Variables:
Keep all existing variables (especially `METALS_DEV_API_KEY`)

---

## Option 2: Railway CLI

If you have Railway CLI installed:

```bash
cd battery-valuator-monorepo

# Login to Railway
railway login

# Link to your existing project
railway link

# Set root directory
railway service --root apps/api

# Deploy
railway up
```

---

## Option 3: railway.toml File

Create `railway.toml` in the monorepo root:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "cd apps/api && gunicorn src.main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120"
healthcheckPath = "/api/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

Then commit and push:
```bash
git add railway.toml
git commit -m "Add Railway configuration for monorepo"
git push
```

---

## Verification

After deploying, test your API:

```bash
curl https://your-railway-app.up.railway.app/api/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "Battery Valuator API",
  "version": "1.0.0"
}
```

---

## Troubleshooting

### Import Errors

If you see import errors like `ModuleNotFoundError: No module named 'src'`:

**Fix:** Update start command to:
```bash
cd apps/api && python -m gunicorn src.main:app --bind 0.0.0.0:$PORT
```

### Port Not Binding

Make sure your start command includes `--bind 0.0.0.0:$PORT`

### Dependencies Not Installing

Check that `requirements.txt` is in `apps/api/` directory

---

## Rollback Plan

If something goes wrong:

1. Go to Railway dashboard
2. Click **Deployments**
3. Find your last working deployment
4. Click **Redeploy**

Or revert the git commit:
```bash
git revert HEAD
git push
```

---

## Cost Impact

**No change** - Same pricing as before. Monorepo doesn't affect Railway costs.
