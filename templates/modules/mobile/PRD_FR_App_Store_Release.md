---
doc: PRD_FR_App_Store_Release
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — App Store Release & Updates

## Purpose & Scope
Store presence, review compliance, versioning, and forced-update policy
for iOS/Android distribution. Boundary: push infrastructure →
Notifications; build pipeline → Architecture.

## Platform Matrix
| Platform | Min OS | Store Requirements Watchlist (privacy labels, data-safety form, sign-in rules, payment rules) |
|---|---|---|

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-REL-001 | Must | Store compliance per matrix: privacy declarations match actual data flows (cross-check PRD_Data_Overview classification) | Given the data-safety form, when audited against Data Overview, then no undeclared collection exists | |
| FR-REL-002 | Must | Version support policy: how many prior versions serve; API compatibility window stated | Given the oldest supported version, when used, then all served APIs function per the window | |
| FR-REL-003 | Must | Forced vs soft update: criteria (security = forced; features = soft), in-app messaging path for both | Given a below-minimum version, when opening, then a blocking update screen with store deep-link appears | blocking screen explains why |
| FR-REL-004 | Should | Staged rollout with halt criteria (crash rate, key-metric regression thresholds) | | |
| FR-REL-005 | Should | Store-review survival: demo account, reviewer notes, feature flags to soften review-risky features | | |
| FR-REL-006 | Could | In-app review prompting per platform rules (frequency caps) | | never after a failure moment |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| ClientVersion (server-known min/current) | R | drives FR-REL-003 |

## States & Transitions
Release: built → in-review → staged(<N>%) → full | halted → hotfix.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Store review rejection | flag-off the contested feature path; resubmit runbook | FR-REL-005 |
| Server API change lands before clients update | compatibility window honored; old clients degrade declared, not crash | FR-REL-002 |
| Rollout halt with half the fleet updated | both versions must be servable; halt ≠ rollback of users | FR-REL-004 |
| User can't update (old OS) | end-of-support messaging + data export path | FR-REL-002 |

## Dependencies
- Notifications (update prompts), Architecture (version gate endpoint), Security (forced-update triggers)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Fleet on supported versions | G-0X | ≥95% within <N> weeks |
| Crash-free sessions on new releases | G-0X (quality) | |

## Out of Scope for This Module
- CI/CD mechanics; store optimization/ASO marketing

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
