# PROFILES.md — Document Profiles

A **profile** is a document set for a class of thing-being-specified whose
structure — not just vocabulary — differs from the product PRD. Domain
flavor within a structure is a module library, never a profile.

## Shipped profiles
| Profile | Spec | For | Explicit flag |
|---|---|---|---|
| product (default) | AGENTS.md §2 | software products & features | — |
| game | templates/gdd/README.md | games (GDD set) | `prd-new game …` |
| research | templates/research/README.md | studies, experiments, simulation campaigns | `prd-new research …` |
| devtool | templates/devtool/README.md | libraries, SDKs, CLIs, APIs-as-product | `prd-new devtool …` |
| bio | templates/bio/README.md | evidence-graded models of biological systems | `prd-new bio …` |

The orchestrator infers the profile from the brief and confirms it at the
scoping checkpoint; explicit flags skip inference. MANIFEST records it.

## The profile contract
A new profile MUST ship all of the following, or it isn't a profile:
1. **README spec** under `templates/<profile>/`: role mapping onto the four
   framework roles, document set per tier, fold rules, checklist additions
   (AGENTS.md §5 always applies in full), and any new ID registers.
2. **Core docs** with standard front-matter and tier tags; requirement
   tables keep `FR-<AREA>-NNN` + Given/When/Then (or the profile defines
   its acceptance analog explicitly — e.g. research decision criteria).
3. **A Light-tier doc** (or a stated reuse of an existing one).
4. **A failure-mode rubric** with the disposition protocol (pass with
   evidence / flag / N-A with reason) and a shipped review-artifact
   template — the game profile's DESIGN_RUBRIC is the reference
   implementation.
5. **Validator compatibility**: filename prefix registered in
   tools/validate.sh scans; new ID registers added to tools/specgraph.py
   and AGENTS.md §6; every Must row ships with a filled acceptance cell.
6. **Specialization lens** if the domain has strong subtypes (genres,
   study types) — and it binds at scoping like the game genre lens, or it
   states why no lens is needed.

## Roadmap (build when the trigger fires)
| Candidate | Trigger to build |
|---|---|
| hardware/embedded | first real request pairing firmware specs with BOM/compliance needs — requires domain review before authoring cert content |
| education/course | first curriculum-shaped brief; learning-objective registers (LO-) map cleanly onto the FR discipline |

Rejected as profiles (covered elsewhere): ML products (product + ai/
modules), model development (research profile), migrations/ops (product +
brownfield §8).

## Profile composition
Profiles compose rather than merge. A bio-model project that also runs
experiments scopes a research-profile study alongside its bio set; a game
with a research arm does the same. The MANIFEST records the primary
profile and any composed secondary set, and each keeps its own registers
and rubric.
