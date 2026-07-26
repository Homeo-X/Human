---
doc: RES_Reproducibility
tier: standard+   # foldable into Data_Management/Impl_Notes for small scopes
version: 0.0.0
status: template
owner: architect
last_updated: —
---

# Reproducibility

## Reproduction Levels (declare the target)
| Level | Meaning | Target? |
|---|---|---|
| Re-run | same machine, same env, same seeds → same numbers | Must |
| Re-create | clean checkout + documented setup → same conclusions | Must |
| Independent | another group, from the writeup alone → same conclusions | aspiration; the writeup is written toward it |

## Environment
Pinned everything: language/runtime versions, dependency lockfile,
container/image if used, hardware notes where results are
hardware-sensitive (GPU nondeterminism stance stated).

## Determinism & Seeds
Sources of nondeterminism enumerated (RNG, parallelism, floating-point
reduction order, external services) and per-source: controlled, tolerated
(with declared tolerance), or documented as irreducible.

## One-Command Reproduction
`<command>` reruns EXP-<id> end-to-end from raw generation to figures.
Partial targets allowed (`repro figures` from archived raw) but the full
path exists and is CI-exercised at the declared cadence.

## Testable Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | Notes |
|---|---|---|---|---|
| FR-REPR-001 | Must | Re-run level: identical results per determinism stance | Given the recorded env and seeds, when EXP-01 reruns, then reported metrics match within declared tolerance | |
| FR-REPR-002 | Must | Re-create level: clean-checkout reproduction | Given a fresh clone and the setup doc only, when the one-command path runs, then conclusions (DC dispositions) are unchanged | |
| FR-REPR-003 | Must | Writeup claims carry artifact refs | Given any quantitative claim, when checked, then it names its EXP/DC and the artifact hash or run id | |

## Archival
What is frozen at writeup time (code tag, env lock, raw data snapshot,
figure sources) and where the frozen bundle lives.
