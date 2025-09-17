# Method
_Educational only; not investment advice._

## Overview
Memo Maker scores stocks with a transparent 10-point checklist (TRP-1) and optionally runs a tiny event study (T-1..T+3) vs. SPY for context.

## TRP-1 checklist (0–10)
1. Business quality  
2. Financial quality  
3. Risk / leverage  
4. Valuation sanity  
5. Unit economics / margins  
6. Growth durability (LTM → 3y)  
7. Cash generation / FCF  
8. Competitive moat / switching costs  
9. Management & incentives  
10. Narrative consistency & evidence  

Each “yes” = 1 point. In memos, note brief support for each item.

## Event study (optional)
- Pick an event date (e.g., earnings).  
- Compute simple returns for Stock and SPY on T-1, T0, T+1, T+2, T+3.  
- Abnormal = Stock − SPY.  
- Report the table; no inference is implied.

## Reproducibility
- Data: 10-K/10-Q, transcripts, IR; prices via `yfinance`.  
- Script: `cli/evaluate_stock.py`  
- Example:
