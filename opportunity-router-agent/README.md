# Opportunity Router Agent

Autonomous discovery, verification and solution preparation for **sales-free public reward opportunities**.

## v0.3 pipeline

```
Discovery Agent
    ↓
Safety / eligibility filter
    ↓
Verification Agent
    ↓
VERIFIED / REVIEW / REJECT
    ↓
Solution Preparation Agent
    ├─ task classification
    ├─ acceptance-criteria extraction
    ├─ effort estimate
    ├─ competition adjustment
    ├─ success-probability estimate
    ├─ expected payout
    ├─ expected value / hour
    ├─ implementation plan
    └─ test strategy
    ↓
READY_FOR_REVIEW / LOW_EV / HOLD
    ↓
Human approval gate
```

## Outputs

Every run generates:

- `output/latest.json` — ranked and verified opportunities
- `output/LATEST.md` — human-readable opportunity dashboard
- `output/solutions.json` — prepared solution economics and plans
- `output/SOLUTIONS.md` — implementation/test plan queue

The GitHub Issue dashboard is refreshed with both discovery/verification and solution-preparation output.

## Decision semantics

**VERIFIED** means the public opportunity signals passed the trust threshold. It is not a payment guarantee.

**READY_FOR_REVIEW** means a VERIFIED opportunity has explicit reward information and crosses the current expected-value/hour threshold under the heuristic model. It still requires a human decision before any external action.

**LOW_EV** means the opportunity appears real but the expected payout relative to effort/competition is weak.

**HOLD** means payout or success evidence is insufficient.

## Safety / authority boundary

The agent does not automatically:
- claim tasks,
- post comments to external repositories,
- submit pull requests,
- accept marketplace or bounty terms,
- perform KYC,
- create payout accounts,
- move funds,
- or run security/vulnerability/exploit automation.

## Automation

Workflow: `.github/workflows/opportunity-router.yml`

It runs hourly and on manual dispatch/push. GitHub Actions supplies the repository token; no third-party API key is required for the current MVP.

## Run locally

```bash
cd opportunity-router-agent
python -m py_compile agent.py verifier.py solution_preparer.py
python test_agent.py
GITHUB_TOKEN=<token> GITHUB_REPOSITORY=owner/repo python agent.py
```

Environment controls:

```
MAX_RESULTS=25
MAX_VERIFY=20
PUBLISH_ISSUE=true
```

## Next safe stage

Once the router produces a genuinely attractive `READY_FOR_REVIEW` item, the next stage can create a **local draft implementation branch** and run tests. Claiming the bounty or submitting the PR remains a separate approval step.
