import agent
from planner import prepare_plan
from verifier import verify_record

sample = {
    "title": "Implement parser — $500 bounty",
    "body": "Paid after merged PR",
    "labels": [{"name": "bounty"}],
    "author_association": "MEMBER",
    "updated_at": "2026-09-20T12:00:00Z",
    "created_at": "2026-09-20T12:00:00Z",
    "comments": 2,
    "html_url": "https://github.com/example/repo/issues/1",
    "repository_url": "https://api.github.com/repos/example/repo",
}

opportunity = agent.score_issue(sample)
assert opportunity is not None
assert opportunity.reward_estimate == 500.0
assert opportunity.discovery_score >= 50
assert agent.score_issue({**sample, "body": "security vulnerability bounty"}) is None

verified = verify_record(
    {
        "state": "open",
        "author_association": "MEMBER",
        "title": "[BOUNTY $200] Build workflow",
        "body": "Paid on merge",
        "assignees": [],
        "locked": False,
        "comments": 1,
    },
    {"archived": False},
    [],
)
assert verified.status == "VERIFIED"
assert verified.score >= 65

saturated = verify_record(
    {
        "state": "open",
        "author_association": "MEMBER",
        "title": "[BOUNTY $200] Build workflow",
        "body": "Paid on merge",
        "assignees": [],
        "locked": False,
        "comments": 500,
    },
    {"archived": False},
    [],
)
assert saturated.score < verified.score
assert saturated.status != "VERIFIED"

review = verify_record(
    {
        "state": "open",
        "author_association": "MEMBER",
        "title": "[Bounty proposal] Build workflow",
        "body": "Proposed $50 reward paid on merge",
        "assignees": [],
        "locked": False,
        "comments": 0,
    },
    {"archived": False},
    [],
)
assert review.status == "REVIEW"

plan = prepare_plan(
    {
        "title": "[BOUNTY $300] Python API task",
        "body": "- [ ] Add endpoint\n- [ ] Add tests\nPaid on merge",
        "comments": 2,
        "assignees": [],
    },
    verification_score=80,
    reward_estimate=300.0,
)
assert plan.expected_hours > 0
assert plan.risk_adjusted_value is not None
assert plan.risk_adjusted_per_hour is not None
assert plan.action.startswith("PREPARE")

print("Opportunity Router v0.3 tests passed")
