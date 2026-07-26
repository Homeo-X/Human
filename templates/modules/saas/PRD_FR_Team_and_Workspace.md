---
doc: PRD_FR_Team_and_Workspace
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Team & Workspace

## Purpose & Scope
The tenancy model: workspaces/organizations, membership, invitations.
Boundary: role capabilities are PRD_FR_Permissions; seat pricing is
PRD_FR_Subscription_Billing. Decide first (Decision Log): can one user
belong to multiple workspaces? Nested teams?

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-TEAM-001 | Must | Workspace creation + settings (name, domain, defaults) | Given workspace creation, when complete, then the creator is owner and defaults apply | |
| FR-TEAM-002 | Must | Invitations: email invite, link invite?, domain auto-join?, expiry | Given an invite, when accepted before expiry, then membership activates with the invited role | |
| FR-TEAM-003 | Must | Member management: list, change role, remove (data-ownership handling) | Given member removal, when confirmed, then access ends and owned-data disposition follows policy | |
| FR-TEAM-004 | Must | Tenant isolation: no cross-workspace data leakage, ever | Given any request for another workspace's resource, when made, then the response is 404 | |
| FR-TEAM-005 | Should | Workspace switching (if multi-workspace) | | current context always visible |
| FR-TEAM-006 | Could | Workspace deletion/export (admin-initiated, grace period) | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Workspace / Membership / Invitation | RW | every tenant-owned entity carries workspace_id |

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Invite to email that already has an account | attach, don't duplicate | FR-TEAM-002 |
| Removing a member who owns shared resources | transfer or orphan policy | FR-TEAM-003 |
| Seat limit reached at invite time | billing prompt path | FR-TEAM-002 |
| Domain auto-join with a personal-email domain (gmail) | blocklist | FR-TEAM-002 |

## Dependencies
- Authentication, Permissions, Subscription & Billing, Notifications

## Success Metrics
| Metric | Traces To | Target |
|---|---|---|
| Invites sent per new workspace / acceptance rate | expansion KPI | |

## Out of Scope for This Module
-

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
