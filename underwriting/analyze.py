"""Cost and latency totals from captured traces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from underwriting.paths import FAILURE_TRACE_DIR, ROOT, TRACE_DIR

# Illustrative hosted small-model rates. Local Ollama bills nothing.
INPUT_USD_PER_MILLION = 0.10
OUTPUT_USD_PER_MILLION = 0.40
REALTIME_BUDGET_MS = 10_000


def load_case_traces(*trace_dirs: Path) -> List[Dict[str, Any]]:
    """Every trace in the given folders, completed and escalated, sorted by case id."""
    documents = []
    for trace_dir in trace_dirs:
        if not trace_dir.exists():
            continue
        for path in sorted(trace_dir.glob("*.json")):
            with path.open(encoding="utf-8") as handle:
                documents.append(json.load(handle))
    documents.sort(key=lambda document: str(document.get("case_id")))
    return documents


def render_analysis(all_documents: List[Dict[str, Any]]) -> str:
    documents = [d for d in all_documents if d.get("status") != "escalated"]
    escalated = [d for d in all_documents if d.get("status") == "escalated"]
    lines = [
        "# Cost and latency",
        "",
        "A warm-up call was made before these cases so Ollama had already loaded the model. "
        "The latency numbers below are steady-state generation and do not include that cold start. "
        "Warm-up time and tokens are excluded from the totals.",
        "",
        "JSON repair time and tokens, when a repair happened, are already inside the agent span "
        "that produced these totals.",
        "",
        "Actual API cost is $0 because inference ran on local Ollama.",
        "",
        "The hosted equivalent prices the same tokens at ${0:.2f} per million input tokens and "
        "${1:.2f} per million output tokens. That figure is a comparison rate, not a bill.".format(
            INPUT_USD_PER_MILLION,
            OUTPUT_USD_PER_MILLION,
        ),
        "",
    ]
    if not documents:
        lines.append("No completed case traces were found.")
        lines.append("")
        lines.extend(_escalated_section(escalated))
        return "\n".join(lines) + "\n"

    grand_prompt = 0
    grand_completion = 0
    grand_ms = 0
    slowest_ms = 0
    slowest_id = documents[0]["case_id"]

    lines.append("## Per case")
    lines.append("")
    for document in documents:
        totals = _totals(document)
        grand_prompt += totals["prompt_tokens"]
        grand_completion += totals["completion_tokens"]
        grand_ms += totals["duration_ms"]
        if totals["duration_ms"] >= slowest_ms:
            slowest_ms = totals["duration_ms"]
            slowest_id = document["case_id"]
        hosted = _hosted_usd(totals["prompt_tokens"], totals["completion_tokens"])
        lines.append("### {0}".format(document["case_id"]))
        lines.append("")
        lines.append("- Status: {0}".format(document.get("status")))
        decision = (document.get("recommendation") or {}).get("decision")
        lines.append("- Decision: {0}".format(decision))
        lines.append("- Latency: {0} ms ({1:.1f} s)".format(totals["duration_ms"], totals["duration_ms"] / 1000))
        lines.append(
            "- Tokens: {0} prompt, {1} completion".format(
                totals["prompt_tokens"],
                totals["completion_tokens"],
            )
        )
        lines.append("- Actual API cost: $0")
        lines.append("- Hosted equivalent: ${0:.6f}".format(hosted))
        lines.append("")
        lines.append("| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |")
        lines.append("| --- | --- | --- | --- | --- |")
        for agent, row in totals["agents"].items():
            lines.append(
                "| {0} | {1} | {2} | {3} | {4} |".format(
                    agent,
                    row["attempts"],
                    row["duration_ms"],
                    row["prompt_tokens"],
                    row["completion_tokens"],
                )
            )
        lines.append("")

    hosted_total = _hosted_usd(grand_prompt, grand_completion)
    lines.append("## All completed cases")
    lines.append("")
    lines.append("- Cases: {0}".format(len(documents)))
    lines.append("- Total latency: {0} ms ({1:.1f} s)".format(grand_ms, grand_ms / 1000))
    lines.append("- Total tokens: {0} prompt, {1} completion".format(grand_prompt, grand_completion))
    lines.append("- Actual API cost: $0")
    lines.append("- Hosted equivalent: ${0:.6f}".format(hosted_total))
    lines.append("")
    lines.append("## Real-time versus batch")
    lines.append("")
    lines.append(
        "A real-time underwriting response needs the full case, the slowest one here being "
        "{0} at {1} ms ({2:.1f} s), to finish in under {3} ms.".format(
            slowest_id,
            slowest_ms,
            slowest_ms / 1000,
            REALTIME_BUDGET_MS,
        )
    )
    lines.append("")
    if slowest_ms <= REALTIME_BUDGET_MS:
        lines.append(
            "The slowest measured case is inside that budget, so this pipeline can serve a real-time use case "
            "on this machine at the current model size."
        )
    else:
        lines.append(
            "The slowest measured case is over that budget. Four serial generations on local qwen3:8b "
            "are a steady-state batch workload. An overnight batch has room for this latency. "
            "A person waiting on a quote does not."
        )
    lines.append("")
    lines.extend(_escalated_section(escalated))
    return "\n".join(lines)


def _escalated_section(escalated: List[Dict[str, Any]]) -> List[str]:
    lines = ["## Escalated cases", ""]
    if not escalated:
        lines.append("No case was escalated to human review.")
        lines.append("")
        return lines
    lines.append(
        "These cases stopped before a model recommendation and went to human review. "
        "Their time and tokens are not in the completed-case totals above. "
        "Time spent on agents that did finish is still real work, so it is listed here."
    )
    lines.append("")
    lines.append("| SSN | Stopped at | Reason | Latency | Prompt tokens | Completion tokens | Hosted equivalent |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for document in escalated:
        totals = _totals(document)
        hosted = _hosted_usd(totals["prompt_tokens"], totals["completion_tokens"])
        lines.append(
            "| {0} | {1} | {2} | {3:.1f} s | {4} | {5} | ${6:.6f} |".format(
                document.get("case_id"),
                _stopped_at(document),
                _escalation_reason(document),
                totals["duration_ms"] / 1000,
                totals["prompt_tokens"],
                totals["completion_tokens"],
                hosted,
            )
        )
    lines.append("")
    return lines


def _stopped_at(document: Dict[str, Any]) -> str:
    spans = document.get("spans") or []
    if not spans:
        return "before any agent"
    return str(spans[-1].get("agent"))


def _escalation_reason(document: Dict[str, Any]) -> str:
    recommendation = document.get("recommendation") or {}
    rationale = str(recommendation.get("rationale") or "")
    risk = document.get("risk") or {}
    if risk.get("agreed") is False:
        return "risk bands disagree: llm {0} ({1}) vs deterministic {2} ({3})".format(
            risk.get("llm_band"),
            risk.get("llm_score"),
            risk.get("deterministic_band"),
            risk.get("deterministic_score"),
        )
    spans = document.get("spans") or []
    errors = [span for span in spans if span.get("status") == "error"]
    if errors:
        return "{0} attempt(s) failed: {1}".format(len(errors), errors[-1].get("error"))
    if rationale:
        return rationale
    return "escalated"


def write_analysis(
    trace_dir: Optional[Path] = None,
    destination: Optional[Path] = None,
    failure_dir: Optional[Path] = None,
) -> Path:
    trace_dir = trace_dir or TRACE_DIR
    failure_dir = FAILURE_TRACE_DIR if failure_dir is None else failure_dir
    destination = destination or (ROOT / "ANALYSIS.md")
    documents = load_case_traces(trace_dir, failure_dir)
    destination.write_text(render_analysis(documents), encoding="utf-8")
    return destination


def _totals(document: Dict[str, Any]) -> Dict[str, Any]:
    agents: Dict[str, Dict[str, int]] = {}
    prompt_tokens = 0
    completion_tokens = 0
    duration_ms = 0
    for span in document.get("spans") or []:
        usage = span.get("token_usage") or {}
        prompt = int(usage.get("prompt_tokens") or 0)
        completion = int(usage.get("completion_tokens") or 0)
        elapsed = int(span.get("duration_ms") or 0)
        prompt_tokens += prompt
        completion_tokens += completion
        duration_ms += elapsed
        agent = str(span.get("agent"))
        row = agents.setdefault(
            agent,
            {"attempts": 0, "duration_ms": 0, "prompt_tokens": 0, "completion_tokens": 0},
        )
        row["attempts"] += 1
        row["duration_ms"] += elapsed
        row["prompt_tokens"] += prompt
        row["completion_tokens"] += completion
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "duration_ms": duration_ms,
        "agents": agents,
    }


def _hosted_usd(prompt_tokens: int, completion_tokens: int) -> float:
    return (prompt_tokens * INPUT_USD_PER_MILLION + completion_tokens * OUTPUT_USD_PER_MILLION) / 1_000_000


def main() -> None:
    path = write_analysis()
    print("wrote {0}".format(path))


if __name__ == "__main__":
    main()
