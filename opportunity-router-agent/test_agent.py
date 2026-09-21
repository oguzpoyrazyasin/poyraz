import agent
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
    },
    {"archived": False},
    [],
)
assert verified.status == "VERIFIED"
assert verified.score >= 65

review = verify_record(
    {
        "state": "open",
        "author_association": "MEMBER",
        "title": "[Bounty proposal] Build workflow",
        "body": "Proposed $50 reward paid on merge",
        "assignees": [],
        "locked": False,
    },
    {"archived": False},
    [],
)
assert review.status == "REVIEW"

claimed = verify_record(
    {
        "state": "open",
        "author_association": "MEMBER",
        "title": "[BOUNTY $200] Build workflow",
        "body": "Paid on merge",
        "assignees": [{"login": "someone"}],
        "locked": False,
    },
    {"archived": False},
    [{"body": "I am working on this"}],
)
assert claimed.score < verified.score

print("Opportunity Router v0.2 tests passed")
