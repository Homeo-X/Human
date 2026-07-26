---
doc: PRD_FR_Onboarding
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Onboarding

## Purpose & Scope
From first login to first value ("activated"). Define the activation event
explicitly — it anchors this whole module. Boundary: signup mechanics are
PRD_FR_Authentication.

## Activation Definition
Activated = <the specific action correlated with retention>. Time-to-value target: <N>.

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-ONB-001 | Must | First-run setup: minimum questions to personalize; everything else deferred | Given first run, when setup completes, then only the minimum questions were required | every field must earn its place |
| FR-ONB-002 | Should | Guided path to the activation event (checklist / tour / template gallery) | | skippable, resumable |
| FR-ONB-003 | Should | Sample/demo data so the workspace isn't empty | | clearly marked, one-click removal |
| FR-ONB-004 | Should | Team-invite prompt at the moment collaboration becomes relevant | | |
| FR-ONB-005 | Could | Role/segment-specific onboarding branches | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| OnboardingState | RW | per user AND per workspace |

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Invited user joins a configured workspace | member onboarding ≠ owner onboarding | FR-ONB-005 |
| Onboarding abandoned mid-way | resume state; nudge via NTF catalog | FR-ONB-002 |
| Demo data mixed into real reports | excluded from analytics by flag | FR-ONB-003 |

## Dependencies
- Authentication, Team & Workspace, Notifications, Analytics (activation event must be in the event taxonomy)

## Success Metrics
| Metric | Traces To | Target |
|---|---|---|
| Signup → activation rate | activation KPI | |
| Time to first value (median) | activation KPI | |

## Out of Scope for This Module
-

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
