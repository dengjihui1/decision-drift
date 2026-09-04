# Synthetic timeline demo

This demo contains no real person, laboratory, company, price, paper, or private project data. It models a fictional project whose original choices were reasonable under January–March conditions and deserve review after later events.

Run:

```powershell
python scripts/decision_drift.py validate demo/decision-ledger.json demo/events.json
python scripts/decision_drift.py check demo/decision-ledger.json demo/events.json --output-dir demo/output
python scripts/decision_drift.py calibrate demo/decision-ledger.json --output-dir demo/output
```

Expected high-level result:

- SQLite decision: `STALE` after multiple writers appear; PostgreSQL is reopened.
- Compact-model decision: `AT_RISK` after the recorded price premise changes.
- Omitted-metric decision: `STALE` after new synthetic evidence challenges the premise.
- One prediction falls inside its range and one falls above it.
