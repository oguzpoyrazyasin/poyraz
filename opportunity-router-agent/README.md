# Opportunity Router Agent

Autonomous discovery + verification for **sales-free, public reward opportunities**.

## v0.2

The pipeline now has two agents:

```
Discovery Agent
    ↓
Safety / eligibility filter
    ↓
Reward + recency scoring
    ↓
Verification Agent
    ├─ issue still open?
    ├─ repository archived?
    ├─ maintainer/owner authorship signal?
    ├─ compensation wording explicit?
    ├─ reward only proposed/tentative?
    ├─ assignee already present?
    └─ claim/work-in-progress signal in comments?
    ↓
VERIFIED / REVIEW / REJECT
    ↓
Expected-value ranking
    ↓
GitHub Issue dashboard
    ↓
Human approval gate
```

### VERIFIED
Automated public signals clear the trust threshold. This is **not a payment guarantee**.

### REVIEW
Potential opportunity, but at least one important condition still needs human confirmation.

### REJECT
Removed from the published queue.

## Safety boundary

The current release excludes security/vulnerability/exploit work. It does not automatically:
- accept bounty terms,
- claim tasks,
- submit pull requests,
- perform KYC,
- create payout accounts,
- move funds,
- or contact maintainers.

## Automation

Workflow: `.github/workflows/opportunity-router.yml`

- hourly schedule,
- manual dispatch,
- automatic push trigger,
- up to 20 deep verifications per run,
- ranked JSON/Markdown artifact,
- one continuously refreshed GitHub Issue dashboard.

## Run locally

```bash
cd opportunity-router-agent
python -m py_compile agent.py verifier.py
python test_agent.py
GITHUB_TOKEN=<token> GITHUB_REPOSITORY=owner/repo python agent.py
```

Useful environment variables:

```
MAX_RESULTS=25
MAX_VERIFY=20
PUBLISH_ISSUE=true
```

## Next gate

The next safe automation stage is **Solution Preparation**: for VERIFIED items, generate a local implementation plan, estimated effort, test strategy and expected-value calculation. Actual claiming/submission remains behind human approval.
