---
doc: BIO_Physiological_Processes
tier: standard+
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Physiological Processes

_What happens, and how. One `BPR` per process. A process that is named but has no
inputs, outputs, state variables, or timescale is a label — and the rubric
(BRB-17) treats it as one._

## Process Register
| ID | Process | Subsystem | Level(s) | Timescale | Representation Status | Evidence Class |
|---|---|---|---|---|---|---|
| BPR-01 | | | | | | |

_Representation status vocabulary: `described` (prose mechanism only) ·
`structured` (inputs/outputs/state formalized) · `parameterized` (quantities with
sources attached) · `executable` (runnable in the simulation runtime)._

## Process Specifications
_One subsection per `BPR`. Every field is mandatory; "unknown" is a valid entry
and is recorded as such, never left blank._

### BPR-NN — <Process Name>
- **Claim:** what this process does, in one sentence
- **Level / spatial scale:**
- **Timescale:** characteristic duration and the range over which it holds
- **Inputs:** entities consumed — each must resolve to a defined ontology entity
- **Outputs:** entities produced — same rule
- **State variables:** name, unit, normal range, source
- **Mechanism:** the causal chain, step by step
- **Dependencies:** other `BPR` this one requires
- **Feedback loops:** each with its damping mechanism
- **Failure states:** what breaks, what the downstream consequence is
- **Evidence:** `EVC` class + provenance
- **Known limitations:** what this representation deliberately omits

## Multiscale Time
_The timescale map. Processes are not forced into one clock; state the clock
domains and how processes in different domains are composed._

| Timescale Domain | Range | Example Processes | Composition Rule |
|---|---|---|---|

## Cross-Process Interactions
_Where one process's output is another's input, and where two processes contend
for the same state variable._

## Processes Named But Not Modelled
_Explicit list. A process a user might reasonably expect and will not find, with
the reason. This section existing is the point._

| Process | Why Not Modelled | Would Require |
|---|---|---|
