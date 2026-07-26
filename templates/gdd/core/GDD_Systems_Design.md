---
doc: GDD_Systems_Design
tier: standard+
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Systems Design

## Progression System
_What grows (skills, gear, unlocks, knowledge), on what curve, gated by
what. Player-knowledge progression counts even when nothing is stored._
| Track | What Grows | Gate/Pace | Resets? |
|---|---|---|---|

## Economy (sources & sinks)
_Every currency/resource: where it enters, where it leaves, what happens
at the extremes. An economy with sources and no sinks inflates; state the
sink for every source._
| Resource | Sources (faucets) | Sinks (drains) | Cap? | Extreme-state behavior (hoarding / bankruptcy) |
|---|---|---|---|---|

## Progression Math
_For each track: the curve family (linear/exponential/logistic/banded),
the formula or lookup with named constants (→ tuning values), and the
target pace ("level N by hour M"). A curve without a target pace is not
tuned, it's guessed._

## Meta-Systems
_Crafting, collection, housing, relationships — systems that consume the
core loop's outputs. Each earns its place by feeding a pillar and names
its own sources/sinks row above; a meta-system with no sink is a chore
generator._

## Difficulty & Balancing
- Difficulty model: fixed curve / selectable / adaptive — pick, justify
  against pillars
- Tuning-value inventory: every number a designer will tune lives in data
  (→ TECH_Data_Design), never hardcoded; list the top 10 here by name
- Balancing method: what telemetry (→ checklist decision) + playtest
  cadence closes the loop

## System Interaction Map
_Which systems feed which (economy → progression → difficulty → …).
Circular feedback loops are called out explicitly with their damping._

## Testable Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-SYS-001 | Must | Economy behaves per table incl. extreme states | Given max-cap hoarding, when earning more, then the stated behavior occurs (no overflow/exploit) | |
| FR-SYS-002 | Must | All named tuning values data-driven and hot-adjustable in dev builds | Given a dev build, when a named tuning value changes, then behavior updates without recompiling | |
| FR-SYS-003 | Should | Difficulty model per decision, selectable at declared points | | changing difficulty never shames the player |

## Edge Cases
| Scenario | Expected Behavior | Ref |
|---|---|---|
| Player sequence-breaks a gate | soft-lock impossible: state the recovery | FR-SYS-001 |
| Economy exploit found post-launch | tuning values adjustable without client patch (→ LiveOps if scoped) | FR-SYS-002 |

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
