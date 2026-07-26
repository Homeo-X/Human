---
doc: GDD_Content_and_Levels
tier: standard+
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Content & Levels

## World / Structure
_How play-space is organized: linear levels, hub-and-spoke, open world,
procedural runs, level packs — and why that structure serves the pillars._

## Content Scope Table (the budget artifact)
_This table IS the production scope. Every row multiplies into cost;
cutting here is cheaper than cutting in beta._
| Content Type | Count (MVP) | Count (launch) | Unit Cost (rough days) | Reuse Strategy |
|---|---|---|---|---|
| Levels/areas | | | | |
| Enemies/NPCs | | | | |
| Items/abilities | | | | |
| Cutscenes/VO lines | | | | |

## Level Design Language
- The reusable ingredients (mechanics from MECH register + hazards +
  rewards) and the grammar for combining them
- Teaching pattern: introduce-safe → test → combine → twist
- Golden-path length + optionality per level type

## Procedural / Systemic Content (if any)
_Generator inputs, guarantees (what can never be generated: unwinnable
states, unreachable rewards), and authored-vs-generated balance._

## Pacing Curve
_Across the whole game: intensity, novelty (new MECH/ARCH introductions),
and downtime plotted against the golden-path hours. Rules: no two peaks
adjacent; every new mechanic gets a valley to be learned in; the final
stretch recombines, it doesn't introduce._

## Content Pipeline
_Tool → review → integration path; who signs off; how a level goes from
graybox to shipped. Names the DoD gates for content._

## Testable Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-LVL-001 | Must | MVP content counts per scope table, each passing the content DoD gate | Given the MVP scope table, when audited, then every row's count exists and passed its DoD gate | |
| FR-LVL-002 | Must | Every mechanic in MECH register is taught by the teaching pattern before being tested | Given a player following the golden path, when a mechanic is first required, then it was introduced safely earlier | |
| FR-LVL-003 | Must (if procedural) | Generator guarantees hold | Given <N> generated seeds, when validated, then zero unwinnable/unreachable states | |

## Edge Cases
| Scenario | Expected Behavior | Ref |
|---|---|---|
| Player skips optional teaching content | required-path teaching still complete | FR-LVL-002 |
| Content cut late (scope pressure) | scope table row cut cleanly, no dangling references (specgraph check) | FR-LVL-001 |

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
