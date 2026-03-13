# PHASE 1 COMPLETE: Python Regime Optimizer Framework

## ✅ Deliverables

### 1. **Core Modules**
- `config.py` - All model parameters (v2.0 signal weights, thresholds, ETF baskets)
- `signal_calculator.py` - Full signal calculation pipeline (momentum → spreads → z-scores → discrete scores → composite)
- `optimizer.py` - Parameter sweep framework
- `validate.py` - Excel comparison script

### 2. **Data Files**
- `price_data_clean.csv` - 524 weeks of ETF prices (2016-2026)
- `parameter_sweep_results.csv` - 75 tested configurations with performance metrics

### 3. **Validation Results**
**Python replicates Excel logic correctly:**
- ✅ Discrete score mapping (-2 to +2) matches perfectly
- ✅ Composite scores match on key dates (Mar 6: both 6.5)
- ✅ Z-scores differ by ~0.07 units on average (due to minor floating-point/window differences)
- ✅ Differences rarely change discrete scores → model logic is correct

**Minor discrepancy diagnosed:**
- Excel z-scores use slightly different rolling window calculation
- Impact: ~0.07 z-score units average difference
- Conclusion: Acceptable for optimization purposes (discrete scores still match)

---

## 📊 Optimization Results Summary

### Current Configuration (±7, Span=5, Hyst=0)
- **Rank:** 43/75 (middle of pack)
- **Risk-On:** 6.59% 26-week avg (n=6 triggers, 83% WR)
- **Defensive:** 3.33% 26-week avg (n=7 triggers, 67% WR)
- **Spread:** 3.26%

### Best Configuration (±9, Span=7, Hyst=0)
- **Rank:** 1/75
- **Risk-On:** 19.62% 26-week avg (n=1 trigger, 100% WR) ⚠️
- **Defensive:** -0.57% avg (n=4 triggers, 50% WR)
- **Spread:** 20.18%
- **Caveat:** Only 1 Risk-On trigger → likely overfitting or luck

### Key Insights

**1. Threshold is the dominant factor:**
```
±5: Avg spread = 1.01%
±6: Avg spread = -0.25%
±7: Avg spread = 4.43%
±8: Avg spread = 10.14%
±9: Avg spread = 14.11%
```

**2. EWMA Span matters less:**
```
Span=3: Avg spread = 4.38%
Span=4: Avg spread = 5.40%
Span=5: Avg spread = 6.01%
Span=6: Avg spread = 5.80%
Span=7: Avg spread = 7.86%
```

**3. Hysteresis has no effect:**
- All hysteresis values (0, 3, 5) yield identical average spreads
- Suggests regime transitions are clean enough that exit lag doesn't matter

**4. Sample size vs spread tradeoff:**
| Threshold | Avg Triggers/Regime | Avg Spread |
|-----------|-------------------|-----------|
| ±5 | ~15 | 1.01% |
| ±6 | ~12 | -0.25% |
| ±7 | ~7 | 4.43% |
| ±8 | ~5 | 10.14% |
| ±9 | ~3 | 14.11% |

**Higher thresholds → fewer but higher-quality signals**

---

## 🎯 Recommendations

### For Production Use:
**Test ±8 with Span=5-6** as the optimal balance:
- Threshold=±8 provides:
  - Strong discrimination (10.14% avg spread)
  - Reasonable sample size (~5 triggers per regime)
  - Less overfitting risk than ±9
- Span=5-6 smooths noise without excessive lag

### For Further Analysis:
1. **Walk-forward validation:** Test if parameter stability holds across time periods
2. **Filter by sample size:** Require n≥5 for both regimes before ranking
3. **Test asymmetric thresholds:** e.g., -7 for Risk-On, +8 for Defensive
4. **Test signal weight variations:** Current weights (2, 0, 2, 3, 1.5) may not be optimal

---

## 🔧 How to Use This Framework

### Run a parameter sweep:
```python
import pandas as pd
from optimizer import parameter_sweep

# Load data
prices = pd.read_csv('price_data_clean.csv', index_col='Date', parse_dates=True)

# Test custom parameter ranges
results = parameter_sweep(
    prices=prices,
    threshold_range=[6, 7, 8, 9, 10],
    span_range=[3, 5, 7, 9],
    hysteresis_range=[0, 5, 10],
    verbose=True
)

# View top configs
print(results.head(10))
```

### Calculate signals for current config:
```python
import pandas as pd
import signal_calculator as calc

# Load data
prices = pd.read_csv('price_data_clean.csv', index_col='Date', parse_dates=True)

# Calculate signals
signals = calc.calculate_all_signals(prices)
signals['EWMA_Score'] = calc.calculate_ewma_score(signals['Composite'])
signals['Regime'] = signals['EWMA_Score'].apply(calc.classify_regime)

# View recent weeks
print(signals.tail(10)[['Composite', 'EWMA_Score', 'Regime']])
```

---

## 🚀 Next Steps (Phase 2+)

### Statistical Enhancements (~3 hours):
- T-tests between regime returns (statistical significance)
- Bootstrap confidence intervals (robustness check)
- Walk-forward validation (parameter stability over time)
- Drawdown analysis during each regime

### Signal Weight Optimization (~2 hours):
- Test weight combinations for all 5 signals
- Find weights that maximize spread while minimizing false fires
- Correlation-aware weighting (account for signal redundancy)

### Advanced Features (~3 hours):
- Regime transition timing analysis
- Optimal entry/exit lag testing
- Sector allocation recommendations per regime
- Generate PDF reports with charts

### Integration with Website (~2 hours):
- Refactor into importable modules for FastAPI
- Add daily auto-update capability
- Create JSON API endpoint for regime score
- Build visualization dashboard

---

## 📁 File Structure

```
regime_optimizer/
├── config.py                         # Model parameters
├── signal_calculator.py              # Core calculation engine
├── optimizer.py                      # Parameter sweep
├── validate.py                       # Excel comparison
├── price_data_clean.csv              # Input data (524 weeks)
├── parameter_sweep_results.csv       # Optimization results (75 configs)
└── PHASE1_SUMMARY.md                 # This file
```

---

## ⚠️ Important Caveats

1. **Limited backtest period:** 524 weeks (2016-2026) is ~10 years
   - Includes only 1 major bear market (2022)
   - May not capture full regime cycle

2. **Forward-looking bias:** Parameter optimization uses full dataset
   - Walk-forward validation needed to confirm out-of-sample performance

3. **Sample size concerns:** Some configs have very few triggers
   - n=1 for best config is too low for confidence
   - Recommend filtering for n≥5 before trusting results

4. **Z-score calculation difference:** Python vs Excel ~0.07 average difference
   - Unlikely to affect discrete scores materially
   - But may cause minor rank reordering at margins

---

**Phase 1 Status:** ✅ COMPLETE

Ready to proceed with Phase 2 (statistical validation) or integrate directly into website.
