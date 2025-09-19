# memo-maker

Open-source student equity-research toolkit (educational only).

[![Release](https://img.shields.io/github/v/release/bsin-researcher/memo-maker?sort=semver)](https://github.com/bsin-researcher/memo-maker/releases)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://bsin-researcher.github.io/memo-maker/app)

**Links:**  
- **Live App:** https://bsin-researcher.github.io/memo-maker/app  
- **Docs site:** https://bsin-researcher.github.io/memo-maker/  
- **Releases:** https://github.com/bsin-researcher/memo-maker/releases  
- **Submit a memo (web form):** https://github.com/bsin-researcher/memo-maker/issues/new/choose

**Project metrics (update weekly):**  
- Memos published: **8**  
- Latest release: **v0.3.0**  
- CI: **Passing**  

### Join the Memo Challenge
No installs needed. Copy `memos/_TEMPLATE.md`, create `memos/TICKER_YYYY-MM-DD.md`, and open a PR — or submit via **Issues → Memo submission**.


![CI](https://github.com/bsin-researcher/memo-maker/actions/workflows/ci.yml/badge.svg)


- Generates 1-page memos and an optional T-1..T+3 event study
- Transparent, reproducible scoring with a 10-point checklist (TRP-1)
- Python CLI + simple Markdown outputs

**Website (GitHub Pages):** https://bsin-researcher.github.io/memo-maker/

## Links

- **All memos:** [memos/](memos/)
- **Latest example memos:** [HD_2025-09-16](memos/HD_2025-09-16.md) · [CRWD_2025-09-16](memos/CRWD_2025-09-16.md)
- **Method:** [METHOD](docs/METHOD.md)
- **Performance log:** [performance report](studies/performance.md)
- **Public trades CSV:** [trades/trades.csv](trades/trades.csv)
- *Try the app:** [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://memo-maker-dgz58pjc3m8frnappj7dlmb.streamlit.app/)
- [![Release](https://img.shields.io/github/v/release/bsin-researcher/memo-maker?sort=semver)](https://github.com/bsin-researcher/memo-maker/releases)







## Quickstart

> Educational only; not investment advice.

```bash
# 1) Clone + enter the repo
git clone https://github.com/bsin-researcher/memo-maker.git
cd memo-maker

# 2) Create/activate Python env and install deps
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3) Run example evaluations (paste outputs into /memos/*.md)
python cli/evaluate_stock.py CRWD 2025-09-16
python cli/evaluate_stock.py HD   2025-09-16
