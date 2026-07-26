---
doc: GDD_Core_Loop_and_Mechanics
tier: standard+
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Core Loop & Mechanics

## Core Loop
_The repeating cycle at three time scales. Each arrow names what pulls the
player forward (reward, information, tension)._
- **Moment (~30s):** … → … → … → back
- **Session (~5–30min):** …
- **Meta (across sessions):** … (→ Systems Design for progression detail)

## Sixty-Second Walkthrough
_One paragraph of actual play, written as experienced: what the player
sees, presses, and feels for sixty seconds mid-game. If this paragraph is
boring, no systems table will save it. Update it whenever the loop
changes — it is the doc's beating heart._

## Interest Curve
_Within one session: where tension rises and releases. Name the release
valves (safe rooms, vendors, cutscenes) and the rule for spacing peaks._

## Player Verbs
_Everything the player can DO, exhaustively. If it's not a verb here, it's
not in the game._
| Verb | Input (per platform matrix) | Feedback (visual/audio/haptic) | Serves Pillar |
|---|---|---|---|

## Mechanics Register
_One row per mechanic. Depth prompts: what makes it interesting on the
100th use, not the 1st? Which verbs does it combine with?_
| ID | Mechanic | Rules (concise, unambiguous) | Interacts With | Serves Pillar | Tuning Values (named, not fixed) |
|---|---|---|---|---|---|
| MECH-01 | | | | PIL-x | |

## Controls & Game Feel
- Input mapping per platform; remappable (→ accessibility decision)
- Feel targets: input-to-response ≤ <N> frames for core verbs; camera
  behavior; the "juice" checklist for the core verb (anticipation, impact,
  follow-through)

## Failure & Recovery
_What failure means (death/reset/soft-fail), what is lost, and how fast
the player is back in the loop. Time-to-retry is a tuning value._

## Testable Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-LOOP-001 | Must | All verbs implemented per register with feedback triple | Given verb <v>, when performed, then its feedback triple fires within the feel target | |
| FR-LOOP-002 | Must | Failure/recovery per definition; time-to-retry ≤ tuning value | Given failure, when it resolves, then the stated loss applies and retry is available within the target time | retry never buried in menus |

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
