# Market Regime Detection App

**Full-stack application for the Enhanced Momentum Regime Model v2.0**

Live backtesting platform with editable configuration, portfolio allocations, and dividend-adjusted data from Yahoo Finance.

![Version](https://img.shields.io/badge/version-1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Features

### Model Configuration
- **Editable Signal Weights**: DefCyc, ValGrw, HiDivMkt, CrdSprd
- **Adjustable Thresholds**: ±7 optimal, test ±6 to ±9
- **EWMA Span Control**: 3-10 weeks (optimal: 6)
- **Advanced Parameters**: Z-score thresholds, lookback periods
- **Quick Presets**: Optimal, Conservative, Aggressive configs

### Portfolio Backtesting
- **Regime-Specific Allocations**: Risk-On, Neutral, Defensive
- **9 Sector ETFs**: XLF, XLI, XLB, XLK, XLY, XLC, XLU, XLP, XLV
- **Visual Allocation Editor**: Percentage-based with validation
- **Preset Strategies**: Default cyclical tilt, equal weight

### Live Data & Results
- **Current Regime**: Real-time market regime detection
- **Signal Breakdown**: Individual signal contributions
- **Equity Curve**: Visual performance over time
- **Regime Statistics**: Returns, win rates by regime
- **Dividend-Adjusted Data**: Accurate total return calculations

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Git

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/market-regime-app.git
cd market-regime-app
```

2. **Start the backend**
```bash
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

3. **Start the frontend** (new terminal)
```bash
npm install
npm run dev
```

4. **Open browser**
```
http://localhost:3000
```

## 📦 Deployment to Vercel

### One-Command Deploy
```bash
npm install -g vercel
vercel
```

### GitHub → Vercel (Recommended)

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/market-regime-app.git
git push -u origin main
```

2. **Connect to Vercel**
- Go to [vercel.com/new](https://vercel.com/new)
- Import your GitHub repository
- Vercel auto-detects Vite + Python
- Click "Deploy"

3. **Done!** Your app is live at `https://your-app.vercel.app`

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

## 🏗️ Tech Stack

### Frontend
- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **TailwindCSS**: Utility-first styling
- **Recharts**: Data visualization
- **Lucide React**: Icon library

### Backend
- **FastAPI**: Modern Python API framework
- **yfinance**: Yahoo Finance data (dividend-adjusted)
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations

### Deployment
- **Vercel**: Frontend hosting + serverless functions
- **GitHub**: Version control and CI/CD

## 📊 Model Details

### Enhanced Momentum Regime Model v2.0

**Optimal Configuration:**
- Threshold: ±7
- EWMA Span: 6 weeks
- No hysteresis (symmetric entry/exit)

**Signals (5):**
1. **DefCyc** (weight: 2.0): Defensive vs Cyclical sectors
2. **ValGrw** (weight: 2.0): Value (RPV) vs Growth (RPG)
3. **HiDivMkt** (weight: 3.0): High Dividend (VYM) vs Market (SPY)
4. **CrdSprd** (weight: 2.0): Credit Spread (VSCH vs HYG)
5. **LoBHiB** (weight: 0.0): Disabled (redundant with DefCyc)

**Cyclical Basket:**
- XLF (Financials)
- XLI (Industrials)
- XLB (Materials)

**Performance (Backtest 2016-2026):**
- Spread: 12.19% (26-week forward)
- Annualized: ~24% gross alpha
- Changes: ~1.4 per year
- Sample: 4 Risk-On, 4 Defensive periods

## 📁 Project Structure

```
market-regime-app/
├── api/                      # FastAPI backend
│   ├── main.py              # API endpoints & calculations
│   └── requirements.txt     # Python dependencies
├── src/                     # React frontend
│   ├── components/          # UI components
│   │   ├── ConfigEditor.jsx
│   │   ├── PortfolioEditor.jsx
│   │   ├── BacktestResults.jsx
│   │   └── CurrentRegime.jsx
│   ├── App.jsx              # Main app component
│   ├── main.jsx             # React entry point
│   └── index.css            # Tailwind styles
├── index.html               # HTML template
├── vite.config.js           # Vite configuration
├── vercel.json              # Vercel deployment config
├── package.json             # Node dependencies
└── README.md                # This file
```

## 🔧 API Endpoints

### `POST /api/backtest`
Run full backtest with custom config

**Request:**
```json
{
  "config": {
    "weight_defcyc": 2.0,
    "threshold_defensive": 7.0,
    "ewma_span": 6,
    ...
  },
  "portfolio": {
    "risk_on": { "XLF": 0.20, ... },
    "neutral": { ... },
    "defensive": { ... }
  },
  "start_date": "2016-01-01",
  "end_date": "2026-03-15"
}
```

**Response:**
```json
{
  "success": true,
  "current_regime": { ... },
  "performance": {
    "total_return": 0.85,
    "annualized_return": 0.24,
    "regime_stats": { ... },
    "equity_curve": [ ... ]
  }
}
```

### `POST /api/current-regime`
Get current live regime reading

**Request:**
```json
{
  "weight_defcyc": 2.0,
  "threshold_defensive": 7.0,
  ...
}
```

**Response:**
```json
{
  "date": "2026-03-13",
  "regime": "Defensive",
  "ewma_score": 8.75,
  "composite_score": 10,
  "signals": { ... }
}
```

## 🎨 Design Philosophy

**Clean, professional financial interface:**
- IBM Plex Sans font family
- Subtle gradients and shadows
- Clear data hierarchy
- Responsive layout
- Accessible color contrasts

**User Experience:**
- Editable inputs with validation
- Real-time feedback
- Loading states
- Error handling
- Mobile-responsive

## 🔒 Data & Privacy

- All data fetched from Yahoo Finance (public)
- No user data stored
- No authentication required
- Serverless functions (stateless)
- CORS configured for security

## 📈 Performance Considerations

**Frontend:**
- Code splitting with Vite
- Lazy loading components
- Optimized bundle size
- Cached API responses

**Backend:**
- Efficient pandas operations
- Vectorized calculations
- Minimal data transfer
- Response compression

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Credits

- **Model Development**: Connor (Equity Research Analyst)
- **Data Source**: Yahoo Finance API
- **Deployment**: Vercel Platform

## 📞 Support

For issues or questions:
1. Check [DEPLOYMENT.md](./DEPLOYMENT.md)
2. Review Vercel deployment logs
3. Open a GitHub issue

---

**Built with ❤️ for quantitative portfolio management**
