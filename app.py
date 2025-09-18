import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Memo Maker — Snapshot & Event Study", layout="centered")

st.title("Memo Maker — Snapshot & T-1..T+3 Event Study")
st.caption("Educational only, not investment advice.")

ticker = st.text_input("Ticker", "HD").upper().strip()
date_str = st.text_input("Event date (YYYY-MM-DD)", datetime.today().strftime("%Y-%m-%d"))

@st.cache_data(show_spinner=False)
def load_prices(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df

def snapshot(ticker):
    end = datetime.today()
    start = end - timedelta(days=365 + 20)
    px = load_prices(ticker, start, end)["Adj Close"].dropna()
    if len(px) < 40:
        return None
    price = float(px.iloc[-1])
    mom3m = (price/px.iloc[-63]-1)*100 if len(px) > 63 else np.nan
    mom12m = (price/px.iloc[0]-1)*100
    drawdown = ((price/px.max())-1)*100
    return {
        "Price": f"${price:,.2f}",
        "3M momentum": f"{mom3m:.1f}%" if pd.notna(mom3m) else "—",
        "12M momentum": f"{mom12m:.1f}%",
        "Drawdown from 52w high": f"{drawdown:.1f}%"
    }

def event_table(ticker, event_date):
    d0 = pd.to_datetime(event_date)
    start = (d0 - timedelta(days=10)).strftime("%Y-%m-%d")
    end   = (d0 + timedelta(days=10)).strftime("%Y-%m-%d")
    s = load_prices(ticker, start, end)["Adj Close"].dropna().pct_change()
    spy = load_prices("SPY",  start, end)["Adj Close"].dropna().pct_change()
    out = []
    for k,label in [(-1,"T-1"), (0,"T0"), (1,"T+1"), (2,"T+2"), (3,"T+3")]:
        day = (d0 + timedelta(days=k)).strftime("%Y-%m-%d")
        r_s = float(s.loc[day]) if day in s.index else np.nan
        r_m = float(spy.loc[day]) if day in spy.index else np.nan
        out.append([label,
                    f"{r_s*100:.2f}%" if pd.notna(r_s) else "—",
                    f"{r_m*100:.2f}%" if pd.notna(r_m) else "—",
                    f"{(r_s-r_m)*100:.2f}%" if pd.notna(r_s) and pd.notna(r_m) else "—"])
    return pd.DataFrame(out, columns=["Day","Stock","SPY","Abnormal"])

if st.button("Run"):
    try:
        snap = snapshot(ticker)
        if not snap:
            st.error("Not enough price history to compute snapshot.")
        else:
            st.subheader("Snapshot")
            st.json(snap)
            table = event_table(ticker, date_str)
            st.subheader(f"Event study — {ticker} vs SPY")
            st.dataframe(table, use_container_width=True)
            st.caption("Method: simple close-to-close returns; abnormal = stock − SPY.")
    except Exception as e:
        st.exception(e)

st.markdown("---")
st.caption("Source: yfinance. Educational only, not investment advice.")
