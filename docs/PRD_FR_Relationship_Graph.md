---
doc: PRD_FR_Relationship_Graph
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Relationship Graph

## Purpose & Scope
The typed edges that make the model a graph rather than a list: their vocabulary,
inverses, cardinality, admissibility, and provenance. Owns the tree-versus-graph
distinction (D-006) at the data level. Boundary: entity identity → PRD_FR_Ontology;
the navigation tree as a rendered view → PRD_FR_Navigation; cross-scale edge rules
→ PRD_FR_Scale_Bridging.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Student | to see every system an organ participates in, not just its filing location | I understand the pancreas as it actually is |
| Researcher | to traverse typed edges in a query | I can ask "what does this affect" and get a real answer |
| Curator | to record that two things are related before I know how | I do not have to invent a relation type to capture a real observation |
| Curator | to be stopped from asserting an inadmissible relation | the graph does not accumulate quiet nonsense |
| Reviewer | to see which edges are untyped associations awaiting compilation | I know what work remains |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-REL-001 | Must | Every edge carries a type from the BIO_Anatomical_Ontology relation vocabulary; untyped edges are inadmissible | Given an edge submitted without a type, when validated, then it is rejected; and given an edge with a vocabulary type, when validated, then it passes | The vocabulary must be browsable — curators cannot use types they cannot find |
| FR-REL-002 | Must | Every relation type declares an inverse, and the inverse is materialized or derivable for traversal in both directions | Given `pancreas produces insulin`, when insulin's relations are requested, then `produced_by pancreas` is returned; and given a type with no declared inverse, when registered, then registration fails | Users navigate in both directions without knowing which way the edge was authored |
| FR-REL-003 | Must | `part_of` is single-parent and acyclic; multi-system participation uses `member_of` | Given an entity assigned a second `part_of` parent, when validated, then INV-02 fails; and given the pancreas with one `part_of` and two `member_of` edges, when validated, then it passes | The pancreas case must render as two equal memberships, not a primary and a footnote |
| FR-REL-004 | Must | Edges are validated against per-type admissibility between the levels and classes of their endpoints | Given a `secretes` edge from a bone to a region, when validated, then INV-01 fails naming the type and both levels; and given an admissible pairing, when validated, then it passes | The rejection message must be biological, not schematic |
| FR-REL-005 | Must | `causes` requires evidence class EVC-2 or better, and a skip justification when it spans more than one level | Given a `causes` edge backed only by an EVC-5 claim, when validated, then it is rejected and `contributes_to` is suggested; and given an EVC-2-backed single-level `causes` edge, when validated, then it passes | Causal language is what users trust most, so it must be what the model gates hardest |
| FR-REL-006 | Must | `associated_with` records an observed relationship of unstated type, carries its prose justification, and is never rendered as a mechanism or a causal claim | Given an `associated_with` edge, when displayed anywhere, then it is labelled as an untyped association with its justification available; and given an attempt to render it in a mechanism view, when requested, then it is excluded | This is BRB-30; an association drawn like a mechanism is a fabricated mechanism |
| FR-REL-007 | Must | Promoting `associated_with` to a specific type requires a recorded curation decision with a source | Given an `associated_with` edge and a curator selecting `regulates`, when submitted without a source, then it is rejected; and given a source, when submitted, then the edge is retyped and the decision recorded | Show the original prose alongside the proposed type — the prose is the evidence the curator is judging |
| FR-REL-008 | Must | Every edge carries its own provenance; an edge does not inherit its endpoints' evidence | Given an edge whose endpoints are both EVC-2 but which has no source of its own, when validated, then it is flagged incomplete; and given an edge with its own claim, when validated, then it passes | This is BRB-15 — users assume a drawn line is as well-evidenced as the things it joins |
| FR-REL-009 | Should | The navigation tree is computed from the graph as a derived view and is regenerable | Given a change to containment edges, when the tree view is next requested, then it reflects the change without manual curation; and given the tree, when inspected, then it is identifiable as derived | The tree must never be editable as if it were the model |
| FR-REL-010 | Should | Queries can traverse by relation type, direction, and level | Given a query for everything the pancreas affects, when executed, then only `affects` and `contributes_to` edges are traversed; and given an unbounded traversal request, when executed, then it is depth-limited with the limit stated | An unbounded graph traversal returns everything, which is the same as returning nothing |
| FR-REL-011 | Could | Edge sets can be diffed between two knowledge releases | Given two release ids, when diffed, then added, removed, and retyped edges are listed separately | Retyping is the interesting case and should not hide inside add/remove |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Relationship | RW | the edge record |
| RelationshipType | R | vocabulary with inverses and admissibility |
| Entity | R | endpoints |
| Claim | RW | per-edge provenance |
| ScaleLevel | R | admissibility checks |
| CurationTask | W | retyping tasks |
| NavigationView | W | the derived tree |

## States & Transitions
Edge type lifecycle: `associated_with` → a specific type, via a recorded curation
decision. One-way; an edge is never demoted to `associated_with`, because
demotion would discard the reasoning that produced the type. An edge found wrong
is retired and replaced, with both recorded.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: an entity with no edges | returns an empty set with a note that the entity is uncompiled, distinguishing "no relations recorded" from "no relations exist" | FR-REL-001 |
| Invalid input: an edge to a non-existent entity | rejected; dangling edges are never stored | FR-REL-004 |
| Permission denied: a non-curator retypes an edge | rejected; a suggestion is queued instead | FR-REL-007 |
| Concurrency: two curators retype the same association differently | first commit wins; the second is rejected with the current type and both proposals preserved for review | FR-REL-007 |
| External dependency failure: an endpoint's authority is unreachable during admissibility check | the edge is held pending rather than admitted unvalidated | FR-REL-004 |
| Scale extreme: a hub entity with thousands of edges | traversal and rendering are paginated and type-filtered by default; the raw set is available but never the default | FR-REL-010 |
| A cycle is introduced through `part_of` | rejected with the cycle path shown | FR-REL-003 |
| An edge's endpoints are retired | the edge is retired with them and appears in the release diff | FR-REL-011 |

## Dependencies
- On other modules: PRD_FR_Ontology (endpoints), PRD_FR_Evidence (edge
  provenance), PRD_FR_Scale_Bridging (cross-level rules), PRD_FR_Validation
  (INV-01, INV-02, INV-05), PRD_FR_Curation (retyping workflow)
- On external integrations: none directly; relation vocabularies are informed by
  RO (Relations Ontology) conventions but not imported

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Entities carrying at least one typed relation of each mandatory class for their level | G-02 | Phase 3: 95% |
| Edges carrying their own provenance | G-03 | 100% |
| Proportion of seed cross-links still at `associated_with` | G-02 | published per release; falling is the goal, zero is not required |
| Cross-scale edges with justification | G-04 | 100% |

## Out of Scope for This Module
- Rendering the graph (PRD_FR_Navigation, TECH_UI_UX_Design)
- Inferring new edges automatically — no edge is created by inference in Phase 0;
  if it is ever permitted, it will be its own graded claim class
- Importing third-party relation assertions wholesale

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| Does `associated_with` need a sub-vocabulary, or does typing always resolve it? | Biology Lead | Phase 2 |
| Which of the 31 seed cross-links can be typed from their existing sources? | Biology Lead | Phase 1 |
| Should inverse edges be materialized or always derived, given expected hub sizes? | Research Engineer | Phase 1 |
