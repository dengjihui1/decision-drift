# Decision Drift

> Memory that knows when it may be wrong.

Decision Drift turns important choices into living contracts. Each contract records why a decision was made, which premises support it, what evidence may expire, which alternatives were rejected, what was predicted, and what observable event should force reconsideration.

The project is not a task manager, generic RAG memory, or an automated judge. It is an explainable drift detector for research, software, and product decisions.

## Planned MVP

```text
decision ledger + new events
              ↓
observable rule evaluation
              ↓
ACTIVE / AT_RISK / STALE / REPLACED
              ↓
expired evidence + reopened alternatives + next checks
              ↓
Markdown, JSON and Mermaid reports
```

The runtime is local-first and uses Python's standard library only. Synthetic examples are used for public demos.
