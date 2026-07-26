# Game Profile — GDD Document Set

Specification of the **game** profile (AGENTS.md §2). Everything not
stated here follows the framework unchanged: tiers, workflow, IDs,
versioning, scope lifecycle, spec graph, execution modes.

## Role mapping
Same four roles, game-flavored duties:
| Framework Role | Acts As | Owns (game profile) |
|---|---|---|
| Orchestrator | Producer | scoping, MANIFEST, cross-review — unchanged |
| PM | Game Designer | Game Concept, Core Loop & Mechanics, Systems Design, Content & Levels, Narrative, Monetization & Retention, Risks, Acceptance & DoD |
| UX | Player Experience Designer | Player Experience (FTUE, accessibility, game feel review); pass A = playability review of the design docs PLUS the full DESIGN_RUBRIC pass — every RUB item dispositioned (pass/flag/N-A) into `docs/GDD_Design_Review.md`; flags feed the punch list |
| Architect | Technical Director | TECH files (engine choice in System Architecture, save data in Data Design), NFRs (frame-time budget!), Security (anti-cheat when online), Data Overview if complex meta-game state |

## Document set per tier
| Tier | Set |
|---|---|
| **Light** (game jam, prototype, pitch) | `gdd/light/GDD_Prototype_Brief.md` + `core/PRD_Decision_Log` + `core/PRD_Acceptance_Criteria_and_DoD` + `light/TECH_Implementation_Notes` |
| **Standard** (indie production) | GDD core: Game_Concept, Core_Loop_and_Mechanics, Systems_Design, Content_and_Levels, Player_Experience, Art_and_Audio_Direction, Playtesting_and_Telemetry (+ Game_AI_and_Encounters per genre lens); shared core: Scope_and_Roadmap (phases per Production Milestones below), Risks_and_Constraints, Non_Functional_Requirements, Acceptance_Criteria_and_DoD, Decision_Log; TECH: **TECH_Game_Architecture** (replaces TECH_System_Architecture in this profile), Data_Design |
| **Full** (production / online / liveops) | Standard + Narrative + Monetization_and_Retention + Security_Requirements + Data_Overview + TECH_API_Specification (online services may add TECH_System_Architecture for the backend) + scoped `modules/games/` (Multiplayer, Save, LiveOps, Social, Platform_Services, UGC) and other modules (Auth, Analytics, i18n…) |

## Game-profile folds (Standard)
| File | Fold into (when omitted) |
|---|---|
| GDD_Narrative | Game_Concept §Story (premise-only games) |
| GDD_Art_and_Audio_Direction | Game_Concept §Direction (jam-adjacent scope) |
| GDD_Monetization_and_Retention | excluded with reason for premium/one-purchase games — exclusion, not fold |
| GDD_Game_AI_and_Encounters | GDD_Systems_Design §AI notes (genres with light AI) |
| GDD_Playtesting_and_Telemetry | never omitted at Standard+ — the tuning loop is not optional |
| PRD_Data_Overview | TECH_Data_Design (simple save state) |

## Cross-cutting checklist — game additions
AGENTS.md §5 applies in full, PLUS these get an explicit decision each:
platform & input matrix (PC/console/mobile; controller/kb+m/touch) ·
performance budget (target frame time per platform — an NFR row, always) ·
age rating & compliance (ESRB/PEGI/COPPA posture, loot-box law exposure) ·
anti-cheat & fair play (any online play) · save integrity & cloud sync ·
game accessibility (remapping, subtitles, colorblind, difficulty options)
· telemetry for balancing (what the designer needs to tune) ·
localization (text expansion in UI, VO subtitling) · monetization ethics
(no dark patterns; spend limits for minors) · community/UGC surface.

## ID registers (additions)
`PIL-N` design pillars (Game_Concept) · `MECH-NN` mechanics
(Core_Loop_and_Mechanics) · `ARCH-NN` AI archetypes
(Game_AI_and_Encounters). Testable requirements in GDD docs still use
`FR-<AREA>-NNN` (areas: LOOP, SYS, LVL, PXP, MON, GAI, PLAY; module
areas: MP, SAVE, LOPS, SOC, PLAT, UGC) so DoD, specgraph, and implementation tracing work unchanged. Design
prose that can't be Given/When/Then (art direction, narrative tone) is
acceptance-gated by named review gates in Acceptance_Criteria_and_DoD
instead — never left with no gate at all.

## Genre determination is binding, not advisory
The orchestrator classifies genre (primary + modifiers) at scoping and
records it in MANIFEST §Product. If the brief is vague on the
genre-determining axes — core fantasy, session shape, perspective,
competitive vs solitary — those questions are asked AT THE SCOPING
CHECKPOINT; genre is one of the few things never guessed silently. Once
declared, the lens row's extra-depth docs are a depth REQUIREMENT:
cross-review checks them (RUB-25) and a skeletal extra-depth doc is a
finding, not a style choice.

## Feel is a hypothesis, not a specification
Every feel claim (input latency, juice, tension pacing, "weighty",
"snappy") must appear in GDD_Playtesting_and_Telemetry's Feel Hypothesis
table mapped to a playtest rung and a question that could falsify it
(RUB-24). The framework's guarantee is not good feel — no document
produces that — but that no feel claim survives unexamined past the rung
that could kill it.

## What the game profile guarantees — and what it can't
Guaranteed: structural completeness, known-failure-mode coverage (the
rubric), binding genre depth, and early falsification of feel claims.
Not guaranteed: originality and the design insight itself — those remain
the designer's and the playtest loop's. The profile's honest claim is
that it makes bad design VISIBLE early, not that it makes design good.

## Production Milestones (plug into Scope_and_Roadmap phases)
| Milestone | Exit Criteria (minimum) |
|---|---|
| Prototype | The One Question answered (Prototype_Brief); core verb feels right on target input |
| Vertical Slice | One content unit at SHIP quality: full loop, final-quality art/audio for that unit, FTUE draft, frame budget met on min spec, fresh-eyes rung passed |
| Alpha | Feature-complete: every MECH/ARCH/system in, all content graybox+, telemetry live, no placeholder Musts |
| Beta | Content-complete: scope table counts met, loc/cert checklists closing, tuning from target-player rung, crash/frame gates green |
| Gold / Live | Release-level acceptance gates (Acceptance_Criteria_and_DoD) all green; day-one LiveOps config rehearsed if scoped |

## Genre Lens
The profile is one skeleton; genres redistribute depth. Extra-depth =
those docs get full treatment and their punch-list scrutiny in UX pass A;
everything else may stay lean.
| Genre | Extra-Depth Docs | Genre-Specific Prompts |
|---|---|---|
| Action / combat | Core_Loop (feel targets), Game_AI_and_Encounters | recovery windows, hit-stop/juice, encounter intensity grammar |
| RPG | Systems (progression math, meta-systems), Narrative | pace targets per hour, build diversity, choice consequence honesty |
| Strategy / sim | Systems (economy, System Interaction Map), Game_AI, Playtesting | AI as opponent fairness, snowball damping, readable simulation state |
| Puzzle | Content_and_Levels (teaching pattern, difficulty ramp) | mechanic-twist cadence, hint policy, unwinnable-state impossibility |
| Roguelike / run-based | Systems (meta-progression, RNG fairness), Content (procedural guarantees) | seeded fairness, run length vs session shape, knowledge-as-progression |
| Narrative / adventure | Narrative (full, branching honesty), Player_Experience | delivery-method budget, skippability persistence, pacing valleys |
| Competitive multiplayer | Multiplayer module, Systems (balance), Trust patterns | rank integrity, smurf posture, spectator/replay, patch-meta cadence |
| Horror | Player_Experience (pacing, audio), Art_and_Audio | tension/release spacing, safety accessibility (intensity sliders) |
| Casual / mobile | Monetization (ethics!), Player_Experience (session shape), mobile/ modules | one-hand play, interruption tolerance, App_Store_Release + LiveOps |
