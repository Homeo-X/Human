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
| **A — Knowledge representation** | represent what is known about the human body, with evidence grading | Phase 0 substrate built; one vertical slice and 107 organs seeded, none reviewed |
| **B — Visualization** | show the body and its structures in 3D | specified, not built |
| **C — Simulation** | model how the body behaves over time | specified, not built |

Having (A) does not imply (B). Having (B) does not imply (C). Having any of them
does not imply the ability to predict an individual person's health. Every
capability in this repository states its own limits, and the validators enforce
that claims never exceed their evidence.

**This is not a medical device.** Nothing here diagnoses, treats, or advises.

## What the model does not know

The negative space is the point, so it goes here rather than in a footnote.
Every figure below is derived from `ontology/`, not asserted — the command that
produces it is beside it, and a stale number is a bug.

| | count | how to check |
|---|---|---|
| entities **reviewed by a human** | **0 of 276** | `python3 -m homeo.cli coverage --table` |
| claims that are **findings** rather than definitions | **29 of 443** | `python3 tools/biocheck.py ontology/ --strict` |
| entities carrying **geometry** | **15 of 276** | `python3 -m homeo.cli view heart` reports `depicted`; everything else `described` or `unplaced` |
| entities still `narrative` — described, not modelled | **140 of 276** | `python3 -m homeo.cli entity <id>` reports its compilation status |
| organs **located in the body** by containment | **2 of 107** | `python3 tools/biocheck.py ontology/` — INV-21 reports the rest |

Read those together: the substrate mostly knows that a liver exists, what two
systems it belongs to, and which authority named it — and little about what it
*does*. 414 of its 443 claims are terminological (D-021): they record what a
word means on the authority of a source, which is not evidence about a body and
is deliberately kept off the evidence ladder so it can never be cited as one.
The respiratory system is the exception and the template: 20 findings with
units, measurement conditions, discriminating populations, and one genuine
unresolved conflict retained rather than resolved (D-030). No content has been
through domain review, so there are **no EVC-1 claims at all**, and the release
manifest publishes that number rather than the one that flatters.

Fifteen meshes are bound: one artist's exemplar and fourteen surface
reconstructions from BodyParts3D, joined to organs **by FMA identifier** rather
than by name (D-032). **This project holds no measured geometry** — every asset
declares itself `reference_exemplar` or `derived`, and the manifest refuses to
let anything call itself `measured`. The BodyParts3D assets are share-alike, so
they are quarantined at tier T1: a permissive-only build drops all fourteen and
says so, rather than looking complete.

A model that reports this honestly is more useful than one that does not report
it, which is the whole wager of the project.

The same rule now applies to the performance targets. Thirty-one NFR rows
carried a number and **no measurement** until `tools/bench.py` ran them against
synthetic substrates at 1,012 → 100,012 entities (`bench/RESULTS.json`, D-028).
Five rows pass with room to spare; one is a finding — the substrate reaches
NFR-008's Phase 5 volumetrics at **~3 GB resident**, which a server can do and
the offline classroom profile in NFR-013 cannot. Twelve rows needing a browser,
a GPU, geometry or a deployed service are listed as unmeasurable with what each
needs, rather than filled in with a plausible number.

## Repository layout

```
docs/               the specification set — PRD, TECH, and BIO documents
  MANIFEST.md         authoritative scoping record (profile, tier, modules)
  BIO_*.md            ontology, scale contract, processes, evidence, validation
  PRD_FR_*.md         15 functional-requirement modules
  CHALLENGE_REGISTER.md  red-team findings and their dispositions
schemas/            JSON Schemas for the substrate (entity, claim, process, …)
ontology/           canonical data — the L0→L10 vertical slice, the narrative seed
  imported/           organs imported by rule, with the refusals they produced
src/homeo/          the reference implementation of the substrate services
  substrate.py        typed loading of the canonical files
  graph.py            resolution, typed traversal, the derived navigation view
  scale.py            level contracts, declared depth, terminal answers, coverage
  evidence.py         claims, provenance, conflicts, the negative space
  search.py           name, function, clinical, spatial, negative, structured
  groundedness.py     the INV-14 guard — refuses ungrounded output
  promotion.py        the compilation ladder and its gates
  navigation.py       view state, semantic vs physical zoom, addressing
  projection.py       the view specification derived from the graph
  curation.py         the review queue, competence scoping, approval records
  agents.py           the agent runtime — the twelve-facet contract, enforced
  evals.py            the EV-RETR suites that gate a release
  release.py          build, validate, hash, atomic publish
  importers/obo.py    OBO/OBO-JSON import, and the six gates it refuses at
  api.py, cli.py      the API and its command-line equivalent
tests/              518 tests, each tagged with the FR ids it verifies
tools/
  check.sh            everything that must be green (--quick for pre-commit)
  curate_regions.py   adds the L1 regions through the real curation path
  curate_pancreas.py  the multi-membership test case (D-019)
  correct_attribution.py  the D-017 attribution correction, auditable
  split_claim_kinds.py  separates definitions from findings (D-021)
  fetch_authorities.py  pins UBERON/CL/ECO snapshots by SHA-256 (D-024)
  import_l3.py        imports L3 organs by rule from the pinned snapshot
  curate_respiratory.py  the first findings — units, conditions, one conflict
  fetch_assets.py     pins geometry by hash, licence and tier; bytes stay out
  bind_geometry.py    mints minimal spatial identities so a mesh can bind
  synth.py            synthetic substrates at volume — refuses to touch real data
  bench.py            the NFR register, measured (bench/RESULTS.json)
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
python3 -m homeo.cli view heart --evidence EVC-2  # what is in view, and why
python3 -m homeo.cli zoom heart semantic 5        # change ontological resolution
python3 -m homeo.cli zoom heart physical 4        # change magnification only
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
expected for the modules not yet built (personalization and simulation).
A Must that is *claimed* —
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

The specification set is complete and validated. The substrate holds **276
entities**: a cardiovascular **vertical slice** spanning L0 to L10 — organism,
system, heart, left ventricle, myocardium, cardiomyocyte population,
cardiomyocyte, sarcomere, actin/myosin, cross-bridge cycle — the narrative seed
corpus, and **107 organs at L3** across ten organ systems.

Those organs arrived by rule rather than by hand (D-024): `tools/import_l3.py`
walks a **pinned UBERON snapshot**, verified by SHA-256, and admits only terms a
stated rule covers. It refused 99 — 67 without a human warrant, 21 it could not
place in a system, 9 grouping classes, 2 already curated — and reported every
refusal with its reason rather than guessing. Fifteen of the admitted organs belong to more than one system (the
pancreas to digestive and endocrine, the pituitary to three), which is why the
107 organs are counted 123 times across the coverage table and why containment
and membership had to be separate relations from the start. Everything imported
is **provisional**: proposed by an agent, reviewed by nobody, and marked so at
every surface it appears on.

Two things about that slice are worth stating precisely, because the first
version of this README overclaimed them:

- **The containment chain runs unbroken from L0 to L8 for the curated slice —
  and for almost nothing else.** 98 of the 107 organs have no containment
  parent at all: the import placed them by system membership, because UBERON's
  own `part_of` does not supply this project's containment (D-024), and putting
  each organ in a body region is curation nobody has done. They are reachable,
  queryable and correctly graded; they are not *located*. G-04 measures exactly
  this and reads **2%** against a target of 100%, INV-21 reports it on every
  run, and D-029 records why it is counted rather than guessed at. The chain
  below is the seeded path, not the general case: organism → thorax →
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

**140 of the 276 entities are still `narrative`** — described, not modelled —
and no domain reviewer has examined any of it. The import made that deficit
larger, not smaller: it went from 173 unreviewed records to 293, and the honest
reading is that breadth is cheap and review is the constraint (RSK-02). D-026
records the intended answer — certify the *rule* rather than each record — as a
proposal, not as something built.

Built: entity resolution, typed traversal, the derived navigation view, scale
contracts and terminal answers, evidence and provenance, five search modes, the
groundedness guard, the compilation ladder, the EV-RETR suites, the release
pipeline, the read API, the curation plane, the agent runtime, and the
navigation and projection layers.

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

The viewer being gated is why the *navigation model underneath it* was built
instead (D-015). A `ViewState` is immutable and its two zoom axes are separate
operations, so magnifying cannot change a level and changing a level cannot move
the camera; `ProjectionService` computes, from the graph, what is in view —
entities at the requested ontological resolution, their positions, whether
geometry exists, the relations among them, and the evidence behind each.

**The renderer is one client of that specification, not its owner.** The same
substrate answers the read API, the CLI, the agent runtime, the importers, and
the release pipeline, and none of them queries around the projection to get a
different answer. That ordering is what makes the 3D view worth trusting when it
exists, and it is also why its absence costs the project nothing structural:
geometry is an attribute of an entity rather than the condition of its existing,
so an entity with no mesh is `described`, positioned, and navigable, and a failed
asset is reported as a pipeline failure rather than as thin anatomy.
