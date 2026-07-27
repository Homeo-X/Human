---
doc: BIO_Validation_Framework
tier: standard+
version: 1.0.0
status: draft
owner: architect
last_updated: 2026-07-26
---

# Validation Framework

_The model's integrity rules as executable checks. Every `INV` row names the check
that enforces it and the failure it produces; a rule with no check is a finding
(BRB-26), not a rule._

## Integrity Invariants
| ID | Invariant | Rule | Enforced By | Failure Produced | Severity |
|---|---|---|---|---|---|
| INV-01 | Biological consistency | an entity may not hold a relationship its relation type declares inadmissible between their levels or classes (BIO_Anatomical_Ontology §Relationship Types) | `biocheck --rel` | `inadmissible relation: <rel> from <a>(L<n>) to <b>(L<m>)` | blocking |
| INV-02 | Hierarchical consistency | an entity has exactly one `part-of` parent; multiple parenthood is admitted only through declared membership relations, and containment cycles are forbidden | `biocheck --hier` | `multiple part-of parents for <id>` / `containment cycle: <path>` | blocking |
| INV-03 | Functional consistency | every process input and output resolves to a defined entity; no process consumes or produces an undefined thing | `biocheck --proc` | `BPR-<n> references undefined entity <ref>` | blocking |
| INV-04 | Unit consistency | every quantitative value carries a UCUM unit, and values compared or combined share a dimension | `biocheck --units` | `quantity without unit at <path>` / `dimension mismatch: <u1> vs <u2>` | blocking |
| INV-05 | Scale consistency | an entity's level matches its class; cross-scale edges skipping a level carry a recorded justification; no entity exceeds its subsystem's declared max level | `biocheck --scale` | `entity <id> at L<n> exceeds declared depth L<m> for <subsystem>` / `unjustified level skip <n>→<m>` | blocking |
| INV-06 | Temporal consistency | every process declares a timescale domain; a coupling between domains is either declared supported or declared unsupported, never implicit | `biocheck --time` | `BPR-<n> has no timescale domain` / `undeclared coupling <a>↔<b>` | blocking |
| INV-07 | Evidence consistency | every claim carries a complete claim record; confidence does not exceed what the source type admits; no agent-assigned EVC-1 or EVC-2 | `biocheck --evidence` | `incomplete claim record: missing <field>` / `EVC-<n> unsupported by source type <t>` | blocking |
| INV-08 | Personalization consistency | no overlay operation writes to a reference entity; every overlay resolves against a pinned reference release | `biocheck --overlay` | `overlay <id> attempts write to reference entity <ref>` | blocking |
| INV-09 | Individual value completeness | every overlay value carries value, unit, measurement time, method, source, and confidence | `biocheck --overlay` | `overlay value missing <field>` | blocking |
| INV-10 | Identifier integrity | every entity has a resolvable identifier; external xrefs use a registered authority and version; minted local ids are flagged as minted | `biocheck --ids` | `unregistered authority <a>` / `unflagged minted id <id>` | blocking |
| INV-11 | Licence integrity | every asset and source carries a licence and a tier; no T1 or T2 content appears in the T0 ontology or evidence layers | `biocheck --licence` | `tier violation: T<n> content in T0 layer at <path>` | blocking |
| INV-12 | Species provenance | every biological claim carries a species field; a non-human species on a claim presented as human carries a transfer justification | `biocheck --species` | `claim <id> missing species` / `cross-species claim without transfer justification` | blocking |
| INV-13 | Representation honesty | no entity claims a representation mode its level's `SCL` row does not offer; schematic geometry is flagged as schematic wherever it is bound | `biocheck --scale` | `entity <id> claims mode <m> unavailable at L<n>` | advisory |
| INV-14 | Retrieval groundedness | every generated claim in a retrieval response resolves to a graph claim id; unresolvable content is refused, not rendered | runtime guard in PRD_FR_Knowledge_Retrieval, tested by EV-RETR-001 | `ungrounded assertion in response` | blocking |
| INV-16 | Rule/checker agreement | the class table in `tools/biocheck.py` must agree with the EVC ladder in BIO_Evidence_and_Provenance; the document is the authority and the checker derives from it | `biocheck` (always, before any other check) | `INV-16 EVC-n: checker admits X but the document admits Y` | blocking |
| INV-20 | Identity uniqueness | no id is defined twice as an entity, claim, relationship or process; the loader's last-file-wins is not a decision anyone made | `biocheck` (every run) | `INV-20 <id>: defined n times as a <kind>. One id names one thing; whichever record loads last would silently win` | blocking |
| INV-19 | Relation-vocabulary agreement | the relation table in BIO_Anatomical_Ontology §Relationship Types and the `INVERSES`/`ADMISSIBLE` tables in code must define the same relations with the same inverses; the document is the authority | `biocheck` (always, before any substrate check) | `INV-19 <rel>: in the code vocabulary but absent from BIO_Anatomical_Ontology — a relation the document does not define is a relation nobody agreed to` | blocking |
| INV-18 | Claim-kind integrity | a definition is never graded on the evidence ladder and a finding is never graded on the terminological one; every terminological claim names its authority, and TRM-1 names the source it asserts resolves | `biocheck` (every run) | `INV-18 <id>: a terminological claim is graded on the TRM register; EVC-n is an evidence class, and a definition is not evidence` | blocking |
| INV-17 | Review-state integrity | every entity and claim declares `reviewed` or `provisional`; provisional content never names a `human:` assigner; reviewed content always does; nothing unreviewed sits at EVC-1 or EVC-2; a `proposed_class` is never weaker than the class asserted | `biocheck` (every run) | `INV-17 <id>: provisional but assigned_by human:… — an unreviewed claim naming a human reviewer is a fabricated review` | blocking |
| INV-15 | Compilation-status coherence | a `mechanistic` or `parameterized` relationship or process may not depend on a `narrative` endpoint; status is a capability constraint, not only a label | `biocheck --status` | `INV-15 <id> at status <s> depends on narrative <ref>` | blocking |

## Validation Layers
| Layer | Runs When | Scope | Blocking? |
|---|---|---|---|
| Schema validation | on every write to `ontology/` | JSON Schema conformance | yes |
| Invariant harness (`biocheck`) | pre-commit, CI, and pre-release | all INV rows against the whole substrate | yes for blocking severities |
| Spec graph (`specgraph`) | CI and cross-review | the document set: ids, references, traces | yes |
| Retrieval groundedness | per response, at runtime | INV-14 | yes — refuse rather than render |
| Expert review gates | per content release | biological correctness at the declared level | yes |
| Rubric pass (`BIO_RUBRIC`) | each phase gate | the 30 known failure modes | flags, dispositioned |

## Check Specifications
_Per check: the exact condition, the data it reads, and a worked example of both
a pass and a failure. A check whose failure case was never written is a check
nobody has confirmed can fail._

### `--hier` — enforces INV-02
- **Condition:** for every entity, `|part_of| ≤ 1`, and the transitive closure of
  `part_of` contains no cycle.
- **Reads:** `ontology/**/*.json`, `part_of` and `member_of` fields.
- **Passes when:** left ventricle has `part_of: heart` and nothing else;
  membership in the cardiovascular system is expressed as `member_of`, not a
  second parent.
- **Fails when:** an entity carries `part_of: [heart, thorax]` — thorax is a
  region and the relation should be `located_in`.
- **Failure message:** `INV-02 multiple part-of parents for HOX:organ:left-ventricle: [heart, thorax]`

### `--units` — enforces INV-04
- **Condition:** any object with a `value` key has a non-empty `unit` key holding
  a UCUM code; comparisons and arithmetic across values require equal dimension.
- **Reads:** every quantitative field in `ontology/` and in overlays.
- **Passes when:** `{"value": 0.8, "unit": "s"}` for cardiac cycle duration.
- **Fails when:** `{"value": 70}` for stroke volume with no unit — 70 mL and 70 %
  are different claims and the model cannot tell them apart.
- **Failure message:** `INV-04 quantity without unit at BPR-01.state.stroke_volume`

### `--evidence` — enforces INV-07
- **Condition:** every claim has all required record fields for its class; the
  asserted class is admissible for its source type; `assigned_by` is a human
  reviewer when class is EVC-1 or EVC-2.
- **Reads:** all claim records.
- **Passes when:** an EVC-2 claim cites two independent primary studies, carries
  species `Homo sapiens`, a stated population, conditions, and a reviewer.
- **Fails when:** a claim is EVC-1 with `assigned_by: agent:evidence` — the two
  highest classes require a human, precisely because a confident model would
  over-assign them.
- **Failure message:** `INV-07 EVC-1 assigned by non-human reviewer on claim <id>`

### `--scale` — enforces INV-05 and INV-13
- **Condition:** entity level ≤ declared subsystem max; every cross-scale edge
  spanning more than one level has a non-empty `skip_justification`.
- **Reads:** entity `level` and `subsystem` fields, edge records,
  `BIO_Scale_Contract` declared depths.
- **Passes when:** a cardiomyocyte at L7 in the cardiovascular subsystem, which
  is declared to L10.
- **Fails when:** an islet beta cell at L7 in the endocrine subsystem, declared to
  L3 — the content may be correct, but it exceeds what this model claims to hold,
  and shipping it silently would make the declaration meaningless.
- **Failure message:** `INV-05 entity <id> at L7 exceeds declared depth L3 for endocrine`

### `--overlay` — enforces INV-08 and INV-09
- **Condition:** every overlay operation targets an overlay-owned path; no
  operation resolves to a reference entity's canonical fields; every overlay
  value carries the six required provenance fields.
- **Reads:** overlay documents plus the pinned reference release id.
- **Passes when:** an overlay sets an individual resting heart rate with value,
  unit, time, method, source, and confidence, leaving the reference untouched.
- **Fails when:** an overlay contains an operation whose target path is a
  reference entity's `function` field — that is corruption of canonical biology,
  which D-004 forbids at every privilege level.
- **Failure message:** `INV-08 overlay <id> attempts write to reference entity <ref>`

## Negative Testing
_Every invariant is deliberately violated in `biocheck --selftest`. A validator
that cannot fail is not a validator._

| Violation Injected | Enforces | Expected Detection |
|---|---|---|
| a `secretes` edge from a bone to a region | INV-01 | inadmissible relation |
| an entity given two `part_of` parents | INV-02 | multiple parents |
| a process output naming an undefined molecule | INV-03 | undefined entity reference |
| a stroke-volume value with the unit removed | INV-04 | quantity without unit |
| an L7 entity placed in an L3-declared subsystem | INV-05 | depth exceeded |
| a process with its timescale domain removed | INV-06 | missing timescale |
| an UNKNOWN claim promoted to VERIFIED with no source added | INV-07 | unsupported class |
| an overlay operation targeting a reference entity field | INV-08 | reference write attempt |
| an overlay value with its measurement method removed | INV-09 | incomplete individual value |
| an xref to an unregistered authority | INV-10 | unregistered authority |
| a T1 mesh path embedded in a T0 entity record | INV-11 | tier violation |
| a rodent-derived claim with the species field removed | INV-12 | missing species |
| an entity claiming `enumerated` at a `typed` level | INV-13 | mode unavailable |
| an EVC-2 claim reduced to a single source | INV-07 | insufficient independent sources |
| the checker's class table edited to diverge from the ladder | INV-16 | rule/checker divergence |
| an unreviewed claim attributed to a human reviewer | INV-17 | fabricated review |
| unreviewed content sitting at EVC-2 | INV-17 | uncertified strong class |
| an entity marked reviewed with no approval behind it | INV-17 | review asserted without a reviewer |
| a `proposed_class` weaker than the class asserted | INV-17 | assessment used as a downgrade |
| a definition graded as biological evidence | INV-18 | category error between registers |
| a finding graded on the terminological register | INV-18 | category error between registers |
| a terminological claim with no authority behind it | INV-18 | unattributable definition |
| a biological claim carrying a definition source | INV-18 | register leak |
| a relation in the code and not in the document | INV-19 | vocabulary divergence |
| a relation in the document and not in the code | INV-19 | vocabulary divergence |
| an inverse that disagrees between code and document | INV-19 | vocabulary divergence |
| the same entity id defined twice | INV-20 | ambiguous identity |
| a mechanistic relationship pointing at a narrative endpoint | INV-15 | mixed compilation status |
| a retrieval response asserting a claim with no graph id | INV-14 | ungrounded assertion |

## Expert Review Gates
| Gate | Reviewer | Reviews | Binds |
|---|---|---|---|
| New entity admission | domain reviewer for that subsystem | identity, classification, level, parent | that the entity exists as described and belongs where it is placed |
| Class EVC-1 or EVC-2 assignment | domain reviewer | source quality against the claimed class | the claim's weight in every downstream surface |
| Conflict adjudication | two domain reviewers | both positions and the evidence | a recorded adjudication, never an erasure of the conflict |
| Mechanism admission (L9, L10) | domain reviewer with mechanism expertise | chain completeness, conditions, cell-type specificity | that the mechanism is represented as understood, with its boundary stated |
| Process becoming `executable` | reviewer plus Research Engineer | parameter sources, coupling declarations, capability limits | that simulation output does not exceed its data (BRB-20) |
| **Source aptness (sampled)** | domain reviewer, not the reviewer who admitted the claim | a **phase-dependent** sample of admitted claims per release, checking that each cited source actually supports the specific claim attached to it — not that it exists or is well-formatted. Rate: minimum 20 claims while the corpus is under 10³ claims; thereafter a statistically-sized sample (95% confidence, 5% margin) rather than a fixed percentage, with the computed size stated in the release manifest | that citations are apt, which no automated check can establish (BRB-16). A failure rate above 5% blocks the release and triggers a full re-review of that reviewer's admissions for the period. **CH-11:** a flat percentage is either trivial now or impossible at Phase 3 volumes, which is why the rate scales with corpus size rather than with it |
| Content release | Biology Lead | the rubric pass and all open flags | the release |

## What Validation Does Not Establish
Consistency is not truth. Every check in this document verifies that the model
agrees with itself, with its declared scope, and with its own evidence rules.
None of them verifies that the biology is right.

**This section was itself under-stated until D-013.** A fully passing run was
also compatible with the checker enforcing a *different rule* from the one
written down — which is what happened: the ladder forbade textbook-sourced EVC-1
and the checker permitted it, so two claims sat at VERIFIED through every green
run. INV-16 now closes that specific hole, and the general lesson is recorded
here: a rule stated in one place and enforced in another will drift, and the
drift is invisible because both halves look correct in isolation.

Specifically, a fully passing validation run is compatible with: a correctly
formatted claim citing a source that does not support it (BRB-16 — caught only by
the sampled source-aptness gate above, and then only within its sampling rate); an
entity correctly placed in a hierarchy that
reflects an outdated consensus; a mechanism whose steps are each sourced but
whose composition is wrong; and complete coverage of a scope that was declared
too narrow to be useful.

Coverage is not completeness, and passing checks is not expert endorsement. The
expert review gates above are load-bearing, not ceremonial, and the project's
correctness rests on them rather than on this harness.
