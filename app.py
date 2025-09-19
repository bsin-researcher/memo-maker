# app.py
# Memo Maker — Snapshot & T-1..T+3 Event Study (Educational only; not investment advice)
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from pandas.tseries.offsets import BDay
import streamlit as st

# --- Global run counter (CountAPI) ---
import requests  # add this import

COUNT_KEY = "bsin-researcher/memo-maker/app_runs"  # you can change to any URL-safe string

def _countapi_base() -> str:
    return "https://api.countapi.xyz"

def get_run_count() -> int:
    try:
        r = requests.get(f"{_countapi_base()}/get/{COUNT_KEY}", timeout=3)
        return int(r.json().get("value", 0))
    except Exception:
        return 0

def increment_run_count() -> int | None:
    try:
        r = requests.get(f"{_countapi_base()}/hit/{COUNT_KEY}", timeout=3)
        return int(r.json().get("value"))
    except Exception:
        return None
# --------------------------------------

st.set_page_config(page_title="Memo Maker — Snapshot & Event Study", page_icon="📈", layout="centered")

# -------- Data helpers --------
def load_prices(ticker: str, start: str | datetime, end: str | datetime) -> pd.Series:
    """
    Robust loader for a single ticker.
    Works whether yfinance returns 'Adj Close' or 'Close', and with/without MultiIndex.
    """
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if df.empty:
        raise ValueError(f"No price data returned for {ticker} in the requested window.")

    # Handle both single- and multi-index columns
    if isinstance(df.columns, pd.MultiIndex):
        # yfinance uses (field, ticker) for multi-ticker; we requested one, but be safe.
        if ('Adj Close', ticker) in df.columns:
            s = df[('Adj Close', ticker)]
        elif ('Close', ticker) in df.columns:
            s = df[('Close', ticker)]
        else:
            # pick the first level named 'Adj Close' or 'Close' if ticker label differs
            if 'Adj Close' in df.columns.get_level_values(0):
                s = df.xs('Adj Close', level=0, axis=1).iloc[:, 0]
            elif 'Close' in df.columns.get_level_values(0):
                s = df.xs('Close', level=0, axis=1).iloc[:, 0]
            else:
                raise KeyError("Neither 'Adj Close' nor 'Close' found in multi-index columns.")
    else:
        if 'Adj Close' in df.columns:
            s = df['Adj Close']
        elif 'Close' in df.columns:
            s = df['Close']
        else:
            # Fallback: take the last price-like column
            for col in ['Close', 'Adj Close', 'close', 'adjclose']:
                if col in df.columns:
                    s = df[col]
                    break
            else:
                raise KeyError("Neither 'Adj Close' nor 'Close' found in columns.")
    return s.dropna().astype(float)

def nearest_trading_loc(index: pd.DatetimeIndex, when: pd.Timestamp) -> int:
    """Return positional index of the trading day at/just before `when`."""
    pos = index.get_indexer([when], method='pad')[0]
    if pos == -1:
        # if before first point, take first
        pos = 0
    return pos

def pct_change_from(series: pd.Series, steps_back: int) -> float | None:
    """Return percent change from N trading steps back to last point; None if not enough history."""
    if len(series) <= steps_back:
        return None
    now = series.iloc[-1]
    then = series.iloc[-(steps_back + 1)]
    return float((now / then) - 1.0)

def snapshot_metrics(ticker: str, event_date: datetime) -> dict:
    start = event_date - timedelta(days=400)  # enough lookback to compute 12M
    end   = event_date + BDay(4)              # include a bit after for T+1..T+3
    px = load_prices(ticker, start, end)

    # Ensure we only compute up to the event date for snapshot stats
    px_upto_event = px.loc[:event_date]
    price = float(px_upto_event.iloc[-1])

    mom_3m  = pct_change_from(px_upto_event, 63)   # ~63 trading days ~ 3 months
    mom_12m = pct_change_from(px_upto_event, 252)  # ~252 trading days ~ 12 months
    # Drawdown from 52w high up to event date
    if not px_upto_event.empty:
        peak_52w = px_upto_event.iloc[-252:].max() if len(px_upto_event) >= 252 else px_upto_event.max()
        dd_52w = float((price / peak_52w) - 1.0)
    else:
        dd_52w = None

    return {
        "price": price,
        "mom_3m": mom_3m,
        "mom_12m": mom_12m,
        "dd_52w": dd_52w,
        "px": px,  # full series (for event study window)
    }

def event_study_table(ticker: str, event_date: datetime) -> pd.DataFrame:
    # Stock series over a small window around the event
    start = event_date - BDay(3)
    end   = event_date + BDay(4)
    s_px  = load_prices(ticker, start, end)
    spy   = load_prices("SPY", start, end)

    # Align on index
    df = pd.DataFrame({"stock": s_px}).join(spy.rename("spy"), how="inner")
    rets = df.pct_change().dropna()

    # Find event loc by nearest trading day <= event_date
    loc = nearest_trading_loc(df.index, pd.Timestamp(event_date))

    # Build rows T-1, T0, T+1..T+3 (skip if out of bounds)
    rows = []
    def grab(pos: int, label: str):
        if 0 <= pos < len(rets):
            r = rets.iloc[pos]
            rows.append([label, r["stock"], r["spy"], r["stock"] - r["spy"]])
        else:
            rows.append([label, np.nan, np.nan, np.nan])

    grab(loc-1, "T-1")
    grab(loc,   "T0")
    grab(loc+1, "T+1")
    grab(loc+2, "T+2")
    grab(loc+3, "T+3")

    out = pd.DataFrame(rows, columns=["Day", "Stock", "SPY", "Abnormal"])
    # format as percents for display, but keep NaNs
    return out

def fmt_pct(x: float | None) -> str:
    if x is None or pd.isna(x):
        return "—"
    return f"{x*100:.2f}%"

# -------- UI --------
st.title("Memo Maker — Snapshot & T-1..T+3 Event Study")
st.caption("Educational only; not investment advice.")
st.caption(f"Global runs recorded: **{get_run_count()}**")


col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("Ticker", value="HD").strip().upper()
with col2:
    date_str = st.text_input("Event date (YYYY-MM-DD)", value=datetime.today().strftime("%Y-%m-%d"))

run = st.button("Run")

if run:
    try:
        event_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        st.error("Please enter the date as YYYY-MM-DD.")
    else:
        try:
            m = snapshot_metrics(ticker, event_date)
        except Exception as e:
            st.error(f"Data error: {e}")
        else:
            st.subheader("Snapshot")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Price", f"${m['price']:.2f}")
            c2.metric("3M momentum",  fmt_pct(m["mom_3m"]))
            c3.metric("12M momentum", fmt_pct(m["mom_12m"]))
            c4.metric("Drawdown from 52w high", fmt_pct(m["dd_52w"]))

            st.subheader(f"Event study — {ticker} vs SPY (around {event_date.date()})")
            tbl = event_study_table(ticker, event_date).copy()
            # pretty print as percents
            for col in ["Stock", "SPY", "Abnormal"]:
                tbl[col] = tbl[col].apply(lambda v: "—" if pd.isna(v) else f"{v*100:.2f}%")
            st.table(tbl)

st.caption("Source: yfinance. Educational use only.")
