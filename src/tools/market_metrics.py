# tools/market_metrics.py

import numpy as np
import pandas as pd
from typing import Dict, Any
from ..classes.AnalysisPlan import Metric
# from analysis_plan import Metric

TRADING_DAYS = 252


def annualize_return(r: float, periods: int) -> float:
    return (1 + r) ** (TRADING_DAYS / periods) - 1



def compute_total_return(df: pd.DataFrame) -> Dict[str, Any]:
    r = df["price"].iloc[-1] / df["price"].iloc[0] - 1
    return {
        "value": float(r),
        "sample_size": len(df)
    }


def compute_cagr(df: pd.DataFrame) -> Dict[str, Any]:
    n = len(df)
    r = df["price"].iloc[-1] / df["price"].iloc[0] - 1
    cagr = annualize_return(r, n)
    return {
        "value": float(cagr),
        "sample_size": n
    }

def compute_sharpe(df: pd.DataFrame) -> Dict[str, Any]:
    returns = df["returns"]
    sharpe = np.sqrt(TRADING_DAYS) * returns.mean() / returns.std()
    return {
        "value": float(sharpe),
        "sample_size": len(returns)
    }

def compute_max_drawdown(df: pd.DataFrame) -> Dict[str, Any]:
    cum = df["price"] / df["price"].iloc[0]
    peak = cum.cummax()
    drawdown = (cum - peak) / peak
    return {
        "value": float(drawdown.min()),
        "sample_size": len(df)
    }

def compute_realized_volatility(df: pd.DataFrame) -> Dict[str, Any]:
    vol = np.sqrt(TRADING_DAYS) * df["returns"].std()
    return {
        "value": float(vol),
        "sample_size": len(df)
    }


def compute_rolling_volatility(df: pd.DataFrame, window: int = 30) -> Dict[str, Any]:
    rv = np.sqrt(TRADING_DAYS) * df["returns"].rolling(window).std()
    return {
        "value": rv.dropna().to_dict(),
        "window": window,
        "sample_size": len(rv.dropna())
    }

def compute_rolling_correlation(
    data: Dict[str, pd.DataFrame],
    window: int = 30
) -> Dict[str, Any]:
    symbols = list(data.keys())
    if len(symbols) < 2:
        raise ValueError("Rolling correlation requires at least two assets")

    s1, s2 = symbols[:2]
    r1 = data[s1]["returns"]
    r2 = data[s2]["returns"]

    corr = r1.rolling(window).corr(r2)

    return {
        "pair": [s1, s2],
        "value": corr.dropna().to_dict(),
        "window": window,
        "sample_size": len(corr.dropna())
    }


def compute_beta(
    asset_df: pd.DataFrame,
    benchmark_df: pd.DataFrame
) -> Dict[str, Any]:
    r_a = asset_df["returns"]
    r_b = benchmark_df["returns"]

    cov = np.cov(r_a, r_b)[0, 1]
    var = np.var(r_b)

    beta = cov / var

    return {
        "value": float(beta),
        "sample_size": len(r_a)
    }

def compute_volume(df: pd.DataFrame) -> Dict[str, Any]:
    if "volume" not in df.columns:
        return {"value": None, "note": "volume not available"}

    return {
        "value": float(df["volume"].mean()),
        "sample_size": len(df)
    }


def compute_amihud(df: pd.DataFrame) -> Dict[str, Any]:
    if "volume" not in df.columns:
        return {"value": None, "note": "volume not available"}

    illiq = (df["returns"].abs() / df["volume"]).replace([np.inf, -np.inf], np.nan)
    return {
        "value": float(illiq.mean()),
        "sample_size": len(illiq.dropna())
    }

def compute_regime_switching(df: pd.DataFrame) -> Dict[str, Any]:
    # Placeholder: simple volatility thresholding
    vol = df["returns"].rolling(30).std()
    regimes = (vol > vol.median()).astype(int)

    return {
        "regimes": regimes.dropna().to_dict(),
        "sample_size": len(regimes.dropna())
    }

METRIC_FUNCTIONS = {
    Metric.TOTAL_RETURN: compute_total_return,
    Metric.CAGR: compute_cagr,
    Metric.SHARPE_RATIO: compute_sharpe,
    Metric.MAX_DRAWDOWN: compute_max_drawdown,
    Metric.REALIZED_VOLATILITY: compute_realized_volatility,
    Metric.ROLLING_VOLATILITY: compute_rolling_volatility,
    Metric.VOLUME: compute_volume,
    Metric.AMIHUD_ILLIQUIDITY: compute_amihud,
    Metric.REGIME_SWITCHING: compute_regime_switching,
}

