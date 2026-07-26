---
doc: PRD_FR_Save_and_Progression
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Save & Progression Persistence

## Purpose & Scope
Persisting player state: save model, cloud sync, integrity, migration
across game versions. Boundary: WHAT progresses → GDD_Systems_Design; this
module owns that it survives.

## Save Model (decide first)
| Question | Decision |
|---|---|
| Save points (anywhere / checkpoints / autosave cadence) | |
| Slots (count, per-profile) | |
| Cloud sync (platform service / own backend / none) | |
| What is deliberately NOT saved (run-based content?) | |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-SAVE-001 | Must | Save/load per model; atomic writes — a crash mid-save never corrupts the previous save | Given a kill mid-write, when relaunching, then the last good save loads | saving indicator honest but unobtrusive |
| FR-SAVE-002 | Must | Autosave cadence per model with rotation (≥2 generations) | Given autosave cadence, when triggered, then a new generation writes and at least two are retained | never overwrite the only save before a risky moment |
| FR-SAVE-003 | Must | Save-format versioning: any shipped version's save loads in every later version (migration chain tested) | Given a v1.0 save, when loaded in vN, then progression intact | |
| FR-SAVE-004 | Must (if cloud) | Cloud sync with conflict policy (newest / most-progress / user-choice) — never silent loss | Given divergent local+cloud, when syncing, then the policy resolves visibly | |
| FR-SAVE-005 | Should | Save integrity: tamper detection stance (single-player: permissive vs leaderboard-feeding: validated) | | |
| FR-SAVE-006 | Could | Export/import for platform migration | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| SaveGame / Profile | RW | schema version field mandatory from v1 |

## States & Transitions
Save file: writing → valid | corrupt(quarantined, previous restored).
Sync: local-newer / cloud-newer / conflict → resolved.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Storage full at save time | fail with prior save intact + clear message | FR-SAVE-001 |
| Corrupt save detected | quarantine + previous generation offered, never silent reset | FR-SAVE-002 |
| Cloud service unreachable (dependency) | local play unaffected; sync deferred visibly | FR-SAVE-004 |
| Downgrade (older client, newer save) | refuse gracefully with explanation | FR-SAVE-003 |
| Two devices playing simultaneously (conflict) | FR-SAVE-004 policy; no interleaved corruption | FR-SAVE-004 |

## Dependencies
- Systems Design (state inventory), platform services (Architecture), Multiplayer (server-side progression if online)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Save-loss reports | G-0X (trust) | 0 |
| Migration failures per version bump | G-0X | 0 |

## Out of Scope for This Module
- What the progression contains (Systems Design)

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
