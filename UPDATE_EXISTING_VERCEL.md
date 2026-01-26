# 🔄 Update Existing Vercel Project

**Your Vercel Project:** https://vercel.com/zarko-meseldzijas-projects/battery_valuator

Great news! You already have a Vercel project. Let's connect it to your updated GitHub repository.

---

## 🎯 Quick Update (3 Steps)

### Step 1: Connect to GitHub Repository

1. **Go to your Vercel project:**
   https://vercel.com/zarko-meseldzijas-projects/battery_valuator/settings

2. **Click "Git" in the left sidebar**

3. **Connect Repository:**
   - Click "Connect Git Repository"
   - Select: `Teslin92/Battery-Valuator`
   - Click "Connect"

### Step 2: Update Build Settings

1. **Go to Settings → General**

2. **Update Build & Development Settings:**
   
   **Framework Preset:** Vite
   
   **Root Directory:** `./` (leave blank or set to root)
   
   **Build Command:**
   ```bash
   cd frontend && npm run build
   ```
   
   **Output Directory:**
   ```
   frontend/dist
   ```
   
   **Install Command:**
   ```bash
   cd frontend && npm install
   ```

3. **Click "Save"**

### Step 3: Set Environment Variable

1. **Go to Settings → Environment Variables**

2. **Add new variable:**
   ```
   Name:  VITE_API_URL
   Value: https://web-production-e2d0.up.railway.app
   ```

3. **Select environments:**
   - ✅ Production
   - ✅ Preview
   - ✅ Development

4. **Click "Save"**

### Step 4: Redeploy

1. **Go to Deployments tab**

2. **Click "Redeploy" on the latest deployment**
   
   OR
   
3. **Trigger new deployment:**
   - Go to main project page
   - Click "Visit" or "Redeploy"
   - Or just push to GitHub (auto-deploys)

---

## 🔧 Alternative: Use vercel.json (Already Set Up!)

Good news! Your repository already has `vercel.json` configured:

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

Once you connect the Git repository, Vercel will automatically use this configuration!

---

## 📊 What Vercel Will Do

Once connected:

1. **Detect `vercel.json`** - Auto-configure build settings
2. **Install dependencies** - Run `npm install` in `frontend/`
3. **Build** - Run `npm run build` in `frontend/`
4. **Deploy** - Serve from `frontend/dist`
5. **Auto-deploy** - Every push to `main` triggers new deployment

---

## 🎯 Expected Result

After deployment, your Vercel URL will serve:
- React frontend from `frontend/` directory
- Connected to Railway backend API
- All features working (material types, calculations, etc.)

**Your app will be live at:**
- Production: `https://battery-valuator-xxx.vercel.app`
- Or your custom domain if configured

---

## 🐛 If Build Fails

### Check Build Logs

1. Go to Deployments tab
2. Click on the failed deployment
3. View build logs

### Common Issues:

**Issue: "Cannot find module"**
- Solution: Verify `frontend/package.json` exists in repo
- Check that all dependencies are listed

**Issue: "Build command failed"**
- Solution: Test locally first:
  ```bash
  cd frontend
  npm install
  npm run build
  ```

**Issue: "Output directory not found"**
- Solution: Verify build creates `frontend/dist` directory
- Check `vite.config.ts` output settings

---

## 🔄 Manual Deployment (If Git Not Connected)

If you prefer not to connect Git, you can deploy manually:

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Link to existing project
cd "/Users/zarko/Documents/Code/Battery Valuator"
vercel link

# Select:
# - Your team
# - Existing project: battery_valuator

# Deploy
vercel --prod
```

---

## ✅ Verification Steps

After deployment:

1. **Visit your Vercel URL**
2. **Open browser DevTools (F12)**
3. **Check Console tab** - Look for errors
4. **Check Network tab** - Verify API calls to Railway
5. **Test features:**
   - Select material type
   - Enter values
   - Click Calculate
   - Verify results display

---

## 🎊 Benefits of Git Connection

Once connected to GitHub:

✅ **Automatic deployments** - Push to `main` = instant deploy  
✅ **Preview deployments** - Every PR gets preview URL  
✅ **Rollback** - Easy to revert to previous deployment  
✅ **Collaboration** - Team members can see deployments  
✅ **CI/CD** - Integrated with GitHub Actions  

---

## 📝 Quick Checklist

- [ ] Go to Vercel project settings
- [ ] Connect to `Teslin92/Battery-Valuator` repository
- [ ] Verify build settings (or let `vercel.json` handle it)
- [ ] Add `VITE_API_URL` environment variable
- [ ] Trigger redeploy
- [ ] Test deployed application
- [ ] Verify API connection works

---

## 🚀 Ready!

Your existing Vercel project is perfect! Just:

1. **Connect it to GitHub:** https://vercel.com/zarko-meseldzijas-projects/battery_valuator/settings/git
2. **Add environment variable**
3. **Redeploy**

That's it! Your updated frontend will be live in ~2 minutes.

---

**Start here:** https://vercel.com/zarko-meseldzijas-projects/battery_valuator/settings
