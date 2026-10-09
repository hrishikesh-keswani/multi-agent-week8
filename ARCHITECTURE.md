# Architecture

This pipeline underwrites one insurance application at a time. The steps are fixed in advance. Each step reads and writes one shared case object in memory.

## High-level design

```mermaid
flowchart TB
  apps["data/applications.json<br/>submission text with an SSN"]
  bureau["data/bureau.json<br/>keyed by SSN"]
  orch["Orchestrator<br/>run_pipeline"]
  case["CaseRecord<br/>one object in memory"]
  ollama["Local Ollama<br/>qwen3:8b"]

  apps --> orch
  orch --> case
  case --> intake["1. Intake"]
  intake --> enrich["2. Enrichment"]
  bureau --> enrich
  enrich --> risk["3. Risk scoring"]
  risk --> rec["4. Recommendation"]
  rec --> guard["Policy guard"]

  intake --> ollama
  enrich --> ollama
  risk --> ollama
  rec --> ollama

  guard --> done["status = completed<br/>approve, deny, or refer"]
  orch -->|"SSN not in bureau"| human["Human review<br/>status = escalated, decision = refer"]
  intake -->|"still failing after 3 tries"| human
  enrich -->|"still failing after 3 tries"| human
  risk -->|"still failing after 3 tries"| human
  risk -->|"model and code bands disagree"| human
  rec -->|"still failing after 3 tries"| human
  guard -->|"decision = refer"| human

  done --> traces["traces/SSN.json"]
  human --> traces
  human -->|"run_failure.py only"| failtraces["failure-traces/SSN.json"]
  traces --> analysis["ANALYSIS.md"]
  failtraces --> analysis
```

An application is one sentence. A regex reads the SSN out of that sentence and uses it as the case id. The bureau is a local JSON file, not a model call.

`run_pipeline` builds one `CaseRecord` and passes that same object through intake, enrichment, risk scoring, and recommendation. The next agent sees the previous write because both hold that object. Nothing is saved between agents. The JSON under `traces/` is written only after the case finishes.

Each agent makes one JSON chat to local Ollama `qwen3:8b`. A policy guard can change an `approve` to `refer` when the score is 75 or higher or required intake fields are missing.

Risk scoring also computes a deterministic score from the bureau row in code. Both scores are mapped to low, medium, or high. If the bands agree, the case keeps the higher score. If they disagree, the model's number is not trusted on its own.

A finished `refer` is a normal outcome: `status = completed`, `source = model`. Three things stop the chain with `status = escalated`, `decision = refer`, `source = escalation`: a missing bureau SSN, any agent that still fails after three tries, or a risk band disagreement. Later agents do not run. A disagreement is not retried, because the model call succeeded.

`ANALYSIS.md` totals completed cases only. Escalated cases, from `traces/` and `failure-traces/`, are listed in their own section with the time and tokens spent before they stopped.

There is no cross-case memory. One application cannot see another.

### Run one case

`python3 quote.py "Priya Shah, 31, librarian in Vermont. ... SSN 900-01-0001."` runs a single sentence through the same `run_pipeline`, prints the span summary, and writes `quotes/{ssn}.json`. That folder is ignored by git and is not read by the cost analysis, so ad hoc quotes never change the batch analysis. There is no warm-up call, so a cold model makes the first quote slower than the batch numbers. Exit code 0 means completed, 1 means escalated, and 2 means the text had no SSN. `--no-save` prints without writing a file.

## Low-level design

One case through `run_pipeline`. The same `CaseRecord` is passed down the left column. Each box names the function, what it reads, and what it writes.

```mermaid
flowchart TD
  start["run_pipeline(raw_application)"]
  ssn{"extract_ssn finds AAA-GG-SSSS?"}
  crash["ValueError before any agent"]
  record["CaseRecord.from_application<br/>case_id = SSN<br/>raw_application.ssn = SSN<br/>status = in_progress"]
  known{"lookup_bureau(case_id) found?"}
  unknown["No agents called<br/>bureau_lookup span, status = escalated<br/>decision = refer, source = escalation"]

  intake["intake_agent via call_with_retry<br/>read: raw_application<br/>write: case.intake<br/>ssn copied from case_id<br/>missing full_name raises"]
  enrich["enrichment_agent via call_with_retry<br/>read: case.intake<br/>lookup the bureau row again<br/>write: case.enrichment<br/>bureau object copied in code<br/>empty summary raises"]
  risk["risk_scoring_agent via call_with_retry<br/>read: intake and enrichment<br/>write: case.risk<br/>score must be an integer 0 to 100<br/>deterministic_score computed in code"]
  agree{"llm band equals<br/>deterministic band?"}
  disagree["status = escalated<br/>decision = refer, source = escalation<br/>score and band = null"]
  rec["recommendation_agent via call_with_retry<br/>read: intake, enrichment, and risk<br/>model returns decision and rationale"]
  guard{"model said approve,<br/>and score is 75 or higher<br/>or a required field is missing?"}
  changed["final_decision = refer<br/>guard_reason set"]
  unchanged["final_decision = model decision<br/>guard_reason = null"]
  done["status = completed<br/>to_document written to traces/SSN.json"]

  start --> ssn
  ssn -->|no| crash
  ssn -->|yes| record
  record --> known
  known -->|no| unknown
  known -->|yes| intake
  intake -->|span status ok| enrich
  enrich -->|span status ok| risk
  risk -->|span status ok| agree
  agree -->|no| disagree
  agree -->|"yes, score = higher of the two"| rec
  rec --> guard
  guard -->|yes| changed
  guard -->|no| unchanged
  changed --> done
  unchanged --> done
```

A failed attempt does not jump back to intake. It stays inside `call_with_retry` for that same agent. After three failures the pipeline stops, so the agents below that box never run.

```mermaid
flowchart TD
  enter["call_with_retry<br/>attempt starts at 1<br/>snapshot_input copied onto the span"]
  timeout{"TimeoutInjectingClient<br/>and this agent is risk_scoring?"}
  boom["TimeoutError<br/>simulated upstream timeout<br/>no HTTP call"]
  post["POST /api/chat<br/>model qwen3:8b<br/>temperature 0, format json, think false"]
  parsed{"body is one JSON object?"}
  repair["one repair chat<br/>tokens and time added to this same attempt"]
  repaired{"repair body is one JSON object?"}
  bad["LLMError<br/>combined token counts kept"]
  write["agent writes its section on the case"]
  okspan["append span<br/>status = ok, output = that section<br/>return the same case"]
  errspan["append span<br/>status = error, output = null"]
  again{"attempt is under 3?"}
  sleep["sleep 0.05 s, then 0.1 s<br/>attempt = attempt + 1"]
  escalate["append no further agents<br/>status = escalated<br/>decision = refer, source = escalation"]

  enter --> timeout
  timeout -->|yes| boom --> errspan
  timeout -->|no| post --> parsed
  parsed -->|yes| write
  parsed -->|no| repair --> repaired
  repaired -->|yes| write
  repaired -->|no| bad --> errspan
  write -->|section invalid| errspan
  write -->|section valid| okspan
  errspan --> again
  again -->|yes| sleep --> enter
  again -->|no| escalate
```
