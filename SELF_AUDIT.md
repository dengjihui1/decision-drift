# Self-audit

## Round 1 — Product differentiation

**Question:** Is this only a decision log with AI wording?

**Finding:** The initial concept was too close to ADRs and decision journals.

**Change:** The durable object became a falsifiable decision contract. Machine-checkable invalidation, evidence expiry, alternative reopening, and prediction calibration are now required capabilities rather than optional prose sections.

**Residual risk:** Contract capture still requires judgment. The Skill labels inferred assumptions and keeps them reviewable.

## Round 2 — Epistemic and temporal correctness

**Question:** Can incomplete or future information silently produce a confident result?

**Finding:** Missing facts were already represented as `UNOBSERVED`, but the first engine version did not exclude events after the review date.

**Change:** Checks now use a closed as-of window from `made_at` through `review_date`. Future event IDs are disclosed in the report. Trigger entries retain event date, source, fact, observed value, operator, and expected value.

**Residual risk:** A source can still be inaccurate. The engine checks provenance and freshness, not truth.

## Round 3 — Public-release integrity

**Question:** Does the repository overclaim results or leak private material?

**Finding:** A persuasive demo could be mistaken for an empirical validation.

**Change:** All public examples are explicitly synthetic. Research benefits are written as hypotheses with a falsifiable evaluation plan. Reports state that a trigger does not prove a decision was irrational. The runtime is local-first and performs no network calls.

**Residual risk:** Users control what they place in their own ledger and whether they upload it. Private ledgers should remain local by default.
