---
doc: PRD_FR_Ontology
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Ontology

## Purpose & Scope
Canonical identity and classification for every biological entity in the model:
identifier minting, external cross-references, entity classes, levels, naming,
variation, and compilation status. Boundary: relationships between entities →
PRD_FR_Relationship_Graph; what is *known about* an entity → PRD_FR_Evidence;
where an entity is → PRD_FR_Spatial_Representation.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Curator | to add an entity with its external cross-reference resolved | it interoperates with the datasets I want to ingest |
| Curator | to be told when an upstream ontology term I depend on was split or deprecated | I can review the entity rather than discover it broken |
| Researcher | to see whether an identifier is community-standard or minted by this project | I can judge how portable my query results are |
| Student | to see the preferred anatomical term with its synonyms and eponyms | I can connect what my textbook calls it to what my lecturer calls it |
| Integrator | identifiers that never change meaning | my references keep resolving across releases |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-ONTO-001 | Must | Every entity carries a resolvable primary identifier — an external ontology term where one exists, otherwise a minted `HOX:<class>:<slug>` flagged `minted: true` with a reason | Given an entity with a suitable external term available, when it is admitted, then its primary id is that external term; and given an entity with no suitable external term, when it is admitted without `minted: true` and a reason, then admission fails with INV-10 | Minted vs standard must be visible at a glance, not buried in a detail pane |
| FR-ONTO-002 | Must | Every entity declares an entity class and a scale level, and the pair must be admissible per BIO_Anatomical_Ontology §Entity Classes | Given an entity declared as class `Organ` at level L7, when validated, then INV-05 fails naming the class/level mismatch; and given a valid pair, when validated, then it passes | Class and level shown together; a level shown without its representation mode is misleading |
| FR-ONTO-003 | Must | No entity exceeds the declared maximum level of its subsystem | Given an entity at L7 in a subsystem declared to L3, when validated, then INV-05 fails; and given an entity at or above its subsystem's declared depth, when validated, then it passes | When a user reaches the declared depth, the terminal answer is a designed surface, not an empty state |
| FR-ONTO-004 | Must | Identifiers are never reused, renumbered, or repurposed; a retired identifier resolves to a tombstone naming its successor | Given a retired entity id, when resolved, then a tombstone with the successor id is returned; and given an attempt to mint an id matching a retired one, when submitted, then it is rejected | A tombstone must read as "this moved" not "this is broken" |
| FR-ONTO-005 | Must | An upstream split blocks the affected entity from compilation-status promotion until a reviewer assigns it | Given an entity whose external term was split upstream, when promotion is attempted, then it is blocked with the ambiguity cited; and given a reviewer assignment recorded, when promotion is retried, then it proceeds | The block needs to explain the biology of the split, not just report a version change |
| FR-ONTO-006 | Must | Every entity carries a compilation status from the D-007 ladder, and status is exposed on every surface and API response that exposes the entity | Given an entity at `narrative` status, when returned by any API, then the response carries the status; and given a UI rendering it, when displayed, then the status is visible without interaction | This is BRB-29's check; status must not be a tooltip |
| FR-ONTO-012 | Must | Promotion from `narrative` to `structured` requires the subject's claims to carry a population more specific than the source's default; a blanket "unspecified in source" blocks promotion | Given an entity whose claims all carry "unspecified in source" as population, when promotion to `structured` is attempted, then it is blocked naming the field; and given claims with discriminating populations, then promotion proceeds | The field exists to distinguish genuine conflicts from population differences (CH-05); at a constant value it cannot do that job |
| FR-ONTO-007 | Must | Compilation status is promoted only by recorded curation work, never by reformatting or re-ingest | Given a `narrative` entity re-ingested in a structured file format, when processed, then its status remains `narrative`; and given a completed, reviewed typing task, when applied, then the status advances and records the reviewer | Promotion history should be inspectable — it is the record of what was actually done |
| FR-ONTO-008 | Should | Terminology records carry preferred term, synonyms, eponyms, and abbreviations, each with its source and register | Given a structure with a common eponym, when its terminology is requested, then the preferred term is authoritative and the eponym appears as a synonym with its register; and given no authority-defined term, then the fallback is recorded as such | Eponyms are how clinicians actually speak; demoting them must not mean hiding them |
| FR-ONTO-009 | Should | A locale without an authoritative nomenclature falls back to the Latin term rather than a machine translation | Given a locale with no pinned nomenclature authority, when a term is requested, then the Latin term is returned with the fallback stated; and given a locale with an authority, then that authority's term is returned | A plausible mistranslation is worse than an untranslated term, and the UI must say which it is showing |
| FR-ONTO-010 | Should | Anatomical variants are represented as `variant_of` entities or variant relationship sets, with a prevalence claim | Given a structure with a documented presence/absence variant, when requested, then the modal form is returned labelled as modal with variants linked; and given a variant with no prevalence source, when admitted, then it is flagged incomplete | "Reference" must not read as "normal, and yours is wrong" |
| FR-ONTO-011 | Could | The count of minted identifiers is published per release as a drift signal | Given a release, when its manifest is produced, then the minted-id count and its delta from the prior release appear | A rising count is a signal for the team, not a user-facing metric |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Entity | RW | the core record |
| EntityClass | R | controlled vocabulary |
| ScaleLevel | R | SCL contracts |
| Authority | R | external ontology authorities and pinned versions |
| Claim | R | terminology and prevalence claims |
| CurationTask | W | promotion and split-resolution tasks |
| KnowledgeRelease | R | the release an entity belongs to |

## States & Transitions
Entity compilation status: `narrative` → `structured` → `mechanistic` →
`parameterized`. Forward only, one step at a time, each transition requiring a
recorded reviewed task. Additional lifecycle: `proposed` → `admitted` →
`retired` (tombstoned). An entity blocked by an upstream split holds a
`promotion_blocked` flag orthogonal to its status.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: a subsystem with no entities yet | the subsystem resolves and reports zero entities against its declared scope, never a 404 | FR-ONTO-002 |
| Invalid input: an id in a malformed namespace | rejected at ingest with the expected form shown | FR-ONTO-001 |
| Permission denied: a non-curator attempts entity admission | rejected; the proposal is queued for curation rather than discarded | FR-ONTO-007 |
| Concurrency: two curators promote the same entity simultaneously | one succeeds, the other is rejected with the current status; promotion is not idempotent and must not double-advance | FR-ONTO-007 |
| External dependency failure: an authority is unreachable at ingest | ingest halts for entities requiring resolution rather than minting local ids as a fallback — silent minting would corrupt the drift signal | FR-ONTO-001 |
| Scale extreme: an upstream release splits hundreds of referenced terms at once | all affected entities are blocked and batched into one review task; the system does not emit hundreds of individual blocks | FR-ONTO-005 |
| Upstream term is deprecated with no successor | the entity retains the deprecated term, flagged, and a curation task is raised; the entity is not retired automatically | FR-ONTO-005 |

## Dependencies
- On other modules: PRD_FR_Evidence (terminology and prevalence claims),
  PRD_FR_Validation (INV-02, INV-05, INV-10), PRD_FR_Curation (review workflow),
  PRD_FR_Versioning (authority pinning)
- On external integrations: UBERON, FMA, CL, GO, ChEBI, HGNC, UniProt, Terminologia Anatomica

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Entities present against declared per-subsystem scope | G-01 | Phase 3: 90% of declared L0–L3 scope, reported as n/declared_n |
| Entities with a resolvable primary identifier | G-01 | 100% |
| Entities whose compilation status is exposed on every surface | G-03 | 100% |
| Minted-id proportion | G-01 | published per release; no target, tracked as drift |

## Out of Scope for This Module
- Relationships between entities (PRD_FR_Relationship_Graph)
- What is known about an entity (PRD_FR_Evidence)
- Geometry and location (PRD_FR_Spatial_Representation)
- Forking or authoring new external ontology terms (D-002)

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| Where does variation stop being a variant and become a separate entity? | Biology Lead | Phase 3 |
| What is the per-entity review cost to move `narrative` to `structured`, and does it scale to the 157 seed nodes? | Biology Lead | Phase 1 |
| Should minted ids be submitted upstream as term requests, and who owns that relationship? | Research Engineer | Phase 2 |
