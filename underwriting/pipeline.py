"""Fixed workflow: intake, enrichment, risk scoring, recommendation."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Sequence, Tuple

from underwriting.agents import (
    enrichment_agent,
    intake_agent,
    recommendation_agent,
    risk_scoring_agent,
)
from underwriting.state import CaseRecord
from underwriting.tracing import build_span, snapshot_input, snapshot_output

AgentFn = Callable[[CaseRecord, Any], CaseRecord]

AGENTS: Sequence[Tuple[str, AgentFn]] = (
    ("intake", intake_agent),
    ("enrichment", enrichment_agent),
    ("risk_scoring", risk_scoring_agent),
    ("recommendation", recommendation_agent),
)


def run_pipeline(
    raw_application: Dict[str, Any],
    llm: Any,
    max_attempts: int = 3,
    backoff_s: Sequence[float] = (0.05, 0.1),
) -> CaseRecord:
    """Run every agent. On a lasting failure, escalate and stop."""
    case = CaseRecord.from_application(raw_application)
    for agent_name, agent_fn in AGENTS:
        case = call_with_retry(
            case,
            agent_name,
            agent_fn,
            llm,
            max_attempts=max_attempts,
            backoff_s=backoff_s,
        )
        if case.status == "escalated":
            return case
    case.status = "completed"
    return case


def call_with_retry(
    case: CaseRecord,
    agent_name: str,
    agent_fn: AgentFn,
    llm: Any,
    max_attempts: int = 3,
    backoff_s: Sequence[float] = (0.05, 0.1),
) -> CaseRecord:
    for attempt in range(1, max_attempts + 1):
        started_at = datetime.now(timezone.utc)
        started = time.perf_counter()
        case.last_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        received = snapshot_input(agent_name, case)
        try:
            case = agent_fn(case, llm)
        except Exception as exc:
            duration_ms = int(round((time.perf_counter() - started) * 1000))
            usage = _usage_after_error(case, exc)
            case.trace.append(
                build_span(
                    agent=agent_name,
                    attempt=attempt,
                    started_at=started_at,
                    duration_ms=duration_ms,
                    received=received,
                    output=None,
                    status="error",
                    usage=usage,
                    error="{0}: {1}".format(type(exc).__name__, exc),
                    case=case,
                )
            )
            if attempt >= max_attempts:
                _escalate(case, agent_name, exc, max_attempts)
                return case
            time.sleep(_delay(backoff_s, attempt))
            continue
        duration_ms = int(round((time.perf_counter() - started) * 1000))
        case.trace.append(
            build_span(
                agent=agent_name,
                attempt=attempt,
                started_at=started_at,
                duration_ms=duration_ms,
                received=received,
                output=snapshot_output(agent_name, case),
                status="ok",
                usage=dict(case.last_usage),
                case=case,
            )
        )
        return case
    return case


def _escalate(case: CaseRecord, agent_name: str, exc: BaseException, attempts: int) -> None:
    case.status = "escalated"
    case.recommendation = {
        "decision": "refer",
        "rationale": "{0} failed after {1} attempts: {2}".format(agent_name, attempts, exc),
        "source": "escalation",
        "model_decision": None,
        "final_decision": "refer",
        "guard_reason": None,
    }


def _usage_after_error(case: CaseRecord, exc: BaseException) -> Dict[str, int]:
    prompt = getattr(exc, "prompt_tokens", None)
    completion = getattr(exc, "completion_tokens", None)
    if prompt is None and completion is None:
        return dict(case.last_usage)
    return {
        "prompt_tokens": int(prompt or 0),
        "completion_tokens": int(completion or 0),
    }


def _delay(backoff_s: Sequence[float], attempt: int) -> float:
    if not backoff_s:
        return 0
    index = min(attempt - 1, len(backoff_s) - 1)
    return float(backoff_s[index])
