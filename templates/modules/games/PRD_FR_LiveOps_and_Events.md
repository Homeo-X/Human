---
doc: PRD_FR_LiveOps_and_Events
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — LiveOps & Events

## Purpose & Scope
Operating the game as a service: remote config, time-limited events,
seasons, and safe tuning without client patches. Boundary: what's tuned →
Systems Design tuning values; what's sold → Monetization; store release
mechanics → mobile/App_Store_Release if scoped.

## LiveOps Surface (decide first)
| Lever | Remote-Configurable? | Guardrails (min/max, who may change) |
|---|---|---|
| Tuning values (top 10 from Systems Design) | | |
| Event schedule | | |
| Feature flags | | |
| Message of the day / news | | |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-LOPS-001 | Must | Remote config per surface table with guardrails enforced server-side; client caches last-good | Given an out-of-guardrail value pushed, when fetched, then rejected and alarmed, last-good retained | |
| FR-LOPS-002 | Must | Timed events: schedule, start/end behavior mid-session, timezone policy (UTC vs local) stated | Given an event ending mid-session, when it ends, then in-flight progress resolves per stated rule | countdowns honest; no surprise endings |
| FR-LOPS-003 | Must | Config changes audited (who/what/when/before-after) with instant rollback | Given a config change, when applied, then an audit entry exists and rollback restores prior state in one step | |
| FR-LOPS-004 | Should | Seasons: content rotation, catch-up policy for returners (→ Monetization retention rules) | | absence-tolerant |
| FR-LOPS-005 | Should | Staged rollout of config (percentage/region) with halt criteria | | |
| FR-LOPS-006 | Could | A/B tuning experiments with guardrails + ethics constraints (never A/B dark patterns) | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| ConfigVersion / Event / AuditEvent | RW | config versions immutable; rollback = re-point |

## States & Transitions
Event: scheduled → announced → active → ending(grace) → ended → archived.
Config: draft → staged(<N>%) → live | rolled-back.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Client offline through an entire event | catch-up policy or clean miss; no broken state | FR-LOPS-002 |
| Config fetch fails at boot (dependency) | last-good cache; defaults shipped in client as floor | FR-LOPS-001 |
| Clock manipulation by client | server time authoritative for events | FR-LOPS-002 |
| Bad config passes guardrails but breaks balance (scale) | rollback ≤ <N> min per FR-LOPS-003; telemetry alarm | FR-LOPS-003 |
| Event overlaps a version rollout | compatibility window rule (→ App Store Release) | FR-LOPS-005 |

## Dependencies
- Systems Design (tuning inventory), Analytics/telemetry (balancing data, halt criteria), Security (config authenticity), Monetization (event offers)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Config incidents requiring rollback | G-0X | trending ↓ |
| Event participation rate | G-0X | |

## Out of Scope for This Module
- Community management tooling; customer support tooling (Admin Panel)

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
