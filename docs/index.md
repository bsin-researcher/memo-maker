# Memo Maker — Open-Source Equity Research Lab
_Reproducible 1-page memos with a Snapshot and T-1..T+3 event study (educational only)._

<!-- Hero buttons -->
<p>
  <a href="/memo-maker/app"><b>▶︎ Open the App</b></a> ·
  <a href="https://YOUR_YOUTUBE_DEMO_URL_HERE">Demo (90s)</a> ·
  <a href="./memos/HD_2025-09-16.md">Latest memo</a>
</p>

[![Release](https://img.shields.io/github/v/release/bsin-researcher/memo-maker?sort=semver)](https://github.com/bsin-researcher/memo-maker/releases)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://bsin-researcher.github.io/memo-maker/app)

---

## What this does
1. **Generate a Snapshot** — price, 3M/12M momentum, 52-week drawdown.  
2. **Build an event study** — T-1..T+3 vs SPY with abnormal returns.  
3. **Export & publish** — CSV download + copy-to-memo template for reproducible analysis.

> **Educational only; not investment advice.**

---

## Project metrics
_(Update these numbers weekly — they’re for admissions “at-a-glance.”)_
- Memos published: **8**  
- Latest release: **v0.3.0**  
- CI: **Passing**  
- App features: **Batch analysis · CSV export · T0 leaderboard**

---

## Memo Gallery
These examples use event dates ≥3 trading days old so T+ rows are filled.
- [HD — 2025-09-16](./memos/HD_2025-09-16.md)
- [CRWD — 2025-09-16](./memos/CRWD_2025-09-16.md)
<!-- Add more as you publish:
- [AAPL — 2025-08-01](./memos/AAPL_2025-08-01.md)
- [MSFT — 2025-07-24](./memos/MSFT_2025-07-24.md)
- [NVDA — 2025-08-29](./memos/NVDA_2025-08-29.md)
- [AMZN — 2025-08-01](./memos/AMZN_2025-08-01.md)
-->

---

## How to contribute (no installs)
- **Write a memo:** open the template in `memos/_TEMPLATE.md`, copy it, then submit via our web form.  
- **Submit:** [New memo via Issue form](https://github.com/bsin-researcher/memo-maker/issues/new/choose)  
- We’ll review, add Snapshot/T-window if needed, and credit you on the memo.

---

## Method & Performance
- **Method:** how the Snapshot and event study are computed → [METHOD](./METHOD.html)  
- **Performance:** running notes & results → [Performance log](./studies/performance.md)

---

## Links
- **Repository:** https://github.com/bsin-researcher/memo-maker  
- **Releases:** https://github.com/bsin-researcher/memo-maker/releases  
- **Open the App:** [/memo-maker/app](/memo-maker/app)
