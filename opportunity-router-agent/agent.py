"""
Simple Opportunity Router Agent

Provides a function to retrieve the latest ranked opportunities
from a static dataset. In a real implementation this would
query a database or external API. For the purposes of this
repo, the data is hardcoded from the issue description.
"""

from __future__ import annotations

from typing import List, Dict

# Data source: extracted from the issue description
_OPPORTUNITIES = [
    {
        "final": 76.2,
        "verify": "VERIFIED (75)",
        "reward_signal": 138_000,
        "opportunity": "Amazon Alexa+ + Open Source Hackathon — up to $30,000 cash",
        "key_risk": "no immediate verification flag",
    },
    {
        "final": 70.3,
        "verify": "VERIFIED (65)",
        "reward_signal": 138_000,
        "opportunity": "Amazon Developer Hackathon — $138,000 prize pool",
        "key_risk": "no immediate verification flag",
    },
    {
        "final": 69.3,
        "verify": "VERIFIED (65)",
        "reward_signal": 100_000,
        "opportunity": "Future Vision XPRIZE - coordination economy film",
        "key_risk": "no immediate verification flag",
    },
    {
        "final": 69.3,
        "verify": "VERIFIED (65)",
        "reward_signal": 6_000,
        "opportunity": "DataHub Agent Hackathon - ContextBounty",
        "key_risk": "no immediate verification flag",
    },
    {
        "final": 69.1,
        "verify": "VERIFIED (65)",
        "reward_signal": 25_000,
        "opportunity": "Zero-capital trading lane: Recall simulated agent competitions",
        "key_risk": "no immediate verification flag",
    },
    {
        "final": 69.1,
        "verify": "VERIFIED (65)",
        "reward_signal": 10_000,
        "opportunity": "September agent incentive radar: zero/sponsored-capital crypto competitions",
        "key_risk": "no immediate verification flag",
    },
    {
        "final": 65.3,
        "verify": "VERIFIED (65)",
        "reward_signal": 25,
        "opportunity": "What Paid includes: $20 a month, 150 questions, Sonnet 5, one page scan at a time",
        "key_risk": "no immediate verification flag",
    },
    {
        "final": 63.2,
        "verify": "VERIFIED (65)",
        "reward_signal": None,
        "opportunity": "fa2-fp8kv: EngineCore dies when fp8 KV runs 2+ sequences and a prefill chunk exceeds 2048 (not TP-specific)",
        "key_risk": "no immediate verification flag",
    },
    {
        "final": 61.8,
        "verify": "VERIFIED (65)",
        "reward_signal": 4,
        "opportunity": "Snorkel 的18倍增长说明，AI数据正在从人力外包变成产品",
        "key_risk": "no immediate verification flag",
    },
]

def get_latest_ranked_opportunities(limit: int | None = None) -> List[Dict]:
    """
    Return the list of opportunities sorted by `final` score descending.

    Parameters
    ----------
    limit : int | None
        Optional maximum number of items to return.

    Returns
    -------
    List[Dict]
        List of opportunity dictionaries.
    """
    sorted_ops = sorted(_OPPORTUNITIES, key=lambda o: o["final"], reverse=True)
    if limit is not None:
        return sorted_ops[:limit]
    return sorted_ops

def get_opportunity_by_title(title: str) -> Dict | None:
    """
    Retrieve a single opportunity by its title.

    Parameters
    ----------
    title : str
        Exact title string.

    Returns
    -------
    Dict | None
        Matching opportunity or None if not found.
    """
    for op in _OPPORTUNITIES:
        if op["opportunity"] == title:
            return op
    return None
