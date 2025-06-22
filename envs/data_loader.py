# envs/data_loader.py
import yfinance as yf
import numpy as np
import pandas as pd
from typing import List, Tuple

def fetch_price_data(
    tickers: List[str],
    start: str = "2020-01-01",
    end: str | None = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Downloads price data for given tickers and returns:
      - prices: np.ndarray shape (T, N)
      - dates: np.ndarray of datetime64 shape (T,)
    """
    # 1) Download all fields
    df = yf.download(tickers, start=start, end=end or None, progress=False)

    # 2) Try to extract Adjusted Close
    if isinstance(df.columns, pd.MultiIndex):
        # Multi-ticker: first level = field name
        if "Adj Close" in df.columns.levels[0]:
            adj = df["Adj Close"]
        elif "Close" in df.columns.levels[0]:
            adj = df["Close"]
        else:
            raise KeyError("Neither 'Adj Close' nor 'Close' found in data")
    else:
        # Single-ticker: flat columns
        if "Adj Close" in df.columns:
            adj = df["Adj Close"]
        elif "Close" in df.columns:
            adj = df["Close"]
        else:
            raise KeyError("Neither 'Adj Close' nor 'Close' found in data")

    # 3) Ensure DataFrame shape (T, N)
    if isinstance(adj, pd.Series):
        adj = adj.to_frame(name=tickers[0])

    # 4) Drop any rows with NaNs
    adj = adj.dropna(how="any")

    # 5) Return numpy arrays
    prices = adj.values           # shape (T, N)
    dates  = adj.index.to_numpy() # shape (T,)
    return prices, dates
