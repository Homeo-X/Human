---
doc: GDD_Game_AI_and_Encounters
tier: standard+   # optional by genre — see gdd/README genre lens; fold into Systems for light AI needs
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Game AI & Encounter Design

## Purpose & Scope
Opponent/NPC behavior and how encounters are composed from it. Boundary:
LLM/product AI → modules/ai; difficulty *system* → GDD_Systems_Design
(this doc supplies the ingredients that system tunes).

## AI Design Philosophy
_One paragraph: what the AI is FOR — pressure, puzzle, theater, company?
"Smart" is not a goal; readable and exploitable-on-purpose usually is.
State the intelligence illusion budget: what the player must believe._

## Archetype Register
_One row per behavioral archetype, not per skin. Depth prompt: what does
the player LEARN by fighting/meeting it, and which verb does it test?_
| ID | Archetype | Role (tests which player verb / MECH ref) | Behavior Summary (readable tell → action → recovery window) | Counterplay | Tuning Values (named) |
|---|---|---|---|---|---|
| ARCH-01 | | MECH-xx | | | |

## Behavior Model
- Decision model per archetype class (FSM / behavior tree / utility /
  GOAP) — chosen for AUTHORABILITY, justified in the Decision Log
- Perception rules: what AI can know (honest senses vs cheats — cheats
  allowed only when invisible AND serving the fantasy; list them)
- Group behavior: coordination rules, attacker-slot limits, retreat logic

## Encounter Grammar
_Encounters compose archetypes + space + stakes. Define the grammar so
level design (GDD_Content_and_Levels) can author to it._
| Encounter Type | Composition Rule | Intensity Slot (calm/build/peak) | Teaches/Tests |
|---|---|---|---|

## Difficulty Interaction
Which archetype tuning values the difficulty model may touch (HP/damage
scaling is the weakest lever — prefer count, composition, timing windows);
what NEVER changes (readability of tells).

## Testable Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-GAI-001 | Must | Every archetype per register: tell → action → recovery observable and consistent | Given any archetype attack, when it initiates, then its tell precedes it by the tuned window every time | tells readable per art readability rule |
| FR-GAI-002 | Must | Perception per honest-senses rules; listed cheats invisible to players | Given a player outside all sense ranges, when unseen, then no AI reacts to their position | |
| FR-GAI-003 | Must | Encounters authored only from the grammar; intensity slots respected on the golden path | Given the golden path, when audited, then peak encounters never stack beyond the grammar's rule | |
| FR-GAI-004 | Should | Group coordination per rules (slot limits, no surround-lock) | Given N attackers engaged, when exceeding slot limit, then surplus reposition instead of attacking | fair pressure, not mob smothering |

## Edge Cases
| Scenario | Expected Behavior | Ref |
|---|---|---|
| AI pathing fails (unreachable player) | declared fallback (reposition/reset), never idle-stuck in combat | FR-GAI-001 |
| Player exploits a behavior loop | on-purpose exploits kept; degenerate ones patched via tuning values | FR-GAI-004 |
| Two encounter triggers overlap | grammar's composition rule caps combined intensity | FR-GAI-003 |
| AI vs AI interactions (if factions) | rules of engagement stated | — |

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
