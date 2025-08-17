"""Category router mapping question categories to role contracts."""
from __future__ import annotations

from typing import Dict

from backend.models import Planet

_CONTRACTS: Dict[str, Dict[str, Planet]] = {
    "education": {"examiner": Planet.SUN},
}


def get_contract(category: str) -> Dict[str, Planet]:
    """Return role contract for a given category (case-insensitive)."""
    if not category:
        return {}
    return _CONTRACTS.get(category.lower(), {})
