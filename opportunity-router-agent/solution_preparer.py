from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse


@dataclass
class PreparedSolution:
    title: str
    url: str
    task_type: str
    reward_estimate: float | None
    estimated_hours_min: float
    estimated_hours_max: float
    success_probability: float
    expected_payout: float | None
    expected_value_per_hour: float | None
    decision: str
    acceptance_items: list[str]
    implementation_plan: list[str]
    test_plan: list[str]
    risks: list[str]


def _parse_issue_url(url: str) -> tuple[str, int] | None:
    try:
        parts = [x for x in urlparse(url).path.split("/") if x]
        if len(parts) >= 4 and parts[2] == "issues":
            return f"{parts[0]}/{parts[1]}", int(parts[3])
    except (TypeError, ValueError):
        return None
    return None


def _classify(text: str) -> str:
    low = text.lower()
    if any(x in low for x in ("documentation", "docs", "readme", "guide", "translation")):
        return "documentation"
    if any(x in low for x in ("workflow", "n8n", "automation", "cron", "github action")):
        return "automation"
    if any(x in low for x in ("test", "pytest", "unit test", "integration test", "coverage")):
        return "testing"
    if any(x in low for x in ("frontend", "react", "next.js", "ui", "component")):
        return "frontend"
    if any(x in low for x in ("api", "backend", "server", "endpoint", "database", "sql")):
        return "backend"
    if any(x in low for x in ("dataset", "data", "csv", "parser", "etl")):
        return "data"
    return "general"


def _acceptance_items(body: str) -> list[str]:
    items = []
    for line in body.splitlines():
        stripped = line.strip()
        if re.match(r"^[-*]\s*\[[ xX]\]\s+", stripped):
            items.append(re.sub(r"^[-*]\s*\[[ xX]\]\s+", "", stripped))
    return items[:12]


def _estimate_hours(task_type: str, body: str, acceptance_count: int) -> tuple[float, float]:
    base = {
        "documentation": (1.0, 3.0),
        "automation": (3.0, 8.0),
        "testing": (2.0, 6.0),
        "frontend": (4.0, 10.0),
        "backend": (4.0, 12.0),
        "data": (3.0, 9.0),
        "general": (3.0, 8.0),
    }[task_type]

    complexity = 0.0
    low = body.lower()
    complexity += min(4.0, acceptance_count * 0.35)
    if any(x in low for x in ("integration", "multiple", "production-ready", "migration", "authentication")):
        complexity += 1.5
    if any(x in low for x in ("screenshot", "real instance", "benchmark", "e2e")):
        complexity += 1.0
    return round(base[0] + complexity * 0.35, 1), round(base[1] + complexity, 1)


def _success_probability(verification_score: int, comments: int, reward: float | None) -> float:
    verification_factor = max(0.35, min(0.95, verification_score / 100))
    if comments <= 3:
        competition = 0.90
    elif comments <= 10:
        competition = 0.78
    elif comments <= 30:
        competition = 0.62
    elif comments <= 100:
        competition = 0.42
    else:
        competition = 0.18

    payout_factor = 1.0 if reward else 0.65
    probability = 0.82 * verification_factor * competition * payout_factor
    return round(max(0.03, min(0.85, probability)), 3)


def _implementation_plan(task_type: str, acceptance: list[str]) -> list[str]:
    common = [
        "Reproduce the requested behavior on a clean branch/fork.",
        "Map every acceptance criterion to one concrete implementation or evidence item.",
    ]
    specific = {
        "documentation": [
            "Draft the requested documentation using the repository's existing terminology and structure.",
            "Validate commands, links and examples against the current codebase.",
        ],
        "automation": [
            "Model the workflow inputs, triggers, credentials and failure paths before implementation.",
            "Build the smallest importable/runnable workflow that satisfies all required integrations.",
        ],
        "testing": [
            "Create a failing regression test that captures the requested behavior.",
            "Implement the smallest change needed to make the targeted test suite pass.",
        ],
        "frontend": [
            "Identify the affected components, data flow and UI states.",
            "Implement the smallest component-level change with loading/error/empty-state handling.",
        ],
        "backend": [
            "Trace the affected API/data path and define the contract before modifying behavior.",
            "Implement the change with explicit validation, error handling and backward compatibility checks.",
        ],
        "data": [
            "Define input/output schemas and edge cases before implementation.",
            "Implement deterministic parsing/transformation with fixture-based validation.",
        ],
        "general": [
            "Inspect the repository conventions and identify the minimal change surface.",
            "Implement acceptance criteria in isolated commits with reproducible evidence.",
        ],
    }[task_type]
    tail = ["Prepare a concise PR description with evidence for each acceptance criterion."]
    if acceptance:
        tail.insert(0, f"Track {len(acceptance)} explicit acceptance criteria as a completion checklist.")
    return common + specific + tail


def _test_plan(task_type: str, acceptance: list[str]) -> list[str]:
    tests = [
        "Run the repository's existing formatter/linter/test commands that cover the changed area.",
        "Add or capture a reproducible verification artifact for each material acceptance criterion.",
    ]
    if task_type == "documentation":
        tests.append("Verify every command/example on a clean environment where practical.")
    elif task_type == "automation":
        tests.append("Execute one happy-path run and at least one controlled failure-path run.")
    elif task_type in {"backend", "data", "testing"}:
        tests.append("Add regression coverage for normal, boundary and failure cases.")
    elif task_type == "frontend":
        tests.append("Verify primary UI state plus error/empty/loading states.")
    if acceptance:
        tests.append("Attach acceptance-criteria-to-evidence mapping in the draft PR.")
    return tests


def prepare_solutions(
    opportunities: list[dict[str, Any]],
    token: str | None,
    request_fn: Callable[[str, str, str | None, dict[str, Any] | None], Any],
) -> list[PreparedSolution]:
    prepared: list[PreparedSolution] = []

    for op in opportunities:
        if op.get("verification_status") != "VERIFIED":
            continue

        parsed = _parse_issue_url(str(op.get("url") or ""))
        if not parsed:
            continue
        repo, issue_number = parsed

        try:
            issue = request_fn("GET", f"/repos/{repo}/issues/{issue_number}", token, None)
        except Exception:
            continue

        title = str(issue.get("title") or op.get("title") or "")
        body = str(issue.get("body") or "")
        comments = int(issue.get("comments") or op.get("comments") or 0)
        reward = op.get("reward_estimate")
        verification_score = int(op.get("verification_score") or 0)

        task_type = _classify(f"{title}\n{body}")
        acceptance = _acceptance_items(body)
        min_h, max_h = _estimate_hours(task_type, body, len(acceptance))
        probability = _success_probability(verification_score, comments, reward)
        midpoint = (min_h + max_h) / 2.0
        expected_payout = round(float(reward) * probability, 2) if reward else None
        evph = round(expected_payout / midpoint, 2) if expected_payout is not None and midpoint > 0 else None

        risks = list(op.get("risks") or [])
        if comments > 30:
            risks.append(f"high visible competition ({comments} comments)")
        if reward is None:
            risks.append("no explicit reward amount")
        if max_h >= 10:
            risks.append("high implementation effort")

        if reward is None:
            decision = "HOLD"
        elif probability < 0.15:
            decision = "HOLD"
        elif evph is not None and evph >= 12:
            decision = "READY_FOR_REVIEW"
        else:
            decision = "LOW_EV"

        prepared.append(
            PreparedSolution(
                title=title,
                url=str(op.get("url") or ""),
                task_type=task_type,
                reward_estimate=reward,
                estimated_hours_min=min_h,
                estimated_hours_max=max_h,
                success_probability=probability,
                expected_payout=expected_payout,
                expected_value_per_hour=evph,
                decision=decision,
                acceptance_items=acceptance,
                implementation_plan=_implementation_plan(task_type, acceptance),
                test_plan=_test_plan(task_type, acceptance),
                risks=risks[:8],
            )
        )

    prepared.sort(
        key=lambda x: (
            x.decision == "READY_FOR_REVIEW",
            x.expected_value_per_hour or 0,
            x.expected_payout or 0,
        ),
        reverse=True,
    )
    return prepared


def render_solutions_markdown(prepared: list[PreparedSolution]) -> str:
    lines = [
        "# Solution Preparation Queue",
        "",
        "Only VERIFIED opportunities enter this stage. Figures are heuristic estimates, not guarantees.",
        "",
        "| Decision | Reward | Success est. | Effort | Expected payout | EV/hour | Opportunity |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    if not prepared:
        lines.append("| — | — | — | — | — | — | No VERIFIED opportunities currently available |")

    for p in prepared:
        reward = f"{p.reward_estimate:,.0f}" if p.reward_estimate is not None else "—"
        payout = f"{p.expected_payout:,.2f}" if p.expected_payout is not None else "—"
        evph = f"{p.expected_value_per_hour:,.2f}" if p.expected_value_per_hour is not None else "—"
        title = p.title.replace("|", "\\|")
        lines.append(
            f"| {p.decision} | {reward} | {p.success_probability:.1%} | "
            f"{p.estimated_hours_min}-{p.estimated_hours_max}h | {payout} | {evph} | [{title}]({p.url}) |"
        )

    for idx, p in enumerate(prepared, start=1):
        lines += [
            "",
            f"## {idx}. {p.title}",
            "",
            f"**Decision:** {p.decision}  ",
            f"**Task type:** {p.task_type}  ",
            f"**Estimated effort:** {p.estimated_hours_min}-{p.estimated_hours_max} hours  ",
            f"**Estimated success probability:** {p.success_probability:.1%}",
            "",
            "### Implementation plan",
            "",
        ]
        lines.extend(f"- {x}" for x in p.implementation_plan)
        lines += ["", "### Test plan", ""]
        lines.extend(f"- {x}" for x in p.test_plan)
        if p.risks:
            lines += ["", "### Risks", ""]
            lines.extend(f"- {x}" for x in p.risks)

    lines += [
        "",
        "## Human approval gate",
        "",
        "READY_FOR_REVIEW means the opportunity is economically worth a manual decision under the current heuristic. The agent does not claim tasks, contact maintainers, submit PRs, accept terms, perform KYC or move funds automatically.",
    ]
    return "\n".join(lines) + "\n"


def write_solution_reports(prepared: list[PreparedSolution], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "solutions.json"
    md_path = output_dir / "SOLUTIONS.md"
    json_path.write_text(
        json.dumps([asdict(x) for x in prepared], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    md_path.write_text(render_solutions_markdown(prepared), encoding="utf-8")
    return json_path, md_path
