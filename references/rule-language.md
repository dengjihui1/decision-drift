# Observable rule language

Rules describe the event condition that should trigger review. They are deliberately small, deterministic, and non-executable.

## Shape

```json
{
  "id": "rule-multi-writer",
  "assumption_id": "assumption-single-user",
  "fact": "team.concurrent_writers",
  "operator": "gt",
  "value": 1,
  "severity": "invalidate",
  "message": "The storage choice assumed a single writer."
}
```

## Supported operators

| Operator | Trigger condition |
| --- | --- |
| `eq` | observed value equals `value` |
| `ne` | observed value differs from `value` |
| `gt` | observed value is greater than `value` |
| `gte` | observed value is greater than or equal to `value` |
| `lt` | observed value is less than `value` |
| `lte` | observed value is less than or equal to `value` |
| `contains` | observed string/list contains `value` |
| `not_contains` | observed string/list does not contain `value` |
| `in` | observed value appears in the rule's `value` list |
| `not_in` | observed value does not appear in the rule's `value` list |
| `changed_from` | observed value differs from the rule's baseline `value` |
| `exists` | the fact path is present in the event |

If the fact path is absent, every operator returns `UNOBSERVED`, including `exists`. There is intentionally no rule that treats missing data as proof that a premise failed.

## Severity

- `warning` means the decision should be inspected and can move to `AT_RISK`.
- `invalidate` means a stated premise has been contradicted and can move the decision to `STALE`.

Severity describes review priority, not certainty or harm.

## Rule design

Prefer a measurable trigger such as `data.size_gb > 1` over language such as “the dataset becomes large”. When a threshold is uncertain, keep it as an assumption for user review rather than manufacturing precision.

Avoid executable expressions, arbitrary code, network calls, or rules that infer intent. The rule evaluator operates only on supplied JSON facts.
