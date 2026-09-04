# Decision Drift Report

Project: **Synthetic Lab Platform**  
Review date: **2026-08-01**
Eligible events as of review date: **3 / 3**

## Status summary

| ACTIVE | AT_RISK | STALE | REPLACED |
| ---: | ---: | ---: | ---: |
| 0 | 1 | 2 | 0 |

## Use SQLite for experiment metadata

- Decision: `decision-local-store`
- Choice: Store experiment metadata in a local SQLite database.
- Status: **ACTIVE → STALE**
- Reversibility: `medium`
- Review schedule: **OVERDUE**

### Triggered premises

- **INVALIDATE** `rule-multiple-writers` via `event-team-growth`: `team.concurrent_writers` observed as `4`. The local storage choice assumed a single writer. Source: `synthetic://project/change-requests/collaboration`
- **WARNING** `rule-data-growth` via `event-team-growth`: `data.metadata_size_gb` observed as `2.4`. Metadata reached the review threshold recorded in the original decision. Source: `synthetic://project/change-requests/collaboration`

### Evidence freshness

- `evidence-january-load-test` expired on 2026-05-09: synthetic://benchmarks/2026-01-load-test

### Counterfactual alternatives

- **REOPENED:** Move metadata to PostgreSQL (triggered by `rule-data-growth`, `rule-multiple-writers`)
  - Originally rejected because: Operational overhead was unnecessary for a single-user prototype.

### Unknown observations

- All rule fact paths were observed at least once.

### Bounded next actions

- Run a 30-minute concurrent-write benchmark on the current workload.
- Compare migration cost and operational burden before changing storage.

## Use a compact model for triage

- Decision: `decision-small-model`
- Choice: Use a compact model for first-pass issue triage.
- Status: **ACTIVE → AT_RISK**
- Reversibility: `easy`

### Triggered premises

- **WARNING** `rule-frontier-price-drop` via `event-model-price`: `model.frontier_input_cost_per_million_usd` observed as `1.5`. The cost reason for rejecting a larger model may no longer hold. Source: `synthetic://pricing/2026-07`

### Evidence freshness

- No dated evidence has expired.

### Counterfactual alternatives

- **REOPENED:** Re-evaluate a larger model for difficult cases (triggered by `rule-frontier-price-drop`)
  - Originally rejected because: It exceeded the recorded input-token cost ceiling.

### Unknown observations

- All rule fact paths were observed at least once.

### Bounded next actions

- Benchmark the compact and larger model on the same 100 synthetic issues.

## Exclude recovery time from the dashboard

- Decision: `decision-drop-metric`
- Choice: Omit recovery time because the initial pilot found high measurement noise.
- Status: **ACTIVE → STALE**
- Reversibility: `easy`
- Review schedule: **OVERDUE**

### Triggered premises

- **INVALIDATE** `rule-new-metric-evidence` via `event-new-literature`: `literature.recovery_metric_supported` observed as `True`. New evidence directly challenges the premise used to omit the metric. Source: `synthetic://literature/recovery-review`

### Evidence freshness

- No dated evidence has expired.

### Counterfactual alternatives

- **REOPENED:** Reintroduce recovery time with repeated measurements (triggered by `rule-new-metric-evidence`)
  - Originally rejected because: The first pilot showed high noise and no separation.

### Unknown observations

- No supplied event observed the facts required by: `rule-reliability-improved`

### Bounded next actions

- Read the cited method section before treating the external result as transferable.
- Run a blinded repeated-measurement reliability pilot.

## Interpretation boundary

A triggered rule means a recorded premise deserves review. It does not prove that the original decision was irrational or that a reopened alternative is now best.
