# Opportunity Router Agent

Autonomous **discovery → verification → solution preparation** for sales-free public reward opportunities.

## v0.3 pipeline

```
Discovery Agent
    ↓
Safety / eligibility filter
    ↓
Reward + recency scoring
    ↓
Verification Agent
    ├─ open / archived state
    ├─ maintainer authority
    ├─ confirmed vs proposed reward
    ├─ assignees / claim signals
    └─ competition density
    ↓
VERIFIED / REVIEW / REJECT
    ↓
Solution Preparation Agent (VERIFIED only)
    ├─ acceptance-criteria extraction
    ├─ domain detection
    ├─ effort range
    ├─ success probability
    ├─ gross reward/hour
    ├─ risk-adjusted value/hour
    ├─ implementation plan
    └─ test strategy
    ↓
GitHub dashboard + JSON solution queue
    ↓
Human approval gate
```

The priority metric is not bounty size alone. The router prefers opportunities with stronger **risk-adjusted expected value per hour**.

## Outputs

- `output/latest.json` — complete scored queue.
- `output/LATEST.md` — human-readable dashboard.
- `output/solution_queue.json` — technical plans for VERIFIED opportunities only.
- GitHub Issue dashboard — continuously refreshed by the Action.

## Automation

Workflow: `.github/workflows/opportunity-router.yml`

- runs hourly,
- verifies up to 20 candidates,
- generates plans only for VERIFIED opportunities,
- publishes the ranked dashboard,
- uploads the output folder as an Actions artifact.

## Safety / approval boundary

The agent does **not** automatically claim tasks, post to third-party issues, submit PRs, accept terms, perform KYC, create payout accounts, move funds, or run security/exploit work.

## Run locally

```bash
cd opportunity-router-agent
python -m py_compile agent.py verifier.py planner.py
python test_agent.py
GITHUB_TOKEN=<token> GITHUB_REPOSITORY=owner/repo python agent.py
```

Environment variables:

```
MAX_RESULTS=25
MAX_VERIFY=20
PUBLISH_ISSUE=true
```

## Decision labels

- `PREPARE_HIGH_PRIORITY`: strong risk-adjusted value/hour.
- `PREPARE`: viable candidate for human review.
- `HOLD_COMPETITION`: reward exists but probability is too low.
- `HOLD_LOW_EV`: expected value per hour is weak.
- `HOLD_NO_CONFIRMED_REWARD`: no explicit monetary value.
