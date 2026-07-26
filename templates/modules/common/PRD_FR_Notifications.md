---
doc: PRD_FR_Notifications
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Notifications

## Purpose & Scope
Everything the system proactively tells users, on any channel. Boundary:
channel infrastructure/providers live in External Integrations; message
content rules live here.

## Notification Catalog (the core artifact)
| ID | Event Trigger | Audience | Channels (in-app/email/push/SMS) | Urgency | Batching/Digest? | Opt-out Allowed? |
|---|---|---|---|---|---|---|
| NTF-01 | | | | | | |

Fill this before writing requirements — most notification bugs are catalog
gaps, not delivery failures. Transactional vs. marketing must be flagged
per row (different legal rules).

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-NTF-001 | Must | Deliver catalog events on their channels within urgency SLA | Given a catalog event, when triggered, then delivery on its channels meets the urgency SLA | |
| FR-NTF-002 | Must | Per-user preferences honoring the Opt-out column | Given an opted-out category, when its event fires, then no notification is delivered to that user | granular but not overwhelming |
| FR-NTF-003 | Should | In-app notification center (read/unread, history window) | | |
| FR-NTF-004 | Should | Digest/batching for low-urgency events | | |
| FR-NTF-005 | Must | Suppression: no notifications to deactivated users; respect quiet hours if defined | Given a deactivated user, when any event fires, then no notification is sent | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| NotificationPreference | RW | |
| Notification / Delivery log | W | retention per Data Overview |

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Channel provider outage | queue + retry policy; which events may be dropped | FR-NTF-001 |
| Event storm (bulk action triggers 500 notifications) | collapse/batch rule | FR-NTF-004 |
| User opted out of everything but a legally required notice fires | transactional bypass | FR-NTF-002 |
| Stale notification links to a deleted resource | | FR-NTF-003 |

## Dependencies
- Integrations: email/push/SMS providers · Modules: whichever emit catalog events

## Success Metrics
| Metric | Traces To | Target |
|---|---|---|
| Notification opt-out rate | engagement KPI | below X% |
| Delivery success within SLA | reliability KPI | |

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
