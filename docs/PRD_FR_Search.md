---
doc: PRD_FR_Search
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Search

## Purpose & Scope
Finding things by name, by function, by clinical term, by structured graph query,
and by spatial predicate — plus querying the negative space, which is what
distinguishes this from a search box. Boundary: natural-language explanation →
PRD_FR_Knowledge_Retrieval; traversal semantics → PRD_FR_Relationship_Graph;
navigation → PRD_FR_Navigation.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Student | to find a structure by the name my textbook uses | synonyms and eponyms do not block me |
| Clinician | to search by the clinical term I actually say | I do not have to translate into formal anatomy first |
| Educator | to find structures by function — "what secretes insulin" | I can build a lesson around a process |
| Researcher | to run a structured query over the graph | I can extract a slice with its provenance |
| Researcher | to ask what is *not* known about a structure | the gaps are findable rather than inferred from silence |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-SRCH-001 | Must | Name search resolves preferred terms, synonyms, eponyms, and abbreviations, and states which matched | Given a search for an eponym, when executed, then the entity is returned with the preferred term shown and the eponym marked as the match; and given no match, then near matches are offered rather than an empty result | Showing which term matched teaches the vocabulary, not just the answer |
| FR-SRCH-002 | Must | Every result carries the entity's compilation status and the evidence class of the claim that matched | Given a result matched on a `narrative` entity, when displayed, then its status is visible in the result row; and given a result matched on an EVC-6 claim, then the class is shown | A results list is where evidence grading is most easily lost and most needed |
| FR-SRCH-003 | Must | Function search matches against function and process claims, not only labels | Given "what secretes insulin", when executed, then entities with a `produces` edge to insulin are returned; and given a function with no compiled representation, then the narrative entity is returned marked as narrative | Function search over `narrative` content must not imply the function is modelled |
| FR-SRCH-004 | Must | Negative-space query is supported: what is unknown, unrepresented, or unmodelled about a subject | Given a query for what is unknown about the pancreas, when executed, then EVC-8 claims, unpopulated declared levels, and processes named-but-not-modelled are returned; and given a fully covered subject, then an explicit "no recorded gaps at this level" answer | This is the feature that makes honesty usable rather than merely present |
| FR-SRCH-005 | Must | Structured graph query supports filtering by entity class, level, subsystem, relation type, evidence class, and compilation status | Given a query for all L3 entities in the cardiovascular system with EVC-2 or better function claims, when executed, then exactly those are returned; and given an unbounded traversal, then a depth limit applies and is stated | The query surface is how researchers get value; it must be documented, not discovered |
| FR-SRCH-006 | Must | Results never present a claim without its grade, and never rank by confidence in a way that hides low-graded content | Given mixed-grade results, when ranked, then grade influences ordering only alongside relevance and the ordering basis is stated; and given a filter for high-grade only, then the count of excluded results is shown | Silently burying EVC-6 content is a subtler version of deleting it |
| FR-SRCH-007 | Should | Spatial query supports containment, adjacency, and laterality predicates | Given "what is adjacent to the left ventricle", when executed, then adjacency edges from its spatial identity are returned; and given entities lacking spatial identities, then they are excluded with a stated reason | Spatial search must work on spatial identities, not on mesh proximity |
| FR-SRCH-008 | Should | Clinical-term search maps lay and clinical vocabulary to canonical entities, with the mapping shown | Given "heart attack", when searched, then the mapping to the affected structures is shown as a mapping, not as a diagnosis; and given an ambiguous clinical term, then the alternatives are offered | The non-diagnostic boundary applies here — clinical search must not become clinical answering |
| FR-SRCH-009 | Should | Query results are exportable with the provenance of every returned claim | Given an exported result set, when inspected, then each claim carries its full provenance record and the release id | An export without provenance recreates exactly the problem this project exists to solve |
| FR-SRCH-010 | Could | Saved queries can be re-run against a later release and diffed | Given a saved query and two release ids, when re-run, then results are diffed by entity and by claim | Turns the knowledge base into something researchers can track over time |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Query | RW | query records and saved queries |
| Entity | R | search targets |
| Claim | R | function, clinical, and evidence matching |
| Relationship | R | graph queries |
| SpatialIdentity | R | spatial predicates |
| ScaleLevel | R | level filters and unpopulated-level reporting |
| KnowledgeRelease | R | queries are release-scoped |

## States & Transitions
Saved query lifecycle: `draft` → `saved` → `pinned to release` or `floating`. A
pinned query returns stable results forever; a floating query returns current
results and reports which release answered it. Neither is the default silently —
the choice is explicit at save time.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: a query with no matches | near matches and the reason for zero results; a query that matched nothing because a level is unpopulated says so | FR-SRCH-001 |
| Invalid input: malformed structured query | syntax error with position and a corrected suggestion; never a silent partial execution | FR-SRCH-005 |
| Permission denied: not applicable for reference-model search | stated explicitly; personalized search is Phase 7 and separately governed | — |
| Concurrency: a release is published mid-query | the query completes against its starting release, and the newer release is noted | FR-SRCH-010 |
| External dependency failure: the search index is stale or unavailable | fall back to direct graph query with reduced ranking and say so; never return silently degraded results as complete | FR-SRCH-005 |
| Scale extreme: a query matching most of the graph | paginated with total count; an unbounded export requires explicit confirmation | FR-SRCH-005 |
| A clinical term maps to a pathology the model does not represent | returns the structures involved and states the pathology itself is out of scope | FR-SRCH-008 |
| Negative-space query on an entity that has never been curated | distinguishes "no gaps recorded because nothing was assessed" from "assessed, no gaps" | FR-SRCH-004 |

## Dependencies
- On other modules: PRD_FR_Ontology (terminology), PRD_FR_Relationship_Graph
  (traversal), PRD_FR_Evidence (grades, UNKNOWN claims), PRD_FR_Scale_Bridging
  (unpopulated levels), PRD_FR_Spatial_Representation (spatial predicates),
  PRD_FR_Versioning (release scoping)
- On external integrations: none

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Results carrying compilation status and evidence class | G-03 | 100% |
| Negative-space queries returning an explicit answer rather than an empty set | G-03 | 100% |
| Exports carrying full provenance | G-07 | 100% |
| Entities reachable by at least one non-preferred term | G-02 | Phase 2: 80% of L0–L3 |

## Out of Scope for This Module
- Natural-language answering and summarization (PRD_FR_Knowledge_Retrieval)
- Diagnosis or clinical interpretation of any search term
- Full-text search of source documents — the model indexes claims, not literature

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| Does evidence-class ranking bias users away from legitimately uncertain content? | Model Reviewer | Phase 2 |
| What clinical vocabulary is authoritative for lay-term mapping, and who maintains it? | Biology Lead | Phase 2 |
| Should negative-space query be a mode or a facet of every search? | Model Reviewer | Phase 2 |
