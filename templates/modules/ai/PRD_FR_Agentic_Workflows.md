---
doc: PRD_FR_Agentic_Workflows
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Agentic Workflows

## Purpose & Scope
For products where the AI takes multi-step actions with tools, not just
single responses. Boundary: single-turn behavior, contracts, and evals →
PRD_FR_AI_Behavior (this module ASSUMES it is scoped alongside); the tools
themselves → their owning modules.

## Formal Model Binding
Each agent in this product has a PRD_FR_Agent_Definition file (AGT
register); this module owns the cross-agent workflow UX. The Action
Inventory below is the union view of the agents' TOOL tables — per-agent
authority lives in the Agent Definitions, and the runtime object model
(SPEC_MODEL.md) is the shared persistence contract.

## Action Inventory (the core artifact)
| Action/Tool | Effect (read-only / reversible write / irreversible) | Autonomy (auto / confirm / forbidden) | Rate/Scope Limits |
|---|---|---|---|
Every action gets an autonomy decision. Irreversible + auto requires an
explicit Decision Log entry justifying it.

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-AGNT-001 | Must | Plan-and-execute runs over the Action Inventory, honoring every autonomy column entry | Given an action marked confirm, when reached, then the run pauses for approval with the exact effect shown | |
| FR-AGNT-002 | Must | Run transparency: live step log — action, input summary, result — inspectable during and after | Given a completed run, when reviewed, then every mutation traces to a step | collapse detail by default, never hide it |
| FR-AGNT-003 | Must | Interruption & recovery: user can pause/cancel; partial work is either rolled back or explicitly kept, per action class | Given cancel mid-run, when confirmed, then state matches the declared policy per completed step | |
| FR-AGNT-004 | Must | Bounded autonomy: step budget, wall-clock budget, and cost budget per run (NFR refs); exhaustion = graceful stop + summary | Given any budget exhausted, when reached, then the run stops gracefully with a summary of work done | honest "why I stopped" |
| FR-AGNT-005 | Should | Human-in-the-loop checkpoints configurable per workflow (always / on-irreversible / never-for-read-only) | | |
| FR-AGNT-006 | Should | Failure containment: a failed step retries per policy; repeated failure degrades to suggestion mode, never silent skip | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| AgentRun / RunStep | RW | append-only step log; retention policy |

## States & Transitions
Run: queued → planning → executing → (awaiting_approval ⇄ executing) →
succeeded | partial | cancelled | failed. Define per terminal state what
happened to side effects.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Tool returns adversarial content (injection via tool output) | tool outputs treated as data; autonomy column cannot be escalated by content | FR-AGNT-001 |
| Two runs mutate the same resource (conflict) | lock or serialize; declared policy | FR-AGNT-003 |
| Approval never granted (abandoned run) | timeout → cancelled per rollback policy | FR-AGNT-001 |
| Budget exhausted mid-irreversible-sequence | stop only at declared safe points | FR-AGNT-004 |
| Model proposes an action not in the inventory | rejected + logged, never executed | FR-AGNT-001 |

## Dependencies
- PRD_FR_AI_Behavior (contracts, EV rows for planning quality), Permissions (runs act AS the user, never above), Notifications (approval requests)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Runs completing without human rescue | G-0X | |
| Approval-gate response time | G-0X (friction) | |

## Out of Scope for This Module
- Tool implementations; model choice (Architecture)

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
