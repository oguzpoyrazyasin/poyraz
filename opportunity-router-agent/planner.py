from __future__ import annotations

import math
import re
from dataclasses import dataclass, asdict
from typing import Any

CHECKBOX_RE = re.compile(r"^\s*[-*]\s*\[[ xX]\]\s+(.+)$", re.MULTILINE)
CODE_HINTS = {
    "python": ("python", ".py", "pytest", "pip"),
    "javascript": ("javascript", "typescript", "node", "npm", "next.js", "react", ".ts", ".js"),
    "workflow": ("n8n", "workflow", "automation", "cron"),
    "docs": ("documentation", "docs", "readme", "guide", "translation", "quickstart"),
    "api": ("api", "endpoint", "http", "rest", "graphql"),
    "database": ("sqlite", "postgres", "mysql", "database", "migration", "sql"),
}

@dataclass
class SolutionPlan:
    estimated_hours_low: float
    estimated_hours_high: float
    expected_hours: float
    success_probability: float
    reward_estimate: float | None
    gross_per_hour: float | None
    risk_adjusted_value: float | None
    risk_adjusted_per_hour: float | None
    acceptance_criteria_count: int
    detected_domains: list[str]
    implementation_steps: list[str]
    test_strategy: list[str]
    action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _acceptance_criteria(body: str) -> list[str]:
    items = [x.strip() for x in CHECKBOX_RE.findall(body or "")]
    return items[:25]


def _domains(text: str) -> list[str]:
    low = text.lower()
    found: list[str] = []
    for domain, hints in CODE_HINTS.items():
        if any(hint in low for hint in hints):
            found.append(domain)
    return found or ["general"]


def _effort_hours(body: str, domains: list[str], criteria_count: int) -> tuple[float, float]:
    text = body or ""
    base = 0.75
    base += min(4.0, len(text) / 3500.0)
    base += min(4.0, criteria_count * 0.35)

    complexity = 0.0
    if "api" in domains:
        complexity += 0.75
    if "database" in domains:
        complexity += 1.0
    if "workflow" in domains:
        complexity += 0.75
    if "javascript" in domains or "python" in domains:
        complexity += 0.5
    if "docs" in domains and len(domains) == 1:
        complexity -= 0.4

    low = max(0.5, base + complexity)
    high = max(low + 0.5, low * 1.9)
    return round(low, 1), round(high, 1)


def _success_probability(verification_score: int, comments: int, assignees: int) -> float:
    p = max(0.05, min(0.9, verification_score / 100.0))
    if comments >= 200:
        p *= 0.12
    elif comments >= 100:
        p *= 0.2
    elif comments >= 50:
        p *= 0.35
    elif comments >= 20:
        p *= 0.55
    elif comments >= 10:
        p *= 0.72
    elif comments >= 5:
        p *= 0.85
    if assignees:
        p *= 0.45
    return round(max(0.02, min(0.9, p)), 2)


def _steps(domains: list[str], criteria: list[str]) -> list[str]:
    steps = [
        "Reproduce the requested behavior in a clean local environment.",
        "Map each acceptance criterion to one implementation or verification task.",
    ]
    if "api" in domains:
        steps.append("Trace API contracts, error paths and request/response fixtures before changing behavior.")
    if "database" in domains:
        steps.append("Define schema/migration impact and add a reversible local migration path.")
    if "workflow" in domains:
        steps.append("Build the workflow with configurable inputs and an exportable/reproducible artifact.")
    if "docs" in domains:
        steps.append("Preserve code samples/commands exactly and validate all documented steps end to end.")
    steps += [
        "Implement the smallest change set that satisfies the acceptance criteria.",
        "Run automated checks plus one real-world smoke test.",
        "Prepare a concise PR description with evidence mapped to the acceptance criteria.",
    ]
    return steps[:8]


def _tests(domains: list[str], criteria: list[str]) -> list[str]:
    tests = ["Run the repository's existing test/lint/build commands before and after the change."]
    if "python" in domains:
        tests.append("Add or run targeted pytest/unit coverage for the changed behavior.")
    if "javascript" in domains:
        tests.append("Run package tests, type-check and lint; add a focused regression test where practical.")
    if "api" in domains:
        tests.append("Verify happy path, invalid input and upstream/network failure behavior with fixtures or mocks.")
    if "database" in domains:
        tests.append("Test migration on a fresh database and an existing database snapshot.")
    if "workflow" in domains:
        tests.append("Execute the workflow end to end with non-secret test credentials and capture reproducible evidence.")
    if "docs" in domains:
        tests.append("Execute every documented command/link/sample from a clean checkout.")
    if criteria:
        tests.append("Produce an acceptance matrix showing evidence for each checklist item.")
    return tests[:7]


def prepare_plan(
    issue: dict[str, Any],
    verification_score: int,
    reward_estimate: float | None,
) -> SolutionPlan:
    title = str(issue.get("title") or "")
    body = str(issue.get("body") or "")
    text = f"{title}\n{body}"
    criteria = _acceptance_criteria(body)
    domains = _domains(text)
    low, high = _effort_hours(body, domains, len(criteria))
    expected = round((low + high) / 2.0, 1)

    comments = int(issue.get("comments") or 0)
    assignees = len(issue.get("assignees") or [])
    probability = _success_probability(verification_score, comments, assignees)

    gross_per_hour = None
    risk_adjusted_value = None
    risk_adjusted_per_hour = None
    if reward_estimate is not None and expected > 0:
        gross_per_hour = round(reward_estimate / expected, 2)
        risk_adjusted_value = round(reward_estimate * probability, 2)
        risk_adjusted_per_hour = round(risk_adjusted_value / expected, 2)

    if reward_estimate is None:
        action = "HOLD_NO_CONFIRMED_REWARD"
    elif probability < 0.2:
        action = "HOLD_COMPETITION"
    elif risk_adjusted_per_hour is not None and risk_adjusted_per_hour >= 25:
        action = "PREPARE_HIGH_PRIORITY"
    elif risk_adjusted_per_hour is not None and risk_adjusted_per_hour >= 10:
        action = "PREPARE"
    else:
        action = "HOLD_LOW_EV"

    return SolutionPlan(
        estimated_hours_low=low,
        estimated_hours_high=high,
        expected_hours=expected,
        success_probability=probability,
        reward_estimate=reward_estimate,
        gross_per_hour=gross_per_hour,
        risk_adjusted_value=risk_adjusted_value,
        risk_adjusted_per_hour=risk_adjusted_per_hour,
        acceptance_criteria_count=len(criteria),
        detected_domains=domains,
        implementation_steps=_steps(domains, criteria),
        test_strategy=_tests(domains, criteria),
        action=action,
    )
