---
doc: DESIGN_RUBRIC
tier: standard+   # game profile — applied by UX pass A, dispositions in docs/GDD_Design_Review.md
version: 0.0.0
status: template
owner: ux
last_updated: —
---

# Game Design Rubric

_Known failure modes of game design, phrased as checks. This is not a
style guide; it is the accumulated ways games go wrong on paper before
they go wrong in players' hands. **Protocol:** in UX pass A, every item
gets a disposition — **pass** (with one line of evidence), **flag**
(becomes a punch-list item), or **N/A** (with the reason) — recorded in
`docs/GDD_Design_Review.md`. Silence is not a disposition. Flags that
survive the punch list become Decision Log entries: shipping a known
failure mode is allowed, but only on purpose._

## Core loop & feel
| ID | Check | How to Verify |
|---|---|---|
| RUB-01 | The loop closes without a meaningful decision — the player watches, doesn't play | name the decision inside the Sixty-Second Walkthrough; if none exists there, flag |
| RUB-02 | A dominant strategy is visible on paper | for each MECH, name the situation where it is NOT the best choice; any mechanic without one, flag |
| RUB-03 | A core verb lacks its feedback triple (anticipation, impact, follow-through) | verb table's feedback column vs feel targets |
| RUB-04 | Verb count masquerades as depth — many verbs, few interactions | MECH register's "Interacts With" column: mechanics interacting with ≤1 other, flag |
| RUB-05 | Failure costs time without teaching | trace one failure in the walkthrough: what did the player LEARN before retry? |
| RUB-24 | A feel target has no mapped playtest question | every feel number appears in the Playtesting feel-hypothesis table |

## Systems & economy
| ID | Check | How to Verify |
|---|---|---|
| RUB-06 | A source without a sink (or sink without source) | economy table row-by-row; inflation/starvation column filled honestly |
| RUB-07 | A snowball loop without damping | System Interaction Map: every reinforcing cycle names its damper |
| RUB-08 | Progression outpaces mastery — numbers grow, play doesn't change | per progression track: what does the PLAYER do differently at stage N+1? |
| RUB-09 | Difficulty scales by stat inflation only | difficulty model's levers: HP/damage scaling as the primary lever, flag |
| RUB-10 | Optimal play is boring play | describe the min-maxer's session; if it's a grind loop, players will do it and blame the game |

## Content & pacing
| ID | Check | How to Verify |
|---|---|---|
| RUB-11 | A mechanic is introduced and never recombined | teaching pattern: every MECH appears in ≥1 "combine/twist" beat after introduction |
| RUB-12 | Adjacent intensity peaks / no valley after a new mechanic | pacing curve vs the spacing rules it declares |
| RUB-13 | Content counts justified by comparisons, not by the loop | scope table rationale: "genre games have N levels" is a flag; "the loop sustains N" is a pass |

## Onboarding & player experience
| ID | Check | How to Verify |
|---|---|---|
| RUB-14 | Teaching by text where doing is possible | FTUE table: any "player reads" row where a "player does" row could exist |
| RUB-15 | First meaningful choice arrives late | FTUE minute-by-minute: minute of first decision that matters; beyond target, flag |
| RUB-16 | Accessibility rows defaulted to "no" without a reason | accessibility table: every "no" has its stated reason |

## AI & encounters
| ID | Check | How to Verify |
|---|---|---|
| RUB-17 | An archetype tests no player verb — damage furniture | archetype register's "tests which verb" column; blanks flag |
| RUB-18 | An AI cheat is perceivable | listed cheats vs the invisibility rule; any cheat a streamer would clip, flag |

## Narrative
| ID | Check | How to Verify |
|---|---|---|
| RUB-19 | Ludonarrative contradiction — story says X, systems reward not-X | themes vs economy/progression rewards, one pass |
| RUB-20 | A flavor-only branch presented as consequence | branching table's "what actually differs" column vs its presentation |

## Monetization & retention
| ID | Check | How to Verify |
|---|---|---|
| RUB-21 | Money buys power where a pillar claims skill | offer surface vs PIL register |
| RUB-22 | A retention hook punishes absence | returning-player path: what did a two-week absence cost beyond missed fun? |

## Meta
| ID | Check | How to Verify |
|---|---|---|
| RUB-23 | A pillar is unfalsifiable — nothing could violate it | each PIL's "rules OUT" column is non-empty and bites |
| RUB-25 | Genre-lens extra-depth docs were left at skeleton depth | lens row for the declared genre vs actual doc depth; skeletal extra-depth doc, flag |

## What this rubric cannot do
It catches known failure modes; it does not generate originality, and it
does not replace play. Feel is a hypothesis until a playtest confirms it —
the rubric's job is to ensure every such hypothesis is stated, mapped to a
rung (RUB-24), and falsified as early as possible.
