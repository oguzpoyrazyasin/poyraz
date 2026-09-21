# Token Radar Agent

Autonomous read-only scanner for new/emerging crypto tokens plus a self-owned-wallet reward eligibility layer.

## Pipeline

Token market discovery:
DEX Screener latest profiles and boosts -> deepest-pool enrichment -> liquidity, volume, transaction, age and FDV risk model -> CoinPaprika broad-market activity -> JSON/Markdown/HTML dashboard.

Wallet reward layer:
SELF_OWNED_WALLETS_JSON -> owner-verified address filter -> optional native balance RPC -> configured official reward allocation/API checks -> gross value -> gas/swap/off-ramp/risk deductions -> CLAIM_REVIEW / LOW_EV.

OBSERVE and CLAIM_REVIEW are investigation/review states, not buy or execution instructions.

## Mathematical model

Token priority:
priority_score = signal_score * (1 - 0.72 * risk_score / 100)

Reward net expected value:
Net EV = gross token value - gas - swap fee - off-ramp fee - risk haircut

## Outputs

- output/latest.json
- output/LATEST.md
- output/dashboard.html
- output/wallet_rewards.json
- output/WALLET_REWARDS.md

## Private configuration

Do not commit personal wallet addresses. Store them in the GitHub Actions secret SELF_OWNED_WALLETS_JSON.

Example secret value:
[{"chain":"ethereum","address":"0xYOURADDRESS","owner_verified":true,"rpc_env":"ETH_RPC_URL","label":"primary"}]

Optional RPC secrets:
- ETH_RPC_URL
- BASE_RPC_URL
- ARBITRUM_RPC_URL
- OPTIMISM_RPC_URL
- POLYGON_RPC_URL
- BSC_RPC_URL
- AVALANCHE_RPC_URL

Official reward adapters are configured in reward_sources.example.json. Only official/published allocation JSON or official address APIs should be enabled.

## Safety boundary

No private keys or seed phrases. No abandoned-wallet sweeping. No third-party wallet claims. No unauthorized airdrop farming. No exploits, sybil farming, front-running, wash trading, custody, trading, signing or automatic claim transactions.

## Run locally

cd token-radar-agent
python -m py_compile scanner.py wallet_rewards.py
python test_scanner.py
python test_wallet_rewards.py
python scanner.py
python wallet_rewards.py

The GitHub workflow runs hourly and uploads all outputs as artifacts while refreshing Token Radar and Wallet Rewards issues.
