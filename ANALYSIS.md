# Cost and latency

A warm-up call was made before these cases so Ollama had already loaded the model. The latency numbers below are steady-state generation and do not include that cold start. Warm-up time and tokens are excluded from the totals.

JSON repair time and tokens, when a repair happened, are already inside the agent span that produced these totals.

Actual API cost is $0 because inference ran on local Ollama.

The hosted equivalent prices the same tokens at $0.10 per million input tokens and $0.40 per million output tokens. That figure is a comparison rate, not a bill.

## Per case

### 900-01-0001

- Status: completed
- Decision: approve
- Latency: 15160 ms (15.2 s)
- Tokens: 1269 prompt, 338 completion
- Actual API cost: $0
- Hosted equivalent: $0.000262

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4088 | 206 | 98 |
| enrichment | 1 | 5286 | 241 | 124 |
| risk_scoring | 1 | 2464 | 368 | 48 |
| recommendation | 1 | 3322 | 454 | 68 |

### 900-01-0002

- Status: completed
- Decision: approve
- Latency: 16644 ms (16.6 s)
- Tokens: 1316 prompt, 360 completion
- Actual API cost: $0
- Hosted equivalent: $0.000276

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4517 | 210 | 104 |
| enrichment | 1 | 5835 | 247 | 136 |
| risk_scoring | 1 | 2866 | 386 | 56 |
| recommendation | 1 | 3426 | 473 | 64 |

### 900-01-0003

- Status: completed
- Decision: approve
- Latency: 14697 ms (14.7 s)
- Tokens: 1220 prompt, 311 completion
- Actual API cost: $0
- Hosted equivalent: $0.000246

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4294 | 203 | 99 |
| enrichment | 1 | 4483 | 241 | 102 |
| risk_scoring | 1 | 2468 | 346 | 46 |
| recommendation | 1 | 3452 | 430 | 64 |

### 900-01-0004

- Status: completed
- Decision: approve
- Latency: 15330 ms (15.3 s)
- Tokens: 1258 prompt, 334 completion
- Actual API cost: $0
- Hosted equivalent: $0.000259

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4397 | 207 | 100 |
| enrichment | 1 | 4803 | 243 | 115 |
| risk_scoring | 1 | 2769 | 361 | 56 |
| recommendation | 1 | 3361 | 447 | 63 |

### 900-01-0005

- Status: completed
- Decision: approve
- Latency: 15097 ms (15.1 s)
- Tokens: 1235 prompt, 337 completion
- Actual API cost: $0
- Hosted equivalent: $0.000258

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4191 | 203 | 100 |
| enrichment | 1 | 4484 | 242 | 107 |
| risk_scoring | 1 | 2572 | 352 | 55 |
| recommendation | 1 | 3850 | 438 | 75 |

### 900-01-0006

- Status: completed
- Decision: approve
- Latency: 14126 ms (14.1 s)
- Tokens: 1209 prompt, 314 completion
- Actual API cost: $0
- Hosted equivalent: $0.000246

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4022 | 201 | 96 |
| enrichment | 1 | 4439 | 237 | 106 |
| risk_scoring | 1 | 2237 | 346 | 47 |
| recommendation | 1 | 3428 | 425 | 65 |

### 900-01-0007

- Status: completed
- Decision: approve
- Latency: 16514 ms (16.5 s)
- Tokens: 1275 prompt, 355 completion
- Actual API cost: $0
- Hosted equivalent: $0.000269

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4196 | 203 | 100 |
| enrichment | 1 | 5320 | 243 | 125 |
| risk_scoring | 1 | 2931 | 371 | 57 |
| recommendation | 1 | 4067 | 458 | 73 |

### 900-01-0009

- Status: completed
- Decision: deny
- Latency: 18290 ms (18.3 s)
- Tokens: 1373 prompt, 393 completion
- Actual API cost: $0
- Hosted equivalent: $0.000295

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4722 | 212 | 108 |
| enrichment | 1 | 6982 | 250 | 157 |
| risk_scoring | 1 | 2846 | 410 | 56 |
| recommendation | 1 | 3740 | 501 | 72 |

### 900-01-0010

- Status: completed
- Decision: deny
- Latency: 18057 ms (18.1 s)
- Tokens: 1298 prompt, 371 completion
- Actual API cost: $0
- Hosted equivalent: $0.000278

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4721 | 205 | 105 |
| enrichment | 1 | 6148 | 246 | 133 |
| risk_scoring | 1 | 2740 | 382 | 50 |
| recommendation | 1 | 4448 | 465 | 83 |

### 900-01-0011

- Status: completed
- Decision: deny
- Latency: 18493 ms (18.5 s)
- Tokens: 1337 prompt, 380 completion
- Actual API cost: $0
- Hosted equivalent: $0.000286

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4812 | 207 | 106 |
| enrichment | 1 | 6678 | 248 | 148 |
| risk_scoring | 1 | 2994 | 399 | 50 |
| recommendation | 1 | 4009 | 483 | 76 |

### 900-01-0012

- Status: completed
- Decision: deny
- Latency: 18031 ms (18.0 s)
- Tokens: 1360 prompt, 377 completion
- Actual API cost: $0
- Hosted equivalent: $0.000287

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4878 | 211 | 111 |
| enrichment | 1 | 6699 | 254 | 151 |
| risk_scoring | 1 | 2697 | 408 | 45 |
| recommendation | 1 | 3757 | 487 | 70 |

### 900-01-0013

- Status: completed
- Decision: deny
- Latency: 18897 ms (18.9 s)
- Tokens: 1346 prompt, 400 completion
- Actual API cost: $0
- Hosted equivalent: $0.000295

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4503 | 203 | 103 |
| enrichment | 1 | 7122 | 245 | 165 |
| risk_scoring | 1 | 3175 | 405 | 56 |
| recommendation | 1 | 4097 | 493 | 76 |

### 900-01-0014

- Status: completed
- Decision: deny
- Latency: 17697 ms (17.7 s)
- Tokens: 1333 prompt, 371 completion
- Actual API cost: $0
- Hosted equivalent: $0.000282

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4448 | 204 | 102 |
| enrichment | 1 | 6773 | 244 | 156 |
| risk_scoring | 1 | 2476 | 403 | 39 |
| recommendation | 1 | 4000 | 482 | 74 |

### 900-01-0019

- Status: completed
- Decision: refer
- Latency: 14535 ms (14.5 s)
- Tokens: 1170 prompt, 305 completion
- Actual API cost: $0
- Hosted equivalent: $0.000239

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 3755 | 188 | 85 |
| enrichment | 1 | 4716 | 227 | 108 |
| risk_scoring | 1 | 2216 | 338 | 41 |
| recommendation | 1 | 3848 | 417 | 71 |

### 900-01-0020

- Status: completed
- Decision: refer
- Latency: 17097 ms (17.1 s)
- Tokens: 1264 prompt, 360 completion
- Actual API cost: $0
- Hosted equivalent: $0.000270

| Agent | Attempts | Latency ms | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| intake | 1 | 4282 | 195 | 98 |
| enrichment | 1 | 5818 | 240 | 129 |
| risk_scoring | 1 | 2521 | 372 | 47 |
| recommendation | 1 | 4476 | 457 | 86 |

## All completed cases

- Cases: 15
- Total latency: 248665 ms (248.7 s)
- Total tokens: 19263 prompt, 5306 completion
- Actual API cost: $0
- Hosted equivalent: $0.004049

## Real-time versus batch

A real-time underwriting response needs the full case, the slowest one here being 900-01-0013 at 18897 ms (18.9 s), to finish in under 10000 ms.

The slowest measured case is over that budget. Four serial generations on local qwen3:8b are a steady-state batch workload. An overnight batch has room for this latency. A person waiting on a quote does not.

## Escalated cases

These cases stopped before a model recommendation and went to human review. Their time and tokens are not in the completed-case totals above. Time spent on agents that did finish is still real work, so it is listed here.

| SSN | Stopped at | Reason | Latency | Prompt tokens | Completion tokens | Hosted equivalent |
| --- | --- | --- | --- | --- | --- | --- |
| 900-01-0008 | risk_scoring | risk bands disagree: llm medium (35) vs deterministic low (25) | 10.4 s | 756 | 223 | $0.000165 |
| 900-01-0015 | risk_scoring | risk bands disagree: llm high (85) vs deterministic medium (45) | 11.7 s | 776 | 259 | $0.000181 |
| 900-01-0016 | risk_scoring | risk bands disagree: llm low (20) vs deterministic medium (50) | 10.1 s | 742 | 224 | $0.000164 |
| 900-01-0017 | risk_scoring | risk bands disagree: llm low (20) vs deterministic medium (50) | 10.4 s | 774 | 237 | $0.000172 |
| 900-01-0018 | risk_scoring | risk bands disagree: llm low (30) vs deterministic medium (35) | 12.1 s | 797 | 273 | $0.000189 |
| 900-10-0099 | risk_scoring | 3 attempt(s) failed: TimeoutError: simulated upstream timeout | 10.2 s | 427 | 217 | $0.000130 |
