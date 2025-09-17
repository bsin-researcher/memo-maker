# memo-maker

[![Site](https://img.shields.io/badge/site-live-brightgreen)](https://bsin-researcher.github.io/memo-maker/)

**What it is:** Transparent, reproducible equity-research kit (student project).  
**Outputs:** 1-page memos + T−1..T+3 event study _(educational only)_.

## Quickstart
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# examples (dates = memo date)
python cli/evaluate_stock.py CRWD 2025-09-16
python cli/evaluate_stock.py HD   2025-09-16
