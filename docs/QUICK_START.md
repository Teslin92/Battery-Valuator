# Battery Valuator - Quick Start Guide

**Ready to migrate? Here's what you need to do:**

---

## 🚀 Option 1: Automated Setup (Recommended)

Run the automated setup script:

```bash
cd "/Users/zarko/Documents/Code/Battery Valuator"
./setup-monorepo.sh
```

This will:
- ✅ Create the monorepo structure
- ✅ Copy all backend files
- ✅ Copy all frontend files (if available)
- ✅ Setup dependencies
- ✅ Create git repository
- ✅ Commit everything

**Time:** ~5-10 minutes

---

## 📋 Option 2: Manual Setup

Follow the step-by-step guide in `MIGRATION_GUIDE.md`

**Time:** ~30-60 minutes

---

## 🎯 What You'll Need

### Before Starting:
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] GitHub account (for pushing code)

### Optional (for deployment):
- [ ] Railway account + CLI
- [ ] Vercel account + CLI

---

## 📦 After Setup

Once the monorepo is created, you'll have:

```
battery-valuator-monorepo/
├── apps/
│   ├── api/          # Your Python backend ✅
│   ├── web/          # Your React frontend ✅
│   └── streamlit/    # Your Streamlit UI ✅
├── packages/
│   ├── contracts/    # (Phase 2) OpenAPI spec
│   └── constants/    # (Phase 2) Shared constants
└── docs/             # All documentation ✅
```

---

## 🧪 Testing Your Setup

### Test API:
```bash
cd battery-valuator-monorepo
npm run dev:api
```
Then visit: http://localhost:5000/api/health

### Test Web:
```bash
cd battery-valuator-monorepo
npm run dev:web
```
Then visit: http://localhost:3000

---

## 🚢 Deployment

### Current Setup (No Changes Needed):
- **API:** Still deploys to Railway (same as before)
- **Web:** Still deploys to Vercel (same as before)

### What Changes:
- Both apps now live in one repo
- You can deploy them together or separately
- Railway and Vercel configs will need minor updates

---

## 📚 Documentation

All your documentation is preserved:

- **ARCHITECTURE_REVIEW.md** - Complete technical analysis
- **MONOREPO_PROPOSAL.md** - Full implementation plan
- **MIGRATION_GUIDE.md** - Step-by-step instructions
- **QUICK_START.md** - This file!

---

## 🆘 Need Help?

### API won't start?
```bash
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Web won't start?
```bash
cd apps/web
npm install
npm run dev
```

### Want to undo?
The script doesn't modify your original files. Just delete the `battery-valuator-monorepo` directory.

---

## 🎉 Next Steps After Phase 1

1. **Test everything works**
2. **Push to GitHub**
3. **Proceed to Phase 2:** Shared Contracts
   - Create OpenAPI specification
   - Generate TypeScript types
   - Add runtime validation

---

## 💡 Pro Tips

1. **Keep both repos for now** - Don't delete the old repos until you're confident
2. **Test thoroughly** - Make sure calculations match exactly
3. **Deploy to staging first** - Test in production-like environment
4. **Update deployment configs** - Railway and Vercel need to know about monorepo structure

---

## 📞 Questions?

- Check the detailed docs in `/docs`
- Review the architecture analysis
- Open an issue on GitHub

---

**Ready? Run the setup script and let's go! 🚀**

```bash
./setup-monorepo.sh
```
