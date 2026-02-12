# nodes/data_cleaning.py
from typing import Dict
import pandas as pd
from classes.state import MarketAnalysisState

def data_cleaning_node(state: MarketAnalysisState) -> dict:
    """
    Clean and preprocess raw market data.

    Produces a canonical dataset per symbol with:
    - price (Adj Close preferred, else Close)
    - price_raw (Close)
    - returns
    - normalized price (base 100)
    - volume (if available)

    Deterministic, metric-agnostic, loop-safe.
    """

    raw_data = state.get("raw_market_data")

    if raw_data is None:
        raise ValueError("raw_market_data is required before cleaning")

    cleaned: Dict[str, pd.DataFrame] = {}

    # ---- Per-symbol cleaning ----
    for symbol, df in raw_data.items():
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected DataFrame for {symbol}")

        df = df.copy()
        df.index = pd.to_datetime(df.index)

        # Validate required columns
        if "Close" not in df.columns:
            raise ValueError(f"'Close' column missing for {symbol}")

        use_adj = "Adj Close" in df.columns

        # Build canonical frame
        out = pd.DataFrame(index=df.index)

        out["price"] = df["Adj Close"] if use_adj else df["Close"]
        out["price_raw"] = df["Close"]

        if "Volume" in df.columns:
            out["volume"] = df["Volume"]

        # Drop rows with missing prices
        out = out.dropna(subset=["price"])

        # Normalized price (base 100)
        out["price_normalized"] = out["price"] / out["price"].iloc[0] * 100

        # Returns
        out["returns"] = out["price"].pct_change()

        # Drop first row introduced by pct_change
        out = out.dropna()

        cleaned[symbol] = out

    # ---- Align time index across all symbols ----
    common_index = None
    for df in cleaned.values():
        common_index = df.index if common_index is None else common_index.intersection(df.index)

    for symbol in cleaned:
        cleaned[symbol] = cleaned[symbol].loc[common_index]

    return {
        "cleaned_market_data": cleaned
    }
