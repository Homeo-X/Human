---
doc: PRD_Glossary_and_References
tier: standard+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Glossary, References & Document Appendix

## Glossary
_Terms this spec uses with a specific meaning, especially those the project
redefines. One canonical term per concept._

| Term | Definition | Do Not Confuse With |
|---|---|---|
| Reference model | the canonical, immutable representation of one declared population | "the human body"; it is a stated position about one population, not a universal |
| Overlay | individual data applied over the reference at read time, never merged into it | a personalized copy or fork of the model |
| Individual model | reference ⊕ overlay, resolved at read time | a digital twin, which implies predictive fidelity this does not have |
| Entity | a biological thing with identity, class, and level | a mesh, a node in the navigation tree, or a database row |
| Spatial identity | the record of where an entity is, independent of any geometry | the geometry itself; a spatial identity exists with no mesh |
| Claim | a graded, sourced assertion about an entity or relation | a fact; a claim carries its evidence class and can be UNKNOWN |
| Evidence class (EVC) | the grade constraining what may be said with a claim | confidence, which is a subjective feeling; EVC is a data field with rules |
| Compilation status | how far a piece of content has moved from prose to model | evidence class; a `mechanistic` entity can rest on weak evidence |
| Representation status | how far a process has moved from named to executable | compilation status, which applies to entities and relations |
| Representation mode | how a level represents its content — enumerated, typed, statistical, exemplar, referenced, absent | level of detail, which is a rendering concern |
| Declared depth | the maximum level a subsystem is modelled to, binding at scoping | the deepest content that happens to exist |
| Resolution limit | the honest statement of what a level cannot represent | precision, which is about digits rather than about scope |
| Semantic zoom | changing the level of biological abstraction | physical zoom, which changes magnification and changes no claim |
| Navigation tree | a derived spanning view over the graph, for orientation | the model's structure; the graph is the model (D-006) |
| Association (`associated_with`) | an observed relationship whose type is not yet established | a mechanism or a cause; rendering one as the other is BRB-30 |
| Spanning process | a process acting at several levels simultaneously | a process that skips levels, which requires justification |
| Timescale domain | the temporal band a process operates in and composes within | a simulation timestep; there is no global clock (D-005) |
| Vertical slice | one subsystem taken to full depth to prove the substrate | coverage; a slice is explicitly not breadth |
| Licence tier | T0 core, T1 share-alike, T2 reference-only | copyright status; tiering is about downstream obligation |
| Minted identifier | a local id created where no external term exists, flagged as minted | an external ontology term; the minted count is a drift signal |
| Terminal answer | the designed response when a user reaches declared depth | an empty state or an error |
| Negative knowledge | recorded UNKNOWN claims and enumerated unrepresented content | missing data, which is an absence nobody asserted |
| Curator | a person with write authority within a competence scope | an agent, which may only propose |
| Frontier node | seed-corpus content marking a genuinely open scientific question | content the project has not got to yet |
| G-NN | a KPI id in the Executive Summary that module metrics trace to | a target; the id is the trace anchor |
| INV-NN | an integrity invariant with an executable check | a guideline; an invariant without a check is a finding |
| BRB-NN | a rubric item — a known failure mode of biological modelling | a requirement; the rubric checks for failure, it does not specify behaviour |
| SCL-NN | a scale-level contract row | a level number; the contract is what the level promises and refuses |
| BPR-NN | a biological process specification | a process that runs; most are `narrative` |
| EVC-N | an evidence class definition | an individual claim's grade, which references one |
| PRD | Product Requirements Document | |
| DoD | Definition of Done | |

## Reference Documents
| Document | Location | Relevance |
|---|---|---|
| AGENTS.md | repository root | the framework standard this spec is written under |
| PROFILES.md | repository root | profile inventory and the contract the bio profile satisfies |
| templates/bio/README.md | repository | the bio profile specification, including the scale-depth lens |
| RED_TEAM.md | repository root | adversarial review protocol governing the challenge register |
| MEMORY.md | repository root | the spec-as-memory model and the sufficiency probe |
| UPSTREAM.md | repository root | vendored framework baseline and every applied delta |
| A Map of the Human Body | seed corpus, ingested per D-007 | 157 nodes, 31 cross-links, per-node reading lists; the narrative seed |
| Terminologia Anatomica | external, cited | anatomical nomenclature authority |
| UBERON, FMA, CL, GO, ChEBI, HGNC, UniProt | external, pinned per release | identity authorities per level (D-002) |
| UCUM | external | the unit vocabulary INV-04 enforces |

## Document Set Appendix
Inventory and per-file versions live in `MANIFEST.md`; decision history lives in
`PRD_Decision_Log.md`. This file carries no change log — the Decision Log and git
history are the audit trail (AGENTS.md §7).
