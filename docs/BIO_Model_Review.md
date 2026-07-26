---
doc: BIO_Model_Review
tier: standard+
version: 1.0.0
status: draft
owner: ux
last_updated: 2026-07-26
---

# Model Review — Rubric Dispositions

_One row per BIO_RUBRIC item. **pass** requires one line of evidence; **flag**
names the punch-list item it became; **N/A** states the reason._

- **Scale depth under review:** cardiovascular L10 (vertical slice); respiratory,
  nervous, urinary L5; musculoskeletal L4; remainder L3 — per MANIFEST §Product
- **Reviewed:** 2026-07-26 · **Reviewer role:** ux (Model Reviewer) · **Phase:** 0

| BRB | Disposition | Evidence / Punch Item / Reason |
|---|---|---|
| BRB-01 | pass | BIO_Scale_Contract has all eleven SCL rows with a populated resolution-limit column; specgraph errors on an empty one (verified by smoke test) |
| BRB-02 | pass | Every quantitative row in BPR-01's state table and the cross-bridge quantity table carries an evidence class; FR-EVID-002 requires class display wherever a claim appears |
| BRB-03 | pass | EVC-8 is a first-class asserted claim, queryable via FR-SRCH-004 and counted in G-03; BIO_Evidence_and_Provenance §Negative Knowledge specifies storage and surfacing |
| BRB-04 | pass | FR-SPAT-004 requires a declared representation kind per asset and marks schematic content at every binding site; PRD_Information_Architecture layer 1 keeps evidence class always-visible |
| BRB-05 | pass | G-01 and G-02 report `n / declared_n`; BR-021 forbids narrowing the denominator outside a Scope Reopen; the Executive Summary carries an explicit metric-integrity note |
| BRB-06 | pass | BIO_Scale_Contract §Cross-Scale Linkage Rules requires recorded justification for any level-skipping edge; INV-05 enforces; FR-REL-005 additionally gates `causes` at EVC-2 |
| BRB-07 | pass | BPR-01 declares `spatial_scale` L3/L7/L8/L9/L10 with per-level contribution; FR-SCAL-005 requires it, FR-SCAL-006 forbids spanning as a depth bypass |
| BRB-08 | pass | BIO_Scale_Contract §Semantic Zoom vs Physical Zoom defines both with four transition rules; FR-NAV-001 requires distinct controls |
| BRB-09 | **flag** | **PUNCH-01.** Nine of ten registered processes are `narrative`, and eight of eleven subsystems have zero entities at their declared depth. The declarations are honest, but "declared L5" with no L5 content is a promise the Coverage surface must show as unmet — currently only G-01 reports it, and only at release. Coverage must show declared-vs-populated per level from Phase 1, not Phase 3. |
| BRB-10 | pass | INV-05 enforces per-subsystem depth; FR-SCAL-002's acceptance criteria explicitly reject correct-but-too-deep content; the endocrine islet-cell example is written into the check specification |
| BRB-11 | pass | EVC ladder ties class to source type; EVC-1 admits only reproduced human in-vivo measurement; BR-002 forbids agent assignment of the top two classes |
| BRB-12 | pass | FR-EVID-006 retains both claims and forbids silent selection; adjudication creates a new claim citing both originals rather than deleting either |
| BRB-13 | pass | Species is a mandatory claim field (INV-12); BIO_Cell_and_Molecular_Model §Species Provenance marks rodent-derived kinetics explicitly and grades them EVC-4 |
| BRB-14 | pass | D-003 tiering, INV-11 enforcement, per-asset licence metadata; FR-VER-009 refuses or tier-splits exports crossing tiers |
| BRB-15 | pass | FR-REL-008 requires per-edge provenance and forbids inheriting endpoint evidence |
| BRB-16 | **flag** | **PUNCH-02.** No mechanism detects a correctly-formatted citation that does not actually support its claim. FR-EVID-010 guarantees the record is *retrievable*, not that it is *apt*. BIO_Validation_Framework §What Validation Does Not Establish names this honestly, but the expert-review gates do not currently mandate source-aptness spot-checking as a sampled, recorded activity. It should be a named gate with a sampling rate, not an implied reviewer duty. |
| BRB-17 | pass | FR-PHYS-001 requires representation status wherever a process appears; nine of ten processes are openly `narrative`; BPR-01 is the only `structured` one and carries every mandatory field |
| BRB-18 | pass | INV-03 requires every process input and output to resolve to a defined entity; FR-PHYS-003 offers entity creation as a curation task rather than permitting a dangling reference |
| BRB-19 | pass | D-005 forbids a global clock; BIO_Physiological_Processes §Multiscale Time declares eight domains with an explicit composition rule; INV-06 fails an undeclared coupling |
| BRB-20 | pass | FR-SIM-001's gate requires every parameter sourced before a process becomes executable; no process is executable in Phase 0 and none will be before Phase 6 |
| BRB-21 | pass | BPR-01's Frank–Starling feedback names its damping (descending limb, pericardial restraint) and the process carries a four-row failure-state table; FR-PHYS-007 enforces both |
| BRB-22 | pass | D-004 makes immutability structural; INV-08 checks it; AGT-9 has no credential that could write to the reference; `--selftest` injects the violation |
| BRB-23 | pass | FR-PERS-006 enforces source rank; BIO_Personalization_Model §Source Hierarchy orders seven source classes and gates propagation on rank |
| BRB-24 | pass | Every overlay value carries measurement time (INV-09); FR-PERS-009 shows out-of-policy values as historical and returns "no current value" rather than a stale one |
| BRB-25 | **flag** | **PUNCH-03.** The most clinically-suggestive surface is a personalized comparison against a reference range — a user sees their value outside a range and will read it as a finding, regardless of the boundary text. FR-PERS-007 requires the boundary; nothing specifies how the *comparison itself* is framed to avoid implying significance. The visual treatment of out-of-range needs a design decision, not just a disclaimer, and TECH_UI_UX_Design must carry it. |
| BRB-26 | pass | All fourteen INV rows name an executable check and a failure message; FR-VALD-001 errors at harness startup on an unimplemented invariant |
| BRB-27 | pass | INV-14 refuses ungrounded assertions; EV-RETR-001 through EV-RETR-006 test groundedness, gap honesty, class fidelity, clinical refusal, association phrasing, and compilation-status fidelity |
| BRB-28 | pass | The lens's six extra-depth docs are all at substantive depth: Scale_Contract has eleven contracts plus linkage rules; Evidence has the full ladder, source register, tiers, pipeline; Validation has fourteen invariants with check specifications and negative tests; Cell_and_Molecular carries its own false-precision register |
| BRB-29 | pass | Compilation status is required on every surface and API response (FR-ONTO-006), in search results (FR-SRCH-002), and in retrieval responses (FR-RETR-008); D-007 forbids promotion by reformatting |
| BRB-30 | pass | D-006 makes the tree a derived view; FR-NAV-004 requires it be labelled as one; FR-REL-006 and FR-RETR-009 forbid rendering or describing an association as a mechanism; the pancreas journey is the acceptance test |

## Unresolved Flags
Three flags are open. Each is a real gap, not a wording preference, and each is
recorded here rather than resolved by the reviewer:

| Punch | Item | Routed To | Status |
|---|---|---|---|
| PUNCH-01 | Coverage must show declared-vs-populated per level from Phase 1, not only through G-01 at release | PM → PRD_FR_Scale_Bridging FR-SCAL-010, PRD_Scope_and_Roadmap Phase 1 exit | **applied** — FR-SCAL-010 exists; Phase 1 exit criteria updated to require the Coverage surface |
| PUNCH-02 | Source-aptness spot-checking must be a named review gate with a sampling rate, not an implied duty | PM → BIO_Validation_Framework §Expert Review Gates | **applied** — a sampled source-aptness gate has been added to the gate table |
| PUNCH-03 | The framing of out-of-range personalized comparisons needs a design decision, not only boundary text | UX pass B → TECH_UI_UX_Design | **carried to pass B** — recorded there as a required design decision |

No flag remains unaddressed at cross-review exit. PUNCH-03 is carried rather than
closed: it is a design obligation on a Phase 7 surface, and closing it now would
be closing it on paper.
