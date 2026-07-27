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
ontology/           canonical data — the L0→L10 vertical slice + the narrative seed
src/homeo/          the reference implementation of the substrate services
  substrate.py        typed loading of the canonical files
  graph.py            resolution, typed traversal, the derived navigation view
  scale.py            level contracts, declared depth, terminal answers, coverage
  evidence.py         claims, provenance, conflicts, the negative space
  search.py           name, function, clinical, spatial, negative, structured
  groundedness.py     the INV-14 guard — refuses ungrounded output
  promotion.py        the compilation ladder and its gates
  curation.py         the review queue, competence scoping, approval records
  agents.py           the agent runtime — the twelve-facet contract, enforced
  evals.py            the EV-RETR suites that gate a release
  release.py          build, validate, hash, atomic publish
  api.py, cli.py      the API and its command-line equivalent
tests/              308 tests, each tagged with the FR ids it verifies
tools/
  check.sh            everything that must be green (--quick for pre-commit)
  curate_regions.py   adds the L1 regions through the real curation path
  biocheck.py         executes the BIO_Validation_Framework invariants (INV-NN)
  specgraph.py        spec-graph validator (framework, extended for the bio profile)
  validate.sh         static checker for the framework tree and generated docs
templates/bio/      the bio document profile added to the framework
AGENTS.md           the PRD-Agent Framework standard this project is specified under
FRAMEWORK.md        the vendored framework's own README
UPSTREAM.md         what was vendored, and every delta applied to it
```

## Using it

```bash
export PYTHONPATH=src

python3 -m homeo.cli entity UBERON:0000948        # resolve and describe
python3 -m homeo.cli descend GO:0030017           # one level down, or the limit
python3 -m homeo.cli unknowns UBERON:0002349      # what the model does not know
python3 -m homeo.cli search cor --mode name       # synonyms, eponyms, registers
python3 -m homeo.cli path UBERON:0000468 GO:0030017   # cross-scale path
python3 -m homeo.cli coverage --table             # declared vs populated
python3 -m homeo.cli publish rel-2026-07-26 --out releases
python3 -m homeo.cli serve --port 8080            # the read API, no write surface
```

The review commands are a separate plane, reached deliberately. They need a
reviewer identity, they refuse anything outside that reviewer's declared
competence, and they are the only way content becomes canonical:

```bash
python3 -m homeo.cli queue    --reviewer human:anatomy-reviewer-01
python3 -m homeo.cli review   TASK:00001 accept \
    --reviewer human:anatomy-reviewer-01 --reason "TA division, UBERON resolves"
python3 -m homeo.cli operator                     # depth, throughput, blocked
python3 -m homeo.cli serve --queue curation/queue.json   # opt in to the plane
```

Started without `--queue`, the server has no curation service at all — the write
endpoints are not merely unauthorized there, they do not exist.

The API's status codes encode the project's posture: **the model's limits are
200s, and only genuine caller errors are 4xx.** `/descend` past a declared depth
returns 200 with `NOT_REPRESENTED`; a refused generation returns 200 with its
reason. A system that 404s "we do not model that" teaches its users that its
honesty is a malfunction.

## Verifying the repository

```bash
bash tools/check.sh              # everything below, in order
bash tools/check.sh --quick      # substrate + tests only, for a pre-commit hook
```

Individually:

```bash
python3 tools/biocheck.py ontology/ --strict    # biological integrity invariants
python3 tools/biocheck.py ontology/ --selftest  # every invariant, deliberately violated
PYTHONPATH=src:. python3 -m unittest discover -s tests -t . -q
bash tools/validate.sh                          # framework tree, incl. templates/bio/
bash tools/validate.sh --docs docs/             # the generated specification
python3 tools/specgraph.py docs/ --strict       # spec graph: ids, refs, traces
python3 tools/specgraph.py docs/ --trace src tests tools   # FR to code and test
```

`--selftest` is the one that matters most: each invariant is deliberately
violated and must be detected. A validator that cannot fail is not a validator.

The trace report distinguishes two things. A Must with **no** implementation is
expected for the modules not yet built (personalization, simulation, and the two
viewer requirements — D-011). A Must that is *claimed* —
code exists but no test verifies it — is a failure, and `check.sh` holds that
count at zero.

## Scientific honesty

Every entity, claim, and quantity in `ontology/` carries an evidence class:
`VERIFIED` · `STRONGLY_SUPPORTED` · `MODELLED` · `APPROXIMATED` · `INFERRED` ·
`HYPOTHESIZED` · `CONFLICTING_EVIDENCE` · `UNKNOWN`.

`UNKNOWN` is a valid, first-class answer. The invariants forbid silently
promoting `UNKNOWN` to an assumption, or an approximation to a fact. The model is
intended to be more trustworthy *because* it represents what it does not know.

## Current state

Phase 0, with the substrate services implemented.

The specification set is complete and validated. The substrate holds a cardiovascular **vertical slice** spanning L0 to L10 —
organism, system, heart, left ventricle, myocardium, cardiomyocyte population,
cardiomyocyte, sarcomere, actin/myosin, cross-bridge cycle — plus the narrative
seed corpus.

Two things about that slice are worth stating precisely, because the first
version of this README overclaimed them:

- **The containment chain now runs unbroken from L0 to L8**: organism → thorax →
  heart → left ventricle → myocardium → cardiomyocyte population → cardiomyocyte
  → sarcomere. It did not before. L1 was empty across the whole substrate, so
  the chain jumped organism straight to organ; the nine anatomical regions were
  added through the curation path (`tools/curate_regions.py`, D-014) and the
  heart's containment corrected — a heart is *in* the thorax and a *member of*
  the cardiovascular system, which is why L2 is absent from the chain rather
  than missing from it. `homeo.cli path` measures this rather than asserting it,
  and reports `complete: false` with the missing levels named whenever a real
  gap exists (D-013).
- **L9 and L10 attach by participation, not containment.** Biomolecules and the
  cross-bridge mechanism are reached through `participates_in` and `consumes`,
  which is correct biology — a molecule is not *part of* a sarcomere in the
  containment sense — but it means the slice is not one unbroken parent chain
  from top to bottom.

**90% of entities are still `narrative`** — described, not modelled — and no
domain reviewer has yet examined any of it, so the substrate currently contains
**no EVC-1 claims at all**. The release manifest publishes both figures.

Built: entity resolution, typed traversal, the derived navigation view, scale
contracts and terminal answers, evidence and provenance, five search modes, the
groundedness guard, the compilation ladder, the EV-RETR suites, the release
pipeline, the read API, the curation plane, and the agent runtime.

The last two are the ones that determine whether anything else can be trusted,
so they are enforced rather than documented. No proposal becomes canonical
content without an Approval record from a reviewer whose declared competence
covers that subsystem and level; no agent can assign EVC-1 or EVC-2, promote a
compilation status, or publish, because the runtime checks the tool contract
before the tool is reached. Ten deliberate mutations of those gates — deleting
the competence check, permitting a forbidden tool, dropping the approval
requirement — each turn the suite red.

Not built, deliberately: the 3D viewer and the study UI (behind the Phase 1
entry gate, D-011), the simulation runtime (Phase 6), and personalization
(Phase 7). Roadmap phases 1–7 are specified in
`docs/PRD_Scope_and_Roadmap.md`.
