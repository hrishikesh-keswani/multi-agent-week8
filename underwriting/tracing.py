"""Span records for each agent attempt."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from underwriting.state import CaseRecord

SECTION_BY_AGENT = {
    "intake": "intake",
    "enrichment": "enrichment",
    "risk_scoring": "risk",
    "recommendation": "recommendation",
}


def snapshot_input(agent: str, case: CaseRecord) -> Dict[str, Any]:
    if agent == "intake":
        payload: Dict[str, Any] = {"raw_application": case.raw_application}
    elif agent == "enrichment":
        payload = {"intake": case.intake}
    elif agent == "risk_scoring":
        payload = {"intake": case.intake, "enrichment": case.enrichment}
    elif agent == "recommendation":
        payload = {
            "intake": case.intake,
            "enrichment": case.enrichment,
            "risk": case.risk,
        }
    else:
        payload = {}
    return copy.deepcopy(payload)


def snapshot_output(agent: str, case: CaseRecord) -> Optional[Dict[str, Any]]:
    section = SECTION_BY_AGENT.get(agent)
    if section is None:
        return None
    value = getattr(case, section)
    if value is None:
        return None
    return copy.deepcopy(value)


def build_span(
    agent: str,
    attempt: int,
    started_at: datetime,
    duration_ms: int,
    received: Dict[str, Any],
    output: Optional[Dict[str, Any]],
    status: str,
    usage: Dict[str, int],
    error: Optional[str] = None,
    case: Optional[CaseRecord] = None,
) -> Dict[str, Any]:
    ended_at = datetime.now(timezone.utc)
    span: Dict[str, Any] = {
        "agent": agent,
        "attempt": attempt,
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "duration_ms": duration_ms,
        "input": received,
        "output": output,
        "status": status,
        "error": error,
        "token_usage": {
            "prompt_tokens": int(usage.get("prompt_tokens", 0)),
            "completion_tokens": int(usage.get("completion_tokens", 0)),
        },
    }
    if agent == "recommendation":
        recommendation = {} if case is None or case.recommendation is None else case.recommendation
        span["model_decision"] = recommendation.get("model_decision")
        span["final_decision"] = recommendation.get("final_decision")
        span["guard_reason"] = recommendation.get("guard_reason")
    return span


def format_trace(case: CaseRecord) -> str:
    lines = ["case_id={0} status={1}".format(case.case_id, case.status)]
    for span in case.trace:
        usage = span["token_usage"]
        lines.append(
            "[{0}] attempt {1} {2} duration_ms={3} prompt_tokens={4} completion_tokens={5}".format(
                span["agent"],
                span["attempt"],
                span["status"],
                span["duration_ms"],
                usage["prompt_tokens"],
                usage["completion_tokens"],
            )
        )
        if span.get("error"):
            lines.append("  error: {0}".format(span["error"]))
        if span["agent"] == "recommendation" and span["status"] == "ok":
            lines.append(
                "  model_decision={0} final_decision={1} guard_reason={2}".format(
                    _shown(span.get("model_decision")),
                    _shown(span.get("final_decision")),
                    _shown(span.get("guard_reason")),
                )
            )
    if case.recommendation:
        lines.append(
            "recommendation decision={0} source={1}".format(
                case.recommendation.get("decision"),
                case.recommendation.get("source"),
            )
        )
    return "\n".join(lines)


def _shown(value: Any) -> str:
    if value is None:
        return "null"
    return str(value)
