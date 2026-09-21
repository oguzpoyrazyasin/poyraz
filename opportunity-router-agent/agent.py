from __future__ import annotations

import json
import math
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from solution_preparer import prepare_solutions, write_solution_reports
from verifier import verify_record

API = "https://api.github.com"
REPORT_TITLE = "[Opportunity Router] Latest ranked opportunities"
DEFAULT_QUERIES = [
    'bounty in:title,body is:issue is:open',
    'reward in:title,body is:issue is:open',
    '"cash prize" in:title,body is:issue is:open',
    '"paid issue" in:title,body is:issue is:open',
]
EXCLUDED_TERMS = {
    "security", "vulnerability", "exploit", "credential", "phishing", "malware",
    "ransomware", "cve", "xss", "sql injection", "ddos", "brute force",
}
CURRENCY_RE = re.compile(
    r"(?:(?:US?\$|\$|€|EUR\s?|USD\s?)(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?))|"
    r"(?:(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)\s?(?:USD|EUR|dollars?|euros?))",
    re.IGNORECASE,
)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def github_request(method: str, path: str, token: str | None, payload: dict[str, Any] | None = None) -> Any:
    url = path if path.startswith("http") else f"{API}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "opportunity-router-agent/0.3",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {url} failed: {exc.code} {body[:500]}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error calling GitHub API: {exc}") from exc


def normalize_amount(raw: str) -> float | None:
    s = raw.strip().replace(" ", "")
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif s.count(",") == 1 and len(s.split(",")[-1]) <= 2:
        s = s.replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def extract_reward(text: str) -> float | None:
    amounts: list[float] = []
    for match in CURRENCY_RE.finditer(text):
        candidate = match.group(1) or match.group(2)
        if candidate:
            value = normalize_amount(candidate)
            if value and 1 <= value <= 1_000_000:
                amounts.append(value)
    return max(amounts) if amounts else None


def is_excluded(text: str) -> bool:
    low = text.lower()
    return any(term in low for term in EXCLUDED_TERMS)


def parse_issue_url(url: str) -> tuple[str, int] | None:
    try:
        parts = [x for x in urlparse(url).path.split("/") if x]
        if len(parts) >= 4 and parts[2] == "issues":
            return f"{parts[0]}/{parts[1]}", int(parts[3])
    except (ValueError, TypeError):
        return None
    return None


@dataclass
class Opportunity:
    title: str
    url: str
    repository_url: str
    updated_at: str
    author_association: str
    labels: list[str]
    comments: int
    reward_estimate: float | None
    discovery_score: float
    verification_score: int
    verification_status: str
    final_score: float
    rationale: list[str]
    risks: list[str]


def score_issue(item: dict[str, Any]) -> Opportunity | None:
    title = item.get("title") or ""
    body = item.get("body") or ""
    labels = [str(x.get("name", "")) for x in (item.get("labels") or [])]
    combined = "\n".join([title, body, " ".join(labels)])
    if is_excluded(combined):
        return None

    reward = extract_reward(combined)
    score = 0.0
    rationale: list[str] = []
    low = combined.lower()

    if reward is not None:
        reward_points = min(35.0, 8.0 + 9.0 * math.log10(max(reward, 1)))
        score += reward_points
        rationale.append(f"explicit reward signal ≈ {reward:,.0f}")
    elif "bounty" in low or "reward" in low or "paid" in low:
        score += 10
        rationale.append("reward/bounty wording present")

    association = str(item.get("author_association") or "NONE")
    if association in {"OWNER", "MEMBER", "COLLABORATOR"}:
        score += 18
        rationale.append(f"posted by {association.lower()}")
    elif association == "CONTRIBUTOR":
        score += 8
        rationale.append("posted by repository contributor")

    updated_raw = item.get("updated_at") or item.get("created_at")
    if updated_raw:
        age_days = max(0.0, (now_utc() - parse_dt(updated_raw)).total_seconds() / 86400)
        freshness = max(0.0, 22.0 - min(22.0, age_days / 4.0))
        score += freshness
        if age_days <= 14:
            rationale.append("recently active")

    label_text = " ".join(labels).lower()
    if any(x in label_text for x in ("bounty", "reward", "paid")):
        score += 12
        rationale.append("reward-related label")
    if any(x in label_text for x in ("good first issue", "help wanted")):
        score += 6
        rationale.append("contributor-friendly label")

    comments = int(item.get("comments") or 0)
    if comments <= 5:
        score += 5
        rationale.append("limited visible contention")
    elif comments >= 30:
        score -= 6
        rationale.append("high discussion/competition")

    discovery_score = round(max(0.0, min(100.0, score)), 1)
    return Opportunity(
        title=title.strip(),
        url=str(item.get("html_url") or ""),
        repository_url=str(item.get("repository_url") or ""),
        updated_at=str(updated_raw or ""),
        author_association=association,
        labels=labels,
        comments=comments,
        reward_estimate=reward,
        discovery_score=discovery_score,
        verification_score=0,
        verification_status="UNVERIFIED",
        final_score=round(discovery_score * 0.45, 1),
        rationale=rationale,
        risks=[],
    )


def verify_opportunity(op: Opportunity, token: str | None) -> Opportunity:
    parsed = parse_issue_url(op.url)
    if not parsed:
        op.verification_status = "REJECT"
        op.risks.append("could not parse GitHub issue URL")
        return op

    repo, issue_number = parsed
    try:
        issue = github_request("GET", f"/repos/{repo}/issues/{issue_number}", token)
        repository = github_request("GET", f"/repos/{repo}", token)
        comments: list[dict[str, Any]] = []
        if int(issue.get("comments") or 0) > 0:
            comments = github_request(
                "GET",
                f"/repos/{repo}/issues/{issue_number}/comments?per_page=30",
                token,
            ) or []

        verification = verify_record(issue, repository, comments)
        op.verification_score = verification.score
        op.verification_status = verification.status
        op.rationale.extend(verification.reasons)
        op.risks.extend(verification.risks)
        op.final_score = round(
            min(100.0, op.discovery_score * 0.45 + verification.score * 0.55),
            1,
        )
    except Exception as exc:
        op.verification_status = "REVIEW"
        op.risks.append(f"verification API error: {exc}")
        op.final_score = round(op.discovery_score * 0.45, 1)
    return op


def discover(token: str | None, max_results: int, max_verify: int) -> list[Opportunity]:
    seen: set[str] = set()
    opportunities: list[Opportunity] = []
    candidate_limit = max(max_results * 3, max_verify)

    for query in DEFAULT_QUERIES:
        params = urlencode({"q": query, "sort": "updated", "order": "desc", "per_page": 50})
        data = github_request("GET", f"/search/issues?{params}", token)
        for item in data.get("items", []):
            url = str(item.get("html_url") or "")
            if not url or url in seen:
                continue
            seen.add(url)
            scored = score_issue(item)
            if scored:
                opportunities.append(scored)
        time.sleep(0.2)

    opportunities.sort(key=lambda x: (x.discovery_score, x.reward_estimate or 0), reverse=True)
    opportunities = opportunities[:candidate_limit]

    for idx, op in enumerate(opportunities[:max_verify], start=1):
        print(f"Verifying {idx}/{min(max_verify, len(opportunities))}: {op.url}")
        verify_opportunity(op, token)
        time.sleep(0.15)

    verified = [op for op in opportunities if op.verification_status != "REJECT"]
    verified.sort(
        key=lambda x: (
            x.verification_status == "VERIFIED",
            x.final_score,
            x.reward_estimate or 0,
        ),
        reverse=True,
    )
    return verified[:max_results]


def render_markdown(opportunities: list[Opportunity], ready_count: int) -> str:
    stamp = now_utc().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Opportunity Router — {stamp}",
        "",
        "v0.3 adds Solution Preparation after verification. Results are estimates, not guaranteed payouts. No task is automatically claimed or submitted.",
        "",
        "## Ranked opportunities",
        "",
        "| Final | Verify | Reward signal | Opportunity | Key risk |",
        "|---:|---|---:|---|---|",
    ]
    if not opportunities:
        lines.append("| — | — | — | No eligible opportunities found in this run | — |")
    for op in opportunities:
        reward = f"{op.reward_estimate:,.0f}" if op.reward_estimate else "not explicit"
        risk = "; ".join(op.risks[:2]) if op.risks else "no immediate verification flag"
        safe_title = op.title.replace("|", "\\|")
        lines.append(
            f"| {op.final_score:.1f} | {op.verification_status} ({op.verification_score}) | "
            f"{reward} | [{safe_title}]({op.url}) | {risk} |"
        )

    verified_count = sum(1 for op in opportunities if op.verification_status == "VERIFIED")
    review_count = sum(1 for op in opportunities if op.verification_status == "REVIEW")
    lines += [
        "",
        f"**Queue:** {verified_count} VERIFIED · {review_count} REVIEW · {ready_count} READY_FOR_REVIEW solution(s)",
        "",
        "## Approval policy",
        "",
        "- VERIFIED means the public GitHub signals passed the automated trust threshold; it does not guarantee payment.",
        "- VERIFIED items are passed to Solution Preparation for effort, probability and expected-value estimation.",
        "- REVIEW requires a human check before any work starts.",
        "- REJECT items are removed from the published queue.",
        "- The agent does not claim tasks, contact maintainers, submit PRs, accept terms, perform KYC, move funds, or run vulnerability/exploit automation.",
    ]
    return "\n".join(lines) + "\n"


def write_reports(opportunities: list[Opportunity], ready_count: int) -> tuple[Path, Path]:
    out = Path(__file__).resolve().parent / "output"
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "latest.json"
    md_path = out / "LATEST.md"
    payload = {
        "generated_at": now_utc().isoformat(),
        "version": "0.3",
        "count": len(opportunities),
        "verified": sum(1 for x in opportunities if x.verification_status == "VERIFIED"),
        "review": sum(1 for x in opportunities if x.verification_status == "REVIEW"),
        "ready_for_review": ready_count,
        "opportunities": [asdict(x) for x in opportunities],
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(opportunities, ready_count), encoding="utf-8")
    return json_path, md_path


def publish_issue(token: str, repo: str, body: str, solution_body: str) -> None:
    issues = github_request("GET", f"/repos/{repo}/issues?state=open&per_page=100", token)
    current = next((x for x in issues if x.get("title") == REPORT_TITLE and "pull_request" not in x), None)
    combined = (body + "\n\n---\n\n" + solution_body)[:60000]
    payload = {"title": REPORT_TITLE, "body": combined}
    if current:
        github_request("PATCH", f"/repos/{repo}/issues/{current['number']}", token, payload)
        print(f"Updated issue #{current['number']}")
    else:
        created = github_request("POST", f"/repos/{repo}/issues", token, payload)
        print(f"Created issue #{created.get('number')}")


def main() -> int:
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    max_results = int(os.getenv("MAX_RESULTS", "25"))
    max_verify = int(os.getenv("MAX_VERIFY", "20"))
    try:
        opportunities = discover(token, max_results, max_verify)
        prepared = prepare_solutions([asdict(x) for x in opportunities], token, github_request)
        out_dir = Path(__file__).resolve().parent / "output"
        solution_json, solution_md = write_solution_reports(prepared, out_dir)
        ready_count = sum(1 for x in prepared if x.decision == "READY_FOR_REVIEW")
        json_path, md_path = write_reports(opportunities, ready_count)
        print(
            f"Wrote {json_path}, {md_path}, {solution_json}, {solution_md}; "
            f"{len(opportunities)} opportunities, {len(prepared)} prepared"
        )
        if token and repo and os.getenv("PUBLISH_ISSUE", "true").lower() == "true":
            publish_issue(
                token,
                repo,
                md_path.read_text(encoding="utf-8"),
                solution_md.read_text(encoding="utf-8"),
            )
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
