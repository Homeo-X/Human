---
doc: MANIFEST
tier: light+
version: 1.0.0
status: draft
owner: orchestrator
last_updated: 2026-07-26
---

# MANIFEST — Project Human Organism

_Authoritative record of what this spec is and contains. Where this file and any
copy elsewhere (e.g. the FR Overview's cross-cutting table) disagree, THIS file
wins; cross-review re-syncs the copies from here._

## Product
- **Brief digest:** A computational, semantically structured, evidence-grounded
  model of the human organism spanning L0–L10 (whole body to biochemical
  process), architected as a knowledge substrate with 3D and simulation as
  projections of it. Begins as an immutable generic reference model and is built
  so individual data can later be applied as an overlay without mutating that
  reference. Scientific honesty — what the model does not know — is a
  first-class, machine-checked property rather than a disclaimer.
- **Profile:** bio (per AGENTS.md §2, PROFILES.md) — new profile, built to the
  PROFILES.md profile contract; product profile is the base document set, bio
  extends it. See `templates/bio/README.md` for why research was rejected.
- **Scale depth (bio profile):** declared per subsystem below — lens extra-depth
  docs: BIO_Anatomical_Ontology, BIO_Scale_Contract, BIO_Cell_and_Molecular_Model,
  BIO_Evidence_and_Provenance, BIO_Validation_Framework, BIO_Personalization_Model

  | Subsystem | Max Level (Phase 0–3) | Mode at Max |
  |---|---|---|
  | Cardiovascular | L10 (vertical slice only) | exemplar |
  | Respiratory | L5 | typed |
  | Nervous | L5 | typed |
  | Urinary | L5 | typed |
  | Musculoskeletal | L4 | enumerated |
  | Digestive, Endocrine, Immune, Lymphatic, Integumentary, Reproductive | L3 | enumerated |

  Exactly one subsystem is taken to L10, as a vertical slice, to prove the
  substrate carries real biology across every level. Breadth at depth is a later
  phase, and the contract says so rather than implying it.
- **Tier:** Full — multi-team scope, external data provenance with licence
  obligations, health-adjacent personal data in a later phase, an agentic
  subsystem, 15 modules, and scientific claims that require explicit sign-off.
- **Scope state:** locked (D-001) — per AGENTS.md §9
- **Generated:** 2026-07-26 · **Last cross-review:** 2026-07-26

## FR Modules & Area Registry
| Module | File | AREA | Source | Rationale |
|---|---|---|---|---|
| Ontology | PRD_FR_Ontology.md | ONTO | _MODULE_TEMPLATE | canonical entities, identity, classification, xrefs |
| Relationship Graph | PRD_FR_Relationship_Graph.md | REL | _MODULE_TEMPLATE | typed relations, inverses, admissibility |
| Evidence | PRD_FR_Evidence.md | EVID | _MODULE_TEMPLATE | claims, grading, provenance, conflict, licensing |
| Scale Bridging | PRD_FR_Scale_Bridging.md | SCAL | _MODULE_TEMPLATE | L0–L10 contracts and cross-scale linkage |
| Spatial Representation | PRD_FR_Spatial_Representation.md | SPAT | _MODULE_TEMPLATE | geometry, coordinate frames, entity-to-mesh binding |
| Navigation | PRD_FR_Navigation.md | NAV | _MODULE_TEMPLATE | semantic vs physical zoom, layers, isolation |
| Search | PRD_FR_Search.md | SRCH | _MODULE_TEMPLATE | name, function, clinical and spatial query |
| Process Models | PRD_FR_Process_Models.md | PHYS | _MODULE_TEMPLATE | physiological process definitions |
| Simulation | PRD_FR_Simulation.md | SIM | _MODULE_TEMPLATE | timescale-aware execution, capability limits |
| Personalization | PRD_FR_Personalization.md | PERS | _MODULE_TEMPLATE | overlay algebra, measurement provenance |
| Validation | PRD_FR_Validation.md | VALD | _MODULE_TEMPLATE | executable integrity invariants |
| Knowledge Retrieval | PRD_FR_Knowledge_Retrieval.md | RETR | _MODULE_TEMPLATE | evidence-bound retrieval and explanation |
| Agent Definition | PRD_FR_Agent_Definition.md | AGD | modules/ai/ | the 12 agents, 12 facets, runtime contract |
| Curation | PRD_FR_Curation.md | CUR | _MODULE_TEMPLATE | expert review workflow, ingestion approval, admin |
| Versioning | PRD_FR_Versioning.md | VER | _MODULE_TEMPLATE | knowledge-base releases, migration, reproducibility |

**Naming correction at scoping:** the brief's `FR-3D-NNN` is inadmissible —
AGENTS.md §6 fixes AREA at 2–5 uppercase *letters*, and `tools/validate.sh`'s
AREA-uniqueness scan would not see it. Renamed `FR-SPAT-NNN`. The brief's
`FR-CELL` is absorbed by SCAL (levels L6–L8 are scale contracts, not a separate
capability) and `FR-AI` by RETR and AGD. Recorded in D-001.

## Cross-Cutting Concern Decisions
_One row per checklist item in AGENTS.md §5, plus the bio profile's additions._

| Concern | Decision | Reason |
|---|---|---|
| Search & findability | own module (SRCH) | four distinct query modalities over a graph; not a text box |
| Permissions / roles / sharing | folded into PRD_FR_Curation §Permissions and PRD_Security_Requirements | only curators and administrators have write access; readers are unauthenticated on the reference model |
| Analytics & telemetry | folded into PRD_Non_Functional_Requirements §Observability and the Executive Summary KPIs | instrumentation serves the seven KPIs; there is no product-analytics surface |
| Notifications | excluded | the reference model has no asynchronous actor to notify; curation hand-offs are in-session and queue-based, specified in CUR |
| Internationalization | folded into PRD_Non_Functional_Requirements and PRD_FR_Ontology §Naming | anatomical terminology is nomenclature-anchored, so term localization is an ontology property, not a string-table property |
| Accessibility | PRD_Non_Functional_Requirements rows and TECH_UI_UX_Design §Accessibility | a spatial 3D UI is the hard case; it needs design treatment, not just a WCAG row |
| Audit & compliance logging | folded into PRD_FR_Versioning and PRD_FR_Evidence | knowledge lineage is the audit trail here; a separate log would duplicate provenance |
| Import / export & portability | folded into PRD_FR_Versioning §Export | the knowledge base is the export; releases are versioned addressable artifacts |
| Offline / degraded connectivity | PRD_Non_Functional_Requirements rows | classroom use offline is a stated requirement of the brief |
| AI behavior, evals & cost | PRD_FR_Knowledge_Retrieval and PRD_FR_Agent_Definition, EV rows in both | every generated claim must resolve to a graph node; this is where the model can hallucinate biology |
| Admin / operator tooling | own module (CUR) | curation is an expert workflow with review gates, not CRUD |
| Onboarding & empty states | folded into TECH_UI_UX_Design §Key Screens | the honest empty state, "we do not model this", is a core surface here — designed, not defaulted |
| Units & quantities | PRD_FR_Validation invariants and PRD_FR_Evidence | UCUM; every quantitative value carries a unit or is rejected |
| Species provenance | PRD_FR_Evidence §Claim Record and BIO_Cell_and_Molecular_Model | a human model holding unlabelled animal data is wrong, not approximate |
| Source licensing tier | PRD_FR_Evidence §Licensing and PRD_External_Integrations | share-alike geometry segregated so relicensing stays possible (D-003) |
| Uncertainty representation | BIO_Personalization_Model and TECH_UI_UX_Design | uncertainty must be legible, not merely stored |
| Declared scale depth | this file §Product and BIO_Scale_Contract | binding, per the scale-depth lens |
| Conflicting-evidence posture | PRD_FR_Evidence §Conflict | both claims shown with their sources; the system never silently picks |
| Non-diagnostic boundary | BIO_Research_Charter and every personalized surface | standing statement, with enumerated placements |
| Population & variation | BIO_Research_Charter §Reference Subject and BIO_Anatomical_Ontology §Variation | the reference is a stated population, never "a human" |
| Negative knowledge | PRD_FR_Evidence (EVC-8) and PRD_FR_Search | UNKNOWN is stored, queryable, and counted in G-03 |

## Fold Record
_Full tier: no core file omitted. The rows below record content deliberately
placed in a host document rather than given its own file._

| Folded Content | Landed In |
|---|---|
| Permissions model | PRD_FR_Curation §Permissions and Review Roles |
| Telemetry and instrumentation | PRD_Non_Functional_Requirements §Observability |
| Terminology localization | PRD_FR_Ontology §Naming and Terminology |
| Audit trail | PRD_FR_Versioning §Provenance of Releases |
| Export and portability | PRD_FR_Versioning §Export |
| Onboarding and empty states | TECH_UI_UX_Design §Key Screens |

## File Inventory
| File | Owner | Version | Status |
|---|---|---|---|
| MANIFEST.md | orchestrator | 1.0.0 | draft |
| PRD_Decision_Log.md | orchestrator | 1.0.0 | draft |
| PRD_Executive_Summary.md | pm | 1.0.0 | draft |
| PRD_Scope_and_Roadmap.md | pm | 1.0.0 | draft |
| PRD_Business_Rules.md | pm | 1.0.0 | draft |
| PRD_FR_Overview.md | pm | 1.0.0 | draft |
| PRD_Risks_and_Constraints.md | pm | 1.0.0 | draft |
| PRD_Acceptance_Criteria_and_DoD.md | pm | 1.0.0 | draft |
| PRD_Glossary_and_References.md | pm | 1.0.0 | draft |
| PRD_Information_Architecture.md | ux | 1.0.0 | draft |
| PRD_User_Flows_and_Use_Cases.md | ux | 1.0.0 | draft |
| PRD_Data_Overview.md | architect | 1.0.0 | draft |
| PRD_External_Integrations.md | architect | 1.0.0 | draft |
| PRD_Non_Functional_Requirements.md | architect | 1.0.0 | draft |
| PRD_Security_Requirements.md | architect | 1.0.0 | draft |
| TECH_System_Architecture.md | architect | 1.0.0 | draft |
| TECH_Data_Design.md | architect | 1.0.0 | draft |
| TECH_API_Specification.md | architect | 1.0.0 | draft |
| TECH_UI_UX_Design.md | ux | 1.0.0 | draft |
| BIO_Research_Charter.md | pm | 1.0.0 | draft |
| BIO_Scale_Contract.md | pm | 1.0.0 | draft |
| BIO_Anatomical_Ontology.md | pm | 1.0.0 | draft |
| BIO_Physiological_Processes.md | pm | 1.0.0 | draft |
| BIO_Cell_and_Molecular_Model.md | pm | 1.0.0 | draft |
| BIO_Evidence_and_Provenance.md | architect | 1.0.0 | draft |
| BIO_Validation_Framework.md | architect | 1.0.0 | draft |
| BIO_Personalization_Model.md | pm | 1.0.0 | draft |
| BIO_Model_Review.md | ux | 1.0.0 | draft |
| PRD_FR_Ontology.md | pm | 1.0.0 | draft |
| PRD_FR_Relationship_Graph.md | pm | 1.0.0 | draft |
| PRD_FR_Evidence.md | pm | 1.0.0 | draft |
| PRD_FR_Scale_Bridging.md | pm | 1.0.0 | draft |
| PRD_FR_Spatial_Representation.md | pm | 1.0.0 | draft |
| PRD_FR_Navigation.md | pm | 1.0.0 | draft |
| PRD_FR_Search.md | pm | 1.0.0 | draft |
| PRD_FR_Process_Models.md | pm | 1.0.0 | draft |
| PRD_FR_Simulation.md | pm | 1.0.0 | draft |
| PRD_FR_Personalization.md | pm | 1.0.0 | draft |
| PRD_FR_Validation.md | pm | 1.0.0 | draft |
| PRD_FR_Knowledge_Retrieval.md | pm | 1.0.0 | draft |
| PRD_FR_Agent_Definition.md | pm | 1.0.0 | draft |
| PRD_FR_Curation.md | pm | 1.0.0 | draft |
| PRD_FR_Versioning.md | pm | 1.0.0 | draft |
| CHALLENGE_REGISTER.md | redteam | 1.0.0 | draft |

## Tooling (generation provenance — see INTEGRATIONS.md)
| Tool | Detected | Used For |
|---|---|---|
| codebase-memory-mcp | no | greenfield: the repository was empty at intake |
| graphify | no | not installed; the source corpus was parsed and ingested directly |
| rtk | no | none |
| ponytail | handoff-only | recommended for the Phase 1 implementation handoff |

**Source corpus (AGENTS.md §8 grounding).** This run received a document corpus,
"A Map of the Human Body" — 157 tree nodes across 20 branches, each with a
definition and a textbook reading list, plus 31 prose cross-links and a node
typology including `frontier` (unsettled science). It was parsed and ingested
under D-007 at `narrative` compilation status:

| Ingested | Count |
|---|---|
| Entities (Function class, narrative) | 140 |
| Definition claims (EVC-2, or EVC-6 for `frontier` nodes) | 140 |
| Untyped associations (`associated_with`, prose retained) | 26 |
| Nodes skipped — branch outside declared scope | 16 |
| Associations dropped — endpoint out of scope | 5 |

Seed-derived content carries `provenance_source` naming the corpus and its ingest
date. Nothing from it is typed, mechanistic, or parameterized; its narrative
status is visible on every surface per FR-ONTO-006. `ontology/seed/MANIFEST.json`
records the ingest.

The framework itself is vendored at the repository root; see `UPSTREAM.md` for
the vendored baseline and every delta applied, including the new `bio` profile.

## Phase 0 Delivery State
| Artifact | State |
|---|---|
| Specification set | 44 files in `docs/`, all `status: draft`, validating clean |
| Decisions | D-001 … D-010, append-only, integrity-hashed |
| Rubric pass | 30 BRB items dispositioned; 3 flags raised, 2 applied, 1 carried to UX pass B by design |
| Red team | 13 challenges; 8 accepted, 4 acknowledged, 1 refuted with evidence; 2 S1 escalated verbatim |
| Schemas | 7 JSON Schemas in `schemas/` |
| Substrate | 374 records: cardiovascular vertical slice L0→L10 (15 entities, 9 claims, 19 relations, 1 process, 3 spatial identities) + 306 seed records |
| Invariants | INV-01 … INV-15; 14 executable, all fail when violated; INV-14 is runtime-enforced |
| Coverage | published per subsystem per level; only cardiovascular has depth, and the matrix says so |

## Assumptions Made at Scoping
- The reference subject is a healthy adult; its population parameters are
  declared in BIO_Research_Charter, not assumed to be "average".
- External anatomical ontologies (UBERON, FMA, CL, GO, ChEBI, HGNC) remain
  available and citable; the project references their terms rather than forking
  them (D-002).
- No individual human data of any kind is handled in Phases 0 through 6. Phase 7
  is where the privacy posture becomes load-bearing, and it is specified now so
  the architecture does not have to change then.
- Expert biological review capacity exists at the gates named in
  BIO_Validation_Framework. Automated checks establish consistency; they never
  establish correctness, and this spec does not pretend otherwise.
- The product is not a medical device and will not be submitted for regulatory
  clearance. If that changes, the tier and the security document change with it.
