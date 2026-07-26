# Bio Profile — Biological Model Document Set

Specification of the **bio** profile (PROFILES.md). For systems whose primary
deliverable is a **structured, evidence-graded model of a biological system** —
one that is explored spatially, queried semantically, reasoned about
mechanistically, and only selectively simulated. Everything not stated here
follows the framework unchanged: tiers, workflow, IDs, versioning, scope
lifecycle, spec graph, execution modes.

## Why this is a profile and not a module library

The product profile assumes the thing being specified is software, and that what
the software knows is content. Here the inversion is the point: the knowledge
substrate is the product, and the software is a set of projections of it. Three
structural needs have no home in the product set —

1. **Representation honesty per scale.** A biological model spans levels whose
   representability differs by orders of magnitude. Which level is represented
   *how*, and where representation stops, is a first-class, machine-checked
   contract (`SCL`), not a paragraph in an architecture doc.
2. **Evidence as a data field, not a citation style.** Every assertion carries a
   grade (`EVC`) and a provenance chain, and the grade constrains what the system
   is allowed to say. This is a schema obligation, not a documentation habit.
3. **Reference/individual separation.** The canonical model must remain immutable
   under personalization. That is an invariant (`INV`) with an executable check,
   not an architectural preference.

The **research** profile was considered and rejected for this class of work: its
`HYP → CM → EXP → DC` chain presumes the project *generates* knowledge through
experiments it designs. A bio-model project *curates and grades* knowledge others
generated, and additionally ships a product surface (viewers, APIs, search) the
research set has no place for. Where a bio project does run experiments, it
scopes a research-profile study alongside — the profiles compose, they do not
merge.

## Role mapping
| Framework Role | Acts As | Owns (bio profile) |
|---|---|---|
| Orchestrator | Program Lead | scoping, scale-depth declaration, MANIFEST, cross-review — otherwise unchanged |
| PM | Biology Lead | BIO_Research_Charter, BIO_Anatomical_Ontology, BIO_Scale_Contract, BIO_Physiological_Processes, BIO_Cell_and_Molecular_Model, BIO_Personalization_Model, FR modules, Risks, Acceptance & DoD |
| UX | Model Reviewer | BIO_RUBRIC pass A → `docs/BIO_Model_Review.md`; Information Architecture and User Flows for cross-scale navigation; the UX review of PM's FR files; owns the legibility of uncertainty in every surface |
| Architect | Research Engineer | BIO_Evidence_and_Provenance, BIO_Validation_Framework, Data Overview, External Integrations (ontology and geometry sources incl. licences), NFRs, Security, TECH files |

The **Model Reviewer** is not a graphic-design role. Its subject is whether a
reader can tell, at a glance, what the model knows from what it is guessing —
which is a user-experience property before it is a scientific one.

## Document set per tier
| Tier | Set |
|---|---|
| **Light** (a single system or a feasibility slice) | `bio/light/BIO_Model_Brief.md` + `core/PRD_Decision_Log` + `core/PRD_Acceptance_Criteria_and_DoD` + `light/TECH_Implementation_Notes` |
| **Standard** (one organism system, or a multi-system model at declared shallow depth) | BIO core: Research_Charter, Anatomical_Ontology, Scale_Contract, Physiological_Processes, Evidence_and_Provenance, Validation_Framework (+ Cell_and_Molecular_Model per the scale-depth lens; + Personalization_Model if any individualization is in scope) + BIO_RUBRIC pass (→ BIO_Model_Review) + shared: Executive_Summary, Scope_and_Roadmap, FR_Overview, Data_Overview, Risks_and_Constraints, Non_Functional_Requirements, Acceptance_Criteria_and_DoD, Decision_Log + TECH: System_Architecture, Data_Design |
| **Full** (multi-system, personalization-bound, agentic, or externally published) | Standard + all 8 BIO core docs + the remaining `templates/core/` set + scoped FR modules |

## Bio-profile folds (Standard)
| File | Fold into (when omitted) |
|---|---|
| BIO_Cell_and_Molecular_Model | BIO_Anatomical_Ontology §Sub-Organ and Cellular Levels — only when the scale-depth lens declares max depth ≤ L5 for every system |
| BIO_Personalization_Model | excluded with reason when no individualization is in scope — an exclusion, not a fold |
| BIO_Evidence_and_Provenance | **never omitted at any tier.** A biological model without a provenance model is an assertion with a nice interface |
| BIO_Validation_Framework | **never omitted at Standard+.** Invariants that live only in prose are not invariants |
| BIO_Scale_Contract | **never omitted at any tier.** This is the document that stops the project overclaiming |

## The scale ladder
The profile fixes a canonical ladder so that cross-project comparison and
cross-scale linkage mean the same thing everywhere:

    L0  whole organism          L6   cell populations
    L1  anatomical regions      L7   individual cell types
    L2  organ systems           L8   subcellular structures
    L3  organs                  L9   molecular mechanisms
    L4  sub-organ structures    L10  biochemical / physical processes
    L5  tissues

A project may declare fewer levels. It may not redefine one.

## Scale-Depth Lens (binds at scoping, like the game profile's genre lens)
The orchestrator declares, at the scoping checkpoint and in MANIFEST §Product,
the **maximum represented level per subsystem** and the representation mode at
that level. This is binding, not advisory:

- Every declared level needs a filled `SCL` row before any entity may claim it.
- An entity asserting a level deeper than its subsystem's declaration is a
  cross-review finding (BRB-20), not a stretch goal.
- Claiming a depth without an evidence-backed mechanism at that depth is the
  profile's characteristic failure and the rubric hunts it specifically.

| Declared Depth | Extra-Depth Docs | Depth-Specific Prompts |
|---|---|---|
| ≤ L3 (organ-level) | Anatomical_Ontology, Scale_Contract | organ boundaries and naming authority; what "an organ" is when it is diffuse (e.g. immune, endocrine) |
| L4–L5 (sub-organ, tissue) | Anatomical_Ontology, Physiological_Processes | tissue-type taxonomy; where structure stops being discrete and becomes gradient |
| L6–L7 (cellular) | Cell_and_Molecular_Model, Evidence_and_Provenance | cell-type authority (which taxonomy, which version); population vs individual-cell representation; species provenance of the underlying data |
| L8–L9 (subcellular, molecular) | Cell_and_Molecular_Model, Validation_Framework | mechanism completeness vs mechanism sketch; how a pathway is bounded; what "the" mechanism means when it is cell-type-specific |
| L10 (biochemical / physical) | Physiological_Processes, Validation_Framework | rate constants and their conditions; in-vitro vs in-vivo transfer; whether the process is represented or merely named |
| any depth + personalization | Personalization_Model, Evidence_and_Provenance | overlay algebra; measurement provenance; what an individual value may and may not override |

## Checklist additions (AGENTS.md §5 applies in full, plus)
Each gets an explicit decision at scoping:

- **units & quantities** — every quantitative value carries a unit; the unit
  vocabulary is named (UCUM or stated alternative)
- **species provenance** — human vs animal-derived data, marked per claim; a
  model of a human that silently contains mouse data is wrong, not approximate
- **source licensing tier** — ontology terms and geometry assets tracked with
  licence and attribution; share-alike sources segregated so downstream
  relicensing stays possible
- **uncertainty representation** — how a value's spread, staleness, and
  measurement method are carried and displayed
- **declared scale depth** — the lens above, per subsystem
- **conflicting-evidence posture** — what the system shows when sources disagree
  (it must not silently pick one)
- **non-diagnostic boundary** — the standing statement that the model does not
  diagnose, treat, or advise, and where it appears in the product
- **population and variation posture** — whose body the reference model is, and
  how anatomical variation is represented rather than averaged away
- **negative knowledge** — where `UNKNOWN` is stored, surfaced, and counted

## Acceptance analog
Given/When/Then is retained for all `FR` rows. Assertions that are biological
rather than behavioural are gated differently: a biological claim is accepted
when it carries an `EVC` class, a provenance chain, and passes the `INV`
invariants — recorded in Acceptance_Criteria_and_DoD as evidence gates. Prose
that can be neither Given/When/Then'd nor evidence-graded is not admissible
content.

## Tree and graph
A profile-level rule, because it is the mistake this domain invites most often:
where a document set describes a hierarchy of biological entities, the hierarchy
is a **navigation view** and the typed relationship graph is the **model**. A
document that presents a tree as the structure of the biology, without saying
that multi-participation exists and is represented elsewhere, fails BRB-30. The
canonical illustration is any organ belonging to two systems.

## Compilation status
Narrative sources are not structured models, and the difference must survive
ingest. Profiles specifying a model built from prose sources carry a compilation
ladder — `narrative` → `structured` → `mechanistic` → `parameterized` — on every
entity and relation, visible wherever the content is. Promotion requires the
typing work to have been done and reviewed; reformatting promotes nothing. An
un-laddered ingest of narrative sources is BRB-29.

## The bio trace chain (specgraph-checked)
Every represented mechanism completes this chain or names the missing link as an
open question:

    SCL-nn (level contract)
        → entity (at that level, with EVC + provenance)
        → relationship (typed, admissible at that level)
        → BPR-nn (process consuming/producing those entities)
        → INV-nn (invariants the process must not violate)
        → FR-<AREA>-nnn (the requirement that realizes it)

Chain edges live in the tables' reference columns; `tools/specgraph.py` warns on
defined-but-unreferenced `BPR` and on `SCL` rows with an undeclared
representation mode, evidence model, or resolution limit — a level nothing uses,
or a level whose limits were never stated, is a broken chain.

## ID registers (additions)
`SCL-NN` scale-level contract (BIO_Scale_Contract) · `BPR-NN` biological process
model (BIO_Physiological_Processes) · `EVC-N` evidence class
(BIO_Evidence_and_Provenance) · `INV-NN` integrity invariant
(BIO_Validation_Framework) · `BRB-NN` rubric item (BIO_RUBRIC). Testable
requirements keep `FR-<AREA>-NNN` throughout, so DoD, specgraph, and
implementation tracing work unchanged.

## What the bio profile guarantees — and what it can't
**Guaranteed:** that every represented level declares its own limits; that no
claim outranks its evidence; that the reference model cannot be mutated by
individual data; that the ways this class of project overclaims are checked
explicitly rather than hoped against.

**Not guaranteed:** biological correctness itself. No document set makes a model
true. Domain experts and primary sources do that. The profile's honest claim is
that it makes an *unsupported* model visible — to its own authors first.
