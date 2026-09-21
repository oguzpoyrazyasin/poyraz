from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

CLAIM_PATTERNS = [
    r"\bclaimed\b",
    r"\bassigned\b",
    r"\bworking on this\b",
    r"\bi(?:'| a)?m working on (?:this|it)\b",
    r"\bi(?:'| wi)?ll take (?:this|it)\b",
    r"\bi can take this\b",
    r"\bopened (?:a )?pr\b",
    r"\bpull request (?:is )?open\b",
]

TENTATIVE_TERMS = (
    "proposed",
    "proposal",
    "suggested bounty",
    "potential bounty",
    "candidate bounty",
)

COMPENSATION_TERMS = (
    "bounty",
    "reward",
    "paid",
    "payment",
    "payout",
    "prize",
)

PAYMENT_TRIGGER_TERMS = (
    "upon merge",
    "after merge",
    "paid on merge",
    "payment after",
    "payout after",
    "rewarded after",
    "on completion",
    "after completion",
)


@dataclass
class Verification:
    score: int
    status: str
    reasons: list[str]
    risks: list[str]
    claim_signal: bool


def verify_record(
    issue: dict[str, Any],
    repository: dict[str, Any],
    comments: list[dict[str, Any]] | None = None,
) -> Verification:
    comments = comments or []
    score = 0
    reasons: list[str] = []
    risks: list[str] = []

    if issue.get("state") == "open":
        score += 15
        reasons.append("issue is open")
    else:
        risks.append("issue is not open")

    if not repository.get("archived", False):
        score += 10
        reasons.append("repository is not archived")
    else:
        score -= 25
        risks.append("repository is archived")

    association = str(issue.get("author_association") or "NONE")
    if association in {"OWNER", "MEMBER", "COLLABORATOR"}:
        score += 25
        reasons.append(f"posted by repository {association.lower()}")
    elif association == "CONTRIBUTOR":
        score += 10
        reasons.append("posted by repository contributor")
    else:
        risks.append("no repository-authority signal on issue author")

    title = str(issue.get("title") or "")
    body = str(issue.get("body") or "")
    text = f"{title}\n{body}".lower()

    if any(term in text for term in COMPENSATION_TERMS):
        score += 15
        reasons.append("explicit compensation wording")
    else:
        risks.append("no explicit compensation wording")

    if any(term in text for term in PAYMENT_TRIGGER_TERMS):
        score += 10
        reasons.append("payment/completion trigger described")

    if any(term in text for term in TENTATIVE_TERMS):
        score -= 18
        risks.append("reward appears proposed/not final")

    assignees = issue.get("assignees") or []
    if assignees:
        score -= 20
        risks.append("issue already has assignee(s)")

    if issue.get("locked"):
        score -= 8
        risks.append("issue conversation is locked")

    claim_text = "\n".join(str(c.get("body") or "") for c in comments)
    claim_signal = any(re.search(pattern, claim_text, re.IGNORECASE) for pattern in CLAIM_PATTERNS)
    if claim_signal:
        score -= 25
        risks.append("possible claim/work-in-progress signal in comments")

    score = max(0, min(100, int(score)))
    if score >= 65:
        status = "VERIFIED"
    elif score >= 40:
        status = "REVIEW"
    else:
        status = "REJECT"

    return Verification(
        score=score,
        status=status,
        reasons=reasons,
        risks=risks,
        claim_signal=claim_signal,
    )
