---
doc: PRD_FR_Platform_Services
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Platform Services

## Purpose & Scope
First-party platform integration: achievements/trophies, rich presence,
platform friends, cloud saves, entitlements/DLC, platform-specific
requirements. Boundary: save mechanics → Save_and_Progression (this
module binds it to platform cloud); store release → mobile/App_Store_
Release for mobile stores.

## Platform Matrix
| Platform | Achievements | Presence | Cloud Save | Entitlements/DLC | Cert Gotchas Watchlist |
|---|---|---|---|---|---|

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-PLAT-001 | Must | Achievement set: designed once, mapped per platform (name/icon/points rules differ); unlock conditions data-driven | Given an unlock condition met, when it fires, then the platform achievement unlocks exactly once, offline-earned unlocks sync on reconnect | achievements celebrate play styles, not chores |
| FR-PLAT-002 | Must | Entitlement checks for base game + DLC per platform truth; offline grace policy stated | Given owned DLC and no connectivity, when launching within grace, then content remains available | |
| FR-PLAT-003 | Must | Platform account linking (if cross-progression): link/unlink flow, one-source-of-truth rule, support-recovery path | Given an unlink request, when confirmed, then progression ownership follows the stated rule with no orphaned state | irreversibility warned in plain words |
| FR-PLAT-004 | Should | Rich presence per matrix (activity, joinability) honoring privacy modes (FR-SOC-004 if scoped) | Given invisible mode, when playing, then presence shows offline everywhere | |
| FR-PLAT-005 | Should | Platform cert requirements tracked as a checklist per platform from vertical slice onward (suspend/resume, controller disconnect, profile switch) | Given controller disconnect mid-play, when it occurs, then the game pauses with the platform-required prompt | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| AchievementState / Entitlement / AccountLink | RW | platform is source of truth for entitlements |

## States & Transitions
AccountLink: unlinked → linked → (unlink-cooldown) → unlinked.
Achievement: locked → unlocked (monotonic — never revoked).

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Platform service outage (dependency) | play unaffected; unlocks/entitlements queue and reconcile | FR-PLAT-001 |
| Achievement condition met during service outage | local record; sync exactly-once on restore | FR-PLAT-001 |
| Refunded DLC with content in use | entitlement re-check per session; in-progress state follows policy | FR-PLAT-002 |
| Profile switch mid-session (console) | platform-required handling; saves scoped per profile | FR-PLAT-005 |
| Same account linked from two platforms simultaneously | conflict per one-source-of-truth rule | FR-PLAT-003 |

## Dependencies
- Save_and_Progression (cloud binding), Social (friends import), Multiplayer (invites via presence), TECH_Game_Architecture (cert checklist)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Cert submission passes (first attempt) | G-0X (schedule) | |
| Entitlement support tickets | G-0X (trust) | trending ↓ |

## Out of Scope for This Module
- Store page/marketing assets

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
