---
doc: PRD_FR_Trust_and_Safety
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Trust & Safety

## Purpose & Scope
Two-sided trust: reviews/ratings, disputes, fraud posture, enforcement
ladder. Boundary: content-level moderation mechanics → content/Moderation
if scoped; money consequences → Payouts & Escrow.

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-TRST-001 | Must | Two-sided reviews tied to completed transactions only; window + edit rules | Given no transaction, when reviewing, then blocked | simultaneous-reveal option to prevent retaliation |
| FR-TRST-002 | Must | Dispute flow: open → evidence from both sides → resolution (refund/release/split) with SLA; escalation to human | Given a dispute, when resolved, then escrow disposition executes and both parties see the reasoning | |
| FR-TRST-003 | Must | Enforcement ladder per Business Rules: warning → restriction → suspension → ban; every action logged, appealable | Given an enforcement action, when applied, then the rung, reason, and appeal path are recorded and shown | proportionate; reasons cited |
| FR-TRST-004 | Must | Fraud posture: velocity limits, duplicate-account signals, off-platform payment detection stance | Given velocity limits exceeded, when detected, then the configured friction applies and is logged | |
| FR-TRST-005 | Should | Reporting: users can report listings/users; triage queue with SLA | | |
| FR-TRST-006 | Should | Review integrity: verified-transaction badge; brigading/self-review detection stance | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Review / Dispute / EnforcementAction / Report | RW | append-only enforcement history |

## States & Transitions
Dispute: open → awaiting_evidence → under_review → resolved | escalated.
Account standing: good → warned → restricted → suspended → banned (each
transition: trigger, notice, appeal path).

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Both sides present contradictory evidence | human escalation, not coin-flip automation | FR-TRST-002 |
| Review after dispute refund | review allowed, transaction outcome shown alongside | FR-TRST-001 |
| Mass-report brigading a seller | report velocity ≠ guilt; triage weights account signals | FR-TRST-005 |
| Enforcement on a seller with in-flight orders | orders honored or refunded per ladder rules, stated per rung | FR-TRST-003 |
| Appeal succeeds after suspension | restoration path incl. listings and held funds | FR-TRST-003 |

## Dependencies
- Payouts & Escrow (dispute disposition), Listings, Notifications, Admin Panel (triage tooling)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Dispute resolution within SLA | G-0X | |
| Repeat-fraud rate post-enforcement | G-0X (trust) | trending ↓ |

## Out of Scope for This Module
- Insurance/guarantee programs unless scoped

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
