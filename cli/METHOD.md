# TRP-1: Transparent Research Protocol (v0.1)

**Goal:** fast, reproducible screen for quality + discipline. The tool produces
(1) a snapshot of fundamentals, (2) a 10-point score, and (3) an optional T−1..T+3
event study vs. SPY.

## Metrics (TTM where possible)
- Gross margin, Operating margin, FCF margin (≈ OCF − CapEx)
- Price/Sales
- Net cash (cash − total debt)
- 6-month momentum; drawdown from 52-week high

## Score (10 points total)
- Gross margin ≥ 40% (2)
- Operating margin ≥ 10% (2)
- FCF margin ≥ 5% (2)
- 6-month momentum > 0 (2)
- Drawdown < 25% (2)
- Price/Sales ≤ 15× (2)
**Bands:** 8–10 Green, 5–7 Yellow, 0–4 Red

## Event study
Window T−1..T+3 daily returns; abnormal = stock − SPY; cumulated over window.

## Limits
Rough accounting mapping; no sector normalization; P/S cutoff coarse;
yfinance data quality varies. This is a teaching tool, not advice.
