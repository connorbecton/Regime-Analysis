"""
Market Regime Detection API
FastAPI backend for regime model backtesting
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import traceback
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Market Regime API")

# CORS configuration for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS
# ============================================================================

class ModelConfig(BaseModel):
    """Configuration for regime model"""
    # Signal weights
    weight_defcyc: float = 2.0
    weight_lobhib: float = 0.0  # Disabled
    weight_valgrw: float = 2.0
    weight_hidivmkt: float = 3.0
    weight_crdsprd: float = 2.0
    
    # Thresholds
    threshold_defensive: float = 7.0
    threshold_riskon: float = -7.0
    
    # EWMA parameters (single-EWMA legacy fields, kept for compat)
    ewma_span: int = 6
    momentum_lookback: int = 13
    zscore_window: int = 252

    # MomDiv / Speed-Adjusted Blend parameters (primary regime signal)
    ewma_span_fast: int = 3          # Short, aggressive smoother
    ewma_span_slow: int = 5          # Long, conservative smoother
    lambda_blend: float = 0.8        # Divergence weight in blend
    threshold_momdiv: float = 4.0    # Entry threshold on |MomDiv_Score|
    
    # Z-score thresholds
    zscore_moderate: float = 0.75
    zscore_strong: float = 1.5
    
    # Baskets (cyclical)
    cyclical_etfs: List[str] = ["XLF", "XLI", "XLB"]

class PortfolioAllocation(BaseModel):
    """Portfolio allocation for each regime"""
    risk_on: Dict[str, float] = {
        "XLF": 0.20, "XLI": 0.20, "XLB": 0.15, 
        "XLK": 0.10, "XLY": 0.10, "XLC": 0.05,
        "XLU": 0.05, "XLP": 0.05, "XLV": 0.10
    }
    neutral: Dict[str, float] = {
        "XLF": 0.11, "XLI": 0.11, "XLB": 0.11,
        "XLK": 0.11, "XLY": 0.11, "XLC": 0.11,
        "XLU": 0.11, "XLP": 0.11, "XLV": 0.11
    }
    defensive: Dict[str, float] = {
        "XLU": 0.20, "XLP": 0.20, "XLV": 0.20,
        "XLF": 0.10, "XLI": 0.10, "XLB": 0.05,
        "XLK": 0.05, "XLY": 0.05, "XLC": 0.05
    }

def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")

class BacktestRequest(BaseModel):
    """Request for backtesting"""
    config: ModelConfig
    portfolio: PortfolioAllocation
    start_date: str = "2016-01-01"
    end_date: str = Field(default_factory=_today)

# ============================================================================
# CORE CALCULATION FUNCTIONS
# ============================================================================

def _make_session() -> requests.Session:
    """Plain requests session with a browser User-Agent."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
    })
    return session


def _fetch_one_ticker(ticker: str, start_date: str, end_date: str,
                      session: requests.Session) -> pd.Series:
    """
    Fetch weekly close prices from stooq.com for a single ticker.
    stooq serves plain CSV with no auth — cloud IPs are not blocked.
    Returns a Series indexed by date.
    """
    from io import StringIO

    d1 = start_date.replace('-', '')  # YYYYMMDD
    d2 = end_date.replace('-', '')
    stooq_ticker = ticker.lower() + '.us'

    url = f"https://stooq.com/q/d/l/?s={stooq_ticker}&d1={d1}&d2={d2}&i=w"
    resp = session.get(url, timeout=15)
    resp.raise_for_status()

    content = resp.text.strip()
    # stooq returns an HTML page or a short message when ticker is unknown
    if not content or content.startswith('<') or len(content.splitlines()) < 2:
        raise ValueError(f"No data from stooq for {ticker} (ticker may not exist there)")

    df = pd.read_csv(StringIO(content), parse_dates=['Date'])
    df = df.set_index('Date').sort_index()

    if 'Close' not in df.columns:
        raise ValueError(f"Unexpected stooq format for {ticker}: {df.columns.tolist()}")

    return df['Close'].rename(ticker).dropna()


def fetch_price_data(tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch price data from stooq.com for all tickers in parallel.
    stooq.com is used instead of Yahoo Finance because Yahoo Finance actively
    blocks cloud provider IPs with 429 errors (even the auth endpoint).
    Returns weekly Friday-resampled prices.
    """
    logger.info(f"Fetching {len(tickers)} tickers from stooq.com ({start_date} to {end_date})")

    session = _make_session()

    def fetch_with_retry(ticker: str):
        last_err = None
        for attempt in range(3):
            try:
                if attempt > 0:
                    time.sleep(attempt)
                return ticker, _fetch_one_ticker(ticker, start_date, end_date, session)
            except Exception as e:
                last_err = e
                logger.warning(f"{ticker} attempt {attempt + 1} failed: {e}")
        logger.error(f"Giving up on {ticker}: {last_err}")
        return ticker, None

    close_series: Dict[str, pd.Series] = {}
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(fetch_with_retry, t): t for t in tickers}
        for future in as_completed(futures):
            ticker, series = future.result()
            if series is not None:
                close_series[ticker] = series

    if not close_series:
        raise HTTPException(
            status_code=500,
            detail="Could not fetch data for any ticker from Yahoo Finance."
        )

    df = pd.DataFrame(close_series)
    df = df.resample('W-FRI').last()
    df = df.ffill()

    logger.info(f"Fetched {len(df)} weeks for {len(df.columns)}/{len(tickers)} tickers")
    return df

def calculate_momentum(prices: pd.DataFrame, lookback: int = 13) -> pd.DataFrame:
    """Calculate log momentum over lookback period"""
    return np.log(prices / prices.shift(lookback))

def calculate_rolling_zscore(series: pd.Series, window: int = 252) -> pd.Series:
    """Calculate rolling z-score"""
    rolling_mean = series.rolling(window=window, min_periods=30).mean()
    rolling_std = series.rolling(window=window, min_periods=30).std()
    return (series - rolling_mean) / rolling_std

def zscore_to_discrete(z: float, moderate: float = 0.75, strong: float = 1.5) -> int:
    """Map z-score to discrete score (-2 to +2)"""
    if pd.isna(z):
        return 0
    if z >= strong:
        return 2
    elif z >= moderate:
        return 1
    elif z <= -strong:
        return -2
    elif z <= -moderate:
        return -1
    else:
        return 0

def calculate_signals(prices: pd.DataFrame, config: ModelConfig) -> pd.DataFrame:
    """Calculate all regime signals"""
    
    # Define ETF baskets
    defensive_etfs = ["XLU", "XLP", "XLV"]
    cyclical_etfs = config.cyclical_etfs
    
    # Calculate momentum
    momentum = calculate_momentum(prices, config.momentum_lookback)
    
    signals = pd.DataFrame(index=prices.index)
    
    # 1. DefCyc - Defensive vs Cyclical
    def_mom = momentum[defensive_etfs].mean(axis=1)
    cyc_mom = momentum[cyclical_etfs].mean(axis=1)
    signals['Spr_DefCyc'] = def_mom - cyc_mom
    signals['Z_DefCyc'] = calculate_rolling_zscore(signals['Spr_DefCyc'], config.zscore_window)
    signals['Sc_DefCyc'] = signals['Z_DefCyc'].apply(
        lambda x: zscore_to_discrete(x, config.zscore_moderate, config.zscore_strong)
    )
    signals['Wt_DefCyc'] = signals['Sc_DefCyc'] * config.weight_defcyc
    
    # 2. ValGrw - Value vs Growth
    if 'RPV' in prices.columns and 'RPG' in prices.columns:
        signals['Spr_ValGrw'] = momentum['RPV'] - momentum['RPG']
        signals['Z_ValGrw'] = calculate_rolling_zscore(signals['Spr_ValGrw'], config.zscore_window)
        signals['Sc_ValGrw'] = signals['Z_ValGrw'].apply(
            lambda x: zscore_to_discrete(x, config.zscore_moderate, config.zscore_strong)
        )
        signals['Wt_ValGrw'] = signals['Sc_ValGrw'] * config.weight_valgrw
    else:
        signals['Wt_ValGrw'] = 0
    
    # 3. HiDivMkt - High Dividend vs Market
    if 'VYM' in prices.columns and 'SPY' in prices.columns:
        signals['Spr_HiDivMkt'] = momentum['VYM'] - momentum['SPY']
        signals['Z_HiDivMkt'] = calculate_rolling_zscore(signals['Spr_HiDivMkt'], config.zscore_window)
        signals['Sc_HiDivMkt'] = signals['Z_HiDivMkt'].apply(
            lambda x: zscore_to_discrete(x, config.zscore_moderate, config.zscore_strong)
        )
        signals['Wt_HiDivMkt'] = signals['Sc_HiDivMkt'] * config.weight_hidivmkt
    else:
        signals['Wt_HiDivMkt'] = 0
    
    # 4. CrdSprd - Credit Spread
    if 'VSCH' in prices.columns and 'HYG' in prices.columns:
        signals['Spr_CrdSprd'] = momentum['VSCH'] - momentum['HYG']
        signals['Z_CrdSprd'] = calculate_rolling_zscore(signals['Spr_CrdSprd'], config.zscore_window)
        signals['Sc_CrdSprd'] = signals['Z_CrdSprd'].apply(
            lambda x: zscore_to_discrete(x, config.zscore_moderate, config.zscore_strong)
        )
        signals['Wt_CrdSprd'] = signals['Sc_CrdSprd'] * config.weight_crdsprd
    else:
        signals['Wt_CrdSprd'] = 0
    
    # Composite score
    signals['Composite'] = (
        signals['Wt_DefCyc'] + 
        signals['Wt_ValGrw'] + 
        signals['Wt_HiDivMkt'] + 
        signals['Wt_CrdSprd']
    )
    
    # Single-EWMA smoothing (kept for reference / legacy chart overlays)
    signals['EWMA_Score'] = signals['Composite'].ewm(span=config.ewma_span, adjust=False).mean()

    # ------------------------------------------------------------------
    # Speed-Adjusted Blend / MomDiv regime signal
    # ------------------------------------------------------------------
    # Two EWMAs of the composite:
    #   fast (short span, aggressive)
    #   slow (long span, conservative)
    # Divergence = fast - slow (this is the NEWMA detection statistic).
    # MomDiv score = slow + lambda * divergence; regime classified off MomDiv.
    # Reference: Keriven, Garreau, Poli (2020), arXiv:1805.08061.
    # ------------------------------------------------------------------
    signals['EWMA_Fast'] = signals['Composite'].ewm(
        span=config.ewma_span_fast, adjust=False
    ).mean()
    signals['EWMA_Slow'] = signals['Composite'].ewm(
        span=config.ewma_span_slow, adjust=False
    ).mean()
    signals['MomDiv_Divergence'] = signals['EWMA_Fast'] - signals['EWMA_Slow']
    signals['MomDiv_Score'] = (
        signals['EWMA_Slow']
        + config.lambda_blend * signals['MomDiv_Divergence']
    )

    # Regime classification off MomDiv with single entry threshold (+/-threshold_momdiv)
    def classify_regime(score):
        if pd.isna(score):
            return 'Neutral'
        if score >= config.threshold_momdiv:
            return 'Defensive'
        elif score <= -config.threshold_momdiv:
            return 'Risk-On'
        else:
            return 'Neutral'

    signals['Regime'] = signals['MomDiv_Score'].apply(classify_regime)

    return signals

def backtest_portfolio(prices: pd.DataFrame, signals: pd.DataFrame, 
                       portfolio: PortfolioAllocation) -> Dict:
    """Backtest portfolio allocations based on regimes"""
    
    # Calculate weekly returns for each ETF (drop first NaN row)
    returns = prices.pct_change().dropna(how='all')
    
    # Initialize portfolio value
    portfolio_value = []
    current_regime = 'Neutral'
    
    for date, row in signals.iterrows():
        if date not in returns.index:
            continue
            
        regime = row['Regime']
        
        # Get allocation based on regime
        if regime == 'Risk-On':
            allocation = portfolio.risk_on
        elif regime == 'Defensive':
            allocation = portfolio.defensive
        else:
            allocation = portfolio.neutral
        
        # Calculate portfolio return for this period
        period_return = 0
        for ticker, weight in allocation.items():
            if ticker in returns.columns:
                period_return += weight * returns.loc[date, ticker]
        
        portfolio_value.append({
            'date': date,
            'regime': regime,
            'return': period_return
        })
    
    df_performance = pd.DataFrame(portfolio_value)
    df_performance['cumulative'] = (1 + df_performance['return']).cumprod()
    
    # Calculate metrics
    total_return = df_performance['cumulative'].iloc[-1] - 1
    annualized_return = (1 + total_return) ** (52 / len(df_performance)) - 1
    
    # Calculate metrics by regime
    regime_stats = {}
    for regime in ['Risk-On', 'Neutral', 'Defensive']:
        regime_data = df_performance[df_performance['regime'] == regime]
        if len(regime_data) > 0:
            regime_stats[regime] = {
                'count': len(regime_data),
                'avg_return': float(regime_data['return'].mean()),
                'total_return': float((1 + regime_data['return']).prod() - 1),
                'win_rate': float((regime_data['return'] > 0).mean())
            }
    
    def safe_float(v):
        """Return None for NaN/inf so the JSON stays valid."""
        try:
            f = float(v)
            return None if (f != f or f == float('inf') or f == float('-inf')) else f
        except (TypeError, ValueError):
            return None

    equity_curve = []
    for rec in df_performance[['date', 'cumulative', 'regime']].to_dict('records'):
        equity_curve.append({
            'date': rec['date'].strftime('%Y-%m-%d') if hasattr(rec['date'], 'strftime') else str(rec['date']),
            'cumulative': safe_float(rec['cumulative']),
            'regime': rec['regime'],
        })

    return {
        'total_return': safe_float(total_return),
        'annualized_return': safe_float(annualized_return),
        'regime_stats': regime_stats,
        'equity_curve': equity_curve,
    }

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    return {
        "message": "Market Regime Detection API",
        "version": "1.0",
        "endpoints": [
            "/health",
            "/api/backtest (POST)",
            "/api/current-regime (POST)"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    """
    Run full backtest with custom config and portfolio allocations
    """
    try:
        logger.info("Starting backtest...")
        
        # Collect all unique tickers needed
        all_tickers = set(
            ["XLU", "XLP", "XLV", "RPV", "RPG", "VYM", "SPY", "VSCH", "HYG"] +
            request.config.cyclical_etfs +
            list(request.portfolio.risk_on.keys()) +
            list(request.portfolio.neutral.keys()) +
            list(request.portfolio.defensive.keys())
        )
        
        # Fetch price data (dividend-adjusted)
        prices = fetch_price_data(
            list(all_tickers),
            request.start_date,
            request.end_date
        )
        
        # Calculate signals
        signals = calculate_signals(prices, request.config)
        
        # Run portfolio backtest
        backtest_results = backtest_portfolio(prices, signals, request.portfolio)
        
        # Compile regime statistics
        regime_counts = signals['Regime'].value_counts().to_dict()
        regime_changes = (signals['Regime'] != signals['Regime'].shift(1)).sum()
        
        def _sf(v, default=0.0):
            try:
                f = float(v)
                return default if (f != f or f == float('inf') or f == float('-inf')) else f
            except (TypeError, ValueError):
                return default

        # Get current regime
        current_regime = signals['Regime'].iloc[-1]
        current_momdiv = _sf(signals['MomDiv_Score'].iloc[-1])
        current_fast = _sf(signals['EWMA_Fast'].iloc[-1])
        current_slow = _sf(signals['EWMA_Slow'].iloc[-1])
        current_div = _sf(signals['MomDiv_Divergence'].iloc[-1])
        current_ewma = _sf(signals['EWMA_Score'].iloc[-1])
        current_composite = _sf(signals['Composite'].iloc[-1])

        return {
            "success": True,
            "config": request.config.dict(),
            "current_regime": {
                "regime": current_regime,
                "momdiv_score": current_momdiv,
                "fast_ewma": current_fast,
                "slow_ewma": current_slow,
                "divergence": current_div,
                "ewma_score": current_ewma,
                "composite_score": current_composite,
                "threshold_momdiv": float(request.config.threshold_momdiv),
                "date": signals.index[-1].strftime("%Y-%m-%d")
            },
            "regime_summary": {
                "counts": regime_counts,
                "total_changes": int(regime_changes),
                "changes_per_year": float(regime_changes / (len(signals) / 52))
            },
            "performance": backtest_results,
            "signal_history": [
                {
                    "date": idx.strftime("%Y-%m-%d"),
                    "momdiv_score": float(row['MomDiv_Score']) if pd.notna(row['MomDiv_Score']) else None,
                    "fast_ewma": float(row['EWMA_Fast']) if pd.notna(row['EWMA_Fast']) else None,
                    "slow_ewma": float(row['EWMA_Slow']) if pd.notna(row['EWMA_Slow']) else None,
                    "ewma_score": float(row['EWMA_Score']) if pd.notna(row['EWMA_Score']) else None,
                    "composite": float(row['Composite']) if pd.notna(row['Composite']) else None,
                    "regime": row['Regime'],
                }
                for idx, row in signals[['MomDiv_Score', 'EWMA_Fast', 'EWMA_Slow', 'EWMA_Score', 'Composite', 'Regime']].tail(52).iterrows()
            ]
        }
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/current-regime")
async def get_current_regime(config: ModelConfig):
    """Get current regime reading with live data"""
    try:
        # Fetch enough history for the 252-week z-score window (~5yr) plus buffer
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*6)
        
        tickers = ["XLU", "XLP", "XLV", "RPV", "RPG", "VYM", "SPY", "VSCH", "HYG"] + config.cyclical_etfs
        
        prices = fetch_price_data(
            tickers,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        signals = calculate_signals(prices, config)
        
        latest = signals.iloc[-1]
        
        def sf(v, default=0.0):
            """NaN/inf-safe float for JSON serialization."""
            try:
                f = float(v)
                return default if (f != f or f == float('inf') or f == float('-inf')) else f
            except (TypeError, ValueError):
                return default

        return {
            "date": signals.index[-1].strftime("%Y-%m-%d"),
            "regime": latest['Regime'],
            "momdiv_score": sf(latest['MomDiv_Score']),
            "fast_ewma": sf(latest['EWMA_Fast']),
            "slow_ewma": sf(latest['EWMA_Slow']),
            "divergence": sf(latest['MomDiv_Divergence']),
            "ewma_score": sf(latest['EWMA_Score']),  # legacy single-EWMA
            "composite_score": sf(latest['Composite']),
            "threshold_momdiv": float(config.threshold_momdiv),
            "signals": {
                "defcyc": {
                    "z_score": sf(latest['Z_DefCyc']),
                    "discrete": int(latest['Sc_DefCyc']),
                    "weighted": sf(latest['Wt_DefCyc'])
                },
                "valgrw": {
                    "z_score": sf(latest.get('Z_ValGrw', 0)),
                    "discrete": int(latest.get('Sc_ValGrw', 0)),
                    "weighted": sf(latest['Wt_ValGrw'])
                },
                "hidivmkt": {
                    "z_score": sf(latest.get('Z_HiDivMkt', 0)),
                    "discrete": int(latest.get('Sc_HiDivMkt', 0)),
                    "weighted": sf(latest['Wt_HiDivMkt'])
                },
                "crdsprd": {
                    "z_score": sf(latest.get('Z_CrdSprd', 0)),
                    "discrete": int(latest.get('Sc_CrdSprd', 0)),
                    "weighted": sf(latest['Wt_CrdSprd'])
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Current regime error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# For Vercel serverless deployment
app = app
