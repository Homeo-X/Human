---
doc: PRD_FR_Simulation
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Simulation

## Purpose & Scope
Executing process specifications: the timescale-domain runtime, the gate a
process must pass to become executable, capability limits on every result, and
the composition rules between domains. Implements D-005 — no global clock.
Boundary: process specification → PRD_FR_Process_Models; visualization of results
→ TECH_UI_UX_Design; individual parameters → PRD_FR_Personalization.

**Phase status:** Phase 6. Nothing here is built. It is specified now because the
process and parameter records must carry what execution will need, and retrofitting
that later would mean re-curating every process.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Student | to watch a mechanism run rather than read it | timing and dependency become intuitive |
| Educator | to change one parameter and see what follows | I can teach the causal structure |
| Researcher | to know exactly which parameters produced a result | I can reproduce or challenge it |
| Researcher | to be told what a result does not mean | I do not overinterpret a model output |
| Curator | to be prevented from making a process executable on unsourced parameters | a simulation cannot exceed its data quietly |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-SIM-001 | Must | A process becomes executable only when every parameter has a source, every coupling is declared, and capability limits are written | Given a process with one unsourced parameter, when promotion to executable is attempted, then it fails naming the parameter; and given all conditions met and reviewed, then it succeeds | This is BRB-20's gate; it is the difference between a simulation and a demo |
| FR-SIM-002 | Must | Each process executes in its declared timescale domain; there is no global clock | Given two processes in different domains, when both run, then each advances on its own domain and composition occurs only through a declared rule; and given an attempt to couple domains with no rule, then execution is refused | D-005 in one requirement |
| FR-SIM-003 | Must | Every simulation result carries its capability limits, parameter set, parameter provenance, and the release it ran against | Given any result, when returned, then limits, parameters with sources, and release id accompany it; and given a result displayed without them, when reviewed, then it is a defect | A number without its limits is the most portable form of misinformation this system could produce |
| FR-SIM-004 | Must | A result states what it does not represent | Given a cardiac contraction result, when displayed, then it states that it models one exemplar cardiomyocyte's mechanism and not a beating human heart; and given any result, then the analogous statement is present | Users generalize from animations instinctively; the statement must be adjacent to the animation, not in a footnote |
| FR-SIM-005 | Must | Undeclared couplings are refused at execution, not approximated | Given a request to run two processes whose coupling is marked unsupported, when submitted, then execution is refused naming the missing composition rule; and given a supported coupling, then it runs | Refusing is the honest behaviour; approximating an unknown coupling manufactures physiology |
| FR-SIM-006 | Must | Runs are reproducible: the same inputs, parameters, seeds, and release produce identical results | Given a run record, when re-executed, then the result is identical; and given any nondeterminism, when present, then its seed is recorded and reported | G-07 depends on this; irreproducible results are not results |
| FR-SIM-007 | Should | Parameter sensitivity is reportable for any executable process | Given a run, when sensitivity is requested, then the parameters the result is most sensitive to are ranked | The parameters that matter most are usually the ones with the weakest evidence — surfacing that pairing is the point |
| FR-SIM-008 | Should | Execution respects a declared cost and time budget and stops honestly at the ceiling | Given a run exceeding its wall-clock budget, when the ceiling is reached, then it stops at a declared safe point and reports partial state as partial; and given completion within budget, then the full result is returned | Silent truncation would make an incomplete run look like a finished one |
| FR-SIM-009 | Should | Simulation never writes to the reference model | Given a run producing state, when it completes, then state persists in the run record only; and given an attempted write to a reference entity, then INV-08's discipline applies and it is refused | Same guarantee as personalization, same reason |
| FR-SIM-010 | Could | Runs can be compared across releases or parameter sets | Given two run records, when diffed, then differing parameters and resulting state divergence are reported | Makes the effect of new evidence on model behaviour visible |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Process | R | executable specifications |
| ProcessRun | RW | run record: parameters, seeds, results, limits, release |
| Claim | R | parameter values and provenance |
| KnowledgeRelease | R | the release a run pins |
| Overlay | R | Phase 7 only: individual parameters, read-only |

## States & Transitions
Run lifecycle: `queued` → `running` → (`completed` | `stopped_at_budget` |
`refused` | `failed`). `refused` is a first-class outcome carrying the reason —
an undeclared coupling or an unsourced parameter — and is not an error to be
retried blindly. `stopped_at_budget` returns partial state explicitly labelled
partial.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: a request to run a process at `structured` status | refused with the promotion gate's unmet conditions listed | FR-SIM-001 |
| Invalid input: a parameter outside its declared valid range | refused with the range and its source shown; the run does not proceed on a clamped value | FR-SIM-003 |
| Permission denied: not applicable for reference-model runs; personalized runs are Phase 7 | stated explicitly | — |
| Concurrency: two runs of the same process with different parameters | independent run records; no shared mutable state | FR-SIM-006 |
| External dependency failure: compute backend unavailable | the run stays `queued` with the failure reported; a partial result is never fabricated | FR-SIM-008 |
| Scale extreme: a run requesting a duration far beyond its timescale domain | refused with the domain's valid range stated — a millisecond-domain process is not run for a simulated year | FR-SIM-002 |
| A result looks physiologically implausible but the run is correct | returned as-is with its limits; the model reports what its parameters imply and does not silently correct toward expectation | FR-SIM-003 |
| A user asks what the result means for a person | the non-diagnostic boundary is returned; the system does not translate a mechanism run into an individual claim | FR-SIM-004 |

## Dependencies
- On other modules: PRD_FR_Process_Models (specifications and the executable
  gate), PRD_FR_Evidence (parameter provenance), PRD_FR_Validation (INV-06,
  INV-08), PRD_FR_Versioning (release pinning), PRD_FR_Personalization (Phase 7
  parameters, read-only)
- On external integrations: numerical solver libraries; compute backend

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Executable processes with fully sourced parameters | G-03 | 100%, enforced by the gate |
| Runs reproducing identically from their run record | G-07 | 100% |
| Results carrying capability limits and parameter provenance | G-03 | 100% |
| Undeclared couplings executed | G-05 | 0, enforced |

## Out of Scope for This Module
- Whole-body simulation — explicitly and permanently out of scope
- Predicting individual physiological outcomes
- Parameter fitting or inference from data
- Real-time interactive simulation of coupled multi-domain physiology

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| Which numerical methods are admissible per timescale domain, and who validates the choice? | Research Engineer | Phase 6 |
| How is a `refused` outcome presented so it reads as integrity rather than breakage? | Model Reviewer | Phase 6 |
| Can sensitivity analysis be run cheaply enough to be a default rather than an option? | Research Engineer | Phase 6 |
