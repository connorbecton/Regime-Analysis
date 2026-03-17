"""
Configuration parameters for Enhanced Momentum Regime Model v2.0
"""

# Data Parameters
MOMENTUM_LOOKBACK_WEEKS = 13  # 13-week momentum calculation
ZSCORE_WINDOW_WEEKS = 252     # 252-week rolling window for z-scores
MIN_HISTORY_WEEKS = 30        # Minimum weeks before calculations start

# Signal Weights (v2.0)
WEIGHTS = {
    'DefCyc': 2.0,      # Defensive vs Cyclical (upgraded from 1)
    'LoBHiB': 0.0,      # Low Beta vs High Beta (disabled)
    'ValGrw': 2.0,      # Value vs Growth (reduced from 3)
    'HiDivMkt': 3.0,    # High Dividend vs Market (upgraded from 2)
    'CrdSprd': 1.5      # Credit Spread (new in v2.0)
}

# ETF Basket Definitions
DEFENSIVE_ETFS = ['XLU', 'XLP', 'XLV']
CYCLICAL_ETFS = ['XLF', 'XLY', 'XLI', 'XLB', 'XLK', 'XLC']  # XLF instead of XLE in v2.0
LOW_BETA_ETFS = ['SPLV']
HIGH_BETA_ETFS = ['SPHB']
VALUE_ETFS = ['RPV']
GROWTH_ETFS = ['RPG']
MARKET_ETFS = ['SPY']
HIGH_DIV_ETFS = ['VYM']
TREASURY_ETFS = ['IEI']      # 3-7yr Treasury (investment grade)
HIGH_YIELD_ETFS = ['HYG']    # High Yield corporate bonds

# All ETFs in universe
ALL_ETFS = (DEFENSIVE_ETFS + CYCLICAL_ETFS + LOW_BETA_ETFS + HIGH_BETA_ETFS + 
            VALUE_ETFS + GROWTH_ETFS + MARKET_ETFS + HIGH_DIV_ETFS + 
            TREASURY_ETFS + HIGH_YIELD_ETFS)

# EWMA Smoothing Parameters
EWMA_SPAN = 5                                    # 5-week span
EWMA_ALPHA = 2 / (EWMA_SPAN + 1)                # = 0.333
EWMA_HALFLIFE = EWMA_SPAN / 2.0                 # ~1.7 weeks

# Regime Classification Thresholds
THRESHOLD_DEFENSIVE = 7      # EWMA Score >= 7 → Defensive
THRESHOLD_RISKON = -7        # EWMA Score <= -7 → Risk-On
THRESHOLD_NEUTRAL_HIGH = 6   # Between regimes
THRESHOLD_NEUTRAL_LOW = -6

# Hysteresis (exit threshold different from entry)
HYSTERESIS_ENABLED = False
HYSTERESIS_EXIT_OFFSET = 0   # Points to subtract from threshold when exiting

# Z-Score to Discrete Score Mapping
# From white paper: map z-scores to discrete levels (-2, -1, 0, +1, +2)
ZSCORE_THRESHOLDS = {
    'strong_defensive': 1.5,       # Z >= 1.5 → Score = +2
    'moderate_defensive': 0.75,    # 1.5 > Z >= 0.75 → Score = +1
    'neutral_high': 0.0,           # 0.75 > Z >= 0 → Score = 0
    'neutral_low': 0.0,            # 0 > Z > -0.75 → Score = 0
    'moderate_riskon': -0.75,      # -0.75 >= Z > -1.5 → Score = -1
    'strong_riskon': -1.5          # Z <= -1.5 → Score = -2
}

# Maximum Possible Scores
MAX_COMPOSITE_SCORE = sum(WEIGHTS.values()) * 2  # Each signal can be ±2
MIN_COMPOSITE_SCORE = -MAX_COMPOSITE_SCORE

# Data Source
DATA_SOURCE = 'csv'  # 'yahoo' or 'csv'
CSV_DATA_PATH = 'Prices.csv'

# Output
VERBOSE = True
