# Token Radar Agent

Autonomous read-only scanner for new/emerging crypto tokens and broad market activity.

Pipeline: DEX Screener latest profiles and boosts -> deepest pool enrichment -> liquidity, volume, transaction, age and FDV risk model -> CoinPaprika broad-market activity -> JSON, Markdown and HTML dashboard -> GitHub Issue.

OBSERVE is an investigation status, not a buy recommendation.

Safety boundary: no seed/private-key discovery, abandoned-wallet sweeping, unauthorized claims, exploit automation, sybil farming, front-running, wash trading, custody or trading. Future wallet monitoring must be limited to addresses explicitly declared as user-owned.

Scoring model:
priority_score = signal_score * (1 - 0.72 * risk_score / 100)

Outputs:
- output/latest.json
- output/LATEST.md
- output/dashboard.html

Run:
cd token-radar-agent
python -m py_compile scanner.py
python test_scanner.py
python scanner.py

The GitHub workflow runs hourly and uploads the output as an artifact while refreshing the Token Radar issue.
