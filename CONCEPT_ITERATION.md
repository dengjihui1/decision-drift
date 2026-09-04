# Concept iteration

## Round 1 — Decision memory

The first idea was a memory system that records why a choice was made. This was useful but too close to decision logs, architecture decision records, and retrieval systems. Remembering old reasoning does not tell a user whether it remains applicable.

## Round 2 — Invalidation-aware memory

The second idea attached observable invalidation conditions to each assumption. This created a meaningful distinction from ordinary memory: new events can be evaluated against explicit premises. It also introduced evidence freshness, because a decision can become risky even when no contradicting event exists if its supporting source has expired.

## Round 3 — Counterfactual and calibration memory

The final idea adds two compounding loops. Rejected alternatives carry rejection conditions and can re-enter consideration when those conditions disappear. Predictions are later compared with outcomes so the system can measure local decision error without pretending to infer a person's global ability.

## Frozen product thesis

Decision Drift is a local-first protocol and engine for memory that knows when it may be wrong. Its durable object is a decision contract, not a chat transcript or task. The MVP proves four capabilities:

1. machine-checkable premise invalidation;
2. evidence freshness warnings;
3. counterfactual alternative reopening;
4. prediction-versus-outcome calibration.

The MVP deliberately excludes automatic monitoring, probabilistic admission or success predictions, silent decision reversal, and claims that a triggered rule proves the original decision was bad.

## Round 4 — Time-safe replay

A retrospective audit is unreliable if it can accidentally use knowledge that did not exist at the chosen review date. The engine therefore evaluates each decision only against events inside its temporal window: on or after `made_at` and on or before `review_date`. It exposes excluded future event IDs in the report instead of silently dropping them.

This makes the protocol useful for reproducible postmortems and research-method audits. Two people replaying the same ledger, events, and review date receive the same result without hindsight leaking through the event set.
