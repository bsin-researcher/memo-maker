# memo-maker

[![Site](https://img.shields.io/badge/site-live-brightgreen)](https://bsin-researcher.github.io/memo-maker/)

**What it is:** Transparent, reproducible equity-research kit (student project).  
**Outputs:** 1-page memos + T−1..T+3 event study _(educational only)_.

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

