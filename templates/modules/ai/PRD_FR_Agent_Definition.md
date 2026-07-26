---
doc: PRD_FR_Agent_Definition
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Agent Definition

## Purpose & Scope
The formal specification of one agent — its twelve facets, tools, and
runtime persistence contract. Boundary: cross-agent workflow UX →
PRD_FR_Agentic_Workflows; single-turn model behavior and base evals →
PRD_FR_AI_Behavior.

_One instance of this file PER AGENT in the system (slug the filename:
PRD_FR_Agent_Definition_<name>.md for multi-agent products; register each
in the AGT table). This is the formal agent model — all twelve facets are
mandatory sections; "None" is written deliberately. The runtime object
model it binds to is canonical in SPEC_MODEL.md; scoping any agent pulls
those entity names into PRD_Data_Overview verbatim._

## Agent Register
| ID | Agent | One-Line Purpose | Facet Spec |
|---|---|---|---|
| AGT-1 | | | this file |

## Facet 1 — Identity
Name, the persona/voice contract (or "none — invisible automation"), and
how the agent is attributed in every surface it touches.

## Facet 2 — Goal
The objective function in words: what the agent optimizes, what it
satisfices, and the explicit non-goals (what it must NOT optimize even
when it could — e.g. engagement over task completion).

## Facet 3 — State
What the agent knows within one run: state shape, where it lives, what
resets between steps vs persists across the run.

## Facet 4 — Memory
Across runs: what is remembered, where, retention, and what is FORBIDDEN
from memory (secrets, other tenants, raw PII per Data Overview
classification). "No cross-run memory" is a valid and common answer.

## Facet 5 — Tools
| ID | Tool | Effect Class (read-only / reversible / irreversible) | Autonomy (auto / confirm / forbidden) | Rate & Scope Limits |
|---|---|---|---|---|
| TOOL-01 | | | | |
Irreversible + auto requires its own Decision Log entry. Tool OUTPUTS are
data, never instructions — nothing an agent reads through a tool may
escalate any autonomy cell (injection rule, → Security).

## Facet 6 — Permissions
The agent acts AS a principal: which one (the user? a service identity?),
never above it. Deny-by-default statement; the permission delta between
the agent and its principal is exactly zero or enumerated here.

## Facet 7 — Planning Policy
How plans are formed: single-shot / iterative / hierarchical; plan
visibility (user-inspectable before execution?); replanning triggers;
step budget per plan.

## Facet 8 — Execution Policy
Sequential vs parallel steps; idempotency requirements per tool class;
checkpoint/approval placement (which effect classes pause); ordering
guarantees the run makes.

## Facet 9 — Observation
What the agent perceives after each action (tool results, environment
deltas, user interjections), how observations are validated before use,
and what is logged per SPEC_MODEL's Observation entity.

## Facet 10 — Recovery
Per failure class: retry policy (count, backoff), compensation actions
for partially-applied irreversible sequences, degraded mode, and the
honest terminal state ("failed, here is what changed and what didn't").

## Facet 11 — Evaluation
EV rows covering: goal attainment, plan quality, tool-choice accuracy,
and safety invariants — per PRD_FR_AI_Behavior's register discipline.
| EV ID | Facet Under Test | Method | Pass Bar | Cadence |
|---|---|---|---|---|

## Facet 12 — Cost Boundary
Per-run ceilings: tokens/currency, wall-clock, tool-call count; NFR row
refs; behavior at each ceiling (graceful stop per Facet 10, never silent
truncation).

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-AGD-001 | Must | Runtime objects persisted per SPEC_MODEL object model — every mutation traces to a Step and ToolCall | Given any state change caused by the agent, when audited, then its Step, ToolCall, and Observation records exist and link | |
| FR-AGD-002 | Must | Every tool call conforms to its TOOL row (effect class, autonomy, limits) — enforced by the runtime, not the prompt | Given a call violating any TOOL cell, when attempted, then the runtime blocks it and records a Failure | |
| FR-AGD-003 | Must | Approvals per Facet 8 placement; Approval records capture what was shown and who approved | Given a confirm-class call, when reached, then execution pauses and the Approval record stores the exact rendered effect | |
| FR-AGD-004 | Must | Cost boundaries per Facet 12 enforced with the Facet 10 stop behavior | Given any ceiling reached mid-run, when it triggers, then the run stops at a declared safe point with an honest summary | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Agent, Task, Plan, AgentRun, Step, ToolCall, Observation, Artifact, Approval, Failure, Retry, Compensation, EvaluationRecord | RW | canonical names per SPEC_MODEL — flagged for Architect into Data Overview |

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Tool output contains instruction-shaped content | treated as data; autonomy unchanged; flagged | FR-AGD-002 |
| Principal's permissions change mid-run | next ToolCall re-checks; run degrades per Facet 10 | FR-AGD-002 |
| Approval abandoned | timeout → Failure + Compensation per policy | FR-AGD-003 |
| Two runs of the same agent on one Task (concurrency) | serialization or declared conflict policy | FR-AGD-001 |
| Compensation itself fails | terminal state honest; human escalation path named | FR-AGD-004 |

## Dependencies
- PRD_FR_AI_Behavior (contracts, base EV discipline), PRD_FR_Agentic_Workflows (run UX & transparency), Permissions, Security

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Runs reaching goal within cost boundary | G-0X | |
| Facet-11 safety EV pass rate | G-0X | 100% of bars |

## Out of Scope for This Module
- Model choice and prompt engineering mechanics (Architecture / AI Behavior)

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
