---
doc: BIO_Physiological_Processes
tier: standard+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Physiological Processes

_What happens, and how. One `BPR` per process. A process that is named but has no
inputs, outputs, state variables, or timescale is a label — and the rubric
(BRB-17) treats it as one._

## Process Register
| ID | Process | Subsystem | Level(s) | Timescale | Representation Status | Evidence Class |
|---|---|---|---|---|---|---|
| BPR-01 | Cardiac excitation–contraction coupling | cardiovascular | L3, L7, L8, L9, L10 | milliseconds | structured | EVC-2 |
| BPR-02 | Cardiac cycle (mechanical) | cardiovascular | L0, L3 | seconds | structured | EVC-2 |
| BPR-03 | Systemic oxygen transport | cardiovascular | L0, L3, L6, L9 | seconds | narrative | EVC-2 |
| BPR-04 | Blood pressure regulation (baroreflex and RAAS) | cardiovascular, urinary | L0, L2, L3 | seconds to hours | narrative | EVC-2 |
| BPR-05 | Alveolar gas exchange | respiratory | L4, L5 | seconds | narrative | EVC-2 |
| BPR-06 | Glomerular filtration | urinary | L4, L5 | minutes | narrative | EVC-2 |
| BPR-07 | Tubular reabsorption and secretion | urinary | L4, L5 | minutes | narrative | EVC-2 |
| BPR-08 | Neural signalling (action potential propagation) | nervous | L5, L7 | milliseconds | narrative | EVC-2 |
| BPR-09 | Thermoregulation | integumentary, nervous | L0, L2, L3, L5 | seconds to hours | narrative | EVC-2 |
| BPR-10 | Fluid and electrolyte balance | urinary, cardiovascular | L0, L2, L5 | minutes to hours | narrative | EVC-2 |

Only `BPR-01` is specified in full below, at `structured` status, as the Phase 0
vertical slice. The remaining nine are registered at `narrative` status: the seed
corpus describes them, the model has not yet compiled them (D-007). **Registering
a process is not modelling it**, and the status column is what keeps that
distinction visible.

_Representation status vocabulary: `narrative` (prose mechanism only) ·
`structured` (inputs, outputs, and state formalized) · `parameterized`
(quantities with sources attached) · `executable` (runnable in the simulation
runtime). No process in this model is `executable`, and none will be before
Phase 6._

## Process Specifications

### BPR-01 — Cardiac excitation–contraction coupling
- **Claim:** an arriving action potential at the cardiomyocyte membrane is
  converted into mechanical shortening of the sarcomere, and thence into
  ventricular pressure.
- **Level / spatial scale:** L3 (chamber pressure), L7 (cardiomyocyte), L8
  (sarcoplasmic reticulum, T-tubule, sarcomere), L9 (channels, calcium, actin,
  myosin), L10 (cross-bridge cycle kinetics). This is a spanning process per
  BIO_Scale_Contract §Entities Spanning Several Levels.
- **Timescale:** characteristic ~200–300 ms from depolarization to peak tension;
  domain: milliseconds. Holds for adult human ventricular myocardium at
  physiological rate; the relationship changes at extreme rates, which is a
  stated boundary, not an omission.
- **Inputs:** membrane action potential (from BPR-02's conduction step);
  extracellular Ca²⁺ (`CHEBI:29108`); ATP (`CHEBI:15422`).
- **Outputs:** sarcomere shortening; developed tension; Ca²⁺ returned to the
  sarcoplasmic reticulum; ADP and inorganic phosphate.
- **State variables:**

  | Variable | Unit (UCUM) | Normal range | Evidence class | Note |
  |---|---|---|---|---|
  | cytosolic Ca²⁺ concentration, diastolic | `nmol/L` | 100–200 | EVC-3 | predominantly from isolated myocyte preparations; in-vivo human values are inferred |
  | cytosolic Ca²⁺ concentration, systolic peak | `umol/L` | ~1 | EVC-3 | same limitation |
  | sarcomere length, resting | `um` | 1.8–2.2 | EVC-2 | the Frank–Starling operating range |
  | developed tension | `mN/mm2` | reported per preparation | EVC-4 | preparation-dependent; a single human in-vivo figure is not available and is not invented |
  | time to peak tension | `ms` | 150–250 | EVC-3 | varies with rate and temperature |

- **Mechanism:** membrane depolarization → L-type Ca²⁺ channel opening in the
  T-tubule → small Ca²⁺ influx → ryanodine-receptor activation on the
  sarcoplasmic reticulum → calcium-induced calcium release → cytosolic Ca²⁺ rise
  → Ca²⁺ binds troponin C → tropomyosin shifts, exposing actin binding sites →
  myosin cross-bridge attachment → ATP-dependent power stroke → filament sliding
  → sarcomere shortening → tension → chamber pressure. Relaxation: SERCA pumps
  Ca²⁺ back into the sarcoplasmic reticulum and the Na⁺/Ca²⁺ exchanger extrudes
  the remainder → troponin releases Ca²⁺ → cross-bridges detach.
- **Dependencies:** BPR-02 supplies the triggering action potential. No process
  currently in the register depends on BPR-01's output; BPR-02's pressure step
  will, once compiled.
- **Feedback loops:** length-dependent activation (Frank–Starling) — greater
  end-diastolic sarcomere length increases myofilament Ca²⁺ sensitivity and
  developed tension. **Damping:** the relationship is bounded by the descending
  limb of the length–tension curve above roughly 2.2 µm, and by pericardial
  restraint at the chamber level.
- **Failure states:**

  | Failure | Consequence | Downstream |
  |---|---|---|
  | ATP depletion | cross-bridges cannot detach | rigor; loss of relaxation before loss of contraction |
  | SERCA impairment | slowed Ca²⁺ reuptake | impaired relaxation, elevated diastolic Ca²⁺ |
  | L-type channel blockade | reduced trigger Ca²⁺ | reduced developed tension |
  | Ryanodine-receptor Ca²⁺ leak | diastolic Ca²⁺ elevation | reduced SR load, arrhythmogenic potential |

  These are represented as mechanism failure modes, **not as diagnoses**. The
  model states what breaks in the mechanism; it does not name diseases, and
  BIO_Research_Charter's non-diagnostic boundary applies to this table.
- **Evidence:** EVC-2 overall. The mechanism's structure is strongly supported
  and independently reproduced. Individual quantities are weaker than the
  mechanism — a point worth stating, because a well-established mechanism lends
  unearned credibility to the numbers inside it.
- **Known limitations:** quantitative parameters derive predominantly from
  animal and isolated-preparation work; human in-vivo values for cytosolic
  calcium do not exist at this resolution. Cross-species transfer is flagged per
  INV-12. Regional heterogeneity across the ventricular wall is real and is not
  represented. This specification describes one exemplar cardiomyocyte, not a
  population (SCL-07's `typed` mode).

## Multiscale Time
_Processes are not forced into one clock (D-005). These are the declared domains
and how processes in different domains compose._

| Timescale Domain | Range | Example Processes | Composition Rule |
|---|---|---|---|
| Molecular | ns – ms | channel gating, cross-bridge cycling (within BPR-01) | not composed directly with slower domains; enters them as a rate or an aggregate property |
| Cellular electrical | ms | action potential (BPR-08), excitation–contraction coupling (BPR-01) | composes with the organ domain by supplying a per-beat aggregate, never per-timestep coupling |
| Organ mechanical | 100 ms – s | cardiac cycle (BPR-02), alveolar gas exchange (BPR-05) | composes with the organism domain through cycle-averaged quantities |
| Organism regulatory | s – min | baroreflex arm of BPR-04, oxygen transport (BPR-03), glomerular filtration (BPR-06) | composes with slower domains through set-point adjustment |
| Endocrine | min – h | RAAS arm of BPR-04, thermoregulation (BPR-09), tubular reabsorption (BPR-07), fluid and electrolyte balance (BPR-10) | modifies parameters of faster domains rather than sharing their state |
| Immune | h – d | not yet registered | out of the current register |
| Remodelling | d – mo | not yet registered | out of the current register |
| Developmental | mo – y | out of scope | excluded per BIO_Research_Charter |

**The composition rule in one sentence:** a faster domain enters a slower one as
an aggregate or a parameter, never as a shared timestep. Any coupling not
described by a row above is **undeclared and therefore unsupported** — INV-06
fails on it rather than allowing an implicit link.

## Cross-Process Interactions
| Interaction | Processes | Type | Status |
|---|---|---|---|
| conduction supplies the trigger | BPR-02 → BPR-01 | output-to-input | declared, supported |
| contraction generates pressure | BPR-01 → BPR-02 | output-to-input, same subsystem, adjacent domains | declared, supported |
| pressure drives filtration | BPR-02 → BPR-06 | cross-subsystem, adjacent domains | declared; unsupported until BPR-06 is compiled |
| filtration affects volume, which affects pressure | BPR-06 → BPR-04 → BPR-02 | closed regulatory loop across three domains | declared; **unsupported** — this loop crosses three timescale domains and its composition rule is not established. Named here so that it is visibly unsupported rather than silently absent |
| autonomic input modulates rate | nervous → BPR-02 | parameter modulation | declared; unsupported until compiled |

Contention: no two registered processes currently write the same state variable.
When they do — cytosolic calcium is the first likely case, shared between BPR-01
and any future calcium-signalling process — the contention must be resolved by an
explicit ownership or arbitration rule before either becomes executable.

## Processes Named But Not Modelled
_A process a user might reasonably expect and will not find, with the reason.
This section existing is the point._

| Process | Why Not Modelled | Would Require |
|---|---|---|
| Immune response | the immune system is declared to L3, and its real biology is at L6–L9 | raising the immune subsystem's declared depth, and cell-population representation at scale |
| Digestion and absorption | digestive system declared to L3 | tissue and transporter-level representation |
| Hormone synthesis pathways | endocrine declared to L3 | L9 mechanism curation per hormone |
| Muscle contraction (skeletal) | musculoskeletal declared to L4 | tissue and sarcomere-level representation; note that the cardiac mechanism in BPR-01 is **not** transferable — the mechanisms differ in their calcium handling, and presenting one as the other would be a scale-and-class error |
| Wound healing, bone remodelling, tissue turnover | remodelling timescale domain has no registered processes | a domain composition rule for day-to-month processes |
| Anything in development or aging | out of scope | a scope reopen (BIO_Research_Charter) |
| Consciousness, cognition, affect | no admissible representation at these levels | not a scope decision but a representability one; recorded so its absence is not read as an oversight |
