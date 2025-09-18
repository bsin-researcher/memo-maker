# memo-maker

Open-source student equity-research toolkit (educational only).

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
- **Submit a memo:** https://github.com/bsin-researcher/memo-maker/issues/new?template=memo-submission.yml
- [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge.svg)](https://memo-maker-dq25seipc3m8rrmpap7dlmb.streamlit.app)



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
