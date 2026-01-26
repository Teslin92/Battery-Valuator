# Battery Valuator - Migration Checklist

Use this checklist to track your progress through the migration.

---

## ✅ Pre-Migration Checklist

- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.11+ installed (`python --version`)
- [ ] Git installed (`git --version`)
- [ ] GitHub account ready
- [ ] Railway account access (for API deployment)
- [ ] Vercel account access (for Web deployment)
- [ ] Backup of current code (just in case)

---

## 📦 Phase 1: Setup Monorepo

### Step 1: Run Setup Script
- [ ] Navigate to Battery Valuator directory
- [ ] Run `./setup-monorepo.sh`
- [ ] Script completes without errors
- [ ] New directory `battery-valuator-monorepo` created

### Step 2: Verify Structure
- [ ] `apps/api/` exists with backend code
- [ ] `apps/web/` exists with frontend code
- [ ] `apps/streamlit/` exists with Streamlit app
- [ ] `packages/` directory created
- [ ] `docs/` directory has all documentation
- [ ] Root `package.json` exists
- [ ] `turbo.json` exists

### Step 3: Test API Locally
- [ ] `cd battery-valuator-monorepo`
- [ ] `npm run dev:api` starts without errors
- [ ] Visit `http://localhost:5000/api/health`
- [ ] Health check returns JSON response
- [ ] API responds to test requests

### Step 4: Test Web Locally
- [ ] Open new terminal
- [ ] `npm run dev:web` starts without errors
- [ ] Visit `http://localhost:3000`
- [ ] Web app loads successfully
- [ ] Can select material type
- [ ] Can enter values
- [ ] Can run calculation (connects to API)

### Step 5: Commit and Push
- [ ] All files committed to git
- [ ] Created GitHub repository
- [ ] Added remote: `git remote add origin ...`
- [ ] Pushed to GitHub: `git push -u origin main`
- [ ] Verified files on GitHub

---

## 🚢 Phase 2: Deploy to Production

### Step 1: Deploy API to Railway
- [ ] Opened Railway dashboard
- [ ] Found existing API service
- [ ] Updated root directory to `apps/api`
- [ ] Updated build command
- [ ] Updated start command: `gunicorn src.main:app --bind 0.0.0.0:$PORT`
- [ ] Verified environment variables (METALS_DEV_API_KEY)
- [ ] Triggered deployment
- [ ] Deployment succeeded
- [ ] Tested health endpoint: `https://your-app.railway.app/api/health`
- [ ] API returns healthy status

### Step 2: Deploy Web to Vercel
- [ ] Opened Vercel dashboard
- [ ] Found existing Web project
- [ ] Updated root directory to `apps/web`
- [ ] Updated build command
- [ ] Verified environment variables (VITE_API_URL)
- [ ] Triggered deployment
- [ ] Deployment succeeded
- [ ] Tested web app loads
- [ ] Tested calculation works end-to-end

### Step 3: Production Verification
- [ ] Web app loads at production URL
- [ ] Can fetch market data
- [ ] Can parse COA text
- [ ] Can run calculation
- [ ] Results match expected values
- [ ] No console errors
- [ ] No API errors

---

## 🧪 Phase 3: Testing & Validation

### Functional Testing
- [ ] Test all material types (Black Mass, Cathode Foils, etc.)
- [ ] Test all product combinations (Sulphates, MHP, LCE, LiOH)
- [ ] Test all currencies (USD, CAD, EUR, CNY)
- [ ] Test COA parsing with different formats
- [ ] Test validation warnings
- [ ] Test error handling

### Regression Testing
- [ ] Compare results with old app (same inputs)
- [ ] Verify Black Mass has $0 pre-treatment cost
- [ ] Verify other materials have correct shredding cost
- [ ] Verify all calculations match exactly
- [ ] Verify market data fetching works
- [ ] Verify FX rate conversion works

### Performance Testing
- [ ] API response time < 500ms
- [ ] Web page load time < 2s
- [ ] No memory leaks
- [ ] No console warnings

---

## 📚 Phase 4: Documentation & Cleanup

### Update Documentation
- [ ] Update README with new repo structure
- [ ] Update API documentation
- [ ] Update deployment guide
- [ ] Add troubleshooting section
- [ ] Document environment variables

### Cleanup
- [ ] Remove old deployment configs (if any)
- [ ] Archive old repositories (don't delete yet)
- [ ] Update bookmarks/links
- [ ] Notify team members (if any)

---

## 🎯 Future Phases (Optional)

### Phase 5: Shared Contracts
- [ ] Create OpenAPI specification
- [ ] Generate TypeScript types
- [ ] Add runtime validation with Zod
- [ ] Update frontend to use generated types
- [ ] Add contract validation to CI

### Phase 6: Integration Tests
- [ ] Setup Playwright
- [ ] Write E2E tests for all material types
- [ ] Write tests for error cases
- [ ] Add tests to CI pipeline
- [ ] Setup test coverage reporting

### Phase 7: CI/CD
- [ ] Setup GitHub Actions
- [ ] Add automated testing
- [ ] Add automated deployment
- [ ] Add code quality checks
- [ ] Add security scanning

---

## 🐛 Known Issues to Watch For

- [ ] Pre-treatment cost bug (should be fixed in frontend)
- [ ] Import errors in Python (check module paths)
- [ ] CORS errors (verify API allows frontend origin)
- [ ] Environment variables not set
- [ ] Port conflicts (5000, 3000)

---

## 📊 Success Metrics

### Technical
- [ ] Build time < 5 minutes
- [ ] API response time < 500ms
- [ ] Web load time < 2s
- [ ] Zero runtime type errors
- [ ] 99.9% uptime

### Business
- [ ] Calculation accuracy 100%
- [ ] All features working
- [ ] No user-reported bugs
- [ ] Faster development velocity

---

## 🎉 Completion

### Phase 1 Complete When:
- [x] Monorepo created
- [x] Both apps run locally
- [x] Code pushed to GitHub

### Phase 2 Complete When:
- [ ] API deployed to Railway
- [ ] Web deployed to Vercel
- [ ] Both working in production

### Migration Complete When:
- [ ] All tests passing
- [ ] All features working
- [ ] Documentation updated
- [ ] Team trained (if applicable)
- [ ] Old repos archived

---

## 📝 Notes

Use this space to track issues, decisions, or questions:

```
Date: _____________
Issue: _____________
Resolution: _____________

Date: _____________
Issue: _____________
Resolution: _____________
```

---

## 🎯 Current Status

**Phase:** ___________  
**Progress:** _____ %  
**Blockers:** _____________  
**Next Step:** _____________  

---

**Last Updated:** _____________  
**Updated By:** _____________
