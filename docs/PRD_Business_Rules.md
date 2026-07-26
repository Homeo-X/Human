---
doc: PRD_Business_Rules
tier: standard+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Business Rules

_Domain policies that hold regardless of UI: rules the system must enforce even
if every screen changed. In this product the "business" rules are largely
epistemic rules — what may be asserted, by whom, on what basis — because that is
what the product is._

## Rule Register
| ID | Rule | Applies To (entity/module) | Source (law, policy, stakeholder) | Exceptions |
|---|---|---|---|---|
| BR-001 | A claim's evidence class may change only when its evidence changes; reformatting, re-citing, aggregating, or re-hosting changes nothing | Claim, PRD_FR_Evidence | BIO_Evidence_and_Provenance | none |
| BR-002 | No automated actor may assign evidence class EVC-1 or EVC-2 | Claim, PRD_FR_Agent_Definition | BIO_Evidence_and_Provenance, D-001 | none — not overridable at any privilege level |
| BR-003 | UNKNOWN is an asserted claim, never an empty field, and never silently becomes an assumption | Claim | BIO_Evidence_and_Provenance | none |
| BR-004 | Every quantitative value carries a UCUM unit, or it is rejected | Claim, OverlayValue, Process | INV-04 | none |
| BR-005 | No entity or claim may exceed its subsystem's declared maximum scale level, even when correct and well-sourced | Entity, PRD_FR_Scale_Bridging | BIO_Scale_Contract, D-001 | only a Scope Reopen changes the declaration |
| BR-006 | Containment (`part_of`) is single-parent and acyclic; multi-system participation uses membership relations | Entity, Relationship | D-006 | a genuine anatomical ambiguity is recorded as such, never resolved by picking |
| BR-007 | No overlay operation may write to the reference model, at any privilege level including administrative | Overlay, PRD_FR_Personalization | D-004 | none |
| BR-008 | Individual data never enters the reference model, a published release, a training corpus, or an aggregate without separate explicit revocable authorization | Individual, Overlay | D-004, PRD_Security_Requirements | none in Phase 7; aggregate use is out of scope rather than permitted |
| BR-009 | Every canonical change carries an Approval record naming a human reviewer | Approval, PRD_FR_Curation | D-001 | none |
| BR-010 | A reviewer may accept content only within their declared subsystem and level competence | Review | PRD_FR_Curation | escalation to the Biology Lead, recorded |
| BR-011 | Conflicting claims are both retained; the system never silently selects between credible sources | Claim | BIO_Evidence_and_Provenance | adjudication creates a new claim citing both; it never deletes either |
| BR-012 | Every biological claim carries a species field, and cross-species claims carry a transfer justification | Claim | INV-12 | none |
| BR-013 | Share-alike (T1) and reference-only (T2) content never appears in the T0 ontology or evidence layers | GeometryAsset, Source | D-003 | none |
| BR-014 | Every generated natural-language assertion resolves to a graph claim id, or it is not rendered | RetrievalResponse | INV-14 | none |
| BR-015 | An untyped association is never rendered, described, or traversed as a mechanism or a causal claim | Relationship | D-007 | none |
| BR-016 | Compilation and representation status advance only through recorded, reviewed work — never by reformatting or re-ingest | Entity, Process | D-007 | none |
| BR-017 | A process cannot execute unless every parameter has a source, every coupling is declared, and capability limits are written | Process, ProcessRun | D-005, PRD_FR_Simulation | none |
| BR-018 | Cross-timescale-domain coupling that is not declared is refused at execution, never approximated | ProcessRun | D-005 | none |
| BR-019 | The system does not diagnose, treat, advise, or interpret clinically, on any surface, in response to any framing | all user-facing modules | BIO_Research_Charter | none |
| BR-020 | A published release is immutable; a mistaken release is superseded, never edited or withdrawn | KnowledgeRelease | PRD_FR_Versioning | none — withdrawal would break every citation |
| BR-021 | Coverage is reported as `n / declared_n` against the scope declared at scoping; the denominator narrows only by Scope Reopen | KnowledgeRelease, KPIs | PRD_Executive_Summary | none |
| BR-022 | Identifiers are never reused, renumbered, or repurposed after retirement | Entity | PRD_FR_Ontology | none |
| BR-023 | Agents generate no faster than review capacity absorbs; throttling engages before a queue becomes a rubber stamp | CurationTask | PRD_FR_Curation | operator override is recorded and time-boxed |

## Conflicts & Precedence
Where two rules could collide, the ordering is:

1. **BR-019 (non-diagnostic)** outranks everything. No completeness, usefulness,
   or user-satisfaction consideration overrides it.
2. **BR-007 and BR-008 (reference immutability, individual data isolation)**
   outrank any feature requirement. A capability that requires violating either
   is not built.
3. **BR-002, BR-003, BR-011 (evidence integrity)** outrank coverage. It is always
   better to have less content than content graded above its evidence — this
   resolves the standing tension between BR-021's coverage targets and the
   grading rules, and it resolves in favour of grading.
4. **BR-005 (declared depth)** outranks correctness of individual content. Correct
   content exceeding the declaration is rejected, because a declaration that
   yields to good content is not a declaration.
5. **BR-013 (licence tiering)** outranks coverage. A build ships with less
   geometry rather than with an undisclosed obligation.
6. **BR-023 (throttling)** outranks throughput targets. A backlog reviewed
   carelessly is worse than a backlog.

The pattern: **integrity rules outrank completeness rules, in every case.** That
is the product's central trade and it is made here explicitly rather than being
resolved ad hoc each time it comes up.
