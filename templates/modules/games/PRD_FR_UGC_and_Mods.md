---
doc: PRD_FR_UGC_and_Mods
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — UGC & Mods

## Purpose & Scope
Player-created content: creation tools, sharing/discovery, and the safety
+ compatibility rules that keep it healthy. Boundary: moderation pipeline
mechanics → content/Moderation patterns; monetized UGC → Monetization +
marketplace patterns (a serious escalation — own Decision).

## UGC Ambition (decide first, Decision Log)
| Level | In? |
|---|---|
| Sharable configurations (loadouts, blueprints) | |
| In-game editor content (levels, liveries) | |
| External mod support (file/API-level) | |
| Scripted mods (code execution — a security commitment) | |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-UGC-001 | Must | Creation tools per ambition level with validation at save (playability guarantees mirror FR-LVL-003: no unwinnable/broken shares) | Given a creation failing validation, when saving to share, then sharing is blocked with the named failures, local save still allowed | validation teaches, not just rejects |
| FR-UGC-002 | Must | Sharing & discovery: browse/search/rate; creator attribution permanent; report path on every item | Given a shared item, when viewed, then creator, rating, and report action are present | |
| FR-UGC-003 | Must | Safety pipeline: pre-share scan per surface + post-share reports feed moderation; takedown propagates to downloaders' access per policy | Given a takedown, when executed, then the item is undiscoverable and the access policy applies within <N> | |
| FR-UGC-004 | Must (if mods) | Compatibility contract: mod API surface versioned; game updates state breakage policy; broken mods fail safe (disable, never crash-loop) | Given a game update breaking a mod, when launching, then the mod is disabled with notice, the game boots clean | |
| FR-UGC-005 | Must (if scripted) | Sandbox: scripted mods run with declared capabilities only (no filesystem/network beyond grants); multiplayer integrity rules (mods vs anti-cheat) stated | Given a script exceeding its capabilities, when executed, then the call is denied and the mod flagged | |
| FR-UGC-006 | Should | Creator ecosystem hygiene: IP/DMCA process, featured/curation policy, remix rules (can creations build on creations?) | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Creation / CreatorProfile / DownloadRecord | RW | attribution survives account deletion per BR-style credit rule |

## States & Transitions
Creation: draft → validated → shared → (reported → under_review) →
active | delisted | taken_down. Mod: installed → active | disabled(reason).

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Popular creation taken down (many downloaders) | access policy applies uniformly; downloaders notified | FR-UGC-003 |
| Creation depends on delisted creation (remix chain) | dependency rule: freeze-copy vs cascade — stated | FR-UGC-006 |
| Malicious content disguised as level data (scale/adversarial) | validation treats all UGC as untrusted input; parser hardening → Security | FR-UGC-001 |
| Mod conflict (two mods, same hook) | deterministic load order + conflict surfacing | FR-UGC-004 |
| Creator deletes account | creations follow stated disposition; attribution rule holds | FR-UGC-002 |

## Dependencies
- Moderation patterns, Files_and_Media (asset storage), Security (sandbox, parser hardening), Multiplayer (modded-play rules), LiveOps (featured rotation)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| % players engaging with UGC (play or create) | G-0X (retention) | |
| Takedown SLA compliance | G-0X (trust) | per SLA |

## Out of Scope for This Module
- Paid mods/creator revenue share unless the Decision is made explicitly

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
