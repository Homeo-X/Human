---
doc: PRD_External_Integrations
tier: standard+
version: 1.0.0
status: draft
owner: architect
last_updated: 2026-07-26
---

# External Integrations

_One row per third-party system this product depends on. This product's
integration profile is unusual: its critical dependencies are **vocabularies and
datasets**, not services, and the failure mode that matters is upstream change
rather than downtime._

## Integration Register
| System | Category | Purpose | Direction | Criticality | Failure Behavior |
|---|---|---|---|---|---|
| UBERON | domain ontology | primary anatomical identity, L1–L5 | in | **critical** | pinned per release, so runtime unavailability affects ingest only, never reads |
| Foundational Model of Anatomy (FMA) | domain ontology | detailed anatomy where UBERON is coarse | in | high | as above |
| Cell Ontology (CL) | domain ontology | cell-type identity, L6–L7 | in | high (Phase 4+) | as above |
| Gene Ontology (GO) | domain ontology | molecular function, L9 | in | medium | as above |
| ChEBI | domain database | chemical entities, ions, metabolites | in | medium | as above |
| HGNC / UniProt | domain database | gene and protein identity | in | medium | as above |
| UCUM | standard | unit vocabulary | in | **critical** | vendored; a unit vocabulary that changes under you is worse than one that is frozen |
| Terminologia Anatomica | nomenclature | preferred anatomical terms | in | high | terms used, work not reproduced (T2) |
| DOI / PMID resolvers | identifier service | source verification | in/out | medium | verification failure holds a claim pending; never admits unverified |
| BodyParts3D | geometry dataset | anatomical meshes | in | medium | **T1 share-alike, quarantined** (D-003) |
| Z-Anatomy | geometry dataset | anatomical meshes | in | medium | **T1 share-alike, quarantined** (D-003) |
| Language model provider | AI service | phrasing over retrieved claims | in/out | medium | degrade to structured search with the degradation stated (NFR-012); never a cached answer presented as fresh |
| Identity provider | identity/SSO | curator and operator authentication | in/out | high for curation, none for reading | curation unavailable; the public read surface is unaffected because readers do not authenticate |
| Artifact hosting | infrastructure | release and asset distribution | out | high | releases are content-addressed and mirrorable |
| Wearable / health-record integrations | health data | individual values (Phase 7) | in | low | reject at boundary on malformed data; never partial admission |

Categories from the template that do not apply: payments and billing (no money
movement), communications (notifications excluded at scoping — MANIFEST), and
analytics vendors (KPI instrumentation is internal, per the cross-cutting table).

## Per-Integration Notes

### Ontology authorities (UBERON, FMA, CL, GO, ChEBI, HGNC, UniProt)
- **Auth and credentials:** none; all are openly accessible.
- **Rate limits:** applied at ingest only, with backoff. Reads never hit them —
  terms are pinned into each release.
- **Data exchanged:** term identifiers, labels, synonyms, hierarchy. No PII.
- **Sandbox story:** pinned snapshots serve as fixtures; CI never reaches the
  network.
- **Vendor lock-in / exit path:** identifiers propagate everywhere, so this is the
  project's deepest dependency and the least reversible decision (D-002,
  reversibility: low). The exit path is not clean: replacing an authority means
  re-identifying every entity that used it, retiring the old ids to tombstones,
  and re-reviewing every affected claim. This is stated plainly rather than
  softened — RSK-03 tracks it.
- **The real failure mode is upstream change, not downtime:** deprecations,
  merges, and splits. Handled per BIO_Anatomical_Ontology §Identity — splits block
  promotion, merges flag dependent claims, and nothing rewrites silently.

### Geometry datasets (BodyParts3D, Z-Anatomy)
- **Auth:** none.
- **Data exchanged:** meshes and their metadata.
- **Licence:** CC-BY-SA. Attribution plus share-alike, which is the entire reason
  for the T1 tier.
- **Exit path:** genuinely clean, and deliberately so — assets bind through
  spatial identities (D-008), so replacing a geometry source touches no ontology
  content. This is the payoff for the extra indirection.
- **Constraint:** never embedded in T0 records, only referenced by id
  (INV-11).

### Language model provider
- **Auth:** API key in a managed secret store, never in agent run records.
- **Rate limits and cost:** per NFR-024; exceeding degrades rather than truncates.
- **Data exchanged:** the user's question and retrieved claims. **No individual
  data is ever sent** (NFR-031), which in Phase 7 means personalized retrieval is
  constrained by what can be answered without transmitting overlay values — a
  limitation recorded now rather than discovered then.
- **Vendor lock-in:** low by design. The model is a phrasing engine over
  retrieved claims, never a source of biology (FR-RETR-001), so substituting
  providers changes fluency, not correctness.
- **Sandbox story:** a recorded-response fixture set for CI; EV suites run
  against the live provider per release.

### Health integrations (Phase 7)
- **Auth:** per-integration OAuth, individually revocable by the individual.
- **Data exchanged:** health data — the most sensitive class the system holds.
- **Constraint:** every value must arrive with, or be rejected for lack of, the
  six mandatory provenance fields (INV-09). An integration that cannot supply
  measurement method is not integrated, however convenient its data would be.

## Webhooks & Callbacks Inbound
| Source | Event | Endpoint | Idempotency Strategy |
|---|---|---|---|
| Ontology release feeds | new authority version available | `/ingest/authority-notice` | notice by authority + version; re-delivery is a no-op. Raises a curation task; never auto-updates a pin |
| Health integrations (Phase 7) | new measurement available | `/overlay/measurement` | idempotency key per source measurement id; duplicate delivery never creates a second OverlayValue |

There are no outbound webhooks. The product publishes releases as artifacts, not
events, because a citable release is more useful to this audience than a push
notification.
