---
doc: PRD_FR_Moderation
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Moderation

## Purpose & Scope
Policy enforcement over user-generated content: detection, queues,
actions, appeals. Boundary: the policy itself → Business Rules; account-
level enforcement ladders → Trust & Safety if scoped; this module owns the
content-level pipeline.

## Policy Surface Matrix
| Surface (posts/comments/media/profiles/messages) | Detection (pre-publish scan / post-publish reports / both) | Auto-Action Allowed? | Human Review SLA |
|---|---|---|---|

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-MOD-001 | Must | Detection per matrix (automated classifiers and/or user reports) feeding a triage queue | Given a detection or report, when received, then a triage case exists in the correct lane | |
| FR-MOD-002 | Must | Moderator queue: evidence in context, policy cited per decision, per-item actions (remove/restrict/age-gate/allow) | Given a decision, when executed, then the policy clause is recorded with it | moderator wellbeing: blur-by-default for graphic queues |
| FR-MOD-003 | Must | Author notice + appeal: what was actioned, which policy, how to appeal; appeal SLA | Given an appeal upheld, when resolved, then content restored and strike reversed | |
| FR-MOD-004 | Must | Auto-action boundaries per matrix: what may act without a human, with error-rate monitoring and kill switch | Given an auto-action outside its boundary, when attempted, then it is blocked and queued for a human | |
| FR-MOD-005 | Should | Severity lanes: illegal/urgent content fast-laned with its own SLA and escalation contacts | | |
| FR-MOD-006 | Should | Transparency metrics: actions by category/outcome, appeal overturn rate | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| ModerationCase / Decision / Appeal | RW | append-only decisions; retention per legal |

## States & Transitions
Case: detected/reported → queued → decided(actioned|allowed) →
appealed? → upheld | overturned. Content visibility during each state is
declared per surface.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Classifier false-positive storm (scale) | kill switch per FR-MOD-004; queue backpressure visible | FR-MOD-004 |
| Report brigading | velocity ≠ guilt; dedupe reports per item | FR-MOD-001 |
| Content deleted by author mid-case | case proceeds on evidence snapshot (strikes may still apply) | FR-MOD-002 |
| Cross-jurisdiction legality differences | geo-scoped actions if Business Rules require | FR-MOD-005 |
| Moderator disagreement / second opinion | escalation lane defined | FR-MOD-002 |

## Dependencies
- Business Rules (the policy), Content Authoring (visibility hooks), Notifications (notices), Admin Panel (queue tooling), Analytics (FR-MOD-006)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Median time-to-decision per lane | G-0X | per SLA |
| Appeal overturn rate | G-0X (accuracy) | within band |

## Out of Scope for This Module
- Writing the policy itself; law-enforcement response runbooks

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
