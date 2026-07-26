---
doc: PRD_Decision_Log
tier: light+
version: 0.0.0
status: template
owner: orchestrator
last_updated: —
---

# Decision Log

_Append-only. Chronological — new entries go at the END (true append).
Never edit past entries — supersede them. Scoping, contested trade-offs,
resolution-loop outcomes, scope reopenings, review findings, and
reality-driven spec changes all get entries._

## Entry schema
### D-NNN — <short title> (<date>, <role>)
- **Status:** active | superseded-by D-XXX
- **Context:** what forced a choice, in 1–3 sentences
- **Decision:** what was chosen
- **Alternatives:**
  - <option> — rejected_because: <reason>
- **Consequences:** + <benefit> · − <cost or accepted risk>
- **Reversibility:** high | medium | low — with the concrete undo path if
  not low
- **Valid while:** the conditions under which this decision holds
  ("team ≤ 3 devs", "corpus < 10^6 lines") — or "unconditional".
  `specgraph --stale` surfaces conditional decisions for re-examination
- **Affects:** files and/or IDs this binds (e.g. TECH_Data_Design,
  FR-AUTH-004) — when this decision changes, everything listed here is
  re-read
- **Supersedes:** D-XXX or —

---

### D-001 — <first entry written by orchestrator at scoping>
