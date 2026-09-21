# Opportunity Router Agent

An autonomous discovery agent for **sales-free, public reward opportunities**.

## What v0.1 does

- Scans public GitHub issues for explicit bounty / reward / paid-work signals.
- Excludes security, vulnerability and exploit-oriented opportunities in this first release.
- Deduplicates and ranks opportunities using explicit reward signals, recency, poster relationship to the repository, labels and visible contention.
- Publishes the latest ranked shortlist into a single GitHub Issue.
- Runs hourly with GitHub Actions and can also be started manually.
- Requires no external API key for the MVP; GitHub Actions supplies `GITHUB_TOKEN`.

## What it deliberately does not do

It does not automatically accept work, submit pull requests, agree to terms, create payout accounts, perform KYC, move funds, or run vulnerability/exploit automation. Those steps remain behind a human approval gate.

## Agent loop

```
GitHub public issue search
        ↓
Eligibility + safety filter
        ↓
Reward extraction
        ↓
Expected-value heuristic
        ↓
Deduplication + ranking
        ↓
Latest Opportunity Router GitHub Issue
        ↓
Human approval
```

## Run locally

```bash
cd opportunity-router-agent
python test_agent.py
GITHUB_TOKEN=<token> GITHUB_REPOSITORY=owner/repo python agent.py
```

Without `GITHUB_TOKEN`, the scanner can still use public GitHub search subject to lower rate limits and will write results to `output/`.

## Automation

Workflow: `.github/workflows/opportunity-router.yml`

- Schedule: once per hour.
- Trigger: manual dispatch or changes to the agent.
- Output: `opportunity-router-report` Actions artifact.
- Dashboard: one continuously updated Issue titled **[Opportunity Router] Latest ranked opportunities**.

## Next modules

The architecture is intentionally modular. After validating signal quality, the next integrations should be official/authorized feeds for OSS bounty platforms, public innovation challenges, data/ML competitions and grant programs. Each source should have its own eligibility, KYC, ToS and payout checks before it is allowed into the router.

## Important

A discovered reward is not guaranteed income. Every opportunity must be checked against current terms, eligibility, ownership, payment/KYC/tax rules and whether another contributor has already claimed the work.
