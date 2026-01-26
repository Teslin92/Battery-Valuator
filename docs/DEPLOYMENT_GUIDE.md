# Battery Valuator Deployment Architecture

## Repository Structure (Recommended)

### Backend Repository (Current)
- **Repo**: `Black Mass` (this repo)
- **Hosting**: Railway
- **URL**: https://web-production-e2d0.up.railway.app
- **Contains**:
  - `backend.py` - Calculation engine
  - `api.py` - Flask REST API
  - `app.py` - Streamlit UI (optional)

### Frontend Repository (New)
- **Repo**: `battery-valuator-frontend` (create new)
- **Hosting**: Lovable.app or Vercel
- **Contains**: React/TypeScript frontend built in Lovable

## Deployment Steps

### 1. Connect Lovable to GitHub

1. In Lovable project settings, click **"Connect to GitHub"**
2. Choose **"Create new repository"**
3. Name: `battery-valuator-frontend`
4. Lovable auto-pushes code and keeps it synced

### 2. Configure API Connection

In your Lovable project, add the API base URL:

```typescript
// In your API configuration file
const API_BASE_URL = 'https://web-production-e2d0.up.railway.app';

// Or use environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://web-production-e2d0.up.railway.app';
```

### 3. Publish Frontend

**Option A: Lovable Hosting (Easiest)**
- Click **"Publish"** in Lovable
- Get URL: `https://your-app.lovable.app`
- Auto-updates on changes

**Option B: Vercel (Custom Domain)**
1. Go to [vercel.com](https://vercel.com)
2. Import `battery-valuator-frontend` repo
3. Add environment variable: `VITE_API_URL=https://web-production-e2d0.up.railway.app`
4. Deploy
5. Optional: Add custom domain in Vercel settings

## Final Architecture

```
┌─────────────────────────────────────────┐
│  User Browser                           │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Frontend (Lovable/Vercel)              │
│  - React/TypeScript UI                  │
│  - https://your-app.lovable.app         │
│  - Repo: battery-valuator-frontend      │
└─────────────────┬───────────────────────┘
                  │
                  │ API Calls
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Backend API (Railway)                  │
│  - Flask REST API                       │
│  - https://web-production-e2d0...app    │
│  - Repo: Black Mass                     │
│  - Auto-deploys on git push             │
└─────────────────────────────────────────┘
```

## Making Changes

### Frontend Changes
1. Edit in Lovable (or locally if cloned)
2. Changes auto-sync to GitHub
3. Hosting platform auto-deploys

### Backend Changes
1. Edit locally: `backend.py`, `api.py`
2. Test: `python api.py`
3. Commit: `git add . && git commit -m "message"`
4. Push: `git push`
5. Railway auto-deploys in 1-2 minutes

## Testing Integration

```bash
# Test backend API
curl https://web-production-e2d0.up.railway.app/api/health

# Test frontend (after deployment)
# Visit your Lovable/Vercel URL
# Should fetch prices from Railway API
```

## Environment Variables

### Frontend (.env for local development)
```
VITE_API_URL=https://web-production-e2d0.up.railway.app
```

### Backend (Railway)
No environment variables needed - all configured in code

## Monitoring

- **Railway**: Check deployment logs at [railway.app](https://railway.app)
- **Lovable/Vercel**: Check deployment status in respective dashboards
- **API Health**: Monitor `/api/health` endpoint

## Rollback Strategy

### Backend
- Railway keeps deployment history
- Redeploy previous version from Railway dashboard
- Or revert git commit and push

### Frontend
- Vercel/Netlify keep deployment history
- One-click rollback in dashboard
- Or revert git commit
