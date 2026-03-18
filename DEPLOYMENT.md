# Deployment Guide

## Prerequisites
- GitHub account
- Vercel account (free tier works)

## Step-by-Step Deployment

### 1. Initialize Git Repository
```bash
cd regime-app
git init
git add .
git commit -m "Initial commit - Market Regime Detection App"
```

### 2. Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository (e.g., "market-regime-app")
3. Don't initialize with README (we already have files)
4. Copy the repository URL

### 3. Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/market-regime-app.git
git branch -M main
git push -u origin main
```

### 4. Deploy to Vercel

#### Option A: Vercel CLI (Recommended)
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Link to existing project? N
# - Project name: market-regime-app
# - Directory: ./ (current directory)
# - Deploy? Y
```

#### Option B: Vercel Dashboard
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure:
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
4. Click "Deploy"

### 5. Environment Variables (Optional)
If you need to configure CORS or API URLs:

In Vercel Dashboard → Settings → Environment Variables:
- `VITE_API_URL`: Your API URL (defaults to `/api`)

### 6. Custom Domain (Optional)
In Vercel Dashboard → Settings → Domains:
- Add your custom domain
- Follow DNS configuration instructions

## Local Development

### Backend
```bash
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
npm install
npm run dev
```

Visit http://localhost:3000

## Troubleshooting

### Backend Issues
- Check Python version (3.9+)
- Verify all dependencies in requirements.txt
- Check Vercel function logs

### Frontend Issues
- Clear node_modules and reinstall
- Check browser console for errors
- Verify API_URL in App.jsx

### CORS Issues
If you see CORS errors:
1. Update `allow_origins` in `api/main.py`
2. Add your Vercel domain
3. Redeploy

### Data Fetching Issues
- Yahoo Finance API may rate limit
- Consider caching strategies
- Check network tab for failed requests

## Production Optimizations

### Backend
- Add caching for price data
- Implement rate limiting
- Add error logging (Sentry)

### Frontend
- Enable production build optimizations
- Add loading skeletons
- Implement error boundaries

## Monitoring

### Vercel Analytics
Enable in Vercel Dashboard → Analytics

### Error Tracking
Consider adding:
- Sentry for error tracking
- LogRocket for session replay

## Updates

To update the deployed app:
```bash
git add .
git commit -m "Update: description of changes"
git push
```

Vercel will automatically redeploy on push to main branch.

## Cost Considerations

### Vercel Free Tier Limits
- 100 GB bandwidth/month
- 100 serverless function executions/day
- 10 second max function duration

### Yahoo Finance API
- Free tier: adequate for personal use
- Rate limits: ~2000 requests/hour
- Consider caching to reduce API calls

## Support

For issues:
1. Check Vercel deployment logs
2. Review GitHub Actions (if configured)
3. Check browser console
4. Verify API endpoints in Network tab
