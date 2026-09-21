import agent

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
assert opportunity.score >= 50
assert agent.score_issue({**sample, "body": "security vulnerability bounty"}) is None
print("Opportunity Router tests passed")
