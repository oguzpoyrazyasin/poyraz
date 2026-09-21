from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GH_API = "https://api.github.com"
UA = "poyraz-wallet-rewards/0.1"
REPORT_TITLE = "[Wallet Rewards] Latest eligibility"
EVM_ADDR_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")

@dataclass
class Wallet:
    chain: str
    address: str
    owner_verified: bool
    rpc_env: str | None = None
    label: str = ""

@dataclass
class RewardSource:
    program_id: str
    name: str
    official_url: str
    kind: str
    chain: str
    token_symbol: str
    token_price_usd: float | None = None
    allocation_url: str | None = None
    api_url_template: str | None = None
    amount_path: str | None = None
    gas_estimate_usd: float = 0.0
    swap_fee_pct: float = 0.0
    off_ramp_fee_pct: float = 0.0
    risk_haircut_pct: float = 15.0
    minimum_net_ev_usd: float = 5.0
    enabled: bool = True

@dataclass
class WalletBalance:
    chain: str
    address: str
    label: str
    native_balance: float | None
    source: str
    status: str
    error: str | None = None

@dataclass
class RewardResult:
    wallet: str
    chain: str
    program_id: str
    program_name: str
    token_symbol: str
    token_amount: float | None
    gross_value_usd: float | None
    estimated_cost_usd: float
    risk_haircut_usd: float | None
    net_ev_usd: float | None
    decision: str
    confidence: float
    official_url: str
    notes: list[str]

def now() -> datetime:
    return datetime.now(timezone.utc)

def http_json(url: str, method: str = "GET", payload: dict[str, Any] | None = None, timeout: int = 25) -> Any:
    headers = {"Accept": "application/json", "User-Agent": UA}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body[:300]}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(str(exc)) from exc

def gh(method: str, path: str, token: str, payload: dict[str, Any] | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {token}",
        "User-Agent": UA,
    }
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = Request(GH_API + path, data=data, headers=headers, method=method)
    with urlopen(req, timeout=30) as r:
        raw = r.read().decode("utf-8")
        return json.loads(raw) if raw else None

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def load_wallets() -> list[Wallet]:
    inline = os.getenv("SELF_OWNED_WALLETS_JSON")
    raw = json.loads(inline) if inline else load_json(Path(os.getenv("WALLET_CONFIG", "wallets.example.json")))
    out: list[Wallet] = []
    for row in raw if isinstance(raw, list) else []:
        w = Wallet(
            chain=str(row.get("chain") or "").lower().strip(),
            address=str(row.get("address") or "").strip(),
            owner_verified=bool(row.get("owner_verified")),
            rpc_env=str(row.get("rpc_env") or "") or None,
            label=str(row.get("label") or ""),
        )
        if not w.owner_verified:
            continue
        if w.chain in {"ethereum", "base", "arbitrum", "optimism", "polygon", "bsc", "avalanche"} and not EVM_ADDR_RE.match(w.address):
            continue
        out.append(w)
    return out

def load_sources() -> list[RewardSource]:
    raw = load_json(Path(os.getenv("REWARD_SOURCES_CONFIG", "reward_sources.example.json")))
    out: list[RewardSource] = []
    for row in raw if isinstance(raw, list) else []:
        try:
            src = RewardSource(**row)
            if src.enabled:
                out.append(src)
        except TypeError:
            continue
    return out

def rpc_call(rpc_url: str, method: str, params: list[Any]) -> Any:
    data = http_json(rpc_url, "POST", {"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError(str(data["error"]))
    return data.get("result") if isinstance(data, dict) else None

def evm_native_balance(wallet: Wallet) -> WalletBalance:
    if not wallet.rpc_env:
        return WalletBalance(wallet.chain, wallet.address, wallet.label, None, "rpc", "NO_RPC", "rpc_env not configured")
    rpc = os.getenv(wallet.rpc_env)
    if not rpc:
        return WalletBalance(wallet.chain, wallet.address, wallet.label, None, "rpc", "NO_RPC", f"missing env {wallet.rpc_env}")
    try:
        raw = rpc_call(rpc, "eth_getBalance", [wallet.address, "latest"])
        return WalletBalance(wallet.chain, wallet.address, wallet.label, int(str(raw), 16) / 10**18, "rpc", "OK")
    except Exception as exc:
        return WalletBalance(wallet.chain, wallet.address, wallet.label, None, "rpc", "ERROR", str(exc))

def find_amount_in_json(data: Any, address: str) -> float | None:
    target = address.lower()
    if isinstance(data, dict):
        for key, value in data.items():
            if str(key).lower() == target:
                if isinstance(value, (int, float, str)):
                    try:
                        return float(value)
                    except ValueError:
                        pass
                if isinstance(value, dict):
                    for amount_key in ("amount", "allocation", "claimable", "value"):
                        if amount_key in value:
                            try:
                                return float(value[amount_key])
                            except (TypeError, ValueError):
                                pass
            nested = find_amount_in_json(value, address)
            if nested is not None:
                return nested
    elif isinstance(data, list):
        for row in data:
            if isinstance(row, dict):
                candidate = str(row.get("address") or row.get("account") or row.get("wallet") or "").lower()
                if candidate == target:
                    for amount_key in ("amount", "allocation", "claimable", "value"):
                        if amount_key in row:
                            try:
                                return float(row[amount_key])
                            except (TypeError, ValueError):
                                pass
            nested = find_amount_in_json(row, address)
            if nested is not None:
                return nested
    return None

def json_path(data: Any, path: str) -> Any:
    cur = data
    for part in [x for x in path.split(".") if x]:
        if isinstance(cur, dict):
            cur = cur.get(part)
        elif isinstance(cur, list) and part.isdigit():
            idx = int(part)
            cur = cur[idx] if 0 <= idx < len(cur) else None
        else:
            return None
    return cur

def check_source(wallet: Wallet, src: RewardSource) -> RewardResult | None:
    if src.chain.lower() != wallet.chain.lower():
        return None
    amount = None
    notes: list[str] = []
    confidence = 0.0
    try:
        if src.kind == "allocation_json" and src.allocation_url:
            data = http_json(src.allocation_url)
            amount = find_amount_in_json(data, wallet.address)
            confidence = 0.85 if amount is not None else 0.70
            notes.append("checked published allocation JSON")
        elif src.kind == "address_api" and src.api_url_template:
            data = http_json(src.api_url_template.replace("{address}", wallet.address))
            raw = json_path(data, src.amount_path or "amount")
            amount = float(raw) if raw not in (None, "") else None
            confidence = 0.80 if amount is not None else 0.65
            notes.append("checked configured official address API")
        else:
            return None
    except Exception as exc:
        return RewardResult(wallet.address, wallet.chain, src.program_id, src.name, src.token_symbol, None, None, 0.0, None, None, "ERROR", 0.0, src.official_url, [str(exc)])

    if amount is None or amount <= 0:
        return RewardResult(wallet.address, wallet.chain, src.program_id, src.name, src.token_symbol, 0.0, 0.0, 0.0, 0.0, 0.0, "NOT_ELIGIBLE", confidence, src.official_url, notes)

    gross = amount * src.token_price_usd if src.token_price_usd is not None else None
    if gross is None:
        return RewardResult(wallet.address, wallet.chain, src.program_id, src.name, src.token_symbol, amount, None, src.gas_estimate_usd, None, None, "PRICE_REQUIRED", confidence, src.official_url, notes + ["token price missing; no EV computed"])

    variable_cost = gross * (src.swap_fee_pct + src.off_ramp_fee_pct) / 100.0
    risk_haircut = gross * src.risk_haircut_pct / 100.0
    total_cost = src.gas_estimate_usd + variable_cost
    net_ev = gross - total_cost - risk_haircut
    decision = "CLAIM_REVIEW" if net_ev >= src.minimum_net_ev_usd else "LOW_EV"
    return RewardResult(
        wallet.address,
        wallet.chain,
        src.program_id,
        src.name,
        src.token_symbol,
        amount,
        round(gross, 2),
        round(total_cost, 2),
        round(risk_haircut, 2),
        round(net_ev, 2),
        decision,
        confidence,
        src.official_url,
        notes,
    )

def render(balances: list[WalletBalance], rewards: list[RewardResult]) -> str:
    lines = [
        f"# Wallet Rewards — {now().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Read-only ownership-scoped eligibility monitor. No private keys, no signing, no automatic claims.",
        "",
        "## Self-owned wallet health",
        "",
        "|Chain|Wallet|Native balance|Status|",
        "|---|---|---:|---|",
    ]
    if not balances:
        lines.append("|—|No verified wallets configured|—|—|")
    for b in balances:
        address = b.address[:8] + "…" + b.address[-6:]
        balance = "—" if b.native_balance is None else f"{b.native_balance:.6f}"
        lines.append(f"|{b.chain}|{address}|{balance}|{b.status}|")

    lines += [
        "",
        "## Reward eligibility",
        "",
        "|Decision|Program|Wallet|Token|Amount|Gross USD|Net EV USD|Confidence|",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    if not rewards:
        lines.append("|—|No enabled official reward sources or verified wallets|—|—|—|—|—|—|")
    for r in rewards:
        address = r.wallet[:8] + "…" + r.wallet[-6:]
        amount = "—" if r.token_amount is None else f"{r.token_amount:,.6f}"
        gross = "—" if r.gross_value_usd is None else f"{r.gross_value_usd:,.2f}"
        net = "—" if r.net_ev_usd is None else f"{r.net_ev_usd:,.2f}"
        lines.append(f"|{r.decision}|[{r.program_name}]({r.official_url})|{address}|{r.token_symbol}|{amount}|{gross}|{net}|{r.confidence:.0%}|")

    lines += [
        "",
        "## EV model",
        "",
        "Net EV = gross token value - gas - swap fee - off-ramp fee - risk haircut",
        "",
        "CLAIM_REVIEW is only a review state. This agent never signs or submits a transaction.",
        "",
        "## Guardrails",
        "",
        "- Only addresses explicitly marked owner_verified=true are processed.",
        "- No seed phrases/private keys are read or stored.",
        "- No abandoned-wallet or third-party balance scanning.",
        "- No claim transaction generation or signing.",
        "- Only configured official allocation/API sources are queried.",
        "- KYC, tax, sanctions and off-ramp checks remain separate gates.",
    ]
    return "\n".join(lines) + "\n"

def publish(token: str, repo: str, body: str) -> None:
    issues = gh("GET", f"/repos/{repo}/issues?state=open&per_page=100", token)
    current = next((x for x in issues if x.get("title") == REPORT_TITLE and "pull_request" not in x), None)
    payload = {"title": REPORT_TITLE, "body": body[:60000]}
    if current:
        gh("PATCH", f"/repos/{repo}/issues/{current['number']}", token, payload)
    else:
        gh("POST", f"/repos/{repo}/issues", token, payload)

def main() -> int:
    wallets = load_wallets()
    sources = load_sources()
    balances: list[WalletBalance] = []
    rewards: list[RewardResult] = []

    for wallet in wallets:
        if wallet.chain in {"ethereum", "base", "arbitrum", "optimism", "polygon", "bsc", "avalanche"}:
            balances.append(evm_native_balance(wallet))
        for source in sources:
            result = check_source(wallet, source)
            if result is not None:
                rewards.append(result)
            time.sleep(0.03)

    out = Path(__file__).resolve().parent / "output"
    out.mkdir(exist_ok=True)
    payload = {
        "generated_at": now().isoformat(),
        "wallets": [asdict(x) for x in balances],
        "rewards": [asdict(x) for x in rewards],
    }
    (out / "wallet_rewards.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    report = render(balances, rewards)
    (out / "WALLET_REWARDS.md").write_text(report, encoding="utf-8")

    token, repo = os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_REPOSITORY")
    if token and repo and os.getenv("PUBLISH_WALLET_ISSUE", "true").lower() == "true":
        publish(token, repo, report)

    print(f"verified_wallets={len(wallets)} reward_checks={len(rewards)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
