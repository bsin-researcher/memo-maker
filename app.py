# app.py
# Memo Maker — Snapshot & T-1..T+3 Event Study
# Educational only; not investment advice.

from __future__ import annotations

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pandas.tseries.offsets import BDay
import streamlit as st
import requests  # <-- ensure requests is in requirements.txt (see bottom note)

st.set_page_config(page_title="Memo Maker — Snapshot & Event Study", page_icon="📈", layout="centered")

# ---------- Tiny global counter (CountAPI; no images) ----------
COUNT_NS  = "bsin-memo"
COUNT_KEY = "app_runs_v2"

def count_get() -> int | None:
    try:
        r = requests.get(f"https://api.countapi.xyz/get/{COUNT_NS}/{COUNT_KEY}", timeout=3)
        return int(r.json().get("value"))
    except Exception:
        return None

def count_hit() -> int | None:
    try:
        r = requests.get(f"https://api.countapi.xyz/hit/{COUNT_NS}/{COUNT_KEY}", timeout=3)
        return int(r.json().get("value"))
    except Exception:
        return None

def pill(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div style="
          display:inline-flex;gap:10px;align-items:center;
          background:#00e676; color:#111; font-weight:700;
          padding:6px 12px; border-radius:999px; margin:6px 0;">
          <span style="text-transform:uppercase; letter-spacing:.4px; font-size:12px;">{label}</span>
          <span style="font-size:14px;">{value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
# ---------------------------------------------------------------

# ---------- Data helpers ----------
def load_prices(ticker: str, start: str | datetime, end: str | datetime) -> pd.Series:
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if df.empty:
        raise ValueError(f"No price data returned for {ticker} in the requested window.")
    if isinstance(df.columns, pd.MultiIndex):
        if ('Adj Close', ticker) in df.columns:
            s = df[('Adj Close', ticker)]
        elif ('Close', ticker) in df.columns:
            s = df[('Close', ticker)]
        else:
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
            for col in ['Close', 'Adj Close', 'close', 'adjclose']:
                if col in df.columns:
                    s = df[col]; break
            else:
                raise KeyError("Neither 'Adj Close' nor 'Close' found in columns.")
    return s.dropna().astype(float)

def nearest_trading_loc(index: pd.DatetimeIndex, when: pd.Timestamp) -> int:
    pos = index.get_indexer([when], method='pad')[0]
    return 0 if pos == -1 else pos

def pct_change_from(series: pd.Series, steps_back: int) -> float | None:
    if len(series) <= steps_back: return None
    now, then = series.iloc[-1], series.iloc[-(steps_back + 1)]
    return float((now / then) - 1.0)

def snapshot_metrics(ticker: str, event_date: datetime) -> dict:
    start = event_date - timedelta(days=400)
    end   = event_date + BDay(4)
    px = load_prices(ticker, start, end)
    px_upto_event = px.loc[:event_date]
    price = float(px_upto_event.iloc[-1])
    mom_3m  = pct_change_from(px_upto_event, 63)
    mom_12m = pct_change_from(px_upto_event, 252)
    if not px_upto_event.empty:
        lookback = px_upto_event.iloc[-252:] if len(px_upto_event) >= 252 else px_upto_event
        dd_52w = float((price / lookback.max()) - 1.0)
    else:
        dd_52w = None
    return {"price": price, "mom_3m": mom_3m, "mom_12m": mom_12m, "dd_52w": dd_52w, "px": px}

def event_study_table(ticker: str, event_date: datetime) -> pd.DataFrame:
    start = event_date - BDay(3); end = event_date + BDay(4)
    s_px  = load_prices(ticker, start, end)
    spy   = load_prices("SPY", start, end)
    df = pd.DataFrame({"stock": s_px}).join(spy.rename("spy"), how="inner")
    rets = df.pct_change().dropna()
    loc = nearest_trading_loc(df.index, pd.Timestamp(event_date))
    rows = []
    def grab(pos, label):
        if 0 <= pos < len(rets):
            r = rets.iloc[pos]; rows.append([label, r["stock"], r["spy"], r["stock"] - r["spy"]])
        else:
            rows.append([label, np.nan, np.nan, np.nan])
    for off, lab in [(-1,"T-1"), (0,"T0"), (1,"T+1"), (2,"T+2"), (3,"T+3")]:
        grab(loc+off, lab)
    return pd.DataFrame(rows, columns=["Day", "Stock", "SPY", "Abnormal"])

def fmt_pct(x: float | None) -> str:
    return "—" if (x is None or pd.isna(x)) else f"{x*100:.2f}%"
# ---------- UI ----------

st.title("Memo Maker — Snapshot & T-1..T+3 Event Study")
st.caption("Educational only; not investment advice.")

# Show global runs (no increment yet)
initial_total = count_get()
pill("App runs", "unavailable" if initial_total is None else f"{initial_total:,}")

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
            for col in ["Stock", "SPY", "Abnormal"]:
                tbl[col] = tbl[col].apply(lambda v: "—" if pd.isna(v) else f"{v*100:.2f}%")
            st.table(tbl)

            # Increment AFTER a successful run and show updated total immediately
            new_total = count_hit()
            pill("App runs", "unavailable" if new_total is None else f"{new_total:,}")

st.caption("Source: yfinance. Educational use only.")
