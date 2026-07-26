---
doc: PRD_Scope_and_Roadmap
tier: standard+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Scope & Product Roadmap

## In Scope (Phase 0 — this delivery)
Phase 0 delivers the **substrate**, not the model. By FR module:

- **ONTO** — entity classes, identity scheme, external cross-reference strategy,
  minting rules, versioning semantics.
- **REL** — the typed relationship vocabulary with inverses, cardinality, and
  per-level admissibility.
- **EVID** — the claim record, the EVC ladder, conflict representation, source
  register, licence tiers.
- **SCAL** — the eleven SCL level contracts and the cross-scale linkage rules.
- **VALD** — the INV invariants, executable in `tools/biocheck.py`, with negative
  tests proving each can fail.
- **VER** — release semantics for the knowledge base.

Plus the seeded **cardiovascular vertical slice**: one complete L0→L10 path with
every node graded and sourced, and one process (`BPR-01`, excitation–contraction
coupling) specified to `structured` status.

Everything else in the fifteen modules is **specified in Phase 0 and built
later**. The specification existing is not the capability existing, and this
document is the place that distinction is kept.

## Out of Scope (for now)
| Item | Why Out | Trigger to Reconsider |
|---|---|---|
| 3D viewer and mesh pipeline | the substrate must be validated before geometry binds to it; building the viewer first is how a project optimizes for visual impressiveness over the biological substrate | Phase 0 exit gate passed |
| Executable simulation | a process specification is not a runnable model; parameters need sources and coupling rules need review | Phase 5 exit; parameter sources graded at EVC-2 or better |
| Any individual human data | no privacy posture is load-bearing until data exists; specified now so architecture need not change | Phase 6 exit and a completed privacy review |
| Breadth at depth (all systems below L5) | one system at L10 proves the substrate; eleven systems at L10 is a decade of curation | per-subsystem, when domain review capacity exists for that system |
| Pathology, development, aging | the reference is one declared state; variation across states multiplies every entity | after the reference model reaches Phase 3 coverage |
| Clinical decision support | out of scope permanently, not temporarily — see Non-Goals | never; a different product with different obligations |

## Roadmap

### Phase 0 — Foundation (this delivery)
- **Modules:** ONTO, REL, EVID, SCAL, VALD, VER (substrate); all others specified.
- **Exit criteria:** every INV has an executable check and a passing negative
  test; the vertical slice validates clean; `specgraph` and `validate.sh` pass on
  the full document set; the BIO rubric pass has no unresolved flags.

### Phase 1 — Anatomical skeleton
- **Entry gate (CH-01, D-010):** educator validation of the problem statement
  (RSK-01) must resolve **before build begins**. This is a gate, not a milestone:
  the prior arrangement scheduled the validation alongside the work it would
  invalidate.
- **Modules:** SPAT, NAV (first surfaces), ONTO and REL populated to L3.
- **Content:** body, regions, organ systems, major organs, major bones, major
  muscles, major vessels, major nerves, major glands.
- **Exit criteria:** G-01 at 90% of declared L0–L3 scope; every mesh bound to an
  entity id; no unbound geometry ships; asset licence tiers separable in a build;
  **the Coverage surface shows declared-versus-populated per subsystem per level**
  (FR-SCAL-010) — a declared depth with no content must be visible in the product
  from Phase 1, not only in a release metric (BIO_Model_Review PUNCH-01).

### Phase 2 — Semantic anatomy
- **Modules:** SRCH, RETR (retrieval bound to the graph), EVID at scale.
- **Content:** every visual structure resolves to entity, hierarchy, function,
  and evidence.
- **Exit criteria:** G-03 at 100% complete evidence records for all L0–L3
  entities; no user-facing surface displays a claim without its grade.

### Phase 3 — System interactions
- **Modules:** REL extended to functional and regulatory relations, SCAL to L5.
- **Content:** cross-system relationships — cardiovascular, respiratory, nervous,
  endocrine, renal, digestive, immune.
- **Exit criteria:** G-02 at 95%; G-04 at 100% justified cross-scale edges.
- **Conditional on review capacity (CH-04, D-010):** these targets assume review
  throughput sufficient to admit the content. BR-023 throttles generation to
  review capacity and **takes precedence over these targets**. If capacity binds,
  the targets move; the throttle does not. Stating this here rather than
  discovering it at the gate.

### Phase 4 — Cellular representation
- **Modules:** SCAL to L6–L7, CUR at full workflow.
- **Content:** major tissue types, major cell types, cellular functions,
  cell–cell interactions, tissue organization.
- **Exit criteria:** cell-type taxonomy authority pinned and versioned; species
  provenance populated on 100% of cellular claims.

### Phase 5 — Subcellular representation
- **Modules:** SCAL to L8–L9, PHYS extended.
- **Content:** organelles, membrane systems, receptors, ion channels, molecular
  machinery.
- **Exit criteria:** no L9 entity without an evidence-backed mechanism (BRB-09).

### Phase 6 — Process models
- **Modules:** SIM, PHYS to `executable` status for a named process set.
- **Exit criteria:** every executable process names its parameter sources; every
  cross-domain coupling is declared supported or explicitly unsupported; no
  simulation output is presented without its capability limits.

### Phase 7 — Personalization
- **Modules:** PERS, security and privacy controls active.
- **Exit criteria:** G-06 at 100%; INV-08 (reference immutability) passing under
  adversarial test; every personalized surface carries its non-diagnostic
  boundary.

## Release Milestones
| Milestone | Target | Owner | Depends On |
|---|---|---|---|
| Phase 0 substrate validated | this delivery | Research Engineer | none |
| Educator validation of the problem statement | **Phase 1 entry gate** — build blocked until resolved | Biology Lead | recruiting 5–8 educators (RSK-01) |
| L0–L3 content release | Phase 1 exit | Biology Lead | asset licensing resolved per D-003 |
| First external ontology sync | Phase 2 | Research Engineer | D-002 authorities pinned |
| Privacy review | before Phase 7 | Architect | Phase 6 complete |

## Dependencies & Assumptions
| Item | Type | Owner | Resolve By |
|---|---|---|---|
| UBERON, FMA, CL, GO, ChEBI, HGNC remain maintained and openly licensed | dependency | Research Engineer | Phase 1 |
| Open anatomical geometry available under licences compatible with D-003's tiering | dependency | Licence owner | Phase 1 |
| Domain reviewer capacity per subsystem at the declared depth | dependency | Biology Lead | per phase gate |
| The stated user problem is real for medical educators | assumption | Biology Lead | before Phase 1 build (RSK-01) |
| Browser WebGL2 performance suffices for L0–L3 scenes on mid-range hardware | assumption | Architect | Phase 1 prototype |
| Expert review can keep pace with curation throughput | assumption | Biology Lead | Phase 2 (RSK-06) |
