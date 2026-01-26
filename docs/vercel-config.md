# Vercel Configuration for Monorepo

## Current Setup (Before Monorepo)

Your frontend is deployed from the root of the `battery-value-hub` repository.

## New Setup (After Monorepo)

Your frontend will be in `apps/web/` subdirectory.

---

## Option 1: Vercel Dashboard Configuration

1. Go to your Vercel project dashboard
2. Go to **Settings** → **General**
3. Update the following:

### Build & Development Settings:
- **Framework Preset:** Vite
- **Root Directory:** `apps/web`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

### Environment Variables:
Keep all existing variables:
- `VITE_API_URL` = `https://web-production-e2d0.up.railway.app`

---

## Option 2: vercel.json File

Create `vercel.json` in the monorepo root:

```json
{
  "buildCommand": "cd apps/web && npm run build",
  "outputDirectory": "apps/web/dist",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

Then commit and push:
```bash
git add vercel.json
git commit -m "Add Vercel configuration for monorepo"
git push
```

---

## Option 3: Vercel CLI

If you have Vercel CLI installed:

```bash
cd battery-valuator-monorepo

# Login to Vercel
vercel login

# Link to your existing project
vercel link

# Deploy
vercel --prod
```

When prompted:
- **Set up and deploy?** Yes
- **Which scope?** Your account
- **Link to existing project?** Yes
- **What's your project's name?** battery-valuator (or your existing name)
- **In which directory is your code located?** `apps/web`

---

## Environment Variables

Make sure these are set in Vercel dashboard:

```bash
VITE_API_URL=https://web-production-e2d0.up.railway.app
```

Or set via CLI:
```bash
vercel env add VITE_API_URL production
# Enter: https://web-production-e2d0.up.railway.app
```

---

## Verification

After deploying, test your frontend:

1. Visit your Vercel URL
2. Check that the app loads
3. Try running a calculation
4. Verify it connects to the API

---

## Troubleshooting

### Build Fails with "Cannot find module"

**Cause:** Root directory not set correctly

**Fix:** Set root directory to `apps/web` in Vercel dashboard

### API Calls Fail

**Cause:** `VITE_API_URL` not set or incorrect

**Fix:** Check environment variables in Vercel dashboard

### 404 on Refresh

**Cause:** SPA routing not configured

**Fix:** Add rewrites in `vercel.json` (see Option 2 above)

---

## Monorepo Deployment Strategy

### Option A: Deploy from Monorepo (Recommended)

**Pros:**
- Single source of truth
- Easier to keep in sync
- Atomic changes

**Cons:**
- Slightly more complex config

**Setup:**
1. Create new Vercel project from monorepo
2. Set root directory to `apps/web`
3. Deploy

### Option B: Keep Separate Repos

**Pros:**
- No changes to deployment
- Simpler config

**Cons:**
- Need to sync changes manually
- Two repos to maintain

**Setup:**
1. Keep `battery-value-hub` repo
2. Copy changes from monorepo to separate repo
3. Push to trigger deploy

---

## Rollback Plan

If something goes wrong:

1. Go to Vercel dashboard
2. Click **Deployments**
3. Find your last working deployment
4. Click **Promote to Production**

Or revert the git commit:
```bash
git revert HEAD
git push
```

---

## Cost Impact

**No change** - Same pricing as before. Monorepo doesn't affect Vercel costs.

---

## GitHub Integration

If you're using GitHub integration:

1. Vercel will auto-deploy on push to `main`
2. Make sure branch protection rules allow this
3. Test with a staging branch first

### Staging Environment

Create a preview deployment:
```bash
git checkout -b staging
git push origin staging
```

Vercel will automatically create a preview URL.

---

## Performance Considerations

Monorepo doesn't affect build performance significantly:
- Build time: ~same as before
- Bundle size: ~same as before
- Deploy time: ~same as before

---

## Next Steps

After successful deployment:

1. ✅ Test all features work
2. ✅ Update DNS if needed
3. ✅ Monitor for errors
4. ✅ Update documentation with new URLs
