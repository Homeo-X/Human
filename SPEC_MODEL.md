# SPEC_MODEL.md — The Canonical Specification Model

The framework is a **specification compiler**. Markdown is the canonical,
human- and agent-editable *serialization*; this file defines the model
that serialization encodes; `tools/specgraph.py` is the front-end that
parses serialization into a typed IR; renderers are back-ends.

    Human Brief
        ↓  (intake + scoping — AGENTS.md §4)
    Markdown docs  ←— canonical serialization (edited, diffed, reviewed)
        ↓  (specgraph.py: parse + validate)
    Spec IR (typed JSON)
        ↓
    ┌───────────────┬───────────────────┬─────────────────────┐
    Graph checks    Module brief         Trace report
    (validation)    (--brief: agent      (--trace: FR ↔ code)
                    context renderer)

Drift between serialization and IR is a validation failure, never a merge
problem — nothing is ever edited in the IR (AGENTS.md §10).

## Node kinds
| Kind | ID Register | Defined In | Key Fields |
|---|---|---|---|
| goal/kpi | G-NN | Exec Summary / briefs | statement, baseline, target, measure |
| requirement | FR-AREA-NNN | FR modules, GDD/RES/DEV docs | priority, statement, acceptance, ux-notes |
| business-rule | BR-NNN | Business Rules | statement, applies-to, source |
| nfr | NFR-NNN | NFR register | category, number, measured-by |
| risk | RSK-NN | Risks | type, likelihood, impact, mitigation |
| use-case | UC-NN | User Flows | actor, goal, flow, fr-refs |
| decision | D-NNN | Decision Log | status, alternatives, consequences, reversibility, affects, supersedes |
| evaluation | EV-AREA-NNN | AI modules | method, dataset, bar, cadence |
| entity | (name) | Data Overview | attributes, lifecycle, classification |
| notification | NTF-NN | Notification catalogs | trigger, audience, channels |
| pillar | PIL-N | Game Concept | rules-in, rules-out |
| mechanic | MECH-NN | Core Loop | rules, interactions, tuning |
| archetype | ARCH-NN | Game AI | role, behavior, counterplay |
| hypothesis | HYP-N | Research Charter | statement, type, kill-condition |
| experiment | EXP-NN | Experiment Designs | tests, conditions, metrics |
| decision-criterion | DC-N | Analysis Plan | for, pattern, conclusion, threshold |
| causal-mechanism | CM-N | Methodology | claim, estimand, adjustment |
| agent | AGT-N | Agent Definitions | 12 facets (see below) |
| tool | TOOL-NN | Agent Definitions | effect class, autonomy, limits |
| challenge | CH-NN | Red-Team Review | question class, severity, disposition |
| rubric-item | RUB/RRB/BRB-NN | rubrics | check, verification, disposition |
| scale-level | SCL-NN | BIO Scale Contract | level, representation mode, evidence model, resolution limit |
| biological-process | BPR-NN | BIO Physiological Processes | inputs, outputs, state vars, timescale, failure states |
| evidence-class | EVC-N | BIO Evidence & Provenance | admits, sources, forbidden promotion |
| invariant | INV-NN | BIO Validation Framework | rule, enforced-by, failure, severity |

## Edge kinds (trace links)
`tests` (EV/EXP → FR/HYP) · `traces-to` (metric → KPI) · `touches`
(FR → entity) · `affects` (decision → files/IDs) · `supersedes` (D → D) ·
`serves` (MECH/verb → PIL) · `implements` (code/test ref → FR) ·
`operationalizes` (construct → HYP) · `decides` (DC → HYP) ·
`explains` (CM → HYP) · `uses` (agent → tool) · `challenges` (CH → any) ·
`represented-at` (entity → SCL) · `graded-by` (claim → EVC) · `constrains`
(INV → BPR/entity/overlay).
Edges are expressed in serialization as ID references and named table
columns; specgraph materializes them.

## The agent runtime object model (first-class)
For agentic systems, these are canonical entity names — any agentic module
scoped into a spec carries them into PRD_Data_Overview under exactly these
names: **Agent, Task, Plan, AgentRun, Step, ToolCall, Observation,
Artifact, Approval, Failure, Retry, Compensation, EvaluationRecord.**
Their relationships: Task 1—n AgentRun 1—n Step; Step 0—n ToolCall 1—n
Observation; Step 0—n Artifact; ToolCall 0—1 Approval; Step 0—n Failure
0—n Retry; Failure 0—1 Compensation; AgentRun 0—n EvaluationRecord.

## Renderers (back-ends)
Shipped: graph validation + append-only integrity (default) · `--json`
typed IR · `--brief <Module>` agent-context brief · `--trace <src>`
implementation trace (test-verified vs claimed) · memory renderers
`--why` `--impact` `--excluded` `--context` `--digest` `--stale`
`--history` (MEMORY.md). Roadmap (build on demand): test-plan renderer (acceptance rows →
test skeletons) · diff renderer (IR delta between two doc sets).
