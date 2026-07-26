---
doc: PRD_FR_Scale_Bridging
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Scale Bridging

## Purpose & Scope
The L0–L10 level contracts and the rules governing movement and inference between
them: level assignment, declared depth enforcement, cross-scale edges, spanning
entities, and the honest terminal answer below the deepest represented level.
Absorbs the brief's `FR-CELL` — cellular and subcellular content is governed by
its level contract, not by a separate capability. Boundary: entity identity →
PRD_FR_Ontology; edge typing → PRD_FR_Relationship_Graph; the zoom interaction →
PRD_FR_Navigation.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Student | to descend from an organ to the mechanism inside it without losing my place | the levels feel like one object, not eight documents |
| Student | to be told plainly when the model stops | I do not mistake the model's edge for the biology's edge |
| Researcher | to know what each level's representation actually is | I can judge whether a level supports the query I want to run |
| Curator | to be stopped from adding content deeper than the declared depth | the declaration keeps meaning something |
| Reviewer | to see which cross-scale edges skip levels and why | I can check the ones most likely to assert false causation |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-SCAL-001 | Must | Every level L0–L10 has an SCL contract declaring representation mode, data model, spatial model, functional model, evidence model, uncertainty model, cost, and resolution limit | Given an SCL row with an empty resolution limit, when validated, then specgraph errors on the level; and given all eleven rows complete, when validated, then it passes | The resolution limit is the sentence users most need and least expect; it belongs in the level transition, not a reference page |
| FR-SCAL-002 | Must | Each subsystem declares a maximum level; no entity or claim may exceed it | Given an L7 entity in an L3-declared subsystem, when validated, then INV-05 fails; and given an entity at or above its subsystem's declared depth, when validated, then it passes | Correct content that exceeds the declaration is still rejected — that is what makes the declaration a commitment |
| FR-SCAL-003 | Must | Reaching the deepest declared level returns the terminal answer from BIO_Scale_Contract, never an empty view or a generic rendering | Given a user descending past the declared depth of a subsystem, when the request resolves, then the terminal statement is returned naming the level and mode reached; and given available external resources, then they are offered | An empty viewport reads as a bug; a stated limit reads as honesty. The difference is entirely in the design |
| FR-SCAL-004 | Must | Cross-scale edges spanning more than one level carry a recorded skip justification naming the levels skipped | Given a `causes` edge from L9 to L0 with no justification, when validated, then INV-05 fails listing the skipped levels; and given a justification, when validated, then it passes and the justification is displayed with the edge | This is BRB-06 — molecule-to-symptom in one hop is the characteristic false-causation move |
| FR-SCAL-005 | Must | A process or mechanism spanning levels declares `spatial_scale` as an ordered list and, per level, what it contributes there | Given a process spanning L3 to L9 with no per-level contribution stated, when validated, then it is flagged incomplete; and given a complete declaration, when validated, then it passes | A spanning process is one object at several levels, and the UI must not fragment it into several |
| FR-SCAL-006 | Must | Spanning does not bypass declared depth: every listed level must be within the subsystem's declaration | Given a process in an L5-declared subsystem listing L9 in its spatial scale, when validated, then INV-05 fails; and given all listed levels within the declaration, when validated, then it passes | Spanning describes where a process acts, never a route around the contract |
| FR-SCAL-007 | Must | No entity claims a representation mode its level's SCL row does not offer | Given an entity claiming `enumerated` at a level declared `typed`, when validated, then INV-13 flags it; and given a mode the level offers, when validated, then it passes | Schematic content must be marked schematic at every binding site, not once in a legend |
| FR-SCAL-008 | Should | Content arriving under an external level scheme is mapped on ingest, and the mapping is recorded | Given content in the common eight-level scheme, when ingested, then each item's level is assigned per the reconciliation table and the source scheme recorded; and given an unmappable level, when ingested, then it is held for review | A later reader must be able to tell whether a level was chosen or inherited |
| FR-SCAL-009 | Should | A cross-scale path between two entities can be requested and returns the intermediate levels, or states which are missing | Given an L3 organ and an L9 molecule with a complete chain, when a path is requested, then the intermediate entities are returned in level order; and given a broken chain, then the missing level is named | The gap is the interesting result — a path query that silently returns nothing teaches nothing |
| FR-SCAL-010 | Must | Per-subsystem, per-level population is reported against declared scope, and is surfaced in the product from Phase 1 — not only as a release metric | Given a coverage request, when produced, then each subsystem shows entities present against declared scope per level; and given a subsystem declared to a level with zero entities at it, when the Coverage surface renders, then the unmet declaration is visible rather than implied | This is G-01's denominator made visible. Raised from Could to Must by BIO_Model_Review PUNCH-01: a declared depth with no content is a promise, and the product must show it unmet |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| ScaleLevel | RW | the SCL contracts |
| Entity | R | level and subsystem assignment |
| Relationship | R | cross-scale edges and their justifications |
| Process | R | spanning declarations |
| KnowledgeRelease | R | declared depths are release-scoped |

## States & Transitions
A subsystem's declared depth changes only through a Scope Reopen (AGENTS.md §9)
with a Decision entry — deepening admits new content, narrowing requires
retiring or re-scoping anything already deeper. Neither is a routine edit, and
narrowing in particular cannot be used to improve a coverage percentage.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: a declared level with no entities | reports zero against declared scope and states the level is declared but unpopulated | FR-SCAL-010 |
| Invalid input: an entity with a level outside L0–L10 | rejected at ingest | FR-SCAL-001 |
| Permission denied: a curator attempts to deepen a declared depth | rejected; only a Scope Reopen changes a declaration | FR-SCAL-002 |
| Concurrency: two curators add content at a level being narrowed | the narrowing blocks until conflicting content is resolved; content is never silently orphaned | FR-SCAL-002 |
| External dependency failure: the declared-depth source (MANIFEST) is unavailable to a runtime check | fail closed — reject the write rather than admit unvalidated content | FR-SCAL-002 |
| Scale extreme: a user requests a cross-scale path across all eleven levels | returned with per-level counts and a stated traversal limit rather than an unbounded expansion | FR-SCAL-009 |
| A spanning process lists levels in two subsystems with different declared depths | validated against each subsystem's own declaration; the stricter one governs the shared portion | FR-SCAL-006 |
| Correct, well-sourced content is rejected for exceeding declared depth | rejection stands, and a Scope Reopen request is offered with the content attached | FR-SCAL-002 |

## Dependencies
- On other modules: PRD_FR_Ontology (levels on entities),
  PRD_FR_Relationship_Graph (cross-scale edges), PRD_FR_Validation (INV-05,
  INV-13), PRD_FR_Navigation (the zoom surface), PRD_FR_Process_Models (spanning)
- On external integrations: none

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Cross-scale edges with recorded justification | G-04 | 100% |
| L3 entities reachable from L0 by containment | G-04 | 100% |
| SCL rows complete on all declared columns | G-05 | 100%, enforced at validation |
| Entities exceeding declared depth | G-05 | 0, enforced |

## Out of Scope for This Module
- The zoom interaction itself (PRD_FR_Navigation)
- Deciding what depth a subsystem should have — that is a scoping decision
- Automatic inference of cross-scale edges

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| What justification quality is sufficient for a level-skipping `causes` edge? | Biology Lead | Phase 3 |
| Should the terminal answer name external resources, and does that create an implied endorsement? | Model Reviewer | Phase 2 |
| How is a spanning process displayed when the user is at one of its levels but not the others? | Model Reviewer | Phase 3 |
