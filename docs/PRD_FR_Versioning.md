---
doc: PRD_FR_Versioning
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Versioning

## Purpose & Scope
The knowledge base as a versioned, reproducible, addressable artifact: release
semantics, authority pinning, lineage, export, migration, and the reproducibility
guarantee that G-07 measures. Absorbs the audit-trail and import/export
cross-cutting concerns — knowledge lineage *is* the audit trail here. Boundary:
what is released → every content module; validation gating → PRD_FR_Validation.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Researcher | to cite a specific release | my work remains checkable after the model changes |
| Researcher | to rebuild a release from a clean checkout and get the same bytes | reproducibility is demonstrated, not claimed |
| Integrator | to know what changed between releases | I can decide whether to migrate |
| Licence owner | a manifest listing every source and licence in a release | compliance is verifiable per artifact |
| Curator | to see the lineage of any claim back through releases | I can tell when and why something changed |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-VER-001 | Must | Every release is immutable, addressable by id, and carries a content hash | Given a published release id, when fetched at any later time, then identical content is returned; and given an attempted modification, then it is refused | Mutable releases make every citation meaningless |
| FR-VER-002 | Must | Every release rebuilds byte-identically from a clean checkout at its pinned inputs | Given a release id, when rebuilt from a clean checkout, then the output hash matches; and given any nondeterminism, then the build fails rather than producing a near-match | This is G-07; a near-match is a failure, not a success |
| FR-VER-003 | Must | Every release pins the version of every external authority it references | Given a release manifest, when inspected, then each authority and its pinned version appear; and given a claim in that release, then it is re-evaluable against the authority version current when it was made | Without pinning, an upstream change silently rewrites the past |
| FR-VER-004 | Must | Every release manifest lists every source with its licence, tier, and verification date | Given a release, when its manifest is produced, then all sources, licences, tiers, and verification dates appear; and given an unverifiable licence, then the release is blocked | Licence drift is silent until it is expensive |
| FR-VER-005 | Must | A release cannot publish unless validation passed all blocking invariants | Given a release with a blocking violation, when publication is attempted, then it is refused with the violations listed; and given a passing run, then publication proceeds and the result is recorded in the manifest | The gate must be in the pipeline, not in a checklist |
| FR-VER-012 | Must | A release leaves `validated` only when every artifact its manifest names is present and hash-matched; publication is atomic across graph, claims, and asset bundles | Given a manifest naming an asset bundle that failed to upload, when publication is attempted, then it is refused and the release stays `validated`; and given full correspondence, then publication proceeds as one atomic act | CH-07: releases are immutable and cannot be withdrawn, so a partially-published release would be a permanent inconsistent state with no recovery path |
| FR-VER-006 | Must | Breaking and non-breaking changes are distinguished, and breaking changes are enumerated in the release notes | Given a release removing an entity or changing an identifier, when published, then it is marked breaking with the specific changes listed; and given additive changes only, then it is marked non-breaking | Integrators need to know before they upgrade, not after |
| FR-VER-007 | Must | Retired identifiers resolve to tombstones across releases | Given a retired id from an old release, when resolved against a current release, then a tombstone naming the successor is returned; and given no successor, then the retirement reason is returned | A dead link teaches nothing; a tombstone teaches what happened |
| FR-VER-008 | Should | Any claim's lineage is traceable across releases: when it entered, when its class changed, who reviewed it | Given a claim id, when its lineage is requested, then its full history across releases is returned; and given a claim that changed class, then the evidence and reviewer for each change appear | This is the audit trail, and it is a feature rather than a compliance artifact |
| FR-VER-009 | Should | Releases are exportable in full or by scope, with provenance and licence manifests included | Given a scoped export, when produced, then it contains the entities, claims, provenance, and a licence manifest for exactly that scope; and given a scope crossing licence tiers, then the export is refused or tier-split | An export without its licence manifest transfers an obligation the recipient cannot see |
| FR-VER-013 | Must | A Scope Reopen narrowing a declared depth records the coverage delta it produces, and coverage is thereafter reported against both the current and the original scoping denominator | Given a reopen narrowing endocrine from L3 to L2, when the Decision is written, then it states the resulting change in G-01; and given any later coverage report, then both denominators appear while they differ | CH-03: the party measured by the denominator is the party authorized to change it, so the change must be visible rather than merely recorded |
| FR-VER-010 | Should | Migration between releases previews its effects before applying | Given a pinned consumer migrating, when a preview is requested, then changed, added, and removed items are listed; and given the migration, then it is explicit, never automatic | Especially for overlays, where migration changes what a personal model means |
| FR-VER-011 | Could | Two releases can be diffed at entity, claim, and relation granularity | Given two release ids, when diffed, then additions, removals, retypings, and class changes are reported separately | Class changes are the interesting diff and should not hide among additions |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| KnowledgeRelease | RW | the release record, manifest, and hash |
| Authority | R | pinned external ontology versions |
| Source | R | licence manifest |
| LicenceTier | R | export tier splitting |
| Entity | R | release contents |
| Claim | R | release contents and lineage |
| Relationship | R | release contents |
| GeometryAsset | R | asset packages per tier |

## States & Transitions
Release lifecycle: `draft` → `validated` → `published` → `superseded`. Only
`draft` is mutable. `published` is permanent and immutable; a mistaken release is
superseded by a corrected one, never edited or withdrawn, so any citation of it
remains resolvable with its correction visible.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: a release with no content changes | permitted if authority pins changed, and the manifest states that content is unchanged | FR-VER-003 |
| Invalid input: a release referencing an unpinned authority | refused at validation | FR-VER-003 |
| Permission denied: a non-operator attempts publication | refused; publication is a human-confirmed irreversible action | FR-VER-005 |
| Concurrency: two publications from the same draft | serialized; the second is refused against the now-published state | FR-VER-001 |
| External dependency failure: an authority unreachable during pinning | the release is blocked rather than published with an unpinned reference | FR-VER-003 |
| Scale extreme: a release containing millions of claims | manifest and hashing are incremental; export is streamable and resumable | FR-VER-009 |
| A published release is found to contain a serious error | superseded with a correction and a prominent notice on the original; never withdrawn, because withdrawal breaks every citation | FR-VER-001 |
| A source's licence changes after a release was published | the published release is unaffected and remains valid under the terms at publication; the change is recorded and applies to future releases | FR-VER-004 |

## Dependencies
- On other modules: PRD_FR_Validation (release gating), PRD_FR_Evidence (source
  and licence records), PRD_FR_Ontology (authority pinning, tombstones),
  PRD_FR_Curation (publication approval), PRD_FR_Personalization (overlay
  pinning and migration)
- On external integrations: ontology authorities, artifact hosting

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Releases rebuilding byte-identically from a clean checkout | G-07 | 100% |
| Releases with a complete source and licence manifest | G-07 | 100% |
| Claims whose lineage is traceable across releases | G-03 | 100% |
| Releases published with a blocking validation failure | G-05 | 0, enforced |

## Out of Scope for This Module
- Versioning of individual overlays beyond release pinning (PRD_FR_Personalization)
- Distributing releases through package ecosystems in Phase 0
- Automatic migration of pinned consumers

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| What cadence keeps releases citable without making them noise? | Biology Lead | Phase 2 |
| How is byte-identical rebuild maintained as geometry assets grow to gigabytes? | Research Engineer | Phase 1 |
| Should a superseded release stay fetchable indefinitely, and at whose cost? | Architect | Phase 3 |
