from wallet_rewards import Wallet, RewardSource, find_amount_in_json, check_source
import wallet_rewards

def run():
    address = "0x1111111111111111111111111111111111111111"
    assert find_amount_in_json({address: {"amount": "12.5"}}, address) == 12.5

    wallet = Wallet("ethereum", address, True)
    source = RewardSource(
        program_id="demo",
        name="Demo",
        official_url="https://example.org",
        kind="allocation_json",
        chain="ethereum",
        token_symbol="DEMO",
        token_price_usd=2.0,
        allocation_url="https://example.org/alloc.json",
        gas_estimate_usd=1.0,
        risk_haircut_pct=10.0,
    )

    original = wallet_rewards.http_json
    wallet_rewards.http_json = lambda *args, **kwargs: {address: {"amount": "12.5"}}
    try:
        result = check_source(wallet, source)
        assert result is not None
        assert result.decision == "CLAIM_REVIEW"
        assert result.gross_value_usd == 25.0
        assert result.net_ev_usd is not None and result.net_ev_usd > 0
    finally:
        wallet_rewards.http_json = original

    print("wallet rewards tests passed")

if __name__ == "__main__":
    run()
