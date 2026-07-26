---
doc: GDD_Player_Experience
tier: standard+
version: 0.0.0
status: template
owner: ux
last_updated: —
---

# Player Experience

_UX-owned. Pass A here mirrors the product profile: review Core Loop,
Systems, and Content docs for playability and file the punch list before
the Technical Director locks anything._

## First-Time User Experience (FTUE)
_Minute-by-minute for the first session: what the player feels, learns,
and achieves. The first core-loop completion time is a tracked number._
| Minute | Player Does | Player Learns | Risk of Churn Here |
|---|---|---|---|

## Onboarding Principles
- Teach by doing per the level teaching pattern; text is a last resort
- Skippable for returning/experienced players — state how detected/offered

## UI/HUD Direction
- Diegetic vs overlay stance; information hierarchy: the 3 things always
  readable at a glance; menu map (screen list, one line each)

## Game Accessibility
_Each row is a decision, not an aspiration; "no" requires a reason._
| Feature | In? | Notes |
|---|---|---|
| Full input remapping | | |
| Subtitles + speaker labels + size options | | |
| Colorblind-safe critical information | | never color alone |
| Difficulty/assist options | | which knobs |
| Screen shake / flash reduction toggles | | photosensitivity |
| Hold-to-toggle alternatives | | motor accessibility |

## Settings Inventory
_Every player-facing setting, grouped (display/audio/controls/
accessibility/gameplay), each with default + persistence scope. Settings
are requirements, not leftovers — this inventory feeds FR-PXP-002._

## Player Emotional Arc
_Target feeling per phase (first session / mid / mastery) and what
delivers it. This is what playtests validate._

## Testable Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-PXP-001 | Must | FTUE per table; first loop completion ≤ <N> min for ≥80% of playtesters | Given a new playtester, when starting, then first core-loop completion is measured and within target | |
| FR-PXP-002 | Must | Accessibility rows marked "In" implemented and reachable from first boot | Given first boot, when options open before forced input, then every 'In' row is present and functional | options before first forced input |
| FR-PXP-003 | Must | HUD glance test: the 3 always-readable items legible at platform viewing distance | Given target hardware at platform distance, when tested, then all three items pass legibility review | |

## Edge Cases
| Scenario | Expected Behavior | Ref |
|---|---|---|
| Player ignores/skips tutorial | required teaching embedded in play, not skippable text | FR-PXP-001 |
| Second player on same device (if local) | FTUE not re-forced; profile-aware | FR-PXP-001 |

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
