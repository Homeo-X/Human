---
doc: PRD_FR_Process_Models
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Process Models

## Purpose & Scope
The specification of physiological and biochemical processes: inputs, outputs,
state variables, mechanisms, timescales, dependencies, feedback, and failure
states. This module produces process *specifications*; running them is
PRD_FR_Simulation, and the separation is deliberate — a specified process is not
a runnable one. Boundary: entity identity → PRD_FR_Ontology; execution → SIM;
level rules → PRD_FR_Scale_Bridging.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Student | to see a mechanism as an ordered causal chain in its spatial location | I learn how, not just what |
| Student | to see what breaks when a step fails | the mechanism becomes a model I can reason with |
| Educator | to distinguish a process the model has specified from one it has only named | I do not promise students something that is not there |
| Curator | to be prevented from declaring a process complete without its state variables | a label cannot masquerade as a model |
| Researcher | to see every parameter's source and measurement conditions | I can judge transferability myself |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-PHYS-001 | Must | Every process carries a representation status — narrative, structured, parameterized, or executable — visible wherever the process is | Given a `narrative` process displayed, when rendered, then its status is visible without interaction; and given an API response, then the status is in the payload | A named process rendered like a modelled one is BRB-17 |
| FR-PHYS-002 | Must | A process at `structured` status or above declares inputs, outputs, state variables, mechanism, and timescale, with no blank fields | Given a process promoted to `structured` with an empty state-variable table, when validated, then promotion fails naming the field; and given all fields populated, then it succeeds | "Unknown" is a valid entry and must be as easy to record as a value |
| FR-PHYS-003 | Must | Every process input and output resolves to a defined ontology entity | Given a process output naming an undefined molecule, when validated, then INV-03 fails; and given all references resolving, then it passes | The rejection should offer to create the missing entity as a curation task |
| FR-PHYS-004 | Must | Every process declares a timescale domain from BIO_Physiological_Processes §Multiscale Time | Given a process with no timescale domain, when validated, then INV-06 fails; and given a declared domain, then it passes | Timescale is what makes two processes comparable; it belongs in the header, not the detail |
| FR-PHYS-005 | Must | A spanning process declares each level it acts at and what it contributes there | Given a process listing L3 through L9 without per-level contributions, when validated, then it is flagged incomplete; and given complete declarations, then it passes | One object at several levels — the display must not fragment it |
| FR-PHYS-006 | Must | Every state variable carries a unit, a normal range where one exists, and an evidence class | Given a state variable with a value and no unit, when validated, then INV-04 fails; and given a variable with unit, range, and class, then it passes | The class belongs on the variable, not on the process — a strong mechanism can contain weak numbers |
| FR-PHYS-007 | Must | Every declared feedback loop names its damping mechanism, and every process names its failure states | Given a process declaring a reinforcing loop with no damping named, when validated, then it is flagged; and given damping and failure states named, then it passes | This is BRB-21; a drawn loop with no damping is a diagram, not a model |
| FR-PHYS-008 | Must | Failure states are represented as mechanism failures, never as diagnoses | Given a failure state displayed, when rendered, then it names the mechanistic consequence and carries the non-diagnostic boundary; and given content that names a disease as a failure state, when reviewed, then it is rejected | The most tempting overreach in the whole product; the gate belongs in curation, not in wording |
| FR-PHYS-009 | Should | Cross-process interactions are declared, and each is marked supported or unsupported | Given two processes whose coupling crosses three timescale domains with no composition rule, when declared, then it is recorded as unsupported and displayed as such; and given an adjacent-domain coupling with a rule, then it is supported | An unsupported coupling named openly is far better than one quietly absent |
| FR-PHYS-010 | Should | Processes named but not modelled are enumerated with the reason and what modelling would require | Given a user asking about digestion, when the model has no compiled process, then the named-but-not-modelled entry is returned with its reason; and given a modelled process, then the specification is returned | This list is a feature; it is the model's own account of its edges |
| FR-PHYS-011 | Should | State variables written by more than one process are detected and require an explicit ownership or arbitration rule | Given two processes writing cytosolic calcium with no rule, when validated, then it is flagged before either becomes executable; and given a rule, then it passes | Contention discovered at execution time is discovered too late |
| FR-PHYS-012 | Could | A process specification can be exported in a standard systems-biology exchange format | Given a `parameterized` process, when exported, then a valid exchange-format document with provenance annotations is produced | Interoperability matters more than a bespoke format here |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Process | RW | the BPR specification |
| Entity | R | inputs, outputs, participants |
| Claim | RW | parameters and their provenance |
| ScaleLevel | R | spanning declarations |
| Relationship | R | participation and realization edges |
| CurationTask | W | promotion and contention-resolution tasks |

## States & Transitions
Representation status: `narrative` → `structured` → `parameterized` →
`executable`. Forward only, one step per reviewed promotion. Promotion to
`executable` additionally requires PRD_FR_Simulation's gate: every parameter
sourced, every coupling declared, capability limits written. A process may sit at
`structured` indefinitely; that is a valid, honest, permanent state.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: a subsystem with no compiled processes | returns the named-but-not-modelled list rather than nothing | FR-PHYS-010 |
| Invalid input: a mechanism step referencing an undefined entity | rejected with an offer to raise an entity-creation task | FR-PHYS-003 |
| Permission denied: a non-curator promotes a process | rejected; the proposal is queued | FR-PHYS-002 |
| Concurrency: two curators promote the same process | first wins; the second is rejected with current status, and promotion is never applied twice | FR-PHYS-002 |
| External dependency failure: a parameter source is unresolvable at validation | the process is held below `parameterized` rather than promoted with an unverified parameter | FR-PHYS-006 |
| Scale extreme: a process with dozens of state variables | grouped by level and by role; the display never becomes a flat table of numbers | FR-PHYS-005 |
| A process's mechanism is well-supported but its parameters are all EVC-4 | both grades shown separately; the process is not promoted to `parameterized` on mechanism strength | FR-PHYS-006 |
| A user asks what happens when a step fails, and the honest answer is a disease | the mechanistic consequence is given; the disease is not named, and the boundary is stated | FR-PHYS-008 |

## Dependencies
- On other modules: PRD_FR_Ontology (participants), PRD_FR_Evidence (parameter
  provenance), PRD_FR_Scale_Bridging (spanning), PRD_FR_Validation (INV-03,
  INV-04, INV-06), PRD_FR_Simulation (the executable gate), PRD_FR_Curation
- On external integrations: curated pathway databases as sources; systems-biology
  exchange formats for export

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Processes at `structured` or above with no blank mandatory fields | G-05 | 100%, enforced |
| Process parameters carrying unit, conditions, and evidence class | G-03 | 100% |
| Declared cross-process couplings marked supported or unsupported | G-04 | 100% |
| Processes named-but-not-modelled that are enumerated rather than absent | G-03 | 100% |

## Out of Scope for This Module
- Executing processes (PRD_FR_Simulation)
- Diagnosing or naming diseases
- Discovering mechanisms — the module records mechanisms from sources
- Parameter fitting or estimation from data

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| What arbitration rule governs a state variable written by two processes? | Research Engineer | Phase 6 |
| Does the failure-state display survive contact with clinically-minded users without becoming diagnostic? | Model Reviewer | Phase 3 |
| Which exchange format carries provenance annotations well enough to be worth supporting? | Research Engineer | Phase 6 |
