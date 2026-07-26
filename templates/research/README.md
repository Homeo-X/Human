# Research Profile — Study & Experiment Document Set

Specification of the **research** profile (PROFILES.md). For empirical
studies, simulation campaigns, and computational experiments — anywhere
the deliverable is *justified knowledge*, not a product. Everything not
stated here follows the framework unchanged.

## Role mapping
| Framework Role | Acts As | Owns (research profile) |
|---|---|---|
| Orchestrator | Program Lead | scoping, MANIFEST, cross-review — unchanged |
| PM | Principal Investigator | Research_Charter (question, HYP register), Experiment_Designs, Analysis_Plan, Risks, shared Scope_and_Roadmap |
| UX | Methodologist / Reviewer | Methodology (validity threats), the methods-review pass A over Charter/Experiments/Analysis via RESEARCH_RUBRIC → docs/RES_Methods_Review.md; owns clarity of the eventual reporting (figures/claims plan) |
| Architect | Research Engineer | Data_Management, Reproducibility, TECH files (compute, pipelines), NFRs (run budgets) |

## Document set per tier
| Tier | Set |
|---|---|
| **Light** (pilot, exploration, single question) | `light/RES_Study_Brief.md` + PRD_Decision_Log + light/TECH_Implementation_Notes |
| **Standard** (a study / simulation campaign) | RES core: Research_Charter, Methodology, Experiment_Designs, Data_Management, Analysis_Plan, Reproducibility + RESEARCH_RUBRIC pass (→ RES_Methods_Review) + shared: Scope_and_Roadmap (phases = pilot → main runs → analysis → writeup), Risks_and_Constraints, Decision_Log, Acceptance_Criteria_and_DoD (gates below) + TECH: System_Architecture, Data_Design |
| **Full** (multi-study program, external collaborators, publication-bound) | Standard + Security_Requirements (sensitive data), External_Integrations, per-study Experiment_Design files, FR modules for tooling the program builds |

## Folds (Standard)
| File | Fold into |
|---|---|
| RES_Methodology | Research_Charter §Methods (simple single-method studies) |
| RES_Reproducibility | TECH_Implementation_Notes or Data_Management (small scopes) |
| RES_Data_Management | never omitted — data without provenance is anecdote |

## Acceptance analog
Given/When/Then becomes **pre-registered decision criteria**: "given data
pattern X, we conclude Y / update HYP-n this way" — written in the
Analysis_Plan BEFORE data exists. DoD gates: analysis plan frozen before
main runs; every claim in a writeup traces to an EXP + criterion;
reproduction from clean checkout succeeds.

## Checklist additions (AGENTS.md §5 applies in full, plus)
compute budget & run scheduling · seed/randomness policy · data ethics &
sharing (licenses, PII, embargo) · negative-result disposition (where do
failed hypotheses get reported?) · provenance chain (raw → processed →
figure) · stopping rules (what ends a run early, honestly) ·
multiple-comparisons posture · archival (what survives the project).

## Study-type lens (binds at scoping, like the game genre lens)
| Study Type | Extra-Depth Docs | Type-Specific Prompts |
|---|---|---|
| Simulation campaign (ALife/agents/physics) | Experiment_Designs, Reproducibility | seed policy, parameter sweeps as EXP grid, emergence metrics defined pre-run, cherry-picked-run guards |
| Controlled experiment | Methodology, Analysis_Plan | power/sample size, randomization, blinding where possible |
| Observational / dataset study | Data_Management, Methodology | selection bias, confound register, causal-claim discipline |
| Benchmark / evaluation | Analysis_Plan, Reproducibility | baseline fairness, metric gaming, held-out hygiene |
| Theory + formal work | Research_Charter, Methodology | proposition register in place of EXP grid; proof obligations as the acceptance analog |

## The research trace chain (formal, specgraph-checked)
Every confirmatory hypothesis completes this chain or names the missing
link as an open question:

    HYP-n → CM-n (mechanism) → construct rows (operationalization)
        → EXP-nn (tests) → controls/baselines → metrics (measurement)
        → analysis method → DC-n (decision criterion)

Chain edges live in the tables' reference columns (`Explains`, `Tests`,
`For`); `tools/specgraph.py` warns on defined-but-unreferenced HYP and DC
nodes — a hypothesis no experiment tests, or a criterion deciding
nothing, is a broken chain.

## ID registers (additions)
`HYP-N` hypotheses (Research_Charter) · `EXP-NN` experiments
(Experiment_Designs) · `CM-N` causal mechanisms (Methodology) · `DC-N`
decision criteria (Analysis_Plan). Testable tooling requirements keep `FR-<AREA>-NNN`
(areas: DATA, REPR).
