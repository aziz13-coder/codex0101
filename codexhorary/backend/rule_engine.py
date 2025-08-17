"""Rule evaluation utilities implementing tiered priority with first-hit wins."""
from __future__ import annotations

from typing import Iterable, List

import rules

# Fixed priority order for rule tiers
PRIORITY_TIERS = [
    "validity_gates",
    "hard_stoppers",
    "perfection",
    "special_topics",
    "moon",
    "modifiers",
    "thresholds",
]


def evaluate_rules(candidate_ids: Iterable[str]) -> List[str]:
    """Return rule IDs selected according to priority tiers with config gating.

    Parameters
    ----------
    candidate_ids: Iterable[str]
        Iterable of rule IDs that evaluate to true.

    Returns
    -------
    List[str]
        Ordered list of chosen rule IDs, at most one per tier.
    """
    from horary_config import cfg
    config = cfg()
    
    candidates = set(candidate_ids)
    selected: List[str] = []
    for tier in PRIORITY_TIERS:
        tier_rules = sorted(
            (r for r in rules.RULES if r.get("tier") == tier),
            key=lambda r: r["id"],
        )
        for rule in tier_rules:
            if rule["id"] in candidates:
                # Gate void moon rule on configuration
                if rule["id"] == "H2" and not getattr(config.moon, "void_gating", False):
                    continue  # Skip void moon if gating is disabled
                selected.append(rule["id"])
                break  # first-hit wins within tier
    return selected
