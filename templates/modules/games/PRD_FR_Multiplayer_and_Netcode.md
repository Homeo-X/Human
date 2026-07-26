---
doc: PRD_FR_Multiplayer_and_Netcode
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Multiplayer & Netcode

## Purpose & Scope
Networked play: session model, matchmaking, synchronization, disconnect
handling. Boundary: anti-cheat enforcement policy → Security Requirements;
social features (friends/chat) are their own module if scoped.

## Session Model (decide first, Decision Log)
| Question | Decision |
|---|---|
| Topology (dedicated servers / P2P / relay / listen) | |
| Sync model (lockstep / rollback / server-authoritative snapshot) | |
| Player counts (min/typical/max per session) | |
| Cross-play / cross-progression | |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-MP-001 | Must | Session lifecycle: create/join/leave per model; host migration or session end policy stated | Given the authority leaves, when handled, then remaining players get the stated outcome, never a silent hang | |
| FR-MP-002 | Must | Matchmaking per declared criteria (skill/latency/party size) with worst-case wait behavior | Given no suitable match in <N>s, when waiting, then bots/looser criteria/honest ETA per policy | wait screens show progress, allow cancel |
| FR-MP-003 | Must | Latency handling per sync model: feel targets under <N>ms; degradation behavior above | Given <N>+100ms, when playing, then declared degradation (not desync) occurs | |
| FR-MP-004 | Must | Disconnect/rejoin: grace window, state on return, abandon penalties (fair to the disconnected AND the remaining) | Given a disconnect within grace, when rejoining, then the player returns to the declared state | |
| FR-MP-005 | Must | Authority & anti-cheat surface: what the client is trusted with (ideally: inputs only); server validation list | Given a client-sent state mutation outside the trust list, when received, then the server rejects it | |
| FR-MP-006 | Should | Spectate/replay if scoped; network-relevant privacy (IP masking under P2P) | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Session / MatchResult | RW | results server-authoritative |

## States & Transitions
Session: forming → active → (paused?) → completed | abandoned. Player-in-
session: connected ⇄ reconnecting → left.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| All players disconnect simultaneously | session disposition + result policy | FR-MP-004 |
| Clock/tick drift between peers | sync model's correction, bounded | FR-MP-003 |
| Version mismatch at join (post-patch) | blocked with update path, not mid-match kick | FR-MP-001 |
| Matchmaking at 4am in a small region (scale-low) | FR-MP-002 worst-case path honest | FR-MP-002 |
| Malformed/impossible client input | server rejects + flags (→ Security) | FR-MP-005 |

## Dependencies
- Security (anti-cheat policy), Save & Progression (result persistence), Notifications (invites), Architecture (server infra, tick rate → NFR)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Match completion rate (vs abandons) | G-0X | |
| P95 matchmaking wait | G-0X | |

## Out of Scope for This Module
- Voice chat; tournaments/esports features unless scoped

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
