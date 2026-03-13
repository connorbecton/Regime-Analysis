# QUICK START GUIDE: Regime Optimizer

## 🚀 Getting Started (5 minutes)

### Step 1: Install Dependencies
```bash
pip install pandas numpy openpyxl --break-system-packages
```

### Step 2: Test the Calculator
```bash
cd regime_optimizer
python3 signal_calculator.py
```

**Expected output:** Last 10 weeks of signals showing Z-scores, Composite, EWMA, and Regime

### Step 3: Run Optimization
```bash
python3 optimizer.py
```

**Expected output:** 
- Tests 75 parameter combinations
- Saves `parameter_sweep_results.csv`
- Displays top 10 configurations

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `config.py` | Model parameters (weights, thresholds, ETF lists) |
| `signal_calculator.py` | Core calculation engine |
| `optimizer.py` | Parameter sweep tool |
| `validate.py` | Compare Python vs Excel |
| `PHASE1_SUMMARY.md` | Detailed results & analysis |
| `parameter_sweep_results.csv` | All 75 tested configurations |

---

## 💡 Common Tasks

### Change Model Parameters
Edit `config.py`:
```python
# Test different thresholds
THRESHOLD_DEFENSIVE = 8  # Instead of 7
THRESHOLD_RISKON = -8

# Test different weights
WEIGHTS = {
    'DefCyc': 3.0,      # Increase from 2
    'HiDivMkt': 2.5,    # Decrease from 3
    # ...
}
```

### Run Custom Parameter Sweep
```python
from optimizer import parameter_sweep
import pandas as pd

prices = pd.read_csv('price_data_clean.csv', index_col='Date', parse_dates=True)

results = parameter_sweep(
    prices=prices,
    threshold_range=[7, 8, 9, 10],  # Test higher thresholds
    span_range=[4, 5, 6],            # Narrow span range
    hysteresis_range=[0],            # No hysteresis
    verbose=True
)

print(results.head(20))  # Top 20 configs
```

### Calculate Signals for Specific Date
```python
import pandas as pd
import signal_calculator as calc

prices = pd.read_csv('price_data_clean.csv', index_col='Date', parse_dates=True)
signals = calc.calculate_all_signals(prices)
signals['EWMA_Score'] = calc.calculate_ewma_score(signals['Composite'])
signals['Regime'] = signals['EWMA_Score'].apply(calc.classify_regime)

# Check specific date
print(signals.loc['2026-03-06'])
```

---

## 📊 Understanding the Output

### Parameter Sweep Results Columns

**Configuration:**
- `Threshold_Def`, `Threshold_RO` - Entry thresholds
- `EWMA_Span` - Smoothing parameter (3-7 weeks)
- `Hysteresis` - Exit lag (usually 0)

**Performance:**
- `Risk-On_26wk_avg` - Average 26-week return after Risk-On trigger
- `Defensive_26wk_avg` - Average 26-week return after Defensive trigger
- `Spread_26wk` - Risk-On minus Defensive (higher = better)
- `Risk-On_26wk_wr` - Win rate (% positive returns)
- `Risk-On_n` - Number of trigger events

**Key Metric:** `Spread_26wk` (sorted by this)

---

## ⚡ Performance Tips

1. **Filter by sample size first:**
```python
results = results[(results['Risk-On_n'] >= 5) & (results['Defensive_n'] >= 5)]
```

2. **Look for robustness:**
- Configs that rank well across multiple metrics
- Similar performance with/without hysteresis
- Win rates >60%

3. **Avoid overfitting:**
- n=1 or n=2 triggers = too few to trust
- Extreme spreads (>20%) often from lucky single events
- Test out-of-sample if possible

---

## 🔧 Troubleshooting

**"Module not found" error:**
```bash
# Make sure you're in the regime_optimizer directory
cd regime_optimizer
python3 signal_calculator.py
```

**Different results than Excel:**
- Expected: Z-scores differ by ~0.07 on average
- Check: Discrete scores and Composite should match on most dates
- See `validate.py` for detailed comparison

**Optimization runs slow:**
- Expected: ~2-3 seconds per configuration
- 75 configs = ~2-3 minutes total
- Reduce ranges to test fewer combinations

---

## 📈 Next Steps

1. **Review PHASE1_SUMMARY.md** for full analysis
2. **Check parameter_sweep_results.csv** for all configs
3. **Test recommended ±8 threshold** with your Excel model
4. **Consider Phase 2:** Statistical validation, walk-forward testing

---

## ❓ Questions?

Check `PHASE1_SUMMARY.md` for:
- Detailed optimization insights
- Recommendations for production use
- Phase 2 roadmap
- Important caveats & limitations
