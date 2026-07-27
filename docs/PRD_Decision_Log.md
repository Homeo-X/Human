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

### D-013 — Evaluation round: the ladder becomes the single source of truth (2026-07-26, orchestrator)
- **Status:** active
- **Context:** An adversarial self-evaluation of the delivered Phase 0 work found
  five defects, four of them in content and documentation that every validator
  had passed green. The common shape: **the prose was stricter than the
  enforcement.** Specifically — `biocheck`'s class table admitted
  `reference textbook` for EVC-1 while the ladder forbade it, so two claims sat
  at VERIFIED on Gray's Anatomy and Guyton & Hall; 135 seed claims sat at EVC-2
  on a single citation against a stated requirement for independent agreement;
  `cross_scale_path` reported `complete: true` for a chain that skipped L1; and
  the README and MANIFEST described the vertical slice as "one complete L0→L10
  path" when no L1 entity exists anywhere in the substrate. BRB-11 and BRB-05,
  the two rubric items written to catch exactly these, had both been
  dispositioned `pass`.
- **Decision:**
  - The EVC ladder table in BIO_Evidence_and_Provenance gains machine-readable
    `Admissible Source Types` and `Min Independent Sources` columns, and becomes
    **the single authority**. `tools/biocheck.py` derives its rules from that
    table; `src/homeo/evidence.py` derives from `biocheck`. One derivation chain,
    not three copies.
  - **INV-16** (blocking): when the checker's fallback table and the document
    disagree, that divergence is itself an error, reported before any other
    check. Exercised by a negative test like every other invariant.
  - Claims regraded to the ladder as written: two textbook-sourced EVC-1 → EVC-2;
    one single-source EVC-2 → EVC-3; 135 seed EVC-2 → EVC-4. Seed claims are
    reassigned from `human:reviewer-seed-01` to `agent:seed-ingest`, because no
    human reviewed them and recording one was a fiction. **The substrate now
    contains no EVC-1 claims at all**, which is the honest state of a model no
    domain reviewer has examined.
  - `cross_scale_path` distinguishes `path_found` from `level_contiguous` and
    reports `missing_levels`; a path that skips a level is found, not complete.
  - The README and MANIFEST state the slice's real shape: L1 empty, containment
    L0→L8, L9–L10 attached by participation.
  - BRB-11 and BRB-05 re-dispositioned from `pass` to `flag` with a reviewer note
    on *why* they were wrongly passed: both were dispositioned by citing a
    requirement rather than by testing the artifact against it.
- **Alternatives:**
  - Relax the ladder to match the checker (permit textbook-sourced EVC-1) —
    rejected_because: it would resolve the contradiction by lowering the standard
    the project exists to hold, and EVC-1's whole meaning is that it is hard to
    reach.
  - Keep three synchronized copies of the class table with a comparison test —
    rejected_because: synchronization is the failure mode. Derivation removes the
    possibility rather than detecting the symptom.
  - Fix the claims and leave the checker — rejected_because: it fixes the
    instances and leaves the mechanism that produced them.
- **Consequences:** + The rule is enforced where it is written, and a future
  divergence fails the build. The substrate's evidence state is now honest about
  having had no review. − Every strong-class claim in the project disappeared,
  which makes the model look weaker; that appearance is accurate. Regrading is
  also a breaking content change for anyone who pinned the prior release.
- **Reversibility:** high for the code; the regrades are content decisions that
  would need re-review to undo.
- **Valid while:** unconditional.
- **Affects:** BIO_Evidence_and_Provenance, BIO_Validation_Framework, BIO_Model_Review, PRD_FR_Evidence, PRD_FR_Scale_Bridging, MANIFEST.md
- **Supersedes:** none

### D-014 — Scope Reopen: whole-organism declared to L1 (2026-07-26, orchestrator)
- **Status:** active
- **Context:** D-013 recorded that L1 was empty across the entire substrate,
  which is why the cardiovascular slice is not level-contiguous — the
  containment chain jumps L0 to L2. Adding the nine Terminologia Anatomica
  regional divisions requires L1 content, and `whole-organism` was declared to
  L0. The invariant refused the write, correctly: correct content beyond a
  declaration is still out of contract (BR-005).
- **Decision:** Scope Reopen under AGENTS.md §9 clause 2 — `whole-organism`
  deepens from L0 to L1. This is a **widening**, so FR-VER-013's dual-denominator
  rule does not apply; the change adds declared levels rather than removing them,
  and coverage against the new denominator is reported normally. Regions are
  placed in `whole-organism` rather than given their own subsystem because they
  partition the organism itself and belong to no organ system — which is the
  same reason SCL-01 records that they locate rather than function.
- **Alternatives:**
  - Add a separate `regional` subsystem — rejected_because: a subsystem is a
    functional grouping in this model, and regions are explicitly not functional.
    Inventing one to hold them would put a spatial convenience in a functional
    register.
  - Leave L1 empty and accept the non-contiguous slice — rejected_because: the
    gap is real and cheap to close, and leaving it while the README described the
    slice as complete is what produced the D-013 overclaim.
- **Consequences:** + The cardiovascular containment chain becomes contiguous
  from L0 to L8, so `cross_scale_path` reports it complete on its own merits
  rather than by a relaxed check. − One more declared level with content to
  maintain, and the regions carry a boundary problem that is genuinely unsettled:
  several of these planes are placed differently by different authors, which
  every region's claim states rather than resolving.
- **Reversibility:** medium — narrowing back would require retiring nine
  entities with tombstones and would trigger FR-VER-013's dual reporting.
- **Valid while:** unconditional.
- **Affects:** BIO_Scale_Contract, MANIFEST.md, PRD_FR_Scale_Bridging
- **Supersedes:** none

### D-015 — The view is a projection of the graph, not the other way round (2026-07-27, architect)
- **Status:** active
- **Context:** FR-NAV-001 and FR-NAV-006 were the last two unbuilt Must
  requirements outside the Phase 6/7 modules, and both are navigation-state
  concerns rather than rendering concerns. Building them forced the question the
  brief raised at the start: is geometry an attribute of an entity, or is the
  entity a label attached to a mesh? Every anatomy product of the usual kind
  answers the second way — a mesh is authored, a paragraph is attached, and
  anything nobody has modelled does not exist.
- **Decision:** A renderer never queries the substrate. `ProjectionService`
  computes a **view specification** from a `ViewState` — the in-view entity set
  at the requested ontological resolution, each entity's spatial identity,
  depiction status, evidence summary, the relations among the in-view set, and
  the lineage — and a viewer consumes only that. Depiction is a four-valued
  attribute (`depicted` / `described` / `asset_unavailable` / `unplaced`), so an
  entity with no mesh is present, positioned, and navigable, and a failed asset
  is distinguishable from anatomy that was never modelled.
  Correspondingly, semantic zoom and physical zoom are separate operations on
  separate fields of an immutable `ViewState`: `magnify` cannot reach `level`
  and `set_level` does not touch magnification. The API exposes them as
  different endpoints that refuse an unqualified "zoom".
- **Alternatives:**
  - Let the viewer query the graph directly and decide visibility —
    rejected_because: visibility rules would then live in the renderer, where
    they are untestable without a renderer and would diverge per surface.
  - One zoom operation with a mode flag — rejected_because: a flag defaults, and
    a default is how the two collapse back into one. Two endpoints cannot.
  - Represent missing geometry as absence — rejected_because: it makes the model
    look thin exactly where the asset pipeline, not the biology, is incomplete.
- **Consequences:** + The navigation model is fully testable with no viewer in
  existence, which is what allows it to be built while D-011 keeps the viewer
  gated; a future renderer inherits the honesty rules rather than reimplementing
  them. − A view specification is more verbose than a mesh list, and a renderer
  must handle four depiction states rather than one. − `magnification_limit` is
  currently a service-level constant; per-asset limits belong to Phase 1 and are
  not yet expressible.
- **Reversibility:** high — the projection is derived and disposable, like every
  other view in this system.
- **Affects:** PRD_FR_Navigation, PRD_FR_Spatial_Representation,
  TECH_UI_UX_Design, TECH_API_Specification
- **Supersedes:** none

### D-016 — Review findings on the navigation and projection layers (2026-07-27, orchestrator)
- **Status:** active
- **Context:** A review of the D-015 implementation, run immediately after it
  was pushed, found five defects. Two of them were the specific failure this
  project's rubric exists to catch — code that produces a plausible answer while
  ignoring the input it claims to honour — and both had passed a 50-test suite
  and a nine-mutation check, because every test exercised the paths the code got
  right.
- **Decision:** All five fixed, each with a regression test that varies the
  input the implementation had been ignoring:
  1. **The projection ignored the requested level.** It returned the focus and
     its containment children whatever level was asked for, so a view at L3 and
     a view at L7 were byte-identical while the docstring claimed "entities at
     the requested ontological resolution". `_at_level` now walks down to the
     requested level, up to the ancestor at it, or reports that nothing is
     represented there — the one case that must never be silently the wrong set.
  2. **`section` asserted a crossing it had never computed.** It returned every
     spatial identity under the key `crosses` for any plane string, including
     nonsense. Crossing needs geometry and no entity has any, so the method now
     returns `crossing_computed: false` with the candidate population named as
     such.
  3. **The magnification limit was bypassable by editing an address.** It was
     enforced in `magnify` and not in `restore`, so a hand-edited link produced
     unbounded magnification — on precisely the surface (a shared link) where
     the limit is a claim about the assets.
  4. **Levels outside the scale contract were accepted.** `l=99` and `l=-7`
     restored happily. An address outside L0–L10 is malformed input, not a
     model limit, so it raises rather than answering.
  5. **Layer values were not escaped.** `parse_qsl` percent-decoded a value
     before its comma-separated members were split, so an escaped comma inside
     a member decoded first and then split — turning one filter into two, in
     the direction of hiding more than the user asked to hide. Parsing no
     longer decodes before splitting.
- **Alternatives:**
  - Ship items 3–5 as known limitations — rejected_because: each is a few lines,
    and a stated limitation that could have been a fix is how a limitations
    section becomes a place to put defects.
  - Treat item 2 as acceptable until geometry exists — rejected_because: it is
    the exact shape of BRB-05, and it was written by the same process that
    dispositioned BRB-05 as a flag two days earlier.
- **Consequences:** + The level parameter now does what every surface reading
  this API will assume it does. + The address is treated as untrusted input
  rather than as a serialization of trusted state. − `_at_level` walks the
  containment tree per projection, which is linear in the subtree and will need
  an index when a subsystem carries thousands of entities at one level.
  − Sectioning is now visibly unimplemented rather than invisibly wrong, which
  is a worse-looking and more accurate state.
- **Reversibility:** high.
- **Affects:** PRD_FR_Navigation, PRD_FR_Spatial_Representation, MANIFEST.md
- **Supersedes:** none

### D-017 — Provisional admission, and eighteen fabricated reviews (2026-07-27, orchestrator)
- **Status:** active
- **Context:** D-013 recorded the seed corpus being attributed to a fabricated
  `human:reviewer-seed-01`, and corrected it. Three days later this project
  shipped nine cardiovascular claims attributed to `human:reviewer-cardio-01`
  and nine regional claims attributed to `human:anatomy-reviewer-01`. Neither
  reviewer exists. Twelve of the eighteen sat at EVC-2 — a class BR-002 forbids
  any automated actor from assigning, and which
  `BIO_Evidence_and_Provenance` §Pipeline says the canonical graph never admits
  unreviewed. The same defect was therefore committed twice, the second time by
  the process that wrote the rule against it, and it was found only because a
  request to grow the substrate to L3 breadth would have multiplied it by a
  hundred.
- **Decision:** Two changes, one corrective and one structural.
  **Corrective:** `tools/correct_attribution.py` re-attributes all eighteen
  claims to the agents that actually produced them (`agent:evidence`,
  `agent:anatomy`), sets `review_state: provisional`, and caps every EVC-1/EVC-2
  assignment at EVC-4 — retaining the agent's assessment in a new
  `proposed_class` field rather than discarding it. The audit is written to
  `ontology/ATTRIBUTION_CORRECTION.json`, listing every field changed and why.
  The regrade is not a claim that the biology is weaker: `CLM:heart-function-pump`
  cites Gray's and Guyton and the evidence really does support EVC-2. What was
  missing is a curator, not a source, so the twelve capped claims are now a
  *list* — the review backlog, per claim.
  **Structural:** a third admission state. `CurationService.admit_provisional`
  admits content nobody reviewed, refusing any `human:` actor (the one thing
  this path must never do is manufacture the review it substitutes for),
  refusing any class above EVC-3, refusing to downgrade anything already
  approved, and refusing to bypass a rejection. `Entity.review_state` and
  `Claim.review_state` default to `provisional`, so a record that says nothing
  about its review is treated as unreviewed. `accepted_payloads()` keeps its
  old meaning exactly; `provisional_payloads()` is separate. `INV-17` enforces
  all of it, with four negative tests.
- **Alternatives:**
  - Keep the EVC-2 classes and only fix the attribution — rejected_because: the
    pipeline document is explicit that unreviewed content is not admitted at
    those classes, and a rule enforced everywhere except on our own content is
    not a rule.
  - Drop the capped claims entirely — rejected_because: the evidence exists and
    the sources are real; deleting them would lose work and understate the
    model, which is the opposite failure and no more honest.
  - Let provisional content simply be `narrative` — rejected_because:
    compilation status and review status are orthogonal. A well-typed,
    structured entity nobody has reviewed is a real and common state, and
    collapsing the two axes would make one of them meaningless.
- **Consequences:** + The substrate now truthfully reports **zero reviewed
  entities, zero reviewed claims, zero EVC-1 and zero EVC-2**. + The review
  deficit is a published number rather than a risk-register sentence, which is
  the first time RSK-02 has been measurable. + Content can grow without
  fabricating reviewers. − Every downstream consumer must now distinguish
  populated from reviewed, and eight existing tests asserted the old values.
  − No causal relation can be typed in this release, because `causes` requires
  EVC-2 and nothing reaches it; that is a real capability loss and it is
  correct.
- **Reversibility:** low for the corrective half — the claims should never
  return to a fabricated attribution. High for the mechanism.
- **Affects:** ontology/cardiovascular/claims.json, ontology/regions/claims.json,
  src/homeo/curation.py, src/homeo/substrate.py, src/homeo/evidence.py,
  tools/biocheck.py, BIO_Validation_Framework, PRD_FR_Curation, PRD_FR_Evidence
- **Supersedes:** none — extends D-013 rather than replacing it

### D-018 — Coverage is measured against occupiable levels (2026-07-27, architect)
- **Status:** active
- **Context:** `coverage()` built one cell per level from L0 to a subsystem's
  declared depth, so every organ system was charged with L0 (the whole
  organism) and L1 (an anatomical region) — levels an organ system cannot
  occupy, because the organism and its regions belong to `whole-organism` by
  construction. Of the 42 unmet declarations the project published, **24 were
  structurally impossible to meet**. RSK-04 anticipates that honest coverage
  reporting makes the product look worse than competitors reporting bare
  percentages; this made it look worse than honest, which is a different
  failure and not a virtue.
- **Decision:** Coverage cells carry `excluded` with a stated reason for levels
  a subsystem cannot occupy, and those cells are reported as excluded rather
  than unmet. `SUBSYSTEM_FLOOR` records the shallowest level each subsystem can
  hold (L0 for `whole-organism`, L2 for every organ system, since an organ
  system *is* an L2 entity). The summary reports `occupiable_levels` alongside
  `declared_levels`, and every cell now carries `reviewed` beside `populated`
  so breadth cannot inflate the figure that matters (D-017).
- **Alternatives:**
  - Redeclare each subsystem's depth as a range in `declared_depth.json` —
    rejected_because: depth answers "how deep does this go", and overloading it
    with a floor would make a widely-read file mean two things.
  - Leave the metric pessimistic on the grounds that understating is safe —
    rejected_because: a metric that is wrong in a comfortable direction still
    cannot be used to steer, and it invites the eventual correction to be read
    as a retune.
- **Consequences:** + Unmet declarations drop from 42 to 18, and all 18 are
  real gaps someone could close. + The corrected denominator makes the Phase 1
  exit criterion (G-01 at 90% of declared L0–L3 scope) measurable against
  something achievable. − Two published figures change, and any external
  comparison against the old numbers is invalid. − `shallowest_level` is a
  small table that must be extended whenever a subsystem of a genuinely
  different shape is added.
- **Reversibility:** high.
- **Affects:** src/homeo/scale.py, src/homeo/cli.py, src/homeo/evidence.py,
  BIO_Scale_Contract, MANIFEST.md, PRD_FR_Scale_Bridging
- **Supersedes:** none

### D-019 — The pancreas test: three of six probes failed (2026-07-27, orchestrator)
- **Status:** active
- **Context:** "Biology is a graph, not a tree; the pancreas belongs to both the
  digestive and the endocrine system" is the claim this project was founded on,
  and the architecture answered it from the start: containment and membership
  are separate relations (D-006), the tree is derived and never stored, and
  `memberships()` returns a list with no primary. None of it had ever met a case
  that could break it. The substrate held **zero entities with more than one
  membership** and exactly one `member_of` edge, so every test of the founding
  claim ran over a structure containing no instance of the thing being tested.
  `tools/curate_pancreas.py` added one: the pancreas at L3, member of both
  systems, with the exocrine branch (acinus → acinar cell → zymogen granule)
  and the endocrine branch (islet → beta cell → insulin) modelled far enough
  apart to diverge. Six probes were run. **Three failed.**
- **Decision:** Both root causes fixed, and the probes frozen as
  `tests/test_multisystem.py` against the real substrate rather than a fixture
  — a fixture would have passed all six from the beginning, which is exactly
  how the gap survived.
  **Root cause 1 — the derived tree was containment-only.** A system *contains*
  nothing: an organ is `part_of` a body region and a `member_of` a system. So
  navigating from the digestive system reached no organ at all, and the tree
  was structurally incapable of satisfying FR-NAV-005's own acceptance
  criterion ("navigating from the digestive system and from the endocrine
  system, both paths reach it"). `Graph.descendants` now walks containment and
  membership, `TreeNode.child_kinds` records which edge each child was reached
  by, and `ProjectionService._at_level` walks both. Containment stays
  single-parent, so `lineage()` is unchanged and no system ever appears in a
  containment chain.
  **Root cause 2 — `Entity.subsystem` is single-valued**, a tree-shaped field
  in a graph-shaped model. Filed as `digestive`, the pancreas was invisible to
  every endocrine query: coverage reported the endocrine system as having zero
  organs while it contained one, and search by subsystem found it under one
  name only. Rather than make the field a list — which would ripple through
  declared depth, competence scoping, and every schema — membership queries now
  consult the graph via `Graph.in_subsystem`, which is the canonical source for
  membership anyway. The field is now read as the entity's primary filing, not
  as the whole truth about it.
- **Alternatives:**
  - Make `subsystem` multi-valued — rejected_because: it duplicates in a field
    what the `member_of` edges already state, and two sources of the same truth
    is how they come to disagree. Reconsider if a use case needs membership
    without an edge.
  - Add memberships to the tree as a separate "also in" list rather than as
    children — rejected_because: that is what `other_memberships` already did,
    and it is precisely what failed. A link a user cannot follow is a footnote.
  - Accept that a system is not navigable — rejected_because: FR-NAV-005 is a
    Must, and "navigate the body by system" is the first thing any user of an
    anatomy model tries.
- **Consequences:** + The founding claim is now tested against content that
  could falsify it, and six probes hold. + A multi-system organ appears in both
  systems' coverage columns; this is not double-counting a total, since each
  column answers "what does this system have" and the pancreas is a true answer
  to both. − Coverage columns no longer sum to the entity count, and anything
  reading them as a partition will be wrong. − Two subsystems were deepened to
  hold the new content: endocrine L3→L9 (hormones are L9 entities and the
  endocrine system's function is molecular) and digestive L3→L8. Both are Scope
  Reopens under §9 clause 2. − The seven pancreatic entities are provisional and
  unreviewed, like everything else (D-017).
- **Reversibility:** high for the mechanism; medium for the depth declarations,
  which would need tombstones to narrow.
- **Affects:** src/homeo/graph.py, src/homeo/scale.py, src/homeo/search.py,
  src/homeo/projection.py, ontology/pancreas/, PRD_FR_Navigation,
  PRD_FR_Scale_Bridging, BIO_Anatomical_Ontology, MANIFEST.md
- **Supersedes:** none — extends D-006

### D-020 — Content population reopened at L3 (2026-07-27, orchestrator)
- **Status:** active
- **Context:** D-011 split the Phase 1 entry gate: substrate services proceed,
  but the 3D viewer, the study UI, and **L0–L3 content population** stay behind
  RSK-01 (educator validation). Growing the substrate to organ breadth was then
  requested directly. Stepping over the gate silently would make it decorative,
  which is the failure CH-01 identified and D-011 was written to avoid.
- **Decision:** Scope Reopen under AGENTS.md §9 clause 2, superseding **only**
  D-011's content clause. Content population at L0–L3 proceeds; the 3D viewer
  and the study UI remain gated. The split is the same one D-011 made: RSK-01
  asks whether users want evidence grading *surfaced to them*, which is a
  presentation question. It does not ask whether the substrate should contain
  organs. A reference model with no organs cannot be validated by anyone,
  including the educators whose opinion the gate is waiting for.
  All such content is admitted **provisionally** (D-017): agent-proposed,
  human-unreviewed, marked so at every surface, and excluded from every
  reviewed-coverage figure. Breadth therefore cannot be mistaken for progress
  against G-01, whose denominator is reviewed content.
- **Alternatives:**
  - Keep the gate closed — rejected_because: the requester is the stakeholder
    the gate protects, and they asked for the content directly.
  - Open the whole gate including the viewer — rejected_because: the viewer is
    the expensive artifact RSK-01 could invalidate, and nothing about content
    population requires it.
- **Consequences:** + The substrate can hold enough anatomy to be worth an
  educator's time, which makes resolving RSK-01 easier rather than harder.
  − The provisional/reviewed gap widens with every organ added; that gap is
  RSK-02 made visible, and it is reported as a number.
- **Reversibility:** high — provisional content is separable by its own field.
- **Affects:** PRD_Scope_and_Roadmap, MANIFEST.md, PRD_Risks_and_Constraints
- **Supersedes:** D-011 (content clause only; the presentation gate stands)

### D-021 — A definition is not a finding: claims split into two registers (2026-07-27, architect)
- **Status:** active
- **Context:** Probing UBERON ahead of the ontology import surfaced a category
  error already present in the substrate at scale. UBERON's definition of the
  heart cites `Wikipedia:Heart` and a curator's ORCID; imported onto the EVC
  ladder it would be graded as biological evidence. Checking the existing
  substrate showed the same error already made **156 times out of 165 claims —
  94%**. "The heart is a myogenic muscular circulatory organ" was carried as
  APPROXIMATED *evidence*, on the same register as a measured sarcomere length.
  The import would have added tens of thousands more and drowned the nine real
  findings entirely.
- **Decision:** Claims carry a `kind`. **Biological** claims assert something
  about a body and are graded EVC-1…EVC-8 by evidence. **Terminological**
  claims assert what a term denotes and are graded TRM-1…TRM-4 by the authority
  behind them and whether that authority's own cited source resolves. A
  terminological claim may never be cited as evidence for a biological
  assertion, and neither register may carry the other's grades — `INV-18`
  enforces both directions with four negative tests.
  `tools/split_claim_kinds.py` migrated the existing substrate, grading by
  stated rule rather than case by case: seed-corpus definitions restating one
  narrative document with no resolvable source → TRM-3 (140); definitions from
  Gray's, Terminologia Anatomica and Guyton, which are naming authorities with
  resolvable ISBNs → TRM-1 (16). The audit is
  `ontology/CLAIM_KIND_SPLIT.json`.
  A terminological claim is **not weaker** than a biological one; it is about
  something else. TRM-1 is as satisfactory for a definition as EVC-1 is for a
  measurement.
- **Alternatives:**
  - Keep one ladder and add a note to definitional claims — rejected_because:
    a note is not a constraint, and the whole point is that a definition must
    not be *reachable* as evidence for a physiological question.
  - Exclude definitions from the substrate — rejected_because: they are what
    makes the model navigable and searchable, and the ontologies that supply
    breadth supply them by construction.
  - Grade definitions EVC-8 (UNKNOWN) — rejected_because: a definition is not
    an absence of knowledge, and UNKNOWN is a deliberate assertion about
    biology, not a bin for things that do not fit.
- **Consequences:** + The substrate now truthfully reports **9 biological
  findings** — two of them UNKNOWN — rather than 165 claims. That number is
  much smaller and much more useful. + The import can add 16,000 definitions
  without diluting a single evidence figure. + The groundedness guard can
  refuse an assertion about the body grounded only in definitions. − Every
  claim-count figure published before today meant something different, and
  comparisons across the change are invalid. − Two registers is more surface
  for a caller to understand, and `evidence_class` now holds a TRM value for
  terminological claims, which is a naming compromise made to avoid churning
  every consumer.
- **Reversibility:** low. Merging the registers again would reintroduce the
  error deliberately.
- **Affects:** src/homeo/substrate.py, tools/biocheck.py,
  BIO_Evidence_and_Provenance, BIO_Validation_Framework, PRD_FR_Evidence,
  ontology/CLAIM_KIND_SPLIT.json
- **Supersedes:** none

### D-023 — Subsumption is a relation; the vocabulary had no guard (2026-07-27, architect)
- **Status:** active
- **Context:** UBERON carries 19,387 `is_a` edges and the relation vocabulary
  had no subsumption at all — it holds mereological and functional relations
  only, so "a cardiomyocyte *is a* muscle cell" was inexpressible. Dropping the
  edges on import would discard the taxonomy that makes search and
  generalization work; adopting UBERON's hierarchy as structure would be worse,
  because the heart there `is_a` "thoracic segment organ" and "mesoderm-derived
  structure" — concepts, not places.
  **While adding it, the same mistake was made again.** `is_a` went into
  `INVERSES` and `ADMISSIBLE` in code and *not* into the relation table in
  `BIO_Anatomical_Ontology` §Relationship Types. That is precisely the D-013
  divergence — a rule stated in one place and enforced in another — committed
  inside the change whose purpose was to add a relation. It was found by
  re-reading the documents, not by any check, because **the relation table had
  no doc↔code guard while the evidence ladder has had one since D-013.**
- **Decision:** Two parts, and the second matters more.
  **The relation:** `is_a` is admitted with inverse `subsumes`, cardinality
  many-to-many, admissible **same level only** — a class and its superclass
  describe the same kind of thing at the same granularity, so a cross-level
  `is_a` is a classification error worth catching. It is deliberately excluded
  from `STRUCTURAL_RELATIONS`, `lineage()`, `children()`, `descendants()` and
  the navigation tree: a taxonomy is not a body, and admitting subsumption as
  structure would let a user navigate *into* a concept. Six tests pin that,
  against a fixture asserting a true subsumption rather than a plausible-looking
  one.
  **The guard:** `INV-19` parses the documented relation table and compares it
  against the code vocabulary, reporting as errors any relation present in one
  and not the other and any inverse that disagrees. Three negative tests cover
  the three shapes, including the exact one committed today.
- **Alternatives:**
  - Drop `is_a` on import — rejected_because: the class hierarchy is most of
    what an ontology knows, and search over "all muscle cells" needs it.
  - Model subsumption as `part_of` — rejected_because: it is the error the whole
    entry exists to prevent, and it would put "thoracic segment organ" into the
    containment ladder.
  - Fix the document and move on without the check — rejected_because: this is
    the second occurrence of the same class of defect, and the first one got a
    check. A lesson applied once is a coincidence.
- **Consequences:** + Subsumption is expressible and the import can carry it.
  + The relation vocabulary can no longer drift between document and code.
  − One more table the document must keep accurate, now enforced. − `INV-19`
  imports `homeo.substrate` from a validator that was otherwise stdlib-only over
  files; it degrades to a warning when the import fails rather than pretending
  to have checked.
- **Reversibility:** high for the relation; the guard should not be reversed.
- **Affects:** src/homeo/substrate.py, tools/biocheck.py,
  BIO_Anatomical_Ontology, BIO_Validation_Framework, PRD_FR_Relationship_Graph
- **Supersedes:** none — extends D-013's lesson to a second vocabulary
