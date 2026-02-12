# tools/maket_data.py
import yfinance as yf
import pandas as pd
from typing import List, Dict


def _flatten_yfinance_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten yfinance MultiIndex columns to single level.
    Keeps only price field names (Open, Close, etc).
    """

    if isinstance(df.columns, pd.MultiIndex):
        # Drop the ticker level
        df.columns = df.columns.get_level_values(0)

    return df


def fetch_market_data(
    symbols: List[str],
    start_date: str,
    end_date: str,
    frequency: str
) -> Dict[str, pd.DataFrame]:
    """
    Fetch OHLCV data for given symbols.
    Returns a dict: {symbol: DataFrame}
    """

    interval_map = {
        "daily": "1d",
        "weekly": "1wk",
        "monthly": "1mo"
    }

    interval = interval_map[frequency]

    data = {}

    for symbol in symbols:
        df = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            interval=interval,
            auto_adjust=False,
            progress=False
        )

        if df.empty:
            raise ValueError(f"No data returned for {symbol}")
        
        df = _flatten_yfinance_columns(df)

        # Ensure standard column order if present
        preferred_order = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        df = df[[c for c in preferred_order if c in df.columns]]

        data[symbol] = df

    return data
