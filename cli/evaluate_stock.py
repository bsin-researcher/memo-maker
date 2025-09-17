#!/usr/bin/env python3
"""
evaluate_stock.py  —  tiny helper for Memo Maker

Usage (from the repo root):
  python cli/evaluate_stock.py TICKER [EVENT_YYYY-MM-DD]

What it prints:
  1) SNAPSHOT  — price-based quick stats you can paste into your memo.
  2) (Optional) EVENT STUDY table T-1..T+3 vs SPY if you pass an event date.

Notes:
  • Educational use only; not investment advice.
  • Requires: yfinance, pandas, numpy  (pip install -r requirements.txt)
"""

from __future__ import annotations
import sys, math
from datetime import date, datetime, timedelta
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf


# ---------- helpers ----------

def _as_date(s: str) -> date:
    """Parse YYYY-MM-DD -> date."""
    return datetime.strptime(s, "%Y-%m-%d").date()

def _select_price_series(df: pd.DataFrame) -> pd.Series:
    """
    Return a clean price Series from a yfinance download DataFrame.
    Handles:
      - auto_adjust True/False
      - single-level vs MultiIndex columns
      - 'Adj Close' fallback to 'Close'
    """
    if df is None or df.empty:
        raise ValueError("No price data returned.")

    cols = df.columns
    # Choose which top-level field to use
    top = None
    if isinstance(cols, pd.MultiIndex):
        lvl0 = list(cols.get_level_values(0).unique())
        if "Adj Close" in lvl0:
            top = "Adj Close"
        elif "Close" in lvl0:
            top = "Close"
        else:
            top = lvl0[0]
        s = df[top]
        # If it's still a DataFrame (ticker level present), take the first column
        if isinstance(s, pd.DataFrame):
            s = s.iloc[:, 0]
        s.name = "Close"
        return s.dropna()
    else:
        if "Adj Close" in cols:
            s = df["Adj Close"].dropna()
        elif "Close" in cols:
            s = df["Close"].dropna()
        else:
            # take the first numeric column as a last resort
            first = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
            if not first:
                raise KeyError("No numeric price column found.")
            s = df[first[0]].dropna()
        s.name = "Close"
        return s

def _get_prices(ticker: str, start: date, end: date) -> pd.Series:
    """Download a price series for ticker (close/adj-close) with robust column handling."""
    # Turn off auto_adjust so our math stays consistent even if yfinance defaults change.
    df = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)
    return _select_price_series(df)

def _format_pct(x: float) -> str:
    if pd.isna(x) or not np.isfinite(x):
        return "—"
    return f"{x*100:,.1f}%"

def _format_money(x: float) -> str:
    if pd.isna(x) or not np.isfinite(x):
        return "—"
    # show billions if large
    absx = abs(x)
    if absx >= 1e9:
        return f"${x/1e9:,.1f}B"
    if absx >= 1e6:
        return f"${x/1e6:,.1f}M"
    return f"${x:,.2f}"

# ---------- snapshot (price-based) ----------

def snapshot_from_prices(px: pd.Series) -> dict:
    """
    Compute simple, price-only snapshot numbers that are stable:
      - Price (last close)
      - 3M momentum (~63 trading days)
      - 12M momentum (~252 trading days)
      - 52-week drawdown (vs trailing 252d peak)
    """
    if len(px) < 40:
        raise ValueError("Not enough price history for snapshot.")

    last = float(px.iloc[-1])
    # momentum windows (trading days)
    def ret_over(n: int) -> float:
        if len(px) <= n:
            return np.nan
        return (px.iloc[-1] / px.iloc[-1 - n]) - 1.0

    mom_3m = ret_over(63)
    mom_12m = ret_over(252)

    trail = px.tail(252) if len(px) >= 252 else px
    dd = (last / float(trail.max())) - 1.0

    return {
        "price": last,
        "mom_3m": mom_3m,
        "mom_12m": mom_12m,
        "drawdown_52w": dd,
    }

def print_snapshot(ticker: str, px: pd.Series) -> None:
    s = snapshot_from_prices(px)
    print("\nSNAPSHOT")
    print("--------")
    print(f"Ticker: {ticker}")
    print(f"Price:   {_format_money(s['price'])}")
    print(f"3M mom:  {_format_pct(s['mom_3m'])}")
    print(f"12M mom: {_format_pct(s['mom_12m'])}")
    print(f"52w DD:  {_format_pct(s['drawdown_52w'])}")

# ---------- event study ----------

def nearest_index_idx(dts: pd.DatetimeIndex, d: date) -> int:
    """Return the position of the trading day nearest to d."""
    ts = pd.to_datetime(d)
    pos = dts.get_indexer([ts], method="nearest")[0]
    return int(pos)

def event_study(px: pd.Series, spy: pd.Series, event_day: date) -> pd.DataFrame:
    """
    Build a small event-study table with daily returns (T-1..T+3)
    and abnormal = ticker_ret - spy_ret.
    """
    # Align and compute daily returns
    df = pd.DataFrame({
        "px": px,
        "spy": spy.reindex(px.index).ffill()
    }).dropna()
    rets = df.pct_change()

    # Find nearest trading day to event_day
    i0 = nearest_index_idx(df.index, event_day)

    # we want rows: T-1, T0, T+1, T+2, T+3
    rows = []
    labels = ["T-1","T0","T+1","T+2","T+3"]
    offsets = [-1, 0, 1, 2, 3]

    for lab, off in zip(labels, offsets):
        idx = i0 + off
        if 0 <= idx < len(rets):
            r_px = float(rets.iloc[idx]["px"])
            r_spy = float(rets.iloc[idx]["spy"])
            rows.append([lab, r_px, r_spy, r_px - r_spy])
        else:
            rows.append([lab, np.nan, np.nan, np.nan])

    out = pd.DataFrame(rows, columns=["Day", "Stock", "SPY", "Abnormal"])
    return out

def print_event_table(df: pd.DataFrame, ticker: str, event_day: date) -> None:
    print(f"\nEVENT STUDY — {ticker} vs SPY  (around {event_day.isoformat()})")
    print("-----------------------------------------------------------")
    print("| Day |  Stock  |   SPY   | Abnormal |")
    print("|----:|--------:|--------:|---------:|")
    for _, r in df.iterrows():
        stock = "—" if pd.isna(r["Stock"]) else f"{r['Stock']*100:,.2f}%"
        spy   = "—" if pd.isna(r["SPY"])   else f"{r['SPY']*100:,.2f}%"
        abn   = "—" if pd.isna(r["Abnormal"]) else f"{r['Abnormal']*100:,.2f}%"
        print(f"| {r['Day']:>3} | {stock:>7} | {spy:>7} | {abn:>8} |")

# ---------- main ----------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python cli/evaluate_stock.py TICKER [EVENT_YYYY-MM-DD]")
        sys.exit(2)

    ticker = sys.argv[1].upper()
    event_day: Optional[date] = None
    if len(sys.argv) >= 3:
        event_day = _as_date(sys.argv[2])

    # Pull enough history for snapshot and (optional) event window.
    today = date.today()
    start_for_snapshot = today - timedelta(days=600)   # ~2y of trading days is plenty
    end = today + timedelta(days=1)                    # include today

    # Download prices (robust to Adj Close vs Close)
    px  = _get_prices(ticker, start_for_snapshot, end)
    spy = _get_prices("SPY",   start_for_snapshot, end)

    # 1) Snapshot
    print_snapshot(ticker, px)

    # 2) Event study (optional)
    if event_day is not None:
        # sanity: fetch a little extra before/after event
        # (we already have ample history in px/spy)
        tbl = event_study(px, spy, event_day)
        print_event_table(tbl, ticker, event_day)

if __name__ == "__main__":
    main()
