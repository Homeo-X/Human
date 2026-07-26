---
doc: PRD_FR_Personalization
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Personalization

## Purpose & Scope
Applying individual data as an overlay over an immutable reference model:
overlay operations, individual value provenance, uncertainty, propagation limits,
temporal history, and the boundaries on what a personalized view may say.
Implements D-004. Boundary: the reference model → all other modules; privacy
controls → PRD_Security_Requirements; the conceptual model → BIO_Personalization_Model.

**Phase status:** Phase 7. Nothing here is built, and no individual data of any
kind is handled before it. Specified now so the substrate, schemas, and APIs do
not have to change when it arrives — which is the brief's explicit architectural
requirement.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Individual user | to see my measured value beside the reference range | I understand where I sit, with the uncertainty visible |
| Individual user | to delete my data completely | I can leave without residue |
| Clinician | to see the method behind every individual value | I can weigh a wearable reading against a clinical one |
| Researcher | to know exactly what an individual value did and did not change | I am not shown a fabricated physiology built from one number |
| Platform team | an overlay model that does not require rewriting the core | personalization is additive, as promised |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-PERS-001 | Must | No overlay operation writes to a reference entity; the reference is immutable by construction | Given an overlay operation whose target resolves to a reference entity's canonical fields, when validated, then INV-08 fails and it is refused; and given an overlay-owned target, then it is applied | Users need not know this exists; it is why they can trust everything else |
| FR-PERS-002 | Must | Every overlay pins the reference release it resolves against | Given an overlay with no pinned release, when applied, then it is refused; and given a pinned release, then resolution is deterministic across time | An overlay that floats across releases silently changes meaning |
| FR-PERS-003 | Must | Every individual value carries value, unit, measurement time, method, source, and confidence | Given a value missing its measurement method, when submitted, then INV-09 fails naming the field; and given a complete record, then it is accepted | Six required fields is friction; the alternative is an unattributable number, which is worse |
| FR-PERS-004 | Must | Overlay operations are limited to the enumerated algebra; changing a canonical biological fact is impossible at every privilege level | Given a request to alter a reference claim through an overlay, when submitted at any privilege level including administrative, then it is refused; and given an enumerated operation, then it is applied | The absence of an override, even for admins, is the guarantee |
| FR-PERS-005 | Must | Propagation is default-deny: an individual value changes only what BIO_Personalization_Model lists, with its stated basis | Given a measured resting heart rate, when the individual model resolves, then cellular and molecular parameters are unchanged and shown as reference values; and given height with a sourced allometric relationship, then only the listed geometry scales | Uncontrolled propagation turns one measurement into an invented body — the most likely way this feature misleads |
| FR-PERS-006 | Must | Source rank is enforced: a lower-ranked source cannot supersede a higher-ranked one for the same quantity without explicit user action | Given a self-reported value arriving after a clinical measurement, when stored, then it does not supersede automatically and both are retained; and given explicit user selection, then the choice is recorded | Self-reported and clinical must never look identical in the interface |
| FR-PERS-007 | Must | Every personalized surface carries the non-diagnostic boundary, persistently | Given any personalized view, when displayed, then the boundary is present and not dismissible; and given a comparison to a reference range, then it is stated inline | BRB-25 exists for this requirement |
| FR-PERS-008 | Must | Overlay data is individually deletable, and deletion leaves the reference model bit-identical | Given a deletion request, when completed, then no overlay residue remains and the reference release hashes unchanged; and given the deletion, then it is verifiable by the user | Deletion is a tested behaviour, not a policy statement |
| FR-PERS-009 | Should | Stale values are shown as historical, not current, per the class staleness policy | Given a value past its class threshold, when the individual model resolves, then it is presented as historical with its age; and given no in-policy value, then the answer is that there is no current value | Showing a two-year-old measurement as "your value" is a quiet lie |
| FR-PERS-010 | Should | Conflicting individual measurements are both retained and displayed with their methods | Given two same-day readings from a wearable and a clinical device, when displayed, then both appear ordered by source rank with the disagreement stated | Same discipline as reference-model conflicts, same reason |
| FR-PERS-011 | Should | Derived individual quantities are labelled as model outputs with their inputs and assumptions reachable | Given a derived haemodynamic quantity, when displayed, then it is marked derived and its inputs and assumptions are one action away | A derived number looks exactly like a measured one unless the interface intervenes |
| FR-PERS-012 | Could | An individual model can be exported as reference-release-id plus overlay | Given an export request, when fulfilled, then the artifact contains the pinned release id and the overlay, and reconstructs identically | Portability follows from D-004 almost for free |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Overlay | RW | the overlay document, pinned to a release |
| OverlayValue | RW | individual values with full provenance |
| Individual | RW | the overlay owner; the most sensitive record the system holds |
| Entity | R | reference targets, read-only, always |
| Claim | R | reference values for comparison |
| SpatialIdentity | R | geometry replacement targets |
| KnowledgeRelease | R | the pinned release |

## States & Transitions
Overlay lifecycle: `empty` → `active` → (`archived` | `deleted`). Values within
an overlay are append-only with supersession; a value is never edited in place,
so the history of what was believed when is preserved. `deleted` is terminal and
complete — there is no soft-delete state that retains individual data.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: an overlay with no values | resolves to the pure reference model, explicitly labelled as reference, not as "your body" | FR-PERS-005 |
| Invalid input: a value physiologically implausible for the reference population | accepted but flagged, never silently rejected — an unusual person is not a data error, and the flag is shown to the user rather than acted on | FR-PERS-003 |
| Permission denied: any actor other than the individual attempting to read an overlay | refused; access is scoped to the individual by default, with sharing an explicit revocable act | FR-PERS-008 |
| Concurrency: two devices writing the same quantity simultaneously | both retained as conflicting measurements, ordered by source rank | FR-PERS-010 |
| External dependency failure: a wearable integration returns malformed data | rejected at the boundary; partial or unit-less values never enter an overlay | FR-PERS-003 |
| Scale extreme: a continuous wearable stream over years | stored as a series with retention and downsampling policy; provenance is preserved on retained points, and downsampling is recorded rather than silent | FR-PERS-009 |
| The pinned reference release is superseded | the overlay continues resolving against its pinned release; migration is offered and its effects previewed, never applied silently | FR-PERS-002 |
| A user asks what their data means clinically | the non-diagnostic boundary is returned; no interpretation is offered, and this is the answer even when the pattern seems obvious | FR-PERS-007 |

## Dependencies
- On other modules: every reference-model module (read-only), PRD_FR_Validation
  (INV-04, INV-08, INV-09), PRD_FR_Versioning (release pinning),
  PRD_FR_Simulation (individual parameters, Phase 7)
- On external integrations: wearable and health-record integrations, imaging
  segmentation pipelines — all Phase 7, all bounded by
  PRD_Security_Requirements

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Overlay values carrying complete provenance | G-06 | 100%, enforced |
| Overlay write attempts reaching the reference model | G-05 | 0, enforced and adversarially tested |
| Deletions leaving the reference bit-identical | G-07 | 100% |
| Personalized surfaces carrying the non-diagnostic boundary | G-06 | 100% |

## Out of Scope for This Module
- Diagnosis, risk scoring, prediction, or recommendation of any kind
- Inferring unmeasured individual values from measured ones beyond the listed
  propagation paths
- Aggregate or population analysis of individual data
- Genotype-to-phenotype inference

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| Which allometric relationships are sourced well enough to justify geometry scaling? | Biology Lead | Phase 7 |
| How is an implausible-but-real value flagged without implying the person is wrong? | Model Reviewer | Phase 7 |
| What is the retention policy for continuous wearable series, and who decides it? | Architect | Phase 7 |
| Does offering release migration create pressure to migrate that users cannot evaluate? | Model Reviewer | Phase 7 |
