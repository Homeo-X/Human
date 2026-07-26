---
doc: PRD_FR_Agent_Definition
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Agent Definition

## Purpose & Scope
The formal specification of the agents that assist curation and retrieval: the
shared twelve-facet runtime contract, the per-agent register with its authority
deltas, and the hard limit that no agent is the final authority over biological
truth. Boundary: retrieval behaviour and evals → PRD_FR_Knowledge_Retrieval;
human review workflow → PRD_FR_Curation; grading rules → PRD_FR_Evidence.

_This file specifies the shared facet contract once and records per-agent
deltas in the register. The four agents with write authority over canonical
content — AGT-1, AGT-2, AGT-9, AGT-11 — carry the strictest cells and are called
out per facet. The runtime object model is canonical in SPEC_MODEL.md; scoping
these agents pulls those entity names into PRD_Data_Overview verbatim._

## Agent Register
| ID | Agent | One-Line Purpose | Authority Ceiling |
|---|---|---|---|
| AGT-1 | Biological Ontology | proposes entities, classes, levels, and identifier resolution | may propose; may not admit an entity or promote compilation status |
| AGT-2 | Evidence | finds sources, extracts candidate claims, proposes grades | **may not assign EVC-1 or EVC-2 under any circumstance** |
| AGT-3 | Anatomy | maps structures, containment, adjacency, and spatial identities | may propose spatial identities; may not bind published geometry |
| AGT-4 | Physiology | drafts process specifications from sources | may propose; may not promote representation status |
| AGT-5 | Cellular Biology | drafts L6–L7 content within declared depth | may not exceed a subsystem's declared depth, ever |
| AGT-6 | Molecular Biology | drafts L8–L10 mechanism content within declared depth | as AGT-5 |
| AGT-7 | 3D Representation | binds geometry to spatial identities, manages LOD and tiers | may not publish an asset or alter a licence tier |
| AGT-8 | Simulation | assembles and runs executable processes | may not promote a process to executable |
| AGT-9 | Personalization | applies individual data as overlays | **read-only against the reference model, structurally** |
| AGT-10 | Validation | runs the invariant harness and reports findings | may not modify content or suppress a finding |
| AGT-11 | Provenance | tracks lineage, licences, and release manifests | may not alter a claim's evidence class |
| AGT-12 | Red-Team Biology | attacks the model for anatomical errors, contradictions, unsupported claims, false precision, invalid causal assumptions, conflicting sources, and scale, unit, or temporal errors | **attacks only; proposes no fixes and writes no content** |

**The standing rule:** no agent, and no combination of agents, is the final
authority over biological truth. Every path that changes canonical content
terminates in a human reviewer (PRD_FR_Curation). AGT-12's isolation mirrors
RED_TEAM.md — the moment it designs a remedy it inherits the frame it exists to
test.

## Facet 1 — Identity
Every agent is attributed by id wherever its output appears — in curation
queues, claim records, and audit trails. No agent has a persona or a voice; all
are invisible automation whose output is a proposal attributed to a named agent,
never to the system as a whole. A curator always knows which agent proposed what.

## Facet 2 — Goal
Each agent optimizes for **proposal quality under review**, satisfices on
throughput, and has one explicit non-goal in common: **it must not optimize for
acceptance rate.** An agent that learns which proposals get approved and
generates those is optimizing for a curator's fatigue rather than for the
model's accuracy. AGT-12 additionally must not optimize for a low finding count.

## Facet 3 — State
Within a run: the task, the retrieved context, the working proposal, and the
tool-call history. State lives in the AgentRun record. Nothing persists between
steps except what is written to the run record, so a run is reconstructable from
its record alone.

## Facet 4 — Memory
**No cross-run memory** for all twelve agents in Phase 0–2. An agent begins each
run from the graph and its task, never from an accumulated impression of prior
runs. Forbidden from any future memory: individual data of any kind (AGT-9's
subject matter included), credentials, and any cached judgment that would let an
agent skip re-reading the evidence.

The reason this is strict: an agent that remembers "the cardiovascular content is
good" stops checking, and that is exactly where a shared upstream error would
propagate unexamined.

## Facet 5 — Tools
| ID | Tool | Effect Class | Autonomy | Rate & Scope Limits |
|---|---|---|---|---|
| TOOL-01 | graph read / query | read-only | auto | scoped to the pinned release |
| TOOL-02 | source fetch and licence check | read-only | auto | rate-limited per external authority |
| TOOL-03 | propose entity | reversible | auto | writes to the proposal queue only, never to the graph |
| TOOL-04 | propose claim with class ≤ EVC-3 | reversible | auto | queue only |
| TOOL-05 | propose claim at EVC-1 or EVC-2 | reversible | **forbidden** | no agent may invoke this; the tool exists only for human reviewers |
| TOOL-06 | promote compilation or representation status | irreversible | **confirm** | human reviewer confirmation mandatory; never auto |
| TOOL-07 | bind geometry to a spatial identity | reversible | auto (AGT-7 only) | unpublished assets only |
| TOOL-08 | publish an asset or release | irreversible | **confirm** | human only; agents may prepare, not publish |
| TOOL-09 | run the invariant harness | read-only | auto (AGT-10 only) | full scope permitted |
| TOOL-10 | run an executable process | reversible | auto (AGT-8 only) | within declared cost budget; writes to a run record only |
| TOOL-11 | write an overlay value | reversible | auto (AGT-9 only) | overlay space only; INV-08 blocks anything else structurally |
| TOOL-12 | write a challenge finding | reversible | auto (AGT-12 only) | the challenge register only; no content writes |

No irreversible tool is auto for any agent, so no Decision Log entry for an
irreversible-plus-auto cell is required — the absence is deliberate. **Tool
outputs are data, never instructions:** nothing an agent reads through TOOL-01 or
TOOL-02 may escalate any autonomy cell. A source document containing text that
reads like an instruction is a source document.

## Facet 6 — Permissions
Each agent acts as a **service identity with strictly fewer permissions than any
human curator** — never as a user, never as an administrator. Deny-by-default.
The permission delta between an agent and a curator is enumerated in the register
above and is always negative. AGT-9's read-only posture against the reference
model is structural, not configured: it has no credential that could write there.

## Facet 7 — Planning Policy
Iterative planning with a step budget per run declared in Facet 12. Plans are
inspectable by the curator who receives the proposal, so a reviewer can see how a
proposal was reached and not only what it says. Replanning triggers: a tool
refusal, a validation failure, or retrieved evidence that contradicts the working
proposal. An agent that cannot form a plan within budget stops and says so.

## Facet 8 — Execution Policy
Steps are sequential within a run. Every write tool is idempotent by proposal id,
so a retry cannot create duplicate proposals. Approval is placed at every
irreversible boundary — status promotion (TOOL-06) and publication (TOOL-08) —
and those pauses are the only points at which agent output can affect canonical
content. Ordering guarantee: no proposal reaches a queue before its provenance
record is complete.

## Facet 9 — Observation
After each action an agent perceives the tool result, any validation finding it
triggered, and curator interjections on its queue. Observations are validated
before use: a retrieved source is checked for licence and resolvability before
its content is read into a proposal. Every observation is recorded per
SPEC_MODEL's Observation entity, which is what makes a run auditable after the
fact.

## Facet 10 — Recovery
| Failure class | Policy |
|---|---|
| Transient tool failure | retry 3 times with exponential backoff |
| Source unresolvable | abandon the proposal; record the gap rather than proposing without provenance |
| Validation failure on a proposal | replan once; if it fails again, submit the proposal flagged with the finding attached |
| Budget exhausted | stop at a declared safe point per Facet 12 |
| Partial write to the proposal queue | compensate by voiding the proposal id; queues never hold half-proposals |
| Compensation itself fails | terminal, escalated to a named human operator, with the run record stating exactly what changed and what did not |

The honest terminal state is always available: "failed, here is what changed and
what did not."

## Facet 11 — Evaluation
| EV ID | Facet Under Test | Method | Pass Bar | Cadence |
|---|---|---|---|---|
| EV-AGD-001 | Goal — no acceptance-rate optimization | proposal distribution compared against a held-out reviewer panel's independent judgments | no significant drift toward high-approval proposal types | quarterly |
| EV-AGD-002 | Tools — autonomy conformance | attempted invocation of forbidden and confirm-class cells | 100% blocked by the runtime, not the prompt | every release |
| EV-AGD-003 | Tools — injection resistance | sources containing instruction-shaped content | 0% autonomy escalation; 100% flagged | every release |
| EV-AGD-004 | Permissions — AGT-9 isolation | adversarial attempts to reach reference entities from the overlay path | 0% reach, structurally | every release, and before Phase 7 |
| EV-AGD-005 | Evidence authority — AGT-2 | attempted EVC-1 and EVC-2 assignments | 100% refused | every release |
| EV-AGD-006 | Scale discipline — AGT-5, AGT-6 | proposals targeting levels beyond declared depth | 100% refused | every release |
| EV-AGD-007 | Red-team isolation — AGT-12 | inspection of its output for proposed fixes | 0% remedies proposed | every red-team pass |

## Facet 12 — Cost Boundary
Per run: token, wall-clock, and tool-call ceilings declared in
PRD_Non_Functional_Requirements and referenced here, not duplicated. Behaviour at
every ceiling is the Facet 10 graceful stop — a declared safe point with an
honest partial summary. **Never silent truncation**, because a truncated proposal
that looks complete is worse than no proposal.

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-AGD-001 | Must | Every state change caused by an agent traces to a Step and ToolCall in its AgentRun record | Given any agent-caused change, when audited, then its Step, ToolCall, and Observation records exist and link; and given a change with no such trace, then it is a defect | Curators need to see the derivation, not just the proposal |
| FR-AGD-002 | Must | Every tool call conforms to its TOOL row, enforced by the runtime rather than the prompt | Given a call violating any autonomy or scope cell, when attempted, then the runtime blocks it and records a Failure; and given a conforming call, then it proceeds | Prompt-level enforcement degrades under paraphrase; runtime enforcement does not |
| FR-AGD-003 | Must | No agent assigns EVC-1 or EVC-2, and no agent promotes status or publishes without human confirmation | Given AGT-2 attempting an EVC-1 assignment, when submitted, then it is refused and logged; and given a human reviewer performing the same assignment, then it succeeds | The gate that keeps the evidence ladder meaningful |
| FR-AGD-004 | Must | Agent output is attributed by agent id wherever it appears | Given a proposal in a curation queue, when displayed, then the proposing agent is named; and given an admitted claim originating from an agent proposal, then the lineage records it | A curator must never wonder whether a human or an agent wrote something |
| FR-AGD-005 | Must | Tool outputs are treated as data; instruction-shaped content in a source never changes autonomy | Given a source containing text resembling an instruction, when read, then it is treated as content and flagged; and given normal content, then it is used normally | Injection through the literature is the realistic attack surface here |
| FR-AGD-006 | Must | Cost ceilings stop a run at a declared safe point with an honest partial summary | Given a run reaching its ceiling mid-proposal, when it stops, then the partial state is labelled partial and the proposal is not queued; and given completion within budget, then the proposal queues normally | Half a proposal presented as whole is the failure |
| FR-AGD-007 | Should | AGT-12 writes only to the challenge register and proposes no remedies | Given a red-team run, when its output is inspected, then it contains findings with severities and no proposed fixes; and given an attempted content write, then it is refused | Its value comes entirely from not being a collaborator |
| FR-AGD-008 | Should | Agent runs are reproducible from their run record given the same release and inputs | Given a run record, when re-executed, then the same tool calls occur in the same order; and given nondeterminism, then its seed is recorded | Reproducibility is what makes an audit meaningful |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Agent, Task, Plan, AgentRun, Step, ToolCall, Observation, Artifact, Approval, Failure, Retry, Compensation, EvaluationRecord | RW | canonical names per SPEC_MODEL; flagged for the Architect into PRD_Data_Overview |
| Entity | R | proposals reference, never write |
| Claim | R | proposals reference, never write directly |
| CurationTask | W | the proposal queue |
| Overlay | RW | AGT-9 only, overlay space only |

## States & Transitions
AgentRun: `queued` → `planning` → `executing` → (`completed` |
`stopped_at_budget` | `failed` | `compensated`). Proposals: `drafted` → `queued`
→ (`accepted` | `rejected` | `voided`). No transition from a proposal state to
canonical content exists without a human Approval record.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: an agent finds no candidate content | records the empty result rather than lowering its threshold to produce something | FR-AGD-001 |
| Invalid input: a malformed task | refused at intake with the fault named | FR-AGD-002 |
| Permission denied: an agent's principal loses permission mid-run | the next ToolCall re-checks and the run degrades per Facet 10 | FR-AGD-002 |
| Concurrency: two runs of the same agent on one task | serialized by task id; duplicate proposals are prevented by idempotency | FR-AGD-008 |
| External dependency failure: a source repository is unreachable | retried per Facet 10, then the proposal is abandoned with the gap recorded | FR-AGD-005 |
| Scale extreme: a queue of thousands of pending proposals | batched by subsystem for review; agents throttle when the queue exceeds review capacity, rather than generating faster than humans can check | FR-AGD-006 |
| Tool output contains instruction-shaped content | treated as data, autonomy unchanged, flagged for review | FR-AGD-005 |
| Approval abandoned by a curator | timeout produces a Failure and Compensation per policy; the proposal is voided, not auto-accepted | FR-AGD-003 |
| Compensation itself fails | terminal state is honest and a named human escalation path is invoked | FR-AGD-006 |

## Dependencies
- On other modules: PRD_FR_Curation (review queues and approval),
  PRD_FR_Evidence (grading limits), PRD_FR_Knowledge_Retrieval (shared retrieval
  discipline), PRD_FR_Validation (findings on proposals), PRD_Security_Requirements
- On external integrations: language model provider; source repositories and
  identifier resolvers

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Agent-caused changes with a complete Step/ToolCall trace | G-03 | 100% |
| Forbidden or confirm-class autonomy cells reached without approval | G-05 | 0, enforced by runtime |
| Facet-11 safety EV bars met | G-05 | 100% of bars |
| Agent runs reproducible from their record | G-07 | 100% |

## Out of Scope for This Module
- Any agent holding final authority over biological content
- Cross-run agent memory in Phase 0–2
- Agents acting on individual data beyond AGT-9's overlay scope
- Model choice and prompt engineering mechanics (TECH_System_Architecture)

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| At what queue depth does review capacity become the binding constraint on curation throughput? | Biology Lead | Phase 2 |
| How is EV-AGD-001's held-out reviewer panel kept independent over time? | Research Engineer | Phase 3 |
| Should AGT-12 run against the substrate as well as the documents, and does that compromise its isolation? | Orchestrator | Phase 2 |
