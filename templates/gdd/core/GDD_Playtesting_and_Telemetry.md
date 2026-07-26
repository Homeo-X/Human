---
doc: GDD_Playtesting_and_Telemetry
tier: standard+   # the tuning feedback loop — Standard and up
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Playtesting & Telemetry

## Purpose & Scope
The evidence loop that closes design → play → data → tuning. This doc
makes GDD_Systems_Design §Balancing and GDD_Player_Experience §FTUE
*operational*. Boundary: product-analytics tooling → modules/common
Analytics if scoped; LiveOps config levers → games/LiveOps.

## Playtest Ladder
_Each rung has a protocol; skipping rungs is a Decision._
| Rung | Who Plays | Cadence | Protocol | Answers |
|---|---|---|---|---|
| Desk test | dev who built it | every change | self-play checklist | does it function |
| Team test | whole team | weekly | fixed scenario + free play | is it fun to US yet |
| Fresh-eyes | new-to-build outsiders, n≥5 | per milestone | think-aloud, NO HELP given, observer notes only | FTUE truth, teaching gaps |
| Target-player | archetype-matched, n≥8 | vertical slice + beta | tasked + survey (see below) | does the itch get scratched |

## Playtest Protocol Rules
- Observers never help, never explain, never defend — write down the
  moment help was wanted instead
- The survey asks the pillar questions (from PIL register) plus: where
  were you bored, where were you lost, when did you want to stop
- Every session produces a ranked findings list; findings enter the
  Decision Log only when they change a doc

## Feel Hypothesis Register
_Every feel target and adjective from Core Loop / Art & Audio, as a
falsifiable claim. RUB-24 enforces completeness._
| Feel Claim (source doc) | Hypothesis (falsifiable phrasing) | Rung | Question / Measure That Could Kill It |
|---|---|---|---|
| e.g. core verb "snappy" (Core Loop) | input→response ≤ 5 frames feels responsive to ≥4/5 fresh players | Fresh-eyes | "did the character do what you pressed, when you pressed it?" + frame capture |

## Telemetry Taxonomy (for tuning, not vanity)
_Every event serves a named tuning question or KPI; no orphan events._
| Event | Fired When | Properties | Tuning Question / KPI (G-id) It Serves |
|---|---|---|---|
| session_start/end | | build, platform | session length vs target shape |
| loop_completed | core loop closes | duration | first-loop time (FR-PXP-001) |
| death/fail | | cause, location | difficulty spikes, unfair-death hunting |
| economy_delta | source/sink fires | resource, amount | faucet/drain balance vs Systems tables |
| quit_point | session ends | location, state | churn-moment mapping |

## Tuning Cadence
- Data reviewed <weekly>; tuning changes batched, each batch a Decision
  Log entry naming the evidence; A/B only within LiveOps guardrails
- Kill criteria: metrics that trigger design rework rather than tuning
  (e.g. >X% quit in FTUE = teaching redesign, not number nudging)

## Testable Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-PLAY-001 | Must | Telemetry taxonomy implemented; every event verifiable in dev builds | Given a dev build, when each taxonomy event's trigger occurs, then the event arrives with its properties | |
| FR-PLAY-002 | Must | Fresh-eyes rung executed per milestone with findings recorded before milestone exit | Given a milestone review, when exiting, then the fresh-eyes findings list exists and is dispositioned | |
| FR-PLAY-003 | Must | Telemetry consent + privacy per platform rules; opt-out honored | Given opt-out, when playing, then only strictly-functional events fire | |

## Edge Cases
| Scenario | Expected Behavior | Ref |
|---|---|---|
| Playtest contradicts a pillar | escalate per AGENTS.md §9 — pillars change by Decision, not drift | FR-PLAY-002 |
| Telemetry endpoint down | events buffered locally, capped, dropped-oldest | FR-PLAY-001 |
| Data says X, team conviction says Y | run the discriminating test; log the bet either way | — |

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
