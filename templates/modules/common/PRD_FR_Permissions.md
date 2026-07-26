---
doc: PRD_FR_Permissions
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Permissions & Roles

## Purpose & Scope
Authorization model: who may do what on which resource. Boundary:
authentication (identity) is PRD_FR_Authentication; this module assumes an
identified principal. For simple products (≤3 roles, no sharing), fold this
into Authentication and record that in the FR Overview's cross-cutting table.

## Model Decision (pick one, record in Decision Log)
- Flat roles (viewer/editor/admin) · Role-per-workspace/team · Resource-level
  ACLs / sharing · Attribute- or policy-based. Choose the simplest model the
  user flows actually require.

## Role & Permission Matrix
| Capability (verb + resource) | Role A | Role B | Role C |
|---|---|---|---|
| | | | |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-PERM-001 | Must | Deny-by-default enforcement at the API layer | Given no explicit grant, when any endpoint is called, then access is denied and logged | denied actions hidden vs. disabled — pick a convention |
| FR-PERM-002 | Must | Role assignment & change (who can grant which roles) | Given a role change by an authorized granter, when saved, then it takes effect and is audit-logged | |
| FR-PERM-003 | Should | Resource sharing / invitation (if flows require) | | |
| FR-PERM-004 | Should | Permission change takes effect within <N> without re-login | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Role / Membership | RW | |
| AuditEvent | W | every grant/revoke logged |

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Last admin demotes themselves | block or require transfer | FR-PERM-002 |
| Access revoked mid-session | | FR-PERM-004 |
| Orphaned resources after member removal | ownership transfer policy | |
| Permission escalation via sharing chain | | FR-PERM-003 |

## Dependencies
- Authentication; every other module (this is enforced everywhere)

## Success Metrics
| Metric | Traces To | Target |
|---|---|---|
| Permission-related support tickets | support-load KPI | |

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
