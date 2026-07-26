---
doc: PRD_FR_Integrations_Platform
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Integrations (User-Facing)

## Purpose & Scope
Integrations the USER connects (Slack, calendars, webhooks, public API) —
a product feature. Boundary: integrations the SYSTEM depends on live in
PRD_External_Integrations.

## Integration Catalog
| Integration | Direction | What Syncs | Auth (OAuth/API key) | Launch Phase |
|---|---|---|---|---|

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-INTG-001 | Must | Connect/disconnect flow per catalog row; scopes shown at consent | Given a connect flow, when consenting, then requested scopes are shown before authorization | |
| FR-INTG-002 | Must | Connection health surfaced (working / broken / re-auth needed) | Given a broken connection, when its owner views it, then the broken state and fix path show | broken ≠ silent |
| FR-INTG-003 | Should | Outbound webhooks: event selection, signing, retry policy | | |
| FR-INTG-004 | Should | Public API + keys/tokens management (scoped, revocable) | | |
| FR-INTG-005 | Could | Sync conflict policy for two-way integrations | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Connection / WebhookSubscription / ApiKey | RW | third-party tokens encrypted at rest |

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Third-party token revoked externally | detect, mark broken, notify owner | FR-INTG-002 |
| Webhook endpoint failing repeatedly | backoff → suspend + notify | FR-INTG-003 |
| Connector user leaves the workspace | connection ownership transfer | FR-INTG-001 |
| API key leaked | revoke + rotate path; rate anomaly detection stance | FR-INTG-004 |

## Dependencies
- Permissions (who may connect), Notifications, Security Requirements (token handling)

## Success Metrics
| Metric | Traces To | Target |
|---|---|---|
| % workspaces with ≥1 active integration | retention KPI | |

## Out of Scope for This Module
-

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
