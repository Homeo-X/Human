---
doc: PRD_Executive_Summary
tier: standard+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Executive Summary & Product Foundation

## Product Vision
A continuously extensible, evidence-grounded, multiscale computational
representation of the human organism that can be explored spatially, queried
semantically, reasoned about mechanistically, simulated selectively, and
eventually personalized through individual data without corrupting the canonical
reference model.

The 3D model is not the product. It is one projection of a structured biological
substrate, and the substrate is what makes the projection trustworthy.

## Problem Statement
Anatomical software today separates the two things a learner or researcher needs
to hold together. Atlases show structure with little mechanism and no traceable
sourcing; physiology texts describe mechanism with no spatial anchor; ontologies
(UBERON, FMA, CL, GO) hold rigorous structured biology with no spatial or dynamic
surface at all. Nothing connects a rendered structure to a graded claim about
what it does, to the mechanism beneath it, to the evidence for that mechanism.

The cost is specific and observable. Learners acquire structure and function as
disconnected facts. Researchers needing a navigable spatial reference build
bespoke pipelines each time. And every existing 3D anatomy product renders
approximations at the same visual fidelity as measured anatomy, so a user cannot
tell which is which — a well-rendered guess is indistinguishable from a
well-rendered measurement.

Assumption, marked as such: we assert this gap from the structure of available
tools, not from user research. Validating it with medical educators is RSK-01's
trigger and a Phase 1 gate, not a settled fact.

## Target Users & Personas
| Persona | Description | Primary Goal | Frequency of Use |
|---|---|---|---|
| Medical student | pre-clinical or clinical, studying structure alongside function | move from a structure to its mechanism and back without leaving the spatial context | daily during a systems block |
| Educator | teaches anatomy or physiology, often offline in a classroom | show a process unfolding in its real spatial location, with sources they can defend | weekly, in sessions |
| Clinician | explains anatomy to patients or refreshes their own recall | reach a correct, appropriately simplified explanation quickly | occasional, task-driven |
| Biomedical researcher | needs a navigable, data-backed spatial and semantic reference | query across scales and export a slice with its provenance intact | project-driven bursts |
| Platform team | builds personalization, simulation, or XR on top of this core | consume a stable entity model and API that will not be rewritten under them | continuous, as integrators |

## Value Proposition
Three properties, none of which existing tools combine:

1. **Structure and mechanism are one navigable object.** Every rendered entity
   resolves to a graph node carrying function, mechanism, relationships, and
   evidence; every mechanism resolves back to where it happens.
2. **Every claim carries its grade.** A user can always see whether they are
   looking at a measurement, a model, an approximation, or an admission of
   ignorance — and `UNKNOWN` is a displayed answer, not a blank.
3. **The reference model cannot be corrupted by individual data.** Personalization
   is an overlay, enforced structurally (D-004), so the canonical model stays a
   fixed point that a personalized view can always be reduced to.

Against named alternatives: Complete Anatomy and Visible Body render better and
will continue to; neither exposes claim-level provenance nor a queryable
mechanism graph. UBERON and the Human Reference Atlas hold rigorous structured
biology; neither offers a spatial or dynamic surface. This project's contribution
is the binding between them, and the honesty machinery that binding requires.

## Goals & Success Metrics
_Every FR module's Success Metrics section traces back to a KPI id here. Baselines
are stated because a target without a baseline is unverifiable; where the baseline
is zero, that is because the artifact does not yet exist._

| KPI id | Business Goal | KPI | Baseline | Target | Measured By |
|---|---|---|---|---|---|
| G-01 | Anatomical coverage is real and countable | proportion of the declared per-subsystem entity scope present in the graph, per level | 0% (Phase 0: 1 vertical slice) | Phase 3: 90% of declared L0–L3 scope; the denominator is published with the number | `biocheck --coverage` against the declared scope in BIO_Scale_Contract |
| G-02 | Entities are connected, not merely listed | proportion of entities carrying at least one typed relationship of each mandatory class for their level | 0% | Phase 3: 95% | graph query in the validation harness |
| G-03 | Every claim is traceable, including ignorance | proportion of claims carrying a complete evidence record (class, source, species, context, date), plus the absolute count of claims graded UNKNOWN | 0% | 100% complete records; UNKNOWN count published, never minimized | `biocheck` evidence invariants (INV-07) |
| G-04 | Scales are genuinely linked | proportion of cross-scale edges whose skipped levels are justified, and proportion of L3 entities reachable from L0 by containment | 0% | 100% justified; 100% reachable | `biocheck` scale invariants (INV-05) |
| G-05 | The model stays internally consistent | proportion of validation runs passing all blocking invariants, and mean time from a violation being introduced to being detected | not measurable pre-Phase 0 | 100% of releases pass; detection at commit time | CI validation history |
| G-06 | Individual data never loses its provenance | proportion of overlay values carrying value, unit, method, time, source, and confidence | not applicable until Phase 7 | 100% — an incomplete record cannot enter an overlay | overlay schema validation (INV-09) |
| G-07 | Results are reproducible | proportion of published releases that rebuild byte-identically from a clean checkout at their pinned inputs | 0% | 100% | release rebuild job |

**Metric integrity note (BRB-05, red-team Q6):** G-01 and G-02 are gameable by
shrinking the denominator. The denominator for both is the *declared* scope in
BIO_Scale_Contract, which is set at scoping and can only be narrowed through a
Scope Reopen with a Decision entry. Coverage is always published as
`n / declared_n`, never as a bare percentage. G-03's UNKNOWN count is reported
alongside the completeness percentage precisely so that completeness cannot be
raised by deleting the things we do not know.

## Non-Goals
- Diagnosis, treatment recommendation, or any clinical decision support.
- A real-time whole-body physiological simulation. Selected processes are
  modelled; the body is not simulated (Goal C is bounded in BIO_Research_Charter).
- Patient-specific imaging import and automatic mesh deformation in this version.
  The architecture must not block it, and it is specified in
  BIO_Personalization_Model so that it does not.
- Pediatric, geriatric, sex-specific, or pathology-specific base models. These
  derive from the same framework later; the reference is one declared population.
- Multiplayer or collaborative editing of the reference model.
- Competing on visual fidelity. Where realism and honesty conflict, honesty wins,
  and the simplification is declared.

## Key Stakeholders
| Name / Role | Responsibility | Sign-off Required? |
|---|---|---|
| Biology Lead (PM role) | biological scope, ontology shape, process specifications | yes — every phase gate |
| Research Engineer (Architect role) | substrate, evidence pipeline, validation harness | yes — Phase 0 and Phase 6 gates |
| Model Reviewer (UX role) | rubric pass, legibility of uncertainty | yes — every rubric pass |
| External domain reviewers (anatomy, physiology, cell biology) | correctness of represented biology at their level | yes — content release gates, per BIO_Validation_Framework |
| Licence and attribution owner | source licence compliance across asset tiers | yes — any release including geometry |
