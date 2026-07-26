---
doc: PRD_FR_Spatial_Representation
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Spatial Representation

## Purpose & Scope
Where things are, and how that is represented: spatial identities, coordinate
frames, geometry binding, representation kinds, level of detail, and asset
licence tiering. Implements D-008 — geometry attaches to a spatial identity,
never directly to a biological entity. (Renamed from the brief's `FR-3D`; see
PRD_FR_Overview.) Boundary: navigation and zoom → PRD_FR_Navigation; entity
identity → PRD_FR_Ontology; level contracts → PRD_FR_Scale_Bridging.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Student | to see where a structure sits relative to its neighbours | location is part of what I learn, not a separate lookup |
| Researcher | to query spatially — what is adjacent, what is contained | I can ask questions the tree cannot answer |
| Curator | to describe a structure's position before any mesh exists | the model is navigable before it is beautiful |
| Builder | to exclude share-alike assets from a build | downstream licensing stays possible |
| Educator | to know whether a shape is measured or schematic | I do not teach an illustration as an anatomy |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-SPAT-001 | Must | Geometry binds to a spatial identity, which belongs to a biological entity; geometry never binds directly to an entity | Given a geometry asset submitted with an entity id and no spatial identity, when validated, then it is rejected; and given a binding through a spatial identity, when validated, then it passes | Users never see this layer; it exists so that geometry is swappable and licence-separable |
| FR-SPAT-002 | Must | An entity with no geometry is fully valid and fully navigable | Given an entity with a spatial identity but no geometry, when requested, then its position, containment, and adjacency are returned and it appears in navigation; and given a viewer, when it renders such an entity, then a designed no-geometry state is shown | An empty viewport is a bug; a stated "described, not depicted" is information |
| FR-SPAT-003 | Must | Unbound geometry is inadmissible — every asset resolves to a spatial identity | Given a mesh with no spatial identity, when ingested, then it is rejected; and given a full binding chain, when ingested, then it is admitted | Prevents the model growing artwork nobody can explain |
| FR-SPAT-004 | Must | Every geometry asset declares its representation kind: measured, derived, reference-exemplar, or schematic | Given a schematic organelle asset displayed at any level, when rendered, then it is marked schematic; and given an asset with no declared kind, when ingested, then it is rejected | This is BRB-04 — equal visual fidelity across unequal evidence is the field's default failure |
| FR-SPAT-005 | Must | Every asset carries its source, licence, and tier; T1 assets are packaged separately from T0 content | Given a share-alike asset path embedded in an entity or claim record, when validated, then INV-11 fails; and given a T1 asset referenced by id from a separate package, when validated, then it passes | Invisible to readers, decisive for builders |
| FR-SPAT-006 | Must | A build can select asset tiers, and coverage is reported against the same declared denominator regardless of selection | Given a permissive-only build, when produced, then it excludes T1 assets and reports reduced geometry coverage against the unchanged declared scope; and given the full build, then both are reported the same way | A smaller build must look smaller, not look complete |
| FR-SPAT-007 | Must | Spatial identities declare a coordinate frame, and cross-frame queries are explicit | Given two structures in different frames, when adjacency is queried, then the frames are reconciled or the query returns a stated limitation; and given same-frame structures, then the result is direct | Silent frame mixing produces confident nonsense about position |
| FR-SPAT-008 | Should | Spatial relationships — containment, adjacency, laterality, landmarks — are queryable independently of geometry | Given entities with spatial identities but no meshes, when a spatial query runs, then it returns results from the spatial identities alone; and given no spatial identity, then the entity is excluded with a stated reason | Spatial reasoning must not require artwork to exist |
| FR-SPAT-009 | Should | Level-of-detail variants of one asset are alternate representations of the same spatial identity, never separate entities | Given an organ with three LOD meshes, when its geometry is requested at a detail level, then the appropriate variant is returned under one identity; and given a request beyond available detail, then the highest available is returned with that stated | Detail level is a rendering concern; it must never fragment identity |
| FR-SPAT-010 | Should | One spatial identity may carry representations at several levels — organ mesh, tissue region, schematic | Given a heart requested at L3 and at L8, when resolved, then different representations of the same lineage are returned, each marked with its kind | This is what makes semantic zoom a change of representation rather than a change of subject |
| FR-SPAT-011 | Could | Volumetric and point-cloud representations are admissible alongside meshes | Given a volumetric asset with a declared kind and licence, when ingested, then it binds like any other representation | Architecture must not have to change when imaging data arrives |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| SpatialIdentity | RW | coordinate frame, position, containment, adjacency, laterality, landmarks |
| GeometryAsset | RW | mesh, volume, or point cloud with kind and licence |
| LicenceTier | R | T0/T1/T2 |
| Entity | R | the biological subject |
| Source | R | asset provenance |
| ScaleLevel | R | which representations are admissible at a level |

## States & Transitions
Geometry asset lifecycle: `ingested` → `bound` (to a spatial identity) →
`published` (in a release) → `superseded` or `retired`. An asset cannot reach
`published` without a declared kind, licence, and tier. Retiring an asset does not
retire its spatial identity, which persists as the entity's position record.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: an entity with a spatial identity but no geometry | the described-not-depicted state renders, with position and neighbours available | FR-SPAT-002 |
| Invalid input: a malformed or non-manifold mesh | rejected at ingest with the geometric fault named | FR-SPAT-003 |
| Permission denied: a non-curator publishes an asset | rejected; the asset stays at `bound` | FR-SPAT-005 |
| Concurrency: two assets bound to one spatial identity as the same kind and level | the second is held; one identity has one canonical representation per kind and level, alternatives are explicit variants | FR-SPAT-009 |
| External dependency failure: an asset CDN or store is unreachable | the entity renders in its no-geometry state with the failure distinguished from genuine absence | FR-SPAT-002 |
| Scale extreme: a whole-body scene with all L3 meshes on mid-range hardware | LOD and culling hold the frame budget in PRD_Non_Functional_Requirements; detail degrades before frame rate does, and the degradation is not silent | FR-SPAT-009 |
| A T1 asset is referenced by a T0 export | export fails with the tier violation named, rather than shipping an obligation the recipient does not know about | FR-SPAT-005 |
| Two structures overlap geometrically because both are reference exemplars from different sources | the overlap is recorded as a known artifact of exemplar composition, not silently resolved by moving one | FR-SPAT-004 |

## Dependencies
- On other modules: PRD_FR_Ontology (entities), PRD_FR_Scale_Bridging
  (admissible representations per level), PRD_FR_Evidence (asset provenance and
  licence), PRD_FR_Validation (INV-11), PRD_FR_Versioning (asset packaging)
- On external integrations: BodyParts3D, Z-Anatomy (T1); any future imaging
  sources

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Geometry assets bound through a spatial identity | G-01 | 100%, enforced |
| Assets declaring representation kind and licence tier | G-03 | 100% |
| Declared L0–L3 entities with a spatial identity | G-01 | Phase 1: 90% of declared scope |
| T1 content appearing in T0 layers | G-05 | 0, enforced |

## Out of Scope for This Module
- The viewer, camera, and interaction (PRD_FR_Navigation, TECH_UI_UX_Design)
- Authoring or sculpting geometry
- Patient-specific mesh deformation (Phase 7; the binding layer must not block it)
- Physical simulation of deformation

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| Which coordinate frame convention is canonical, and how are imaging-derived frames reconciled to it? | Research Engineer | Phase 1 |
| How is exemplar-composition overlap displayed without implying anatomical error? | Model Reviewer | Phase 1 |
| Does a permissive-only build have enough coverage to be worth shipping? | Licence owner | Phase 1 |
