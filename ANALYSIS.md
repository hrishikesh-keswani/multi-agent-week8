# Cost and latency

A warm-up call was made before these cases so Ollama had already loaded the model. The latency numbers below are steady-state generation and do not include that cold start. Warm-up time and tokens are excluded from the totals.

JSON repair time and tokens, when a repair happened, are already inside the agent span that produced these totals.

Actual API cost is $0 because inference ran on local Ollama.

The hosted equivalent prices the same tokens at $0.10 per million input tokens and $0.40 per million output tokens. That figure is a comparison rate, not a bill.

## Per case

### APP-CLEAN

- Status: completed
- Decision: approve
- Latency: 15287 ms (15.3 s)
- Tokens: 1170 prompt, 338 completion
- Actual API cost: $0
- Hosted equivalent: $0.000252

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 3915 | 184 | 90 |
| enrichment | 1 | 5473 | 233 | 126 |
| risk_scoring | 1 | 2386 | 354 | 48 |
| recommendation | 1 | 3513 | 399 | 74 |

### APP-COAST

- Status: completed
- Decision: deny
- Latency: 19335 ms (19.3 s)
- Tokens: 1247 prompt, 410 completion
- Actual API cost: $0
- Hosted equivalent: $0.000289

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4459 | 187 | 101 |
| enrichment | 1 | 6653 | 243 | 149 |
| risk_scoring | 1 | 2663 | 388 | 49 |
| recommendation | 1 | 5560 | 429 | 111 |

### APP-THIN

- Status: completed
- Decision: refer
- Latency: 15332 ms (15.3 s)
- Tokens: 1116 prompt, 326 completion
- Actual API cost: $0
- Hosted equivalent: $0.000242

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 3873 | 166 | 88 |
| enrichment | 1 | 4869 | 230 | 110 |
| risk_scoring | 1 | 2740 | 336 | 51 |
| recommendation | 1 | 3850 | 384 | 77 |

## All cases

- Cases: 3
- Total latency: 49954 ms (50.0 s)
- Total tokens: 3533 prompt, 1074 completion
- Actual API cost: $0
- Hosted equivalent: $0.000783

## Real-time versus batch

A real-time underwriting response needs the full case, the slowest one here being APP-COAST at 19335 ms (19.3 s), to finish in under 10000 ms.

The slowest measured case is over that budget. Four serial generations on local qwen3:8b are a steady-state batch workload. An overnight batch has room for this latency. A person waiting on a quote does not.
