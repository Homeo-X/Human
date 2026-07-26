---
doc: TECH_Data_Design
tier: standard+
version: 1.0.0
status: draft
owner: architect
last_updated: 2026-07-26
---

# Data Design

_Physical realization of PRD_Data_Overview: same entity names, now with
storage-level decisions. The substrate is files; the indexes are derived and
disposable._

## Storage Overview
| Store | Technology | Holds | Why This Store |
|---|---|---|---|
| Substrate | JSON files on disk, in git | Entity, Relationship, Claim, Source, Process, ScaleLevel, SpatialIdentity | diffable and reviewable in a pull request; hashable; readable with no service running. Git gives lineage for free, which `specgraph --history` already reads |
| Asset bundles | content-addressed blobs, one bundle per licence tier | GeometryAsset | tier separability in a build (D-003); large binaries do not belong in the substrate |
| Release artifact | immutable tarball plus manifest, content-addressed | a built, validated snapshot of substrate + asset references | the unit of citation and reproducibility (G-07) |
| Query index | SQLite, built from a release | derived lookup tables for claims, terms, relations, spatial predicates | derived and disposable — rebuildable from the release, never authoritative |
| Working store | relational (PostgreSQL) | CurationTask, Review, Approval, agent runtime objects, pre-release drafts | mutable, transactional, small; the boring choice is right |
| Personal store (Phase 7) | relational, separate instance and credentials | Individual, Overlay, OverlayValue | physical separation is what makes INV-08 structural (D-004) |

**The rule that orders all of this:** the substrate is canonical, everything else
is derived. An index that disagrees with the substrate is a bug in the index. This
mirrors AGENTS.md §10's treatment of the spec graph, deliberately — the same
discipline that keeps the documents honest keeps the data honest.

## Schemas

### entity
| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | text | PK; external term or `HOX:<class>:<slug>` | never reused (FR-ONTO-004) |
| minted | bool | not null | |
| minted_reason | text | required when minted | INV-10 |
| entity_class | text | not null, FK to vocabulary | |
| level | int | 0–10; null for spanning processes | exactly one of level/spatial_scale is set |
| spatial_scale | int[] | null for located structures | ordered; each within declared depth |
| subsystem | text | not null | governs the INV-05 depth check |
| preferred_term | text | not null | |
| synonyms | jsonb | array of {term, source, register} | |
| xrefs | jsonb | array of {authority, id, pinned_version} | |
| compilation_status | enum | not null | narrative/structured/mechanistic/parameterized |
| promotion_blocked | bool | not null, default false | set by an upstream split |
| variant_of | text | FK entity | requires a prevalence claim |
| retired_at, successor_id | timestamp, text | set together or neither | the tombstone pair |

### claim
| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | text | PK | |
| subject_id | text | not null, FK entity or relationship | |
| predicate | text | not null | |
| object | jsonb | not null | id reference or literal value |
| unit | text | required when object is numeric | UCUM; INV-04 |
| evidence_class | enum | not null | EVC-1…EVC-8 |
| sources | jsonb | required unless EVC-8 | resolvable identifiers |
| source_type | text | not null | constrains admissible class |
| species | text | not null | INV-12 |
| transfer_justification | text | required when species ≠ human | |
| population | text | not null | `unspecified in source` is valid and informative |
| conditions | jsonb | required when quantitative | |
| date_asserted | date | not null | |
| limitations | text | not null | `none identified` must be deliberate |
| conflicts_with | text[] | | symmetric, maintained in pairs |
| assigned_by | text | not null | **must be a human id when class is EVC-1 or EVC-2** |

### relationship
| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | text | PK | |
| source_id, target_id | text | not null, FK entity | |
| type | text | not null, FK relationship_type | no untyped edges (FR-REL-001) |
| skip_justification | text | required when the edge spans >1 level | INV-05 |
| prose_justification | text | required when type is `associated_with` | carried from the seed corpus |
| provenance_claim_id | text | not null, FK claim | edges do not inherit endpoint evidence (FR-REL-008) |

Uniqueness: `(source_id, type, target_id)`. `part_of` additionally carries a
partial unique index on `source_id`, which is how single-parent containment
(INV-02) is enforced by the store rather than by application logic.

### overlay_value (Phase 7)
| Field | Type | Constraints | Notes |
|---|---|---|---|
| id | text | PK | |
| overlay_id | text | not null, FK overlay | |
| target_path | text | not null | **CHECK constraint: must resolve within overlay namespace** — this is INV-08 in the schema |
| value | jsonb | not null | |
| unit | text | not null | INV-04 applies identically to overlays |
| measured_at | timestamptz | not null | |
| method, source_rank, confidence | text | not null | |
| device | text | | |
| superseded_by | text | FK overlay_value | append-only |

## Relationships & Integrity
Integrity is enforced in three places, and the redundancy is deliberate:

1. **JSON Schema** at write time — shape, required fields, enums.
2. **The store** — foreign keys, the `part_of` partial unique index, the
   `target_path` check constraint. These are the constraints that must hold even
   if application code is wrong.
3. **`biocheck`** — everything requiring cross-record reasoning: level
   admissibility, declared depth, evidence-class-versus-source-type, species
   justification, licence tiering.

The split follows a rule: **anything that would be catastrophic if bypassed lives
in the store.** Reference immutability and single-parent containment are in that
category; the rest is in `biocheck`, where the error messages can be biological
rather than schematic (FR-VALD-005).

## Indexing Strategy
| Query Pattern (FR ref) | Index |
|---|---|
| resolve entity by any identifier including retired (FR-ONTO-004) | id PK plus an identifier alias table covering xrefs, synonyms, tombstones |
| relations of an entity by type and direction (FR-REL-010) | `(source_id, type)` and `(target_id, type)` |
| claims for a subject, filtered by class (FR-EVID-002) | `(subject_id, evidence_class)` |
| name, synonym, and eponym search (FR-SRCH-001) | full-text index over the alias table, with the matched form retained |
| function search over claims (FR-SRCH-003) | `(predicate, object)` plus full-text over claim objects |
| negative-space query (FR-SRCH-004) | partial index on `evidence_class = 'EVC-8'`, plus a declared-versus-populated rollup per subsystem and level |
| coverage per subsystem per level (FR-SCAL-010) | materialized rollup, rebuilt per release |
| spatial adjacency and containment (FR-SPAT-008) | adjacency edge index on spatial identities; no geometric index needed at this scale |

The negative-space and coverage indexes are worth noting: most products would not
index absence. Here they serve first-class queries, which is a consequence of
treating UNKNOWN as an asserted claim rather than a missing row.

## Migration & Versioning Strategy
- **Substrate migrations** are ordinary file transformations, reviewed as diffs
  like any other change, and always accompanied by a `biocheck` run.
- **Release compatibility:** additive changes are non-breaking; identifier
  changes, entity removals, relation-semantic changes, and depth narrowing are
  breaking and enumerated in release notes (FR-VER-006).
- **Retired identifiers** persist as tombstone rows forever. They are never
  garbage-collected, because a dead citation is a worse outcome than a large
  tombstone table.
- **Index rebuilds** are never migrations — indexes are dropped and rebuilt from
  the release, which is also the test that they were genuinely derived.
- **Seed and fixture data:** the cardiovascular vertical slice doubles as the
  primary fixture, so every test runs against real, graded, sourced content
  rather than against invented placeholders.

## Consistency Check
Every entity in PRD_Data_Overview appears here, with these deliberate exceptions:

| PRD entity | Why not a schema here |
|---|---|
| EntityClass, RelationshipType, EvidenceClass, LicenceTier, ScaleLevel, Authority | controlled vocabularies, versioned with the release as reference data rather than as mutable tables |
| NavigationView | derived at query time from containment edges; never stored, because storing it would invite editing it (D-006) |
| Query (transient), RetrievalResponse | working-store only, with the retention in PRD_Data_Overview |
| Agent runtime objects (Agent, Task, Plan, AgentRun, Step, ToolCall, Observation, Artifact, Approval, Failure, Retry, Compensation, EvaluationRecord) | working store, conventional relational schema per SPEC_MODEL's object model; `Approval` is shared with curation deliberately, because agent and human proposals reach canonical content through the same gate |
| ProcessRun | working store; not part of a release, since a run is an observation about the model rather than part of it |

No schema here lacks a PRD-level entity.
