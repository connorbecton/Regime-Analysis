"""
Signal Calculator for Enhanced Momentum Regime Model v2.0

Calculates the 5 signals:
1. Defensive vs Cyclical (DefCyc)
2. Low Beta vs High Beta (LoBHiB) - disabled but calculated
3. Value vs Growth (ValGrw)
4. High Dividend vs Market (HiDivMkt)
5. Credit Spread (CrdSprd) - IEI vs HYG

Each signal:
- Calculate 13-week momentum for constituent ETFs
- Compute spread (defensive/safe - cyclical/risky)
- Convert spread to z-score using 252-week rolling window
- Map z-score to discrete score (-2, -1, 0, +1, +2)
- Weight and sum to get composite score
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import config

def calculate_momentum(prices: pd.DataFrame, lookback: int = config.MOMENTUM_LOOKBACK_WEEKS, 
                      half_life: int = 4) -> pd.DataFrame:
    """
    Calculate EWMA momentum using cumulative exponentially weighted average
    
    Excel implementation: cumulative EWMA(halflife=4) of weekly log returns
    This gives exponentially decaying weights to historical returns with ~4 week half-life
    
    Args:
        prices: DataFrame with ETF prices, index = dates
        lookback: Not used (kept for API compatibility)
        half_life: Exponential decay half-life in weeks (default 4)
        
    Returns:
        DataFrame of EWMA momentum values (same shape as prices)
    """
    # Calculate weekly log returns
    returns = np.log(prices / prices.shift(1))
    
    # Apply cumulative EWMA with halflife parameter
    # adjust=False uses recursive formula: y_t = α×x_t + (1-α)×y_{t-1}
    # This matches Excel's implementation
    momentum = returns.ewm(halflife=half_life, adjust=False).mean()
    
    return momentum


def calculate_basket_momentum(prices: pd.DataFrame, etf_list: list) -> pd.Series:
    """
    Calculate equal-weighted average momentum for a basket of ETFs
    
    Args:
        prices: DataFrame with ETF prices
        etf_list: List of ticker symbols
        
    Returns:
        Series of basket momentum
    """
    momentum = calculate_momentum(prices[etf_list])
    basket_momentum = momentum.mean(axis=1)
    return basket_momentum


def calculate_spread(prices: pd.DataFrame, defensive_etfs: list, cyclical_etfs: list) -> pd.Series:
    """
    Calculate momentum spread: defensive - cyclical
    
    Positive spread = defensive outperforming = defensive signal
    Negative spread = cyclical outperforming = risk-on signal
    """
    def_momentum = calculate_basket_momentum(prices, defensive_etfs)
    cyc_momentum = calculate_basket_momentum(prices, cyclical_etfs)
    spread = def_momentum - cyc_momentum
    return spread


def calculate_rolling_zscore(series: pd.Series, window: int = config.ZSCORE_WINDOW_WEEKS) -> pd.Series:
    """
    Calculate z-score using a rolling window (matches Excel implementation)

    Z = (X - rolling_mean) / rolling_std
    """
    rolling_mean = series.rolling(window, min_periods=config.MIN_HISTORY_WEEKS).mean()
    rolling_std = series.rolling(window, min_periods=config.MIN_HISTORY_WEEKS).std()
    zscore = (series - rolling_mean) / rolling_std
    return zscore


def zscore_to_discrete_score(zscore: float) -> int:
    """
    Map continuous z-score to discrete score (-2, -1, 0, +1, +2)
    
    Args:
        zscore: Continuous z-score value
        
    Returns:
        Discrete score in {-2, -1, 0, +1, +2}
    """
    if pd.isna(zscore):
        return 0
    
    thresholds = config.ZSCORE_THRESHOLDS
    
    # Defensive (positive z-scores)
    if zscore >= thresholds['strong_defensive']:
        return 2
    elif zscore >= thresholds['moderate_defensive']:
        return 1
    # Risk-On (negative z-scores)
    elif zscore <= thresholds['strong_riskon']:
        return -2
    elif zscore <= thresholds['moderate_riskon']:
        return -1
    # Neutral
    else:
        return 0


def calculate_all_signals(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all 5 signals with spreads, z-scores, and discrete scores
    
    Args:
        prices: DataFrame with ETF prices (columns = tickers, index = dates)
        
    Returns:
        DataFrame with columns:
        - Spr_DefCyc, Spr_LoBHiB, Spr_ValGrw, Spr_HiDivMkt, Spr_CrdSprd (raw spreads)
        - Z_DefCyc, Z_LoBHiB, Z_ValGrw, Z_HiDivMkt, Z_CrdSprd (z-scores)
        - Sc_DefCyc, Sc_LoBHiB, Sc_ValGrw, Sc_HiDivMkt, Sc_CrdSprd (discrete scores)
        - Wt_DefCyc, Wt_LoBHiB, Wt_ValGrw, Wt_HiDivMkt, Wt_CrdSprd (weighted scores)
        - Composite (sum of weighted scores)
    """
    
    results = pd.DataFrame(index=prices.index)
    
    # 1. Defensive vs Cyclical
    spr_defcyc = calculate_spread(prices, config.DEFENSIVE_ETFS, config.CYCLICAL_ETFS)
    results['Spr_DefCyc'] = spr_defcyc
    results['Z_DefCyc'] = calculate_rolling_zscore(spr_defcyc)
    results['Sc_DefCyc'] = results['Z_DefCyc'].apply(zscore_to_discrete_score)
    results['Wt_DefCyc'] = results['Sc_DefCyc'] * config.WEIGHTS['DefCyc']
    
    # 2. Low Beta vs High Beta (disabled in v2.0 but still calculated)
    spr_lobhib = calculate_spread(prices, config.LOW_BETA_ETFS, config.HIGH_BETA_ETFS)
    results['Spr_LoBHiB'] = spr_lobhib
    results['Z_LoBHiB'] = calculate_rolling_zscore(spr_lobhib)
    results['Sc_LoBHiB'] = results['Z_LoBHiB'].apply(zscore_to_discrete_score)
    results['Wt_LoBHiB'] = results['Sc_LoBHiB'] * config.WEIGHTS['LoBHiB']  # Weight = 0
    
    # 3. Value vs Growth
    spr_valgrw = calculate_spread(prices, config.VALUE_ETFS, config.GROWTH_ETFS)
    results['Spr_ValGrw'] = spr_valgrw
    results['Z_ValGrw'] = calculate_rolling_zscore(spr_valgrw)
    results['Sc_ValGrw'] = results['Z_ValGrw'].apply(zscore_to_discrete_score)
    results['Wt_ValGrw'] = results['Sc_ValGrw'] * config.WEIGHTS['ValGrw']
    
    # 4. High Dividend vs Market
    spr_hidivmkt = calculate_spread(prices, config.HIGH_DIV_ETFS, config.MARKET_ETFS)
    results['Spr_HiDivMkt'] = spr_hidivmkt
    results['Z_HiDivMkt'] = calculate_rolling_zscore(spr_hidivmkt)
    results['Sc_HiDivMkt'] = results['Z_HiDivMkt'].apply(zscore_to_discrete_score)
    results['Wt_HiDivMkt'] = results['Sc_HiDivMkt'] * config.WEIGHTS['HiDivMkt']
    
    # 5. Credit Spread (IEI - HYG momentum)
    # Positive = IEI outperforming = flight to safety = defensive
    # Negative = HYG outperforming = risk appetite = risk-on
    momentum = calculate_momentum(prices[['IEI', 'HYG']])
    spr_crdsprd = momentum['IEI'] - momentum['HYG']
    results['Spr_CrdSprd'] = spr_crdsprd
    results['Z_CrdSprd'] = calculate_rolling_zscore(spr_crdsprd)
    results['Sc_CrdSprd'] = results['Z_CrdSprd'].apply(zscore_to_discrete_score)
    results['Wt_CrdSprd'] = results['Sc_CrdSprd'] * config.WEIGHTS['CrdSprd']
    
    # Composite Score (sum of all weighted signals)
    weight_cols = ['Wt_DefCyc', 'Wt_LoBHiB', 'Wt_ValGrw', 'Wt_HiDivMkt', 'Wt_CrdSprd']
    results['Composite'] = results[weight_cols].sum(axis=1)
    
    return results


def calculate_ewma_score(composite_scores: pd.Series, span: int = config.EWMA_SPAN) -> pd.Series:
    """
    Apply EWMA smoothing to composite scores
    
    Args:
        composite_scores: Series of raw composite scores
        span: EWMA span parameter (default 5)
        
    Returns:
        Series of EWMA-smoothed scores
    """
    # pandas EWMA with span parameter
    # alpha = 2 / (span + 1)
    ewma = composite_scores.ewm(span=span, adjust=False).mean()
    return ewma


def classify_regime(ewma_score: float, previous_regime: str = None) -> str:
    """
    Classify regime based on EWMA score
    
    Args:
        ewma_score: Smoothed composite score
        previous_regime: Previous regime (for hysteresis, if enabled)
        
    Returns:
        'Defensive', 'Neutral', or 'Risk-On'
    """
    if pd.isna(ewma_score):
        return 'Neutral'
    
    # Basic classification (no hysteresis for now)
    if ewma_score >= config.THRESHOLD_DEFENSIVE:
        return 'Defensive'
    elif ewma_score <= config.THRESHOLD_RISKON:
        return 'Risk-On'
    else:
        return 'Neutral'


if __name__ == '__main__':
    # Test with extracted data
    print("Testing signal calculator...")
    
    df_prices = pd.read_csv(config.CSV_DATA_PATH, index_col='Date', parse_dates=True)
    
    print(f"Loaded {len(df_prices)} weeks of price data")
    print(f"Date range: {df_prices.index[0]} to {df_prices.index[-1]}")
    
    # Calculate all signals
    print("\nCalculating signals...")
    signals = calculate_all_signals(df_prices)
    
    # Add EWMA
    signals['EWMA_Score'] = calculate_ewma_score(signals['Composite'])
    signals['Regime'] = signals['EWMA_Score'].apply(classify_regime)
    
    print("\nLast 10 weeks:")
    print(signals.tail(10)[['Z_DefCyc', 'Z_HiDivMkt', 'Z_CrdSprd', 'Composite', 'EWMA_Score', 'Regime']])
    
    print("\nDone!")
