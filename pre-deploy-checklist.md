# Pre-Deployment Checklist

Complete this checklist before deploying to ensure everything works.

## ✅ Local Testing

### 1. Backend Setup
```bash
cd api
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Verify:**
- [ ] Virtual environment created
- [ ] All packages installed without errors
- [ ] Python version is 3.9+

### 2. Backend Test
```bash
# From project root
python test-backend.py
```

**Expected Output:**
- [ ] ✅ All imports successful
- [ ] ✅ Config model works
- [ ] ✅ Data fetch works
- [ ] ✅ Signal calculation works

### 3. Start Backend
```bash
cd api
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Verify:**
- [ ] Server starts without errors
- [ ] Visit http://localhost:8000
- [ ] See: `{"message": "Market Regime Detection API"...}`
- [ ] Visit http://localhost:8000/health
- [ ] See: `{"status": "healthy"...}`

### 4. Frontend Setup
```bash
# New terminal, from project root
npm install
```

**Verify:**
- [ ] All packages installed
- [ ] No vulnerability warnings (or run `npm audit fix`)
- [ ] Node version is 18+

### 5. Start Frontend
```bash
npm run dev
```

**Verify:**
- [ ] Dev server starts
- [ ] Visit http://localhost:3000
- [ ] Page loads with "Market Regime Detection" header
- [ ] No console errors (F12)

### 6. Test Full Workflow
With both backend and frontend running:

- [ ] Click "Current Regime" button
- [ ] See current regime display (may take 10-20 seconds)
- [ ] Navigate to Configuration tab
- [ ] Change a weight value (e.g., DefCyc to 2.5)
- [ ] Navigate to Portfolio tab
- [ ] Adjust an allocation percentage
- [ ] Click "Run Backtest" button
- [ ] Wait for results (30-60 seconds)
- [ ] See equity curve chart
- [ ] See regime statistics

**If any step fails, check:**
- Browser console (F12 → Console)
- Network tab (F12 → Network)
- Backend terminal for errors

## ✅ Git & GitHub Setup

### 1. Initialize Git
```bash
git init
git add .
git commit -m "Initial commit: Market Regime Detection App"
```

**Verify:**
- [ ] `.git` folder created
- [ ] All files committed
- [ ] No errors

### 2. Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `market-regime-app` (or your choice)
3. Description: "Market Regime Detection - Live Backtesting Platform"
4. Public or Private (your choice)
5. **Don't** initialize with README
6. Click "Create repository"

**Verify:**
- [ ] Repository created
- [ ] Copy the HTTPS URL (e.g., https://github.com/YOUR_USERNAME/market-regime-app.git)

### 3. Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/market-regime-app.git
git branch -M main
git push -u origin main
```

**Verify:**
- [ ] Push completes without errors
- [ ] Visit your GitHub repository page
- [ ] See all files uploaded
- [ ] README.md displays properly

## ✅ Vercel Deployment

### Option A: Vercel CLI (Recommended)

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login
```bash
vercel login
```
- [ ] Browser opens for authentication
- [ ] Logged in successfully

### 3. Deploy
```bash
vercel
```

**Answer prompts:**
- Link to existing project? → **N**
- Project name? → **market-regime-app** (or your choice)
- In which directory? → **./** (current)
- Modify settings? → **N**

**Verify:**
- [ ] Build completes
- [ ] Deployment successful
- [ ] Vercel gives you a URL (e.g., https://market-regime-app-xxx.vercel.app)

### 4. Test Production
Visit your Vercel URL:
- [ ] Page loads
- [ ] Click "Current Regime"
- [ ] Works (may take longer on first request)
- [ ] Click "Run Backtest"
- [ ] Results appear

### Option B: Vercel Dashboard

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Find your GitHub repository
4. Click "Import"
5. **Build settings (Vercel should auto-detect):**
   - Framework Preset: **Vite**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
6. Click "Deploy"

**Verify:**
- [ ] Build logs show no errors
- [ ] Deployment succeeds
- [ ] Visit deployment URL
- [ ] Test full workflow

## ✅ Post-Deployment

### 1. Verify API Routes
Visit: `https://your-app.vercel.app/api/health`

**Expected:**
```json
{"status": "healthy", "timestamp": "..."}
```

### 2. Monitor First Requests
- First API call may take 10-20 seconds (cold start)
- Subsequent calls should be faster
- Check Vercel function logs if issues

### 3. Test in Different Browsers
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Mobile browser

### 4. Share URL
Your app is live at: `https://your-app.vercel.app`

Share with:
- [ ] Yourself (bookmark it!)
- [ ] Team members
- [ ] Portfolio managers
- [ ] Stakeholders

## 🔧 Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
cd api
pip install -r requirements.txt
```

**"Yahoo Finance rate limit" errors:**
- Wait 5-10 minutes
- Yahoo Finance free tier limits requests
- Consider caching in production

**Port 8000 already in use:**
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9
# Or use different port
uvicorn main:app --reload --port 8001
```

### Frontend Issues

**"Cannot find module" errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**CORS errors in browser:**
- Check API URL in `src/App.jsx`
- Verify backend is running on port 8000
- Check browser console for exact error

### Deployment Issues

**Build fails on Vercel:**
- Check build logs for specific error
- Verify all dependencies in package.json
- Ensure Python version compatible (3.9+)

**API routes 404 on Vercel:**
- Check `vercel.json` configuration
- Verify `api/main.py` exists
- Check Vercel function logs

**Slow API responses:**
- First request (cold start): 10-20 seconds normal
- Subsequent requests: Should be <5 seconds
- Consider Vercel Pro for faster cold starts

## 📊 Success Criteria

Your deployment is successful when:

- [✓] App loads at Vercel URL
- [✓] "Current Regime" button works
- [✓] Config can be edited
- [✓] Portfolio allocations can be changed
- [✓] "Run Backtest" returns results
- [✓] Charts display properly
- [✓] No console errors
- [✓] Works on mobile

## 🎉 You're Done!

Once all checkboxes are complete:

1. ✅ **Save your Vercel URL** - This is your live app
2. ✅ **Bookmark it** - Quick access for analysis
3. ✅ **Update Excel** - Use these optimal parameters (±7, Span 6)
4. ✅ **Monitor regimes** - Check weekly for signals
5. ✅ **Iterate** - Adjust config and test new strategies

---

**Need Help?**
- Check `DEPLOYMENT.md` for detailed instructions
- Review `QUICKSTART.md` for usage guide
- Check Vercel function logs for API errors
- Verify browser console for frontend issues
