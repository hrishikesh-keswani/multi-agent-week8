# State and memory

## Decision

This pipeline uses a **shared case record**, passed explicitly through a fixed orchestrator.

It is not message passing, and it is not a hidden global. Each agent receives the same `CaseRecord`, reads the sections it needs, and writes its own section back. The orchestrator is a fixed sequence: intake, enrichment, risk scoring, recommendation. The steps are known in advance, so this is a workflow (prompt chaining), not an agent that decides what to run next.

## Why

An underwriting file is the unit of work. Enrichment needs the normalized application, risk scoring needs the bureau facts, and the recommendation needs the score. A failed step has to leave the earlier sections intact for a human underwriter. The trace snapshots that same record, so the log and the case stay aligned.

There is no cross-case memory. One application cannot see another.

The record lives in `underwriting/state.py`:

- `raw_application` — original submission
- `intake` — normalized applicant, coverage, household
- `enrichment` — bureau facts plus the model's gap and red-flag summary
- `risk` — the model's score and band, a deterministic score and band computed in code from the bureau row, whether the two bands agree, the final score and band (null when they disagree), and factors
- `recommendation` — `approve`, `deny`, or `refer`, with a rationale and a `source` of `model` or `escalation`
- `status` — `in_progress`, `completed`, or `escalated`

## Flow

TraceLog sits to the left of the case flow and HumanReview sits to the right, so those edges leave the chain sideways.

```mermaid
flowchart LR
  trace[TraceLog]

  subgraph caseFlow [Case flow]
    direction TB
    raw[RawApplication] --> intake[intake_agent]
    intake --> enrich[enrichment_agent]
    enrich --> risk[risk_scoring_agent]
    risk --> recommend[recommendation_agent]
  end

  human[HumanReview]

  intake --> trace
  enrich --> trace
  risk --> trace
  recommend --> trace
  risk -->|"agent fails after retries"| human
  risk -->|"model and code bands disagree"| human
  recommend -->|"decision = refer"| human
```

Shared CaseRecord is read and written by every agent.

If the submission contains an SSN that is not a key in the bureau, the case goes to HumanReview immediately and no agent is called.

The failure arrow is drawn from `risk_scoring_agent` because that is the simulated timeout. The same retry-then-escalate path applies to every agent: if intake, enrichment, risk scoring, or recommendation still fails after retries, the case goes to HumanReview and later agents do not run. A normal `decision = refer` from `recommendation_agent` is a separate path into HumanReview. That case finished successfully.

Risk scoring has one more path into HumanReview. The agent also scores the bureau row in code with fixed points: a base of 20, plus 15 per prior claim, 0 to 35 for the credit band, 0 to 25 for the occupation class, and 25 for a flood zone, capped at 100. Both scores are mapped to a band: high at 75 or above, medium at 35 or above, otherwise low. If the model's band and the code's band agree, the case continues with the higher of the two scores. If they disagree, the case is escalated with `decision = refer`, `source = escalation`, and the rationale names both bands. That is not retried, because the call itself succeeded and the risk span is `ok`. Recommendation does not run.

## What each agent reads and writes

- **Intake** reads `raw_application`. The case id is the SSN parsed from that submission. Writes `intake`.
- **Enrichment** reads `intake`, then looks up `data/bureau.json` by that SSN. Writes `enrichment`.
- **Risk** reads `intake` and `enrichment`. Writes `risk`. On a band disagreement it also writes `status` and `recommendation`.
- **Recommendation** reads `intake`, `enrichment`, and `risk`. Writes `recommendation`.

A policy guard stops an `approve` when the score is 75 or higher, or when required sections are missing. The recommendation span always stores `model_decision`, `final_decision`, and `guard_reason`. When the guard changes the decision, `guard_reason` says why. When it does not, `guard_reason` is null. `decision = refer` sends the finished case to a human underwriter.
