# Educational only; not investment advice.
# Minimal evaluator + event-study using yfinance.
import sys, os, datetime as dt
import numpy as np, pandas as pd

def pick_price(df):
    """Return a price series from common yfinance column names."""
    for c in ("Adj Close", "Close", "adjclose", "close"):
        if c in df.columns:
            return df[c].astype(float)
    raise KeyError(f"No price column found. Columns: {list(df.columns)}")


try:
    import yfinance as yf
except Exception:
    raise SystemExit("Install yfinance: pip install yfinance")

def ttm_sum(df: pd.DataFrame, key: str) -> float | None:
    if df is None or df.empty or key not in df.index: return None
    vals = df.loc[key].dropna().astype(float)
    if vals.empty: return None
    # prefer last 4 quarterly points if available
    return float(vals.iloc[:4].sum()) if len(vals) >= 4 else float(vals.iloc[0])

def fetch_financials(t: yf.Ticker):
    pick = lambda q, a: q if (q is not None and not q.empty) else (a if a is not None else pd.DataFrame())
    return (
        pick(getattr(t, "quarterly_income_stmt", None), getattr(t, "income_stmt", None)),
        pick(getattr(t, "quarterly_cashflow", None),     getattr(t, "cashflow", None)),
        pick(getattr(t, "quarterly_balance_sheet", None),getattr(t, "balance_sheet", None))
    )

def metrics(ticker: str, months_for_mom: int = 6) -> dict:
    t = yf.Ticker(ticker)
    fast = getattr(t, "fast_info", {}) or {}
    price, mcap = fast.get("last_price"), fast.get("market_cap")
    IS, CF, BS = fetch_financials(t)

    rev_ttm   = ttm_sum(IS, "Total Revenue")
    gross_ttm = ttm_sum(IS, "Gross Profit")
    op_ttm    = ttm_sum(IS, "Operating Income")

    fcf_ttm = None
    if CF is not None and not CF.empty:
        ocf   = ttm_sum(CF, "Operating Cash Flow")
        capex = ttm_sum(CF, "Capital Expenditure")
        if ocf is not None and capex is not None: fcf_ttm = float(ocf - abs(capex))

    def r(a,b): return None if (a is None or b in (None,0)) else float(a)/float(b)
    gross_margin = r(gross_ttm, rev_ttm)
    op_margin    = r(op_ttm, rev_ttm)
    fcf_margin   = r(fcf_ttm, rev_ttm)
    ps_ratio     = r(mcap, rev_ttm)

    net_cash = None
    if BS is not None and not BS.empty:
        cash = BS.loc["Cash And Cash Equivalents", :].dropna().astype(float) if "Cash And Cash Equivalents" in BS.index else pd.Series(dtype=float)
        debt = BS.loc["Total Debt", :].dropna().astype(float) if "Total Debt" in BS.index else pd.Series(dtype=float)
        if not cash.empty: net_cash = float(cash.iloc[0]) - (float(debt.iloc[0]) if not debt.empty else 0.0)

    end = dt.date.today(); start = end - dt.timedelta(days=365)
    px  = yf.download(ticker, start=start, end=end, progress=False)["Adj Close"].dropna()
    mom = float(px.iloc[-1] / px.iloc[max(0,len(px)-int(21*months_for_mom))] - 1) if len(px)>0 else None
    dd  = float(px.iloc[-1]/float(px.max()) - 1) if len(px)>0 else None

    return {"price":price,"market_cap":mcap,"rev_ttm":rev_ttm,
            "gross_margin":gross_margin,"op_margin":op_margin,"fcf_margin":fcf_margin,
            "ps_ratio":ps_ratio,"net_cash":net_cash,"mom_6m":mom,"dd_from_52w_high":dd}

def event_study(ticker: str, event_date: str, pre=1, post=3) -> pd.DataFrame:
    ed = pd.to_datetime(event_date)
    start = (ed - pd.tseries.offsets.BDay(pre + 5)).date()
    end   = (ed + pd.tseries.offsets.BDay(post + 5)).date()
    px = yf.download(ticker, start=start, end=end, progress=False)["Adj Close"].rename("stock").to_frame()
    spy = yf.download("SPY",   start=start, end=end, progress=False)["Adj Close"].rename("spy").to_frame()
    df = px.join(spy, how="inner").pct_change().dropna()
    df["abnormal"] = df["stock"] - df["spy"]
    idx = df.index; t0 = next((i for i,d in enumerate(idx) if d >= ed), len(idx)-1)
    lo, hi = max(0,t0-pre), min(len(idx)-1, t0+post)
    win = df.iloc[lo:hi+1].copy(); win["day"] = range(-pre, -pre + len(win)); win["cum_abnormal"] = win["abnormal"].cumsum()
    return win[["day","stock","spy","abnormal","cum_abnormal"]]

def scorecard(m: dict) -> tuple[int,list[str]]:
    pts, notes = 0, []
    def chk(cond, text, w=2): 
        nonlocal pts; (pts:=pts+w) if cond else None; notes.append(("✓ " if cond else "✗ ")+text)
    chk(m.get("gross_margin",0) is not None and m["gross_margin"] >= 0.40, "Gross margin ≥ 40%")
    chk(m.get("op_margin",0)    is not None and m["op_margin"]    >= 0.10, "Operating margin ≥ 10%")
    chk(m.get("fcf_margin",0)   is not None and m["fcf_margin"]   >= 0.05, "FCF margin ≥ 5%")
    chk(m.get("mom_6m",0)       is not None and m["mom_6m"]        > 0,    "6-month momentum > 0")
    chk(m.get("dd_from_52w_high") is not None and m["dd_from_52w_high"] > -0.25, "Drawdown < 25%")
    chk(m.get("ps_ratio")       is not None and m["ps_ratio"]     <= 15,   "Price/Sales ≤ 15×")
    return pts, notes

def as_md(ticker: str, m: dict, pts: int, notes: list[str], evt: pd.DataFrame|None, event_date: str|None):
    today = dt.date.today().isoformat()
    def fmt(x,pct=False): 
        if x is None: return "n/a"
        return f"{x*100:,.1f}%" if pct else f"{x:,.2f}" if isinstance(x,(int,float)) else str(x)
    md = [f"# {ticker} — Evaluation ({today})",
          "_Educational only; not investment advice._","",
          "## Snapshot",
          f"- Price: {fmt(m.get('price'))}",
          f"- Market cap: {fmt(m.get('market_cap'))}",
          f"- TTM revenue: {fmt(m.get('rev_ttm'))}",
          f"- Gross margin: {fmt(m.get('gross_margin'),True)}",
          f"- Operating margin: {fmt(m.get('op_margin'),True)}",
          f"- FCF margin: {fmt(m.get('fcf_margin'),True)}",
          f"- Price/Sales: {fmt(m.get('ps_ratio'))}",
          f"- Net cash (cash–debt): {fmt(m.get('net_cash'))}",
          f"- 6M momentum: {fmt(m.get('mom_6m'),True)}",
          f"- Drawdown from 52w high: {fmt(m.get('dd_from_52w_high'),True)}","",
          "## Scorecard (10 pts max)"]
    md += [f"- {n}" for n in notes]
    md += [f"", f"**Score:** {pts}/10 → Green (8–10) / Yellow (5–7) / Red (0–4)", ""]
    if evt is not None and not evt.empty:
        md += ["## Event study (abnormal vs. SPY)",
               "| Day | Stock r | SPY r | Abnormal | Cum Abnormal |",
               "|---:|---:|---:|---:|---:|"]
        for _,r in evt.iterrows():
            md.append(f"| {int(r['day'])} | {r['stock']*100:,.2f}% | {r['spy']*100:,.2f}% | {r['abnormal']*100:,.2f}% | {r['cum_abnormal']*100:,.2f}% |")
        md += [f"", f"_Window: T−1..T+3 around {event_date}_", ""]
    md += ["## Notes & sources","- Company 10-K/10-Q, earnings release, investor deck"]
    return "\n".join(md)

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli/evaluate_stock.py TICKER [EVENT_YYYY-MM-DD]"); raise SystemExit(1)
    ticker = sys.argv[1].upper(); event_date = sys.argv[2] if len(sys.argv) >= 3 else None
    m = metrics(ticker); pts, notes = scorecard(m)
    evt = event_study(ticker, event_date) if event_date else None
    os.makedirs("memos", exist_ok=True)
    fname = f"memos/{ticker}_{dt.datetime.now().strftime('%Y-%m-%d_%H%M')}.md"
    with open(fname, "w", encoding="utf-8") as f: f.write(as_md(ticker, m, pts, notes, evt, event_date))
    print(f"Saved {fname}")

if __name__ == "__main__": main()

