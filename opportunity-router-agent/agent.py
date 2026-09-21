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
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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
    r"(?:(?:US?\\$|\\$|€|EUR\\s?|USD\\s?)(\\d{1,3}(?:[.,]\\d{3})*(?:[.,]\\d+)?))|"
    r"(?:(\\d{1,3}(?:[.,]\\d{3})*(?:[.,]\\d+)?)\\s?(?:USD|EUR|dollars?|euros?))",
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
        "User-Agent": "opportunity-router-agent/0.1",
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
    score: float
    rationale: list[str]

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

    return Opportunity(
        title=title.strip(),
        url=str(item.get("html_url") or ""),
        repository_url=str(item.get("repository_url") or ""),
        updated_at=str(updated_raw or ""),
        author_association=association,
        labels=labels,
        comments=comments,
        reward_estimate=reward,
        score=round(max(0.0, min(100.0, score)), 1),
        rationale=rationale,
    )

def discover(token: str | None, max_results: int) -> list[Opportunity]:
    seen: set[str] = set()
    opportunities: list[Opportunity] = []
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
        time.sleep(0.3)
    opportunities.sort(key=lambda x: (x.score, x.reward_estimate or 0), reverse=True)
    return opportunities[:max_results]

def render_markdown(opportunities: list[Opportunity]) -> str:
    stamp = now_utc().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Opportunity Router — {stamp}",
        "",
        "This agent discovers and ranks public, non-security GitHub reward/bounty signals. It does **not** submit work, exploit systems, accept terms, or move money automatically.",
        "",
        "## Ranked opportunities",
        "",
        "| Score | Reward signal | Opportunity | Why it ranked |",
        "|---:|---:|---|---|",
    ]
    if not opportunities:
        lines.append("| — | — | No eligible opportunities found in this run | — |")
    for op in opportunities:
        reward = f"{op.reward_estimate:,.0f}" if op.reward_estimate else "not explicit"
        why = "; ".join(op.rationale[:4]) or "matched discovery query"
        safe_title = op.title.replace("|", "\\|")
        lines.append(f"| {op.score:.1f} | {reward} | [{safe_title}]({op.url}) | {why} |")
    lines += [
        "",
        "## Human approval gate",
        "",
        "Before acting on any result: verify repository ownership, current bounty terms, eligibility, payout method, tax/KYC requirements, scope, and whether the issue is still unclaimed. No task is automatically accepted or submitted.",
    ]
    return "\n".join(lines) + "\n"

def write_reports(opportunities: list[Opportunity]) -> tuple[Path, Path]:
    out = Path(__file__).resolve().parent / "output"
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "latest.json"
    md_path = out / "LATEST.md"
    payload = {
        "generated_at": now_utc().isoformat(),
        "count": len(opportunities),
        "opportunities": [asdict(x) for x in opportunities],
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(opportunities), encoding="utf-8")
    return json_path, md_path

def publish_issue(token: str, repo: str, body: str) -> None:
    issues = github_request("GET", f"/repos/{repo}/issues?state=open&per_page=100", token)
    current = next((x for x in issues if x.get("title") == REPORT_TITLE and "pull_request" not in x), None)
    payload = {"title": REPORT_TITLE, "body": body[:60000]}
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
    try:
        opportunities = discover(token, max_results)
        json_path, md_path = write_reports(opportunities)
        print(f"Wrote {json_path} and {md_path}; {len(opportunities)} opportunities")
        if token and repo and os.getenv("PUBLISH_ISSUE", "true").lower() == "true":
            publish_issue(token, repo, md_path.read_text(encoding="utf-8"))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
