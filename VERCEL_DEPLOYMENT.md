# 🚀 Vercel Deployment Guide

## ✅ Prerequisites Complete

- ✅ Frontend code committed and pushed to GitHub
- ✅ Repository: https://github.com/Teslin92/Battery-Valuator
- ✅ `vercel.json` configuration in place
- ✅ Frontend running locally at http://localhost:8080

## 🎯 Deploy to Vercel (5 minutes)

### Option 1: Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/new
   - Sign in with your GitHub account

2. **Import Repository**
   - Click "Add New Project"
   - Select "Import Git Repository"
   - Choose: `Teslin92/Battery-Valuator`
   - Click "Import"

3. **Configure Project**
   
   Vercel should auto-detect the configuration from `vercel.json`, but verify:
   
   - **Framework Preset:** Vite
   - **Root Directory:** `./` (leave as default)
   - **Build Command:** `cd frontend && npm run build`
   - **Output Directory:** `frontend/dist`
   - **Install Command:** `cd frontend && npm install`

4. **Add Environment Variable**
   
   Click "Environment Variables" and add:
   
   ```
   Name:  VITE_API_URL
   Value: https://web-production-e2d0.up.railway.app
   ```
   
   Select: ✅ Production, ✅ Preview, ✅ Development

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for build to complete
   - You'll get a URL like: `https://battery-valuator-xxx.vercel.app`

### Option 2: Vercel CLI (Alternative)

If you prefer CLI deployment:

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from repository root
cd "/Users/zarko/Documents/Code/Battery Valuator"
vercel --prod
```

The CLI will:
1. Detect `vercel.json` configuration
2. Ask you to link to a project (create new or use existing)
3. Deploy automatically

## 🔧 Vercel Configuration (Already Set Up)

Your `vercel.json` is configured:

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

This tells Vercel:
- Build the frontend from the `frontend/` directory
- Use Vite as the framework
- Handle client-side routing (SPA mode)

## 🌐 After Deployment

### Test Your Deployment

1. **Visit your Vercel URL**
   - Example: `https://battery-valuator-xxx.vercel.app`

2. **Test API Connection**
   - Select a material type
   - Enter some values
   - Click "Calculate"
   - Verify it connects to Railway backend

3. **Check Console**
   - Open browser DevTools (F12)
   - Look for API calls to: `https://web-production-e2d0.up.railway.app`
   - Verify no CORS errors

### Configure Custom Domain (Optional)

In Vercel Dashboard:
1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

## 🔄 Automatic Deployments

Vercel will automatically deploy:
- **Production:** Every push to `main` branch
- **Preview:** Every pull request

No manual deployment needed after initial setup!

## 🐛 Troubleshooting

### Build Fails

**Check build logs in Vercel dashboard:**
- Look for missing dependencies
- Verify `vercel.json` paths are correct
- Ensure `frontend/package.json` exists

**Common fixes:**
```bash
# Locally test the build
cd frontend
npm run build
```

### API Connection Issues

**Verify environment variable:**
1. Go to Vercel Dashboard → Settings → Environment Variables
2. Check `VITE_API_URL` is set correctly
3. Redeploy if you change it

**Check CORS:**
- Your Railway API should allow requests from Vercel domain
- Check Railway logs for CORS errors

### 404 Errors on Refresh

This should be handled by the `rewrites` in `vercel.json`. If you still see 404s:
1. Verify `vercel.json` is in repository root
2. Check Vercel dashboard → Settings → General → Build & Development Settings
3. Ensure "Output Directory" is `frontend/dist`

## 📊 Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Vercel (Frontend)               │
│  https://battery-valuator.vercel.app    │
│                                         │
│  - React 18 + TypeScript                │
│  - Vite Build                           │
│  - Static Assets                        │
│  - Client-side Routing                  │
└─────────────┬───────────────────────────┘
              │
              │ API Calls
              │ (HTTPS)
              ▼
┌─────────────────────────────────────────┐
│        Railway (Backend)                │
│  https://web-production-e2d0...         │
│                                         │
│  - Python Flask API                     │
│  - Calculation Engine                   │
│  - Market Data Fetching                 │
│  - COA Parsing                          │
└─────────────────────────────────────────┘
```

## ✅ Checklist

Before deploying:
- [x] Frontend code committed to GitHub
- [x] `vercel.json` in repository root
- [x] `frontend/package.json` exists
- [x] Frontend builds locally (`npm run build`)
- [x] Backend API is running on Railway

During deployment:
- [ ] Import repository to Vercel
- [ ] Set `VITE_API_URL` environment variable
- [ ] Deploy and wait for build
- [ ] Test the deployed application

After deployment:
- [ ] Verify API connection works
- [ ] Test all features (material types, calculations)
- [ ] Check browser console for errors
- [ ] Share the URL!

## 🎉 Next Steps

Once deployed:
1. **Test thoroughly** - Try all material types and calculations
2. **Monitor** - Check Vercel Analytics for usage
3. **Iterate** - Push changes to `main` for automatic deployment
4. **Share** - Your app is live!

## 📞 Need Help?

- **Vercel Docs:** https://vercel.com/docs
- **Vercel Support:** https://vercel.com/support
- **Your Backend API:** https://web-production-e2d0.up.railway.app/api/health

---

**Ready to deploy!** 🚀

Just go to https://vercel.com/new and import your repository!
