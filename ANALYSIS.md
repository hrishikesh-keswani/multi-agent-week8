# Cost and latency

A warm-up call was made before these cases so Ollama had already loaded the model. The latency numbers below are steady-state generation and do not include that cold start. Warm-up time and tokens are excluded from the totals.

JSON repair time and tokens, when a repair happened, are already inside the agent span that produced these totals.

Actual API cost is $0 because inference ran on local Ollama.

The hosted equivalent prices the same tokens at $0.10 per million input tokens and $0.40 per million output tokens. That figure is a comparison rate, not a bill.

## Per case

### 900-01-0001

- Status: completed
- Decision: approve
- Latency: 18392 ms (18.4 s)
- Tokens: 1269 prompt, 338 completion
- Actual API cost: $0
- Hosted equivalent: $0.000262

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 5108 | 206 | 98 |
| enrichment | 1 | 6371 | 241 | 124 |
| risk_scoring | 1 | 2844 | 368 | 48 |
| recommendation | 1 | 4069 | 454 | 68 |

### 900-01-0002

- Status: completed
- Decision: approve
- Latency: 19156 ms (19.2 s)
- Tokens: 1316 prompt, 360 completion
- Actual API cost: $0
- Hosted equivalent: $0.000276

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 5102 | 210 | 104 |
| enrichment | 1 | 6786 | 247 | 136 |
| risk_scoring | 1 | 3287 | 386 | 56 |
| recommendation | 1 | 3981 | 473 | 64 |

### 900-01-0003

- Status: completed
- Decision: approve
- Latency: 17142 ms (17.1 s)
- Tokens: 1220 prompt, 311 completion
- Actual API cost: $0
- Hosted equivalent: $0.000246

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 5054 | 203 | 99 |
| enrichment | 1 | 5212 | 241 | 102 |
| risk_scoring | 1 | 2836 | 346 | 46 |
| recommendation | 1 | 4040 | 430 | 64 |

### 900-01-0004

- Status: completed
- Decision: approve
- Latency: 18299 ms (18.3 s)
- Tokens: 1258 prompt, 334 completion
- Actual API cost: $0
- Hosted equivalent: $0.000259

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 5038 | 207 | 100 |
| enrichment | 1 | 5956 | 243 | 115 |
| risk_scoring | 1 | 3296 | 361 | 56 |
| recommendation | 1 | 4009 | 447 | 63 |

### 900-01-0005

- Status: completed
- Decision: approve
- Latency: 18132 ms (18.1 s)
- Tokens: 1235 prompt, 337 completion
- Actual API cost: $0
- Hosted equivalent: $0.000258

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 5127 | 203 | 100 |
| enrichment | 1 | 5403 | 242 | 107 |
| risk_scoring | 1 | 3052 | 352 | 55 |
| recommendation | 1 | 4550 | 438 | 75 |

### 900-01-0006

- Status: completed
- Decision: approve
- Latency: 16996 ms (17.0 s)
- Tokens: 1209 prompt, 314 completion
- Actual API cost: $0
- Hosted equivalent: $0.000246

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4946 | 201 | 96 |
| enrichment | 1 | 5347 | 237 | 106 |
| risk_scoring | 1 | 2708 | 346 | 47 |
| recommendation | 1 | 3995 | 425 | 65 |

### 900-01-0007

- Status: completed
- Decision: approve
- Latency: 19325 ms (19.3 s)
- Tokens: 1275 prompt, 355 completion
- Actual API cost: $0
- Hosted equivalent: $0.000269

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 5086 | 203 | 100 |
| enrichment | 1 | 6276 | 243 | 125 |
| risk_scoring | 1 | 3567 | 371 | 57 |
| recommendation | 1 | 4396 | 458 | 73 |

### 900-01-0009

- Status: completed
- Decision: deny
- Latency: 20948 ms (20.9 s)
- Tokens: 1373 prompt, 393 completion
- Actual API cost: $0
- Hosted equivalent: $0.000295

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 5413 | 212 | 108 |
| enrichment | 1 | 7885 | 250 | 157 |
| risk_scoring | 1 | 3249 | 410 | 56 |
| recommendation | 1 | 4401 | 501 | 72 |

### 900-01-0010

- Status: completed
- Decision: deny
- Latency: 20301 ms (20.3 s)
- Tokens: 1298 prompt, 371 completion
- Actual API cost: $0
- Hosted equivalent: $0.000278

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 5216 | 205 | 105 |
| enrichment | 1 | 6771 | 246 | 133 |
| risk_scoring | 1 | 3076 | 382 | 50 |
| recommendation | 1 | 5238 | 465 | 83 |

### 900-01-0011

- Status: completed
- Decision: deny
- Latency: 20886 ms (20.9 s)
- Tokens: 1337 prompt, 380 completion
- Actual API cost: $0
- Hosted equivalent: $0.000286

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 5550 | 207 | 106 |
| enrichment | 1 | 7482 | 248 | 148 |
| risk_scoring | 1 | 3279 | 399 | 50 |
| recommendation | 1 | 4575 | 483 | 76 |

### 900-01-0012

- Status: completed
- Decision: deny
- Latency: 20788 ms (20.8 s)
- Tokens: 1360 prompt, 377 completion
- Actual API cost: $0
- Hosted equivalent: $0.000287

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 5530 | 211 | 111 |
| enrichment | 1 | 7596 | 254 | 151 |
| risk_scoring | 1 | 3179 | 408 | 45 |
| recommendation | 1 | 4483 | 487 | 70 |

### 900-01-0013

- Status: completed
- Decision: deny
- Latency: 21776 ms (21.8 s)
- Tokens: 1346 prompt, 400 completion
- Actual API cost: $0
- Hosted equivalent: $0.000295

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 5336 | 203 | 103 |
| enrichment | 1 | 8293 | 245 | 165 |
| risk_scoring | 1 | 3561 | 405 | 56 |
| recommendation | 1 | 4586 | 493 | 76 |

### 900-01-0014

- Status: completed
- Decision: deny
- Latency: 20785 ms (20.8 s)
- Tokens: 1333 prompt, 371 completion
- Actual API cost: $0
- Hosted equivalent: $0.000282

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 5341 | 204 | 102 |
| enrichment | 1 | 8023 | 244 | 156 |
| risk_scoring | 1 | 2845 | 403 | 39 |
| recommendation | 1 | 4576 | 482 | 74 |

### 900-01-0019

- Status: completed
- Decision: refer
- Latency: 16673 ms (16.7 s)
- Tokens: 1170 prompt, 305 completion
- Actual API cost: $0
- Hosted equivalent: $0.000239

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4419 | 188 | 85 |
| enrichment | 1 | 5415 | 227 | 108 |
| risk_scoring | 1 | 2538 | 338 | 41 |
| recommendation | 1 | 4301 | 417 | 71 |

### 900-01-0020

- Status: completed
- Decision: refer
- Latency: 19047 ms (19.0 s)
- Tokens: 1264 prompt, 360 completion
- Actual API cost: $0
- Hosted equivalent: $0.000270

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4870 | 195 | 98 |
| enrichment | 1 | 6373 | 240 | 129 |
| risk_scoring | 1 | 2809 | 372 | 47 |
| recommendation | 1 | 4995 | 457 | 86 |

## All completed cases

- Cases: 15
- Total latency: 288646 ms (288.6 s)
- Total tokens: 19263 prompt, 5306 completion
- Actual API cost: $0
- Hosted equivalent: $0.004049

## Real-time versus batch

A real-time underwriting response needs the full case, the slowest one here being 900-01-0013 at 21776 ms (21.8 s), to finish in under 10000 ms.

The slowest measured case is over that budget. Four serial generations on local qwen3:8b are a steady-state batch workload. An overnight batch has room for this latency. A person waiting on a quote does not.

## Escalated cases

These cases stopped before a model recommendation and went to human review. Their time and tokens are not in the completed-case totals above. Time spent on agents that did finish is still real work, so it is listed here.

| SSN | Stopped at | Reason | Latency | Prompt tokens | Completion tokens | Hosted equivalent |
| --- | --- | --- | --- | --- | --- | --- |
| 900-01-0008 | risk_scoring | risk bands disagree: llm medium (35) vs deterministic low (25) | 11.6 s | 756 | 223 | $0.000165 |
| 900-01-0015 | risk_scoring | risk bands disagree: llm high (85) vs deterministic medium (45) | 13.6 s | 776 | 259 | $0.000181 |
| 900-01-0016 | risk_scoring | risk bands disagree: llm low (20) vs deterministic medium (50) | 11.7 s | 742 | 224 | $0.000164 |
| 900-01-0017 | risk_scoring | risk bands disagree: llm low (20) vs deterministic medium (50) | 12.5 s | 774 | 237 | $0.000172 |
| 900-01-0018 | risk_scoring | risk bands disagree: llm low (30) vs deterministic medium (35) | 14.0 s | 797 | 273 | $0.000189 |
| 900-10-0099 | risk_scoring | 3 attempt(s) failed: TimeoutError: simulated upstream timeout | 10.7 s | 427 | 217 | $0.000130 |
