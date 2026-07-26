---
doc: TECH_System_Architecture
tier: standard+
version: 1.0.0
status: draft
owner: architect
last_updated: 2026-07-26
---

# System Architecture (SRS)

_Greenfield: no current-state grounding applies. Everything here is to be built,
in the phase order of PRD_Scope_and_Roadmap._

## System Overview
**Shape: a content-addressed knowledge artifact, plus a thin read surface, plus a
separate curation pipeline.** Not a conventional web application with a database.

The reasoning is that the product's central guarantee is reproducibility (G-07)
and immutability of the reference model (D-004). Both are far easier to achieve
when the published thing is an artifact you can hash than when it is the current
state of a mutable database. So:

- The **reference model is built, validated, hashed, and published** as an
  immutable release. Readers consume a release, never a live mutable store.
- The **curation pipeline is a separate system** with its own store, its own
  authentication, and write access to nothing that readers see until a release is
  published.
- **Individual data (Phase 7) lives in a third store**, physically separate, with
  no path to the reference — which is what makes INV-08 structural rather than
  procedural.

This shape fits the team and the scale honestly: the graph fits in memory well
past Phase 3 (PRD_Data_Overview volumetrics), so a distributed graph database
would add operational burden to solve a problem this product does not have.

```
┌─────────────────── CURATION PLANE (authenticated) ───────────────────┐
│  Proposal queue → Review → Approval → Working store (mutable)         │
│         ↑                                     │                       │
│    Agent runners                              ▼                       │
│    (AGT-1…AGT-12)                    Build + validate + hash          │
└───────────────────────────────────────────────│──────────────────────┘
                                                ▼
                                   ┌──────────────────────┐
                                   │  RELEASE (immutable) │
                                   │  graph · claims ·    │
                                   │  assets · manifest   │
                                   └──────────┬───────────┘
                                              │
┌─────────────────── READ PLANE (anonymous) ──┼───────────────────────┐
│  Query service · Retrieval service · Viewer · Offline bundle         │
└─────────────────────────────────────────────────────────────────────┘
                                              │
┌─────────── PERSONAL PLANE (Phase 7, separate store, separate creds) ─┐
│  Overlay store → Overlay resolver (read-only against release)         │
└──────────────────────────────────────────────────────────────────────┘
```

## Tech Stack
| Layer | Choice | Rationale | Locked or Provisional |
|---|---|---|---|
| Substrate format | JSON documents on disk, JSON Schema validated, one file per entity group | diffable, reviewable in a pull request, trivially hashable, and readable without any running service. The substrate outlives any database choice | **locked** — it is the serialization the whole reproducibility story rests on |
| Validation | Python 3, stdlib only (`tools/biocheck.py`, `tools/specgraph.py`) | zero-dependency validators run anywhere, including a curator's laptop and CI, with no environment drift | **locked** |
| Query store | in-process graph loaded from a release; a SQLite index for claim lookup | fits the volumetrics; deterministic; a release is loadable in full | provisional — revisit at Phase 5 volumetrics |
| Read API | HTTP/JSON, read-only, stateless, release-pinned | statelessness is what makes the read plane trivially cacheable and mirrorable | provisional |
| Viewer | WebGL2 baseline, WebGPU when available; TypeScript | NFR-019; WebGPU is not required because classroom hardware is not new hardware | provisional |
| Curation plane | conventional relational store, server-rendered UI | the working store is mutable, transactional, and small; boring technology is correct here | provisional |
| Agent runtime | Python; tool autonomy enforced in the runtime, not the prompt | FR-AGD-002 requires enforcement that survives paraphrase | provisional |
| Retrieval | claim-level retrieval over the release; a language model for phrasing only | FR-RETR-001 makes the model a phrasing engine, never a source | provisional |
| Personal store (Phase 7) | separate database, separate credentials, encrypted at rest | D-004 structural separation | provisional |
| Asset packaging | content-addressed bundles per licence tier | D-003 tier separability in a build | **locked** |

## Component Breakdown
| Component | Responsibility | Talks To | Owns Data? |
|---|---|---|---|
| Substrate | canonical JSON entity, claim, relation, process, spatial records | build pipeline | **yes — the source of truth** |
| `biocheck` | executes INV-01…INV-14 against the substrate | substrate | no |
| `specgraph` | validates the document set: ids, references, traces | `docs/` | no |
| Build pipeline | assembles, validates, hashes, and publishes a release | substrate, validators, asset bundles | no — produces artifacts |
| Release artifact | immutable graph, claims, manifest, asset references | — | yes, immutably |
| Query service | entity, relation, claim, spatial, and negative-space queries | release | no |
| Retrieval service | grounded natural-language responses | query service, language model | no |
| Groundedness guard | refuses any assertion not resolving to a claim id | retrieval service | no |
| Viewer | spatial and semantic navigation | query service, asset bundles | no |
| Offline bundle | a release plus one asset tier, self-contained | — | no |
| Curation service | queues, review, approval, working store | working store, agent runners | yes — pre-release only |
| Agent runners | AGT-1…AGT-12 under the Facet 5 tool contract | curation service, external sources | no |
| Overlay resolver (Phase 7) | applies overlays over a pinned release at read time | personal store, release | no |
| Personal store (Phase 7) | individual data | — | yes, sensitively |

**The architecturally load-bearing component is the groundedness guard**, because
it is the only thing standing between a fluent language model and fabricated
biology — and it works by refusing output rather than by filtering it.

## Data Flow

### Journey 1 — the descent (read path)
Viewer requests entity at level → query service loads from the pinned release →
returns entity, level contract, spatial identity, typed relations, and claims with
their classes → viewer renders, with evidence class and compilation status in the
always-visible layer → level transition requests the next level's contract and
announces its mode and resolution limit → at declared depth the query service
returns the terminal answer rather than an empty result.
**Failure path:** asset bundle unreachable → viewer renders the
described-not-depicted state, visually distinct from genuine absence
(FR-SPAT-002).

### Journey 5 — curating a claim (write path)
Agent runner proposes → proposal lands in the working store's queue with its full
derivation → `biocheck` runs on the proposed change → reviewer opens it within
their competence scope → accepts, producing an Approval record → the working
store is updated → at release time the build pipeline runs full validation, and a
blocking failure stops publication.
**Failure path:** a proposal exceeding declared depth is refused before reaching
review, and appears in the blocked list with its reason (FR-SCAL-002).

### Journey 10 — asking a question (retrieval path)
Question → query service retrieves candidate claims from the release → language
model phrases an answer over exactly those claims → **groundedness guard resolves
every assertion to a claim id** → grounded response returned with per-assertion
classes; or refused and regenerated; or, where no claims exist, the gap is stated
citing the scale contract.
**Failure path:** language model unavailable → structured search results with
the degradation stated (NFR-012).

## Environments & Deployment
- **dev** — local; validators run without network; pinned authority snapshots as
  fixtures.
- **staging** — full build pipeline, release published to a staging artifact
  store, EV suites run here.
- **prod** — read plane serves published releases from content-addressed storage;
  curation plane deployed separately with its own access control.

Promotion is by release artifact, not by code deploy: a release built in staging
is byte-identical to the one served in prod, or it is not promoted. Rollback is
serving the previous release id — instant, and total, because releases are
immutable.

## Architecture Decisions
Significant choices are recorded in PRD_Decision_Log rather than re-argued here:

- **D-002** external ontologies referenced, not forked — the deepest and least
  reversible dependency
- **D-003** share-alike geometry quarantined in a separate asset tier
- **D-004** personalization as overlay; reference immutable — realized as three
  separate stores
- **D-005** no global simulation clock — realized as per-domain runtimes with
  declared composition
- **D-006** tree is a derived view; graph is canonical — realized as a generated
  `NavigationView`, never an authored one
- **D-008** geometry binds through a spatial identity — realized as the
  indirection that makes D-003's tier swap cheap

## What This Architecture Costs
Stated plainly, because an architecture document that lists only benefits is
marketing:

- **Publishing is slow.** Content becomes visible on a release cadence, not on
  save. This is the price of citable immutability, and it will feel wrong to
  anyone used to a CMS.
- **Two stores of similar content** (working and released) means a class of
  drift bug that a single mutable database would not have. The build pipeline's
  validation is what catches it, which is why validation is not optional.
- **Three planes mean three deployments** and more operational surface than a
  monolith, for a team that is not large.
- **The in-memory graph choice will need revisiting** at Phase 5, and the
  provisional marking above is a real commitment to revisit rather than a hedge.
