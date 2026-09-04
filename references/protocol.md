# Decision Contract Protocol v0.1

## Purpose

A decision contract preserves the conditions under which a consequential choice was reasonable. It must be specific enough for a later event to challenge a premise without pretending that a rule can decide the replacement choice.

## Contract anatomy

Each ledger contains project metadata, a review date, and one or more decisions. A decision should include:

- a stable `id`, title, choice, date, owner, rationale, reversibility, and current status;
- assumptions that make the choice locally reasonable;
- evidence supporting those assumptions, with observation dates and optional expiry windows;
- rejected alternatives and the rule IDs that should reopen them;
- numerical predictions that can later be compared with outcomes;
- observable invalidation rules and bounded next actions.

The canonical machine-readable shape is documented in `schemas/decision-ledger.schema.json`.

## Epistemic labels

Assumptions use `source: explicit` when directly stated in source material and `source: inferred` when proposed by an agent. Inferred assumptions must remain reviewable and must not be silently converted into user commitments.

Evidence is a reference, not a truth claim. The engine can detect expiry by date, but cannot establish that a source was accurate, complete, or interpreted correctly.

## State model

```text
ACTIVE ──warning/expiry──▶ AT_RISK ──invalidation──▶ STALE ──superseded──▶ REPLACED
   └──────────────────────── invalidation ────────────────▶ STALE
```

- `ACTIVE`: no observed warning, invalidation, or expired evidence.
- `AT_RISK`: at least one warning rule fired or supporting evidence expired.
- `STALE`: at least one invalidation rule fired, or the ledger was already stale.
- `REPLACED`: retained for history and never automatically reactivated.

The engine never downgrades an existing state. Returning a decision to `ACTIVE` requires an explicit ledger edit with fresh evidence.

## Event protocol

An event is a dated observation with a flat or nested `facts` object and a source string. Facts are addressed with dotted paths such as `team.concurrent_writers` or `data.size_gb`.

Absent facts evaluate to `UNOBSERVED`, not false. This prevents incomplete events from silently reassuring the user.

Checks use time-safe replay: only events dated on or after a decision's `made_at` and on or before the ledger's `review_date` may affect that decision. Future-dated events are reported and excluded so an as-of audit cannot leak later knowledge into an earlier judgment.

## Counterfactual reopening

An alternative lists rule IDs in `reopen_when`. If any referenced rule triggers, the alternative is surfaced as `REOPENED`; this is a prompt to compare options again, not a recommendation to adopt the alternative.

## Calibration

A prediction contains a metric, lower and upper bounds, a unit, and optionally an actual value. Calibration is valid only when metric and unit semantics are unchanged. The runtime reports whether the actual value fell inside the range, distance to the nearest bound, and signed error from the midpoint.

Do not aggregate a small number of predictions into claims about a person's general competence or bias.

## Minimal capture checklist

Before accepting a contract, verify:

1. the choice and rationale are concrete;
2. each rule references an existing assumption;
3. every rule uses an observable fact and supported operator;
4. alternatives reference existing rule IDs;
5. evidence dates are ISO dates and expiry windows are positive;
6. prediction bounds are ordered and units are present;
7. no outcome or external fact was invented.
