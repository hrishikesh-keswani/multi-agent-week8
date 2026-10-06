"""Shared case record passed through the underwriting pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _usage() -> Dict[str, int]:
    return {"prompt_tokens": 0, "completion_tokens": 0}


@dataclass
class CaseRecord:
    """One application. Agents read and write sections on this object."""

    case_id: str
    raw_application: Dict[str, Any]
    status: str = "in_progress"
    intake: Optional[Dict[str, Any]] = None
    enrichment: Optional[Dict[str, Any]] = None
    risk: Optional[Dict[str, Any]] = None
    recommendation: Optional[Dict[str, Any]] = None
    trace: List[Dict[str, Any]] = field(default_factory=list)
    last_usage: Dict[str, int] = field(default_factory=_usage)

    @classmethod
    def from_application(cls, raw: Dict[str, Any]) -> "CaseRecord":
        applicant_id = raw.get("applicant_id")
        if not applicant_id:
            raise ValueError("raw application is missing applicant_id")
        return cls(case_id=str(applicant_id), raw_application=dict(raw))

    def to_document(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "status": self.status,
            "raw_application": self.raw_application,
            "intake": self.intake,
            "enrichment": self.enrichment,
            "risk": self.risk,
            "recommendation": self.recommendation,
            "spans": self.trace,
        }
