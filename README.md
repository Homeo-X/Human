# Project Human Organism

A computational, semantically structured, evidence-grounded model of the human
organism — built as a **knowledge substrate first**, with spatial (3D) and
dynamic (simulation) representations as projections of that substrate, and
architected so that individual data can later be applied as an **overlay**
without ever mutating the canonical reference model.

```
Human body → organ systems → organs → tissues → cells → organelles
           → molecular mechanisms → dynamic physiological processes
           → interactions across scales
                            ↓
        generic reference model  ⊕  individual overlay  =  individual model
```

## What this is — and what it is not

The project separates three goals that are routinely conflated:

| Goal | What it means here | Status |
|---|---|---|
| **A — Knowledge representation** | represent what is known about the human body, with evidence grading | Phase 0 substrate built (one vertical slice seeded) |
| **B — Visualization** | show the body and its structures in 3D | specified, not built |
| **C — Simulation** | model how the body behaves over time | specified, not built |

Having (A) does not imply (B). Having (B) does not imply (C). Having any of them
does not imply the ability to predict an individual person's health. Every
capability in this repository states its own limits, and the validators enforce
that claims never exceed their evidence.

**This is not a medical device.** Nothing here diagnoses, treats, or advises.

## Repository layout

```
docs/               the specification set — PRD, TECH, and BIO documents
  MANIFEST.md         authoritative scoping record (profile, tier, modules)
  BIO_*.md            ontology, scale contract, processes, evidence, validation
  PRD_FR_*.md         15 functional-requirement modules
  CHALLENGE_REGISTER.md  red-team findings and their dispositions
schemas/            JSON Schemas for the substrate (entity, claim, process, …)
ontology/           canonical seed data — the L0→L10 vertical slice
tools/
  biocheck.py         executes the BIO_Validation_Framework invariants (INV-NN)
  specgraph.py        spec-graph validator (framework, extended for the bio profile)
  validate.sh         static checker for the framework tree and generated docs
templates/bio/      the bio document profile added to the framework
AGENTS.md           the PRD-Agent Framework standard this project is specified under
FRAMEWORK.md        the vendored framework's own README
UPSTREAM.md         what was vendored, and every delta applied to it
```

## Verifying the repository

```bash
bash tools/validate.sh                      # framework tree, incl. templates/bio/
bash tools/validate.sh --docs docs/         # the generated specification
python3 tools/specgraph.py docs/ --strict   # spec graph: ids, refs, traces
python3 tools/biocheck.py ontology/ --strict  # biological integrity invariants
```

`biocheck.py --selftest` runs the negative tests: each invariant is deliberately
violated and must fail. A validator that cannot fail is not a validator.

## Scientific honesty

Every entity, claim, and quantity in `ontology/` carries an evidence class:
`VERIFIED` · `STRONGLY_SUPPORTED` · `MODELLED` · `APPROXIMATED` · `INFERRED` ·
`HYPOTHESIZED` · `CONFLICTING_EVIDENCE` · `UNKNOWN`.

`UNKNOWN` is a valid, first-class answer. The invariants forbid silently
promoting `UNKNOWN` to an assumption, or an approximation to a fact. The model is
intended to be more trustworthy *because* it represents what it does not know.

## Current state

Phase 0. The specification set is complete and validated; the substrate holds one
complete cross-scale path (Human → cardiovascular system → heart → left ventricle
→ myocardium → cardiomyocyte → sarcomere → actin/myosin → cross-bridge cycle) as
proof that the schema carries real biology. It is a slice, not coverage.

Roadmap phases 1–7 are specified in `docs/PRD_Scope_and_Roadmap.md`.
