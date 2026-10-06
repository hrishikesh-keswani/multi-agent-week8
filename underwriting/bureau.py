"""Deterministic third-party stand-in keyed by applicant id."""

from __future__ import annotations

import json
from typing import Any, Dict

from underwriting.paths import DATA_DIR

_CACHE: Dict[str, Any] = {}


def lookup_bureau(applicant_id: str) -> Dict[str, Any]:
    records = _load()
    record = records.get(applicant_id)
    if not isinstance(record, dict):
        return {
            "found": False,
            "prior_claims": None,
            "credit_band": None,
            "occupation_class": None,
            "flood_zone": None,
        }
    found = {"found": True}
    found.update(record)
    return found


def _load() -> Dict[str, Any]:
    if not _CACHE:
        path = DATA_DIR / "bureau.json"
        with path.open(encoding="utf-8") as handle:
            loaded = json.load(handle)
        if not isinstance(loaded, dict):
            raise ValueError("bureau.json must be an object keyed by applicant id")
        _CACHE.update(loaded)
    return _CACHE
