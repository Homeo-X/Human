---
doc: PRD_FR_Navigation
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Navigation

## Purpose & Scope
Moving through the model: semantic zoom (changing biological abstraction level)
versus physical zoom (changing magnification), the derived navigation tree,
layers, isolation, sectioning, and the preservation of context across level
transitions. Boundary: what a level *is* → PRD_FR_Scale_Bridging; geometry →
PRD_FR_Spatial_Representation; visual design → TECH_UI_UX_Design.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Student | to zoom into the heart and keep going until the mechanism appears | the scales feel continuous rather than like separate apps |
| Student | to know when the model changed what kind of thing it is showing me | I do not read a schematic as an anatomy |
| Educator | to isolate one system and section through it | I can show what I am talking about |
| Researcher | to navigate the graph rather than the tree when the tree misleads | multi-system organs are reachable from either system |
| Any user | to get back to where I was after descending five levels | exploring is not punished |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-NAV-001 | Must | Semantic zoom and physical zoom are distinct operations with distinct controls | Given a user magnifying the view, when they do so, then the level and the model's claim are unchanged; and given a user changing level, when they do so, then it is an explicit action, never a side effect of scrolling | Conflating them is BRB-08; a scroll wheel that silently changes ontological resolution is the failure |
| FR-NAV-002 | Must | Crossing a level boundary announces the new level, its representation mode, and its resolution limit | Given a transition from L3 to L5, when it completes, then the level, mode, and resolution limit are surfaced; and given a transition into a `typed` or `exemplar` level, then the surface states that what is shown is not a located object in this body | The announcement must be legible without being modal — users will cross levels constantly |
| FR-NAV-003 | Must | Descending past a subsystem's declared depth returns the terminal answer, never an empty view | Given a user descending past declared depth, when the request resolves, then the terminal statement is shown naming the level reached; and given available external resources, then they are offered | The single most important honesty surface in the product |
| FR-NAV-004 | Must | The navigation tree is presented as a derived view and is never editable as if it were the model | Given the tree view, when displayed, then it is identifiable as a navigational view; and given an organ with multi-system membership, when reached via the tree, then its other memberships are visible from that position | This is BRB-30; a tree presented as structure teaches a false containment |
| FR-NAV-005 | Must | Any entity is reachable from every system it participates in, not only from one filing location | Given the pancreas, when navigating from the digestive system and from the endocrine system, then both paths reach it and both memberships are shown as equal | The pancreas test is the acceptance test for D-006 at the UI layer |
| FR-NAV-006 | Must | Navigation state is addressable and restorable | Given a user five levels deep, when they share or reload the address, then the same entity, level, and view state are restored; and given a back action, then the previous state returns | Deep exploration is worthless if it cannot be returned to or handed to a student |
| FR-NAV-007 | Should | Layers can be toggled by system, by tissue class, and by evidence class | Given a user filtering to show only EVC-1 and EVC-2 content, when applied, then lower-graded content is hidden with a count of what was hidden | Filtering by evidence is the feature that makes the grading useful rather than decorative |
| FR-NAV-008 | Should | Isolation and sectioning operate on entities, not on meshes | Given a user isolating the left ventricle, when applied, then the entity and its parts are isolated regardless of how geometry is packaged; and given sectioning, then the cut plane reports which entities it crosses | Operating on meshes would make behaviour depend on artwork packaging |
| FR-NAV-009 | Should | Graph navigation is available alongside tree navigation, traversing typed relations | Given an entity, when the user follows `produces`, then targets are reached with the relation type shown; and given an `associated_with` edge, then it is traversable but labelled as untyped | Users should be able to feel the difference between a mechanism and an association |
| FR-NAV-010 | Should | Context is preserved across level transitions — the parent lineage remains visible | Given a user at L9 within the heart, when they orient, then the lineage from L0 to the current entity is visible and each ancestor is one action away | Losing the thread is the most common failure of deep zoom interfaces |
| FR-NAV-011 | Could | Navigation history can be exported as a path for teaching | Given a sequence of navigation states, when exported, then a replayable path is produced | Educators build sequences; letting them save one is cheap and high value |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| NavigationView | RW | the derived tree and view state |
| Entity | R | navigation targets |
| Relationship | R | graph traversal |
| SpatialIdentity | R | isolation and sectioning targets |
| ScaleLevel | R | transition announcements and terminal answers |
| GeometryAsset | R | rendering |
| Query | W | navigation-originated queries |

## States & Transitions
View state: `{entity, level, camera, layers, isolation, section}`. Level
transitions are explicit and logged in history. Descending past declared depth
transitions to a `terminal` state, which is a first-class view with its own
design, not an error state.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: navigating to an entity with no geometry and no children | the described-not-depicted state with position and relations shown | FR-NAV-003 |
| Invalid input: an address referencing a retired entity | resolves to the tombstone and offers the successor | FR-NAV-006 |
| Permission denied: not applicable — the reference model is readable without authentication | stated explicitly rather than left unconsidered | — |
| Concurrency: the underlying release changes while a user is deep in a session | the session pins its release; a new release is offered, never applied mid-session | FR-NAV-006 |
| External dependency failure: geometry unavailable mid-descent | navigation continues on spatial identities and relations; the failure is distinguished from absence | FR-NAV-003 |
| Scale extreme: a system with thousands of entities at one level | level content is paginated and filtered by default with counts shown; the raw list is reachable but not the default | FR-NAV-007 |
| A user zooms physically far past what the geometry supports | magnification stops with the asset's resolution limit stated, rather than showing polygon detail as if it were anatomy | FR-NAV-001 |
| An entity is reachable by two tree paths | both paths resolve to the same entity and the tree marks that it is showing one of several memberships | FR-NAV-005 |

## Dependencies
- On other modules: PRD_FR_Scale_Bridging (levels, terminal answers),
  PRD_FR_Spatial_Representation (geometry, spatial identities),
  PRD_FR_Relationship_Graph (graph traversal, derived tree),
  PRD_FR_Evidence (evidence-class filtering), PRD_FR_Search (entry by query)
- On external integrations: none

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Level transitions that announce mode and resolution limit | G-04 | 100% |
| Multi-system entities reachable from every system they belong to | G-02 | 100% |
| Navigation states that are addressable and restorable | G-07 | 100% |
| Descents past declared depth returning the terminal answer rather than an empty view | G-03 | 100% |

## Out of Scope for This Module
- Visual design and component specification (TECH_UI_UX_Design)
- Rendering performance targets (PRD_Non_Functional_Requirements)
- Editing the model from a navigation surface (PRD_FR_Curation)
- Personalized views (PRD_FR_Personalization, Phase 7)

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| What is the right control vocabulary for semantic zoom so it never feels like a mode switch? | Model Reviewer | Phase 1 |
| Should evidence-class filtering be discoverable by default, or does it imply the unfiltered view is untrustworthy? | Model Reviewer | Phase 2 |
| How is lineage displayed for a spanning process, which has no single parent at any one level? | Model Reviewer | Phase 3 |
