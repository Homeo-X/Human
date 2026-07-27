---
doc: PRD_Decision_Log
tier: light+
version: 1.0.0
status: draft
owner: orchestrator
last_updated: 2026-07-26
---

# Decision Log

_Append-only. Chronological — new entries go at the END (true append). Never edit
past entries — supersede them. Scoping, contested trade-offs, resolution-loop
outcomes, scope reopenings, review findings, and reality-driven spec changes all
get entries._

## Entry schema
### D-NNN — short title (date, role)
- **Status:** active | superseded-by D-XXX
- **Context:** what forced a choice, in 1–3 sentences
- **Decision:** what was chosen
- **Alternatives:** each with rejected_because
- **Consequences:** benefits and costs, both stated
- **Reversibility:** high | medium | low, with the undo path if not low
- **Valid while:** the conditions under which this holds, or "unconditional"
- **Affects:** files and IDs this binds
- **Supersedes:** D-XXX or none

---

### D-001 — Profile, tier, and module scoping (2026-07-26, orchestrator)
- **Status:** active
- **Context:** The brief asks for a computational model of the human organism
  spanning eleven biological levels, plus a 3D surface, a retrieval surface, an
  agent architecture, and a future personalization layer. No shipped framework
  profile has a home for scale contracts, evidence grading, or biological
  invariants, and the brief explicitly asks whether a new profile is warranted.
- **Decision:** New **bio** profile, built to the PROFILES.md profile contract in
  full — README spec, core docs, Light doc, failure-mode rubric with a
  disposition artifact, validator registration, and a specialization lens.
  **Full** tier. Fifteen FR modules with the AREA codes registered in MANIFEST.
  The brief's `FR-3D` AREA is renamed `FR-SPAT` because AGENTS.md §6 admits only
  letters in an AREA code; `FR-CELL` is absorbed into SCAL and `FR-AI` into RETR
  and AGD.
- **Alternatives:**
  - Product profile with BIO files added ad hoc — rejected_because: the added
    documents would carry no registers, no rubric, and no validator coverage,
    leaving the project's most failure-prone content as the only unvalidated
    content in the set.
  - Research profile — rejected_because: its HYP to CM to EXP to DC chain
    presumes the project generates knowledge through experiments it designs.
    This project curates and grades knowledge others generated, and additionally
    ships a product surface the research set has no place for.
  - Standard tier — rejected_because: personal health data in Phase 7, external
    licence obligations on geometry, an agentic subsystem, and biological claims
    requiring expert sign-off are each independently a tier-up signal.
- **Consequences:** + The ways this class of project overclaims are checked
  mechanically rather than hoped against; the scale contract makes depth honest.
  − A new profile is real maintenance: 44 spec files, a rubric to keep current,
  and framework deltas to re-apply on every upstream update (UPSTREAM.md).
- **Reversibility:** medium — the bio documents could be demoted to plain product
  extras by deleting `templates/bio/` and reverting the two validator deltas, at
  the cost of the checks that make the set trustworthy.
- **Valid while:** the project's primary deliverable remains a knowledge
  substrate rather than a visualization product.
- **Affects:** MANIFEST.md, PRD_FR_Overview, PRD_FR_Ontology, PRD_FR_Spatial_Representation, BIO_Scale_Contract
- **Also binds (outside docs/):** `PROFILES.md`, `AGENTS.md` §2 and §6,
  `templates/bio/`, `tools/specgraph.py`, `tools/validate.sh` — recorded in
  UPSTREAM.md as deltas D1–D5
- **Supersedes:** none

### D-002 — External ontologies are referenced, not forked (2026-07-26, architect)
- **Status:** active
- **Context:** Anatomical, cell-type, and molecular identity are already
  maintained by community ontologies. The project must decide whether to adopt
  their identifiers, copy their content, or mint its own.
- **Decision:** External terms are the **primary cross-reference** and are cited,
  never copied wholesale. A local identifier (`HOX:<class>:<slug>`) is minted
  only where no suitable external term exists, and is flagged as minted so the
  gap stays visible and re-checkable. Authorities are pinned per level and per
  version in BIO_Research_Charter; upstream deprecations, merges, and splits have
  a stated handling rule in BIO_Anatomical_Ontology.
- **Alternatives:**
  - Fork the ontologies into the repository — rejected_because: forks diverge
    silently, and a stale fork of a live ontology is a source of wrong biology
    that looks authoritative.
  - Mint all identifiers locally with mappings — rejected_because: it makes the
    project the authority on questions it is not qualified to settle, and breaks
    interoperability with the datasets we most want to ingest.
- **Consequences:** + Interoperability, upstream corrections flow in, and the
  minted-term count becomes a visible measure of where the project is on its own.
  − A hard dependency on external availability and versioning; upstream churn
  becomes maintenance work (RSK-03).
- **Reversibility:** low — identifiers propagate into every downstream artifact,
  including published releases and any third-party consumer.
- **Valid while:** the referenced ontologies remain maintained and openly licensed.
- **Affects:** PRD_FR_Ontology, BIO_Anatomical_Ontology, BIO_Cell_and_Molecular_Model, PRD_External_Integrations, TECH_Data_Design
- **Supersedes:** none

### D-003 — Share-alike geometry is admitted but quarantined (2026-07-26, architect)
- **Status:** active
- **Context:** The richest open anatomical geometry (BodyParts3D, Z-Anatomy) is
  CC-BY-SA. Share-alike obligations can propagate to derivative works, which
  would bind the whole model if the assets were mixed freely into it.
- **Decision:** Share-alike sources are admitted, but held in a **segregated
  asset tier** with per-asset licence metadata, and the ontology and evidence
  layers never embed share-alike content. A build selects an asset tier, so a
  permissive-only or commercially licensed build is a configuration change rather
  than a re-derivation. Every asset carries its licence, attribution string, and
  downstream constraint.
- **Alternatives:**
  - Permissive-only sources — rejected_because: it materially shrinks day-one
    anatomical coverage, and coverage is KPI G-01.
  - Mix freely and resolve licensing later — rejected_because: share-alike
    obligations attach at the moment of derivation, so "later" means re-deriving.
- **Consequences:** + Downstream relicensing stays possible and the obligation is
  always locatable. − Real engineering cost in the asset pipeline, and a build
  matrix that must be tested per tier.
- **Reversibility:** medium — quarantine can be relaxed cheaply; un-mixing after
  the fact cannot.
- **Valid while:** any consumer of this model may need terms other than share-alike.
- **Affects:** PRD_FR_Spatial_Representation, PRD_FR_Evidence, PRD_External_Integrations, TECH_System_Architecture, RSK-05
- **Supersedes:** none

### D-004 — Personalization is an overlay; the reference is immutable (2026-07-26, pm)
- **Status:** active
- **Context:** The brief requires that individual data never corrupt the canonical
  model. Immutability can be a convention, a review rule, or an enforced
  property, and the three differ entirely under pressure.
- **Decision:** The reference model is **immutable by construction**: individual
  data lives only in overlays, applied at read time, and there is no write path
  from an overlay to a reference entity. The property is enforced by INV-08 and
  the `biocheck` harness, not by reviewer diligence. Overlay operations are
  enumerated in BIO_Personalization_Model; changing a canonical biological fact
  is not among them at any privilege level.
- **Alternatives:**
  - Copy-on-write personalized forks — rejected_because: forks drift from the
    reference, and there is then no single answer to "what does the model say?".
  - Write-through with audit — rejected_because: an audit records corruption, it
    does not prevent it.
- **Consequences:** + The reference model has exactly one state, and a
  personalized view can always be reduced to reference plus a delta.
  − Every read path carries overlay-resolution cost, and propagation rules must
  be specified explicitly rather than emerging.
- **Reversibility:** low — every consumer, API, and stored overlay assumes this shape.
- **Valid while:** unconditional.
- **Affects:** BIO_Personalization_Model, PRD_FR_Personalization, TECH_Data_Design, TECH_API_Specification
- **Supersedes:** none

### D-005 — No global simulation clock (2026-07-26, architect)
- **Status:** active
- **Context:** Represented processes span roughly fifteen orders of magnitude in
  time, from ion-channel gating to tissue remodelling. A single integrator would
  either be intractably fine-grained or silently wrong at one end.
- **Decision:** Processes declare their own **timescale domain**; the runtime
  composes domains explicitly through stated coupling rules rather than a shared
  tick. A process without a declared timescale cannot be executed, and BRB-19
  treats a single global clock as a rubric failure.
- **Alternatives:**
  - One fixed-step global clock — rejected_because: it forces every process to
    the finest step in the system, which is computationally impossible at this
    span, and produces false coupling between processes that do not interact.
  - Adaptive single clock — rejected_because: adaptivity hides the coupling
    question rather than answering it, and the coupling question is the
    scientific content.
- **Consequences:** + Each process is correct in its own domain and its coupling
  is explicit and reviewable. − Cross-domain composition becomes a first-class
  design problem with no default answer, and some couplings will be declared
  unsupported rather than approximated.
- **Reversibility:** medium — the runtime could adopt a global clock later, but
  every existing process specification would need re-derivation.
- **Valid while:** the represented span exceeds roughly six orders of magnitude in time.
- **Affects:** PRD_FR_Simulation, PRD_FR_Process_Models, BIO_Physiological_Processes, TECH_System_Architecture
- **Supersedes:** none

### D-006 — The navigation tree is a view; the graph is the model (2026-07-26, orchestrator)
- **Status:** active
- **Context:** The seed corpus (D-007) is organized as a strict tree of 157
  nodes, which is excellent for navigation and wrong as biology. The pancreas is
  the standing counterexample: it is materially part of both the digestive and
  the endocrine system, produces both digestive enzymes and insulin, responds to
  blood glucose, and affects glucose uptake. A tree can express exactly one of
  those facts.
- **Decision:** Two structures over one entity set. The **graph is canonical**:
  typed, multi-parent where biology is multi-parent, carrying spatial,
  functional, causal, regulatory, temporal, developmental, and evidential
  relations. The **navigation tree is a derived view** — a chosen spanning
  presentation computed from the graph for orientation, never the source of
  truth, and explicitly labelled as a view wherever a user could mistake it for
  structure. `part_of` remains single-parent (INV-02) because containment is
  genuinely single-parent; every other participation is a separate typed relation
  (`member_of`, `produces`, `responds_to`, `affects`), so multi-system membership
  is expressible without corrupting containment.
- **Alternatives:**
  - Tree as canonical with cross-links as annotations — rejected_because: it
    makes the majority of biological relationships second-class, and the
    pancreas's endocrine role would be a footnote on a digestive organ.
  - Graph only, no tree — rejected_because: the seed demonstrates that a tree is
    how people actually navigate this material; discarding it loses real
    usability for no modelling gain.
- **Consequences:** + Biology is representable as it is, and navigation stays
  simple. − Two structures must be kept coherent; a tree view can imply a
  primacy the graph does not assert, which is a UX obligation (TECH_UI_UX_Design)
  and a rubric check (BRB-30).
- **Reversibility:** low — every consumer, query, and surface assumes this split.
- **Valid while:** unconditional.
- **Affects:** PRD_FR_Relationship_Graph, PRD_FR_Ontology, PRD_FR_Navigation, BIO_Anatomical_Ontology, TECH_Data_Design
- **Supersedes:** none

### D-007 — Seed corpus adopted, with a compilation ladder (2026-07-26, pm)
- **Status:** active
- **Context:** A curated corpus arrived — "A Map of the Human Body": 157 nodes
  across 20 branches, each with a definition, three to four core statements, and
  a textbook reading list, plus 31 prose cross-links and a node typology
  (`foundation`, `branch`, `subbranch`, `resolved`, `frontier`). It is
  semantically rich and structurally narrative. Ingesting it naively would fill
  the model with prose wearing a schema.
- **Decision:** Adopt the corpus as a **seed**, ingested at an explicit
  `compilation_status` that is visible everywhere the content is:
  `narrative` (prose as received, machine-readable but not machine-usable) →
  `structured` (entity, class, level, relations typed) → `mechanistic` (inputs,
  outputs, state variables, participants, timescale) → `parameterized`
  (quantities with sources and conditions). Nothing is promoted by reformatting;
  promotion requires the typing work to actually be done and reviewed. The 31
  cross-links enter as `associated_with` with their prose retained as the
  justification — **never as `causes` or as a mechanism** — because the corpus
  states that a relationship exists, not what type it is. The `frontier` nodes
  map to EVC-6 or EVC-8 and are kept, not dropped: they are the corpus's record
  of what medicine has not settled, and discarding them would be exactly the
  manufactured confidence this project exists to avoid.
- **Alternatives:**
  - Ingest as authoritative typed content — rejected_because: it would assert
    relation types nobody chose and evidence grades nobody assigned, which is the
    single fastest way to make the model confidently wrong.
  - Use as reference reading only, ingest nothing — rejected_because: 157 sourced
    definitions and 31 identified real relationships are a genuine head start,
    and refusing them would cost months to re-derive.
- **Consequences:** + A large, coherent, sourced starting corpus, with its
  narrative-ness visible rather than laundered. − `compilation_status` must be
  carried through every surface and API, and the gap between "we have 157
  entities" and "we have 157 modelled entities" must be reported honestly in
  G-01, which means early coverage numbers will look worse than a competitor
  willing to lie about them.
- **Reversibility:** high — seed content is isolable by its provenance and could
  be removed wholesale.
- **Valid while:** the corpus remains a seed rather than the model's substance;
  once entities are `mechanistic`, provenance is per claim, not per corpus.
- **Affects:** PRD_FR_Ontology, PRD_FR_Evidence, PRD_FR_Relationship_Graph, BIO_Evidence_and_Provenance, BIO_Anatomical_Ontology
- **Supersedes:** none

### D-008 — Geometry is bound through a spatial-identity layer (2026-07-26, architect)
- **Status:** active
- **Context:** The conventional anatomy-app construction is a mesh with a
  paragraph attached to it. That inverts the dependency this project needs: it
  makes the artwork the identity, so a structure exists because someone modelled
  it, and its description is decoration.
- **Decision:** Three layers, in this order: **biological entity → spatial
  identity → geometric representation**. The spatial identity is its own record —
  coordinate frame, anatomical position, containment and adjacency, laterality,
  landmarks — and it exists for entities that have no mesh at all. Geometry
  attaches to a spatial identity, never directly to an entity, and one spatial
  identity may carry several representations (organ mesh, tissue region,
  schematic) at different levels and licence tiers. An entity with no geometry is
  fully valid and fully navigable; unbound geometry is not admissible.
- **Alternatives:**
  - Mesh-first with entity metadata — rejected_because: it makes visual coverage
    determine biological coverage, and makes the licence tier of an asset
    infectious to the ontology (D-003).
  - Entity directly to mesh — rejected_because: it cannot express one structure
    represented differently at different levels, which is the whole point of
    semantic zoom.
- **Consequences:** + Geometry becomes swappable and licence-separable, the model
  is navigable before any art exists, and multi-level representation is natural.
  − One more indirection in every spatial query, and a spatial identity with no
  geometry needs a designed surface rather than an empty viewport.
- **Reversibility:** medium — the layer could be collapsed, at the cost of D-003's
  separability.
- **Valid while:** unconditional while geometry comes from mixed-licence sources.
- **Affects:** PRD_FR_Spatial_Representation, PRD_FR_Navigation, TECH_Data_Design, TECH_System_Architecture
- **Supersedes:** none

### D-009 — UX pass A punch list dispositioned (2026-07-26, orchestrator)
- **Status:** active
- **Context:** The Model Reviewer's BIO_RUBRIC pass raised three flags against the
  PM's output — BRB-09 (declared depth with no content is invisible in the
  product), BRB-16 (no gate catches an apt-looking but inapt citation), and
  BRB-25 (an out-of-range personalized comparison implies clinical significance
  no disclaimer removes).
- **Decision:** All three accepted, none contested. PUNCH-01: FR-SCAL-010 raised
  from Could to Must and added to the Phase 1 exit criteria, so the Coverage
  surface shows declared-versus-populated per level from Phase 1. PUNCH-02: a
  sampled source-aptness review gate added to BIO_Validation_Framework — at least
  5% of admitted claims per release, minimum 20, reviewed by someone other than
  the admitting reviewer, with a failure rate above 5% blocking the release.
  PUNCH-03 carried to UX pass B as a required design decision rather than closed
  on paper, because it is a design obligation on a Phase 7 surface.
- **Alternatives:**
  - Contest PUNCH-01 as already covered by G-01 — rejected_because: a metric
    computed at release does not tell a user browsing an empty declared level
    that the level was declared. The gap is in the product, not the reporting.
  - Close PUNCH-03 with stronger disclaimer wording — rejected_because: BRB-25's
    whole point is that disclaimer text does not neutralize a visual signal, and
    accepting wording as the fix would be the failure the rubric describes.
- **Consequences:** + The three most likely ways this spec would have misled
  someone are now structural rather than aspirational. − PUNCH-02 adds real
  recurring review cost per release, which lands on the capacity that RSK-02
  already identifies as the binding constraint.
- **Reversibility:** high — all three are additive specification changes.
- **Valid while:** unconditional.
- **Affects:** PRD_FR_Scale_Bridging, PRD_Scope_and_Roadmap, BIO_Validation_Framework, TECH_UI_UX_Design, BIO_Model_Review
- **Supersedes:** none

### D-010 — Red-team dispositions applied (2026-07-26, orchestrator)
- **Status:** active
- **Context:** The adversarial pass produced thirteen challenges
  (CHALLENGE_REGISTER.md), two rated S1. Eight were accepted, four acknowledged
  as residual risk, one refuted with evidence. The accepted ones are applied here
  as a single entry because they are one review round, not eight decisions.
- **Decision:**
  - **CH-01** — educator validation moves from a Phase 1 *milestone* to a Phase 1
    **entry gate**. Build does not begin until RSK-01 resolves. The prior
    arrangement scheduled the validation alongside the work it would invalidate.
  - **CH-03** — a Scope Reopen that narrows a declared depth must state the
    coverage delta it produces, and coverage is reported against both the current
    and the original scoping denominator whenever they differ.
  - **CH-04** — Phase 3 coverage targets are stated as conditional on review
    capacity, with BR-023's precedence over throughput made explicit in the
    roadmap rather than resolved silently.
  - **CH-05** — the `population` field's discriminating power is a promotion
    requirement: `narrative → structured` requires a population more specific
    than the source's default. The seed ingest's blanket "adult, unspecified in
    source" is recorded as a known limitation on the seed manifest.
  - **CH-07** — a manifest-to-artifact correspondence check is required before a
    release leaves `validated`; publication is atomic across graph, claims, and
    asset bundles, or it does not occur.
  - **CH-10** — G-03 reports asked-for UNKNOWNs separately from unprompted ones,
    so the count cannot be inflated to look scrupulous.
  - **CH-11** — the source-aptness sample is phase-dependent: a fixed minimum now,
    a statistically-sized sample later, with the size stated per release.
  - **CH-13** — a mixed-compilation-status check is added: a `mechanistic`
    relationship or process may not depend on a `narrative` endpoint.
- **Alternatives:**
  - Refute CH-01 on the grounds that RSK-01 is already registered —
    rejected_because: registering a risk is not gating on it, and the register
    was the evidence the red team used against us.
  - Defer CH-05 as a data-quality issue — rejected_because: the field exists
    specifically to distinguish genuine conflicts from population differences,
    and at 94% constant it cannot do that job.
- **Consequences:** + The two ways this spec could have looked rigorous while
  being hollow — an unvalidated premise and a decorative population field — are
  now structural. − Phase 1 cannot start on schedule if educator validation is
  slow, and that is the intended effect.
- **Reversibility:** high — all are specification changes.
- **Valid while:** unconditional.
- **Affects:** PRD_Scope_and_Roadmap, PRD_Risks_and_Constraints, PRD_FR_Evidence, PRD_FR_Versioning, PRD_FR_Ontology, BIO_Validation_Framework, CHALLENGE_REGISTER.md
- **Supersedes:** none

### D-011 — Implementation proceeds on RSK-01-independent infrastructure (2026-07-26, orchestrator)
- **Status:** active
- **Context:** D-010 made educator validation a Phase 1 **entry gate**: build does
  not begin until RSK-01 resolves. Implementation was then requested before that
  validation exists. Stepping over the gate silently would make it decorative —
  which is exactly the failure CH-01 identified.
- **Decision:** Split the gate by what RSK-01 actually threatens. RSK-01 asks
  whether *users want evidence grading surfaced to them*. It therefore governs
  the **presentation** layer — the 3D viewer, the study surfaces, and the
  content-population effort that fills them. It does not govern the substrate
  services, which are required under either answer: a model that abandoned
  evidence grading in its UI would still need entity resolution, typed traversal,
  scale contracts, release immutability, and a query surface.
  Accordingly, implementation proceeds now on: substrate loading, the graph and
  its derived navigation view, scale services, evidence retrieval, search, the
  groundedness guard, the release pipeline, and the read API. **Still gated:** the
  3D viewer, the study UI, and L0–L3 content population.
- **Alternatives:**
  - Build everything including the viewer — rejected_because: it spends the most
    expensive effort on the part RSK-01 could invalidate, and makes the gate a
    formality.
  - Build nothing until validation — rejected_because: the substrate services are
    needed under both outcomes, so blocking them buys no information.
- **Consequences:** + Work proceeds on what is unconditionally needed, and the
  gate keeps its meaning for the part it actually protects. − If educators reject
  evidence grading outright, some API surface (per-assertion classes, the evidence
  panel endpoints) becomes lower-value than built — an accepted, bounded loss.
- **Reversibility:** high.
- **Valid while:** RSK-01 is unresolved. On resolution this decision is superseded
  by one that either opens the presentation gate or re-scopes the product.
- **Affects:** PRD_Scope_and_Roadmap, TECH_System_Architecture, TECH_API_Specification
- **Supersedes:** none

### D-012 — A causal retype may not inherit an association's provenance (2026-07-26, architect)
- **Status:** active
- **Context:** Implementing FR-REL-007 surfaced a gap the specification did not
  close. An untyped `associated_with` edge carries a provenance claim, and the
  retyping check originally consulted that claim's evidence class when gating a
  promotion to `causes`. In the seeded substrate that claim is EVC-1 — strong —
  so the gate passed. But the claim was recorded for a different assertion
  entirely; its strength is evidence about that assertion, not about whether
  causation holds between the endpoints.
- **Decision:** Retyping an association to `causes` or `contributes_to` requires
  a claim **independent of** the one backing the untyped edge, identified by
  claim id rather than by a citation string, and for `causes` graded EVC-2 or
  better. This is FR-REL-008's principle — edges do not inherit their endpoints'
  evidence — applied one level further: a retyped edge does not inherit the
  evidence of its untyped predecessor either.
- **Alternatives:**
  - Keep consulting the existing provenance claim — rejected_because: it lets a
    strong claim about one thing license a causal assertion about another, which
    is the exact laundering the evidence ladder exists to prevent.
  - Accept any non-empty source string — rejected_because: a citation string is
    not a claim and cannot be graded, so the EVC-2 gate would be unenforceable.
- **Consequences:** + The causal gate now actually gates; the 26 seed
  associations cannot be upgraded to causation without new sourcing. − Retyping
  is more expensive, and a curator must create the supporting claim first.
- **Reversibility:** high — a check, not a data shape.
- **Valid while:** unconditional.
- **Affects:** PRD_FR_Relationship_Graph, PRD_FR_Evidence
- **Supersedes:** none
