"""
Parameter Sweep Optimizer for Enhanced Momentum Regime Model

Tests combinations of:
- Threshold (entry/exit levels)
- EWMA Span (smoothing parameter)
- Hysteresis (exit offset)
- Signal Weights (future: test weight variations)

Ranks configurations by forward return performance
"""

import pandas as pd
import numpy as np
from itertools import product
from typing import Dict, List, Tuple
import signal_calculator as calc
import config

def calculate_forward_returns(prices: pd.DataFrame, regime_series: pd.Series, 
                              horizons: List[int] = [4, 13, 26]) -> pd.DataFrame:
    """
    Calculate forward returns from each regime trigger
    
    Args:
        prices: Price data (SPY column required)
        regime_series: Series with regime labels ('Defensive', 'Neutral', 'Risk-On')
        horizons: List of forward return horizons in weeks
        
    Returns:
        DataFrame with trigger dates and forward returns
    """
    # Detect regime changes
    regime_changes = regime_series != regime_series.shift(1)
    trigger_dates = regime_series[regime_changes].index
    
    results = []
    
    for trigger_date in trigger_dates:
        if trigger_date not in prices.index:
            continue
            
        trigger_idx = prices.index.get_loc(trigger_date)
        regime = regime_series.loc[trigger_date]
        
        row = {
            'Date': trigger_date,
            'Regime': regime,
            'From_Regime': regime_series.shift(1).loc[trigger_date] if trigger_idx > 0 else None
        }
        
        # Calculate forward returns at each horizon
        for horizon in horizons:
            future_idx = trigger_idx + horizon
            
            if future_idx < len(prices):
                price_start = prices['SPY'].iloc[trigger_idx]
                price_end = prices['SPY'].iloc[future_idx]
                fwd_return = (price_end / price_start) - 1
                row[f'Fwd_{horizon}wk'] = fwd_return
            else:
                row[f'Fwd_{horizon}wk'] = None
        
        results.append(row)
    
    return pd.DataFrame(results)


def backtest_configuration(prices: pd.DataFrame, 
                          threshold_def: float,
                          threshold_ro: float,
                          ewma_span: int,
                          hysteresis: int = 0) -> Dict:
    """
    Backtest a single parameter configuration
    
    Returns:
        Dictionary with performance metrics
    """
    # Calculate signals with current config
    signals = calc.calculate_all_signals(prices)
    
    # Apply EWMA with specified span
    alpha = 2 / (ewma_span + 1)
    ewma_score = signals['Composite'].ewm(span=ewma_span, adjust=False).mean()
    
    # Classify regime
    def classify(score):
        if pd.isna(score):
            return 'Neutral'
        if score >= threshold_def:
            return 'Defensive'
        elif score <= threshold_ro:
            return 'Risk-On'
        else:
            return 'Neutral'
    
    regime = ewma_score.apply(classify)
    
    # Calculate forward returns
    fwd_returns = calculate_forward_returns(prices, regime)
    
    # Aggregate statistics by regime
    stats = {}
    
    for reg in ['Risk-On', 'Defensive', 'Neutral']:
        reg_data = fwd_returns[fwd_returns['Regime'] == reg]
        
        if len(reg_data) == 0:
            continue
        
        stats[f'{reg}_n'] = len(reg_data)
        
        for horizon in [4, 13, 26]:
            col = f'Fwd_{horizon}wk'
            if col in reg_data.columns:
                valid = reg_data[col].dropna()
                if len(valid) > 0:
                    stats[f'{reg}_{horizon}wk_avg'] = valid.mean()
                    stats[f'{reg}_{horizon}wk_wr'] = (valid > 0).sum() / len(valid)
    
    # Calculate spread (Risk-On minus Defensive) at 26 weeks
    if 'Risk-On_26wk_avg' in stats and 'Defensive_26wk_avg' in stats:
        stats['Spread_26wk'] = stats['Risk-On_26wk_avg'] - stats['Defensive_26wk_avg']
    else:
        stats['Spread_26wk'] = None
    
    # Add configuration parameters
    stats['Threshold_Def'] = threshold_def
    stats['Threshold_RO'] = threshold_ro
    stats['EWMA_Span'] = ewma_span
    stats['Hysteresis'] = hysteresis
    
    return stats


def parameter_sweep(prices: pd.DataFrame,
                   threshold_range: List[int] = [5, 6, 7, 8, 9],
                   span_range: List[int] = [3, 4, 5, 6, 7],
                   hysteresis_range: List[int] = [0, 3, 5],
                   verbose: bool = True) -> pd.DataFrame:
    """
    Run parameter sweep across all combinations
    
    Args:
        prices: Price data
        threshold_range: List of threshold values to test (symmetric: +T for Def, -T for RO)
        span_range: List of EWMA span values
        hysteresis_range: List of hysteresis offsets
        verbose: Print progress
        
    Returns:
        DataFrame with results for all configurations
    """
    results = []
    total_combos = len(threshold_range) * len(span_range) * len(hysteresis_range)
    
    if verbose:
        print(f"Testing {total_combos} parameter combinations...")
        print(f"  Thresholds: {threshold_range}")
        print(f"  Spans: {span_range}")
        print(f"  Hysteresis: {hysteresis_range}")
    
    count = 0
    for threshold, span, hyst in product(threshold_range, span_range, hysteresis_range):
        count += 1
        
        if verbose and count % 10 == 0:
            print(f"  Progress: {count}/{total_combos}")
        
        # Test symmetric thresholds
        stats = backtest_configuration(
            prices=prices,
            threshold_def=threshold,
            threshold_ro=-threshold,
            ewma_span=span,
            hysteresis=hyst
        )
        
        results.append(stats)
    
    df_results = pd.DataFrame(results)
    
    # Sort by 26-week spread (descending)
    if 'Spread_26wk' in df_results.columns:
        df_results = df_results.sort_values('Spread_26wk', ascending=False)
    
    return df_results


if __name__ == '__main__':
    print("=" * 80)
    print("REGIME MODEL PARAMETER OPTIMIZATION")
    print("=" * 80)
    
    # Load data
    print("\nLoading data...")
    df_prices = pd.read_csv(config.CSV_DATA_PATH, index_col='Date', parse_dates=True)
    print(f"Loaded {len(df_prices)} weeks of data ({df_prices.index[0]} to {df_prices.index[-1]})")
    
    # Run parameter sweep
    print("\nRunning parameter sweep...")
    results = parameter_sweep(
        prices=df_prices,
        threshold_range=[5, 6, 7, 8, 9],
        span_range=[3, 4, 5, 6, 7],
        hysteresis_range=[0, 3, 5],
        verbose=True
    )
    
    # Save results
    results.to_csv('/home/claude/regime_optimizer/parameter_sweep_results.csv', index=False)
    print("\nResults saved to: parameter_sweep_results.csv")
    
    # Display top 10 configurations
    print("\n" + "=" * 80)
    print("TOP 10 CONFIGURATIONS (by 26-week spread)")
    print("=" * 80)
    
    display_cols = ['Threshold_Def', 'EWMA_Span', 'Hysteresis', 
                   'Risk-On_n', 'Defensive_n',
                   'Risk-On_26wk_avg', 'Defensive_26wk_avg', 'Spread_26wk',
                   'Risk-On_26wk_wr', 'Defensive_26wk_wr']
    
    print(results[display_cols].head(10).to_string(index=False))
    
    # Summary statistics
    print("\n\n" + "=" * 80)
    print("OPTIMIZATION SUMMARY")
    print("=" * 80)
    
    best = results.iloc[0]
    print(f"\nBest Configuration:")
    print(f"  Threshold: ±{best['Threshold_Def']}")
    print(f"  EWMA Span: {best['EWMA_Span']}")
    print(f"  Hysteresis: {best['Hysteresis']}")
    print(f"\nPerformance:")
    print(f"  Risk-On 26wk return: {best['Risk-On_26wk_avg']:.2%} (n={best['Risk-On_n']:.0f})")
    print(f"  Defensive 26wk return: {best['Defensive_26wk_avg']:.2%} (n={best['Defensive_n']:.0f})")
    print(f"  Spread: {best['Spread_26wk']:.2%}")
    
    # Compare to current config (±7, span=5, hyst=0)
    current = results[(results['Threshold_Def'] == 7) & 
                     (results['EWMA_Span'] == 5) & 
                     (results['Hysteresis'] == 0)]
    
    if len(current) > 0:
        current = current.iloc[0]
        current_idx = results.reset_index(drop=True).index[results.reset_index(drop=True)['Threshold_Def'] == current['Threshold_Def']].tolist()[0]
        print(f"\n\nCurrent Configuration (±7, Span=5, Hyst=0):")
        print(f"  Spread: {current['Spread_26wk']:.2%}")
        print(f"  Rank: {current_idx + 1}/{len(results)}")
    
    print("\n\nDone!")
