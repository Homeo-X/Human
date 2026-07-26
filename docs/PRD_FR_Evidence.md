---
doc: PRD_FR_Evidence
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Evidence

## Purpose & Scope
Claims, their grading, their sources, and everything that follows from taking
provenance seriously: conflict representation, species marking, licence tiering,
and the storage and surfacing of what the model does not know. Boundary: entity
identity → PRD_FR_Ontology; the executable checks → PRD_FR_Validation; release
lineage → PRD_FR_Versioning.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Student | to see whether a statement is measured, modelled, or guessed | I learn the shape of the evidence, not just the fact |
| Educator | to reach the source behind any claim in one step | I can defend what I teach |
| Researcher | to see when sources disagree, and how | I can form my own view instead of inheriting a silent choice |
| Researcher | to ask what is not known about a structure | I can find the open questions rather than infer them from absence |
| Curator | to be prevented from grading a textbook restatement as a verified measurement | the ladder keeps meaning something |
| Licence owner | to know which assets carry share-alike obligations | a downstream build stays possible |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-EVID-001 | Must | Every claim carries a complete claim record per BIO_Evidence_and_Provenance §The Claim Record | Given a claim missing its population field, when submitted, then INV-07 fails naming the field; and given a complete record, when submitted, then it is admitted | The record is long; the display must lead with class and source and let the rest unfold |
| FR-EVID-002 | Must | Every claim carries an evidence class EVC-1…EVC-8, and the class is displayed wherever the claim is | Given any claim rendered in any surface, when displayed, then its class is visible without interaction; and given an API response containing a claim, when returned, then the class is in the payload | This is BRB-02; a bare number is the failure mode |
| FR-EVID-003 | Must | A claim's class changes only when its evidence changes; reformatting, re-hosting, re-citing, or aggregating changes nothing | Given an EVC-5 claim re-ingested with additional citations of the same inference, when processed, then the class is unchanged; and given a new independent qualifying measurement, when reviewed and accepted, then the class advances and records the evidence and reviewer | Show the promotion history — it is the record of what actually changed |
| FR-EVID-004 | Must | No agent may assign EVC-1 or EVC-2; those classes require a human reviewer | Given an agent-proposed EVC-1 claim, when submitted, then it is held for review at its proposed class and not admitted; and given a human reviewer accepting it, when recorded, then it is admitted with the reviewer named | The two heaviest classes are exactly the ones a confident model over-assigns |
| FR-EVID-013 | Must | UNKNOWN claims are counted in two classes: those recorded in response to a query or review, and those asserted unprompted | Given a coverage report, when produced, then asked-for and unprompted UNKNOWN counts appear separately; and given a rising unprompted count with a flat asked-for count, then it is visible as padding rather than as diligence | CH-10: the count detects deletion but rewards inflation unless the two are separated |
| FR-EVID-005 | Must | UNKNOWN (EVC-8) is stored as an asserted claim, is queryable, and is counted | Given an entity with a recorded UNKNOWN claim, when its claims are requested, then the UNKNOWN appears in the result; and given a coverage report, when produced, then the absolute UNKNOWN count appears alongside the completeness figure | An empty field is not UNKNOWN; the distinction must be visible |
| FR-EVID-006 | Must | Conflicting claims are both retained, linked, and displayed with their sources; the system never silently selects one | Given two credible claims with incompatible values, when the entity is displayed, then both appear with their conditions and sources; and given an attempt to store a claim that overwrites a conflicting one, when submitted, then it is stored as a conflict rather than an overwrite | If the conditions explain the difference, show the explanation instead of a range — a range implies uncertainty that may not exist |
| FR-EVID-007 | Must | Every claim carries a species field; a non-human-derived claim presented in a human model carries a transfer justification | Given a rodent-derived claim with no transfer justification, when validated, then INV-12 fails; and given one with a recorded justification, when displayed, then the species and justification are shown | Species must be visible on the claim, not one level away |
| FR-EVID-008 | Must | Every quantitative claim carries a UCUM unit and, where applicable, its measurement conditions | Given a value with no unit, when submitted, then INV-04 rejects it; and given a value with unit and conditions, when displayed, then the conditions appear with the value | 70 mL and 70 % are different claims; the model must never be unable to tell |
| FR-EVID-009 | Must | Every source carries a licence and a tier; T1 and T2 content never appears in the T0 ontology or evidence layers | Given a share-alike mesh path embedded in an entity record, when validated, then INV-11 fails; and given the same mesh referenced from a T1 asset package by id, when validated, then it passes | The tier matters to builders, not readers — surface it in export and release, not in the study view |
| FR-EVID-010 | Must | Any claim can produce its full provenance record on request, without human interpretation | Given any claim id, when its provenance is requested, then class, sources with resolvable identifiers, species, population, conditions, date, limitations, conflicts, and review history are returned; and given a claim that cannot produce this, when validated, then it is not admitted | One click from any displayed claim, always in the same place |
| FR-EVID-011 | Should | A claim's evidence class constrains how downstream surfaces may present it | Given an EVC-6 claim, when a retrieval response uses it, then the response marks it hypothetical; and given an EVC-8 claim, when a summary is generated, then the summary states the gap rather than omitting the topic | The constraint must be enforced in the pipeline, not left to prompt wording |
| FR-EVID-012 | Should | Source licences are re-verified at ingest and at every release | Given a source whose licence cannot be verified at ingest, when processed, then it does not enter; and given a release, when produced, then every source's licence verification date appears in the manifest | Licence drift is silent until it is expensive |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Claim | RW | the core record |
| Source | RW | the source register |
| EvidenceClass | R | the EVC ladder |
| LicenceTier | R | T0/T1/T2 |
| Entity | R | claim subjects |
| Relationship | R | claims about edges |
| Review | RW | reviewer decisions on class assignment |
| CurationTask | W | conflict adjudication and grading tasks |

## States & Transitions
Claim lifecycle: `proposed` → `under_review` → `admitted` → (`conflicted` |
`superseded` | `retired`). A claim never transitions to `admitted` at EVC-1 or
EVC-2 without a reviewer. `conflicted` is a stable state, not an error: it can
persist indefinitely and is resolved only by adjudication, which produces a new
claim rather than deleting the originals.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: an entity with no claims | returns empty with the distinction between "nothing recorded" and "nothing known" made explicit | FR-EVID-005 |
| Invalid input: a claim citing a source with no resolvable identifier | rejected at ingest | FR-EVID-001 |
| Permission denied: an agent attempts an EVC-1 assignment | held at proposed class, queued for review, and logged | FR-EVID-004 |
| Concurrency: two reviewers grade the same claim differently | second is rejected with the current grade; both opinions preserved and escalated to adjudication | FR-EVID-003 |
| External dependency failure: a DOI resolver is unavailable during verification | the claim is held pending, not admitted with an unverified source | FR-EVID-010 |
| Scale extreme: an entity accumulates hundreds of conflicting claims | conflicts are grouped by the quantity in dispute; the display never becomes an undifferentiated list | FR-EVID-006 |
| A source is retracted after claims were admitted from it | all dependent claims are flagged, their class frozen, and a review task raised; claims are not auto-deleted | FR-EVID-012 |
| Sources disagree only because they describe different populations | not a conflict — surfaced as two population-scoped claims, which the mandatory population field makes visible | FR-EVID-006 |

## Dependencies
- On other modules: PRD_FR_Ontology (subjects), PRD_FR_Validation (INV-04, INV-07,
  INV-11, INV-12), PRD_FR_Curation (review workflow), PRD_FR_Versioning (release
  manifests), PRD_FR_Knowledge_Retrieval (class-constrained presentation)
- On external integrations: DOI and identifier resolvers, ontology authorities,
  publisher licence terms

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Claims with a complete evidence record | G-03 | 100% |
| Claims graded UNKNOWN (absolute count) | G-03 | published every release; never minimized |
| Claims whose class was agent-assigned at EVC-1 or EVC-2 | G-05 | 0, enforced |
| Sources with verified licence and tier | G-07 | 100% |

## Out of Scope for This Module
- Deciding what is biologically true — the module records grading, it does not
  adjudicate science
- Automated claim extraction quality (PRD_FR_Knowledge_Retrieval, PRD_FR_Agent_Definition)
- Rendering of evidence panels (TECH_UI_UX_Design)

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| What is the admissible transfer justification for animal-derived mechanism data? | Biology Lead | Phase 5 |
| Does independence for EVC-2 require independent data, or independent analysis of shared data? | Biology Lead | Phase 2 |
| How long may a claim remain `conflicted` before adjudication is forced, if ever? | Biology Lead | Phase 2 |
