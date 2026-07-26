---
doc: PRD_FR_Social_and_Community
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Social & Community

## Purpose & Scope
In-game social fabric: friends, parties, guilds/clans, chat, and the
safety that makes them survivable. Boundary: matchmaking → Multiplayer;
content-level moderation pipeline → content/Moderation patterns; platform
friends import → Platform_Services.

## Social Surface (decide first)
| Surface | In? | Notes |
|---|---|---|
| Friends list (+ platform import) | | |
| Parties / groups (size, cross-play rules) | | |
| Guilds/clans (size, roles, shared assets) | | |
| Text chat (channels: party/guild/global?) | | global chat is a safety commitment — decide deliberately |
| Voice (native / platform / none) | | |
| Emotes/pings (the safe default social layer) | | |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-SOC-001 | Must | Friends: request/accept/remove/block; block is total (invisible both ways, all surfaces) | Given a block, when either player uses any social surface, then neither sees the other anywhere | block requires no confirmation friction |
| FR-SOC-002 | Must | Party lifecycle: form, invite, join-on-friend, leader handoff, cross-session persistence policy | Given the leader disconnects, when grace expires, then leadership transfers per policy, party intact | |
| FR-SOC-003 | Must | Chat safety baseline per surface table: filter defaults ON, mute/report per message, rate limits | Given a reported message, when submitted, then a moderation case exists with context attached | reporting ≤2 interactions from any message |
| FR-SOC-004 | Must | Privacy modes: online status, invites, and profile visibility each independently controllable; minors default maximally private | Given a minor account, when created, then the strictest privacy defaults apply | |
| FR-SOC-005 | Should | Guilds per surface decision: roles, shared progress, succession for inactive leaders | | |
| FR-SOC-006 | Should | Positive-by-default layer: pings/emotes usable with all chat off — the game is fully playable socially-muted | Given all chat disabled, when playing co-op, then coordination via pings suffices for the golden path | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Friendship / Party / Guild / ChatMessage / Block | RW | chat retention per legal + safety policy |

## States & Transitions
Friendship: requested → accepted | declined; blocked (overrides all).
Party: forming → active → disbanded. Guild leadership: active →
inactive(<N> days) → succession.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Block mid-party / mid-match | current match completes with comms severed; never re-matched | FR-SOC-001 |
| Chat storm / spam wave (scale) | rate limits + surface-level slow mode; safety before liveliness | FR-SOC-003 |
| Guild leader banned | succession runs; shared assets follow Trust rules | FR-SOC-005 |
| Cross-platform name collisions/impersonation | display-name rules + unique handle | FR-SOC-004 |
| Underage user in voice (dependency: age gate) | voice off by default for minors; parental surface per platform | FR-SOC-004 |

## Dependencies
- Multiplayer (sessions), Platform_Services (identity/friends import), Moderation patterns (report pipeline), Notifications (invites), Security (harassment escalation)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| % sessions played with friends/party | G-0X (retention) | |
| Report-to-action median time | G-0X (trust) | per SLA |

## Out of Scope for This Module
- Forums/companion apps; esports team management

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
