---
doc: PRD_FR_Curation
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Curation

## Purpose & Scope
The expert workflow through which anything becomes canonical: proposal queues,
review gates, adjudication, promotion, permissions, and operator tooling. This
module is where the project's correctness actually lives — the validators
establish consistency, and human review establishes everything else. Absorbs the
permissions and admin cross-cutting concerns. Boundary: what is reviewed →
PRD_FR_Evidence and PRD_FR_Ontology; who proposes → PRD_FR_Agent_Definition;
release mechanics → PRD_FR_Versioning.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Domain reviewer | to see a proposal with its full derivation and sources | I can judge it without reconstructing it |
| Domain reviewer | to reject with a reason that becomes part of the record | the same bad proposal does not return unchanged |
| Biology Lead | to see review throughput against queue depth | I know whether curation is keeping pace with generation |
| Curator | to adjudicate a conflict without erasing either position | the disagreement stays visible |
| Operator | to see what is blocked and why | I can unblock the pipeline without guessing |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-CUR-001 | Must | Every canonical change passes a human review gate; no path exists from a proposal to canonical content without an Approval record | Given a proposal accepted by any automated path, when audited, then an Approval record with a named human reviewer exists; and given an attempted bypass, then it is refused | The gate is the product's correctness story; it cannot be configurable away |
| FR-CUR-002 | Must | A proposal presents its full derivation: proposing agent or curator, sources, tool calls, and any validation findings | Given a proposal in the queue, when opened, then its derivation and findings are visible without leaving the review surface; and given an incomplete derivation, then the proposal is not reviewable | A reviewer forced to reconstruct context will approve on vibes |
| FR-CUR-003 | Must | Rejections record a reason, and the reason is attached to the proposal lineage | Given a rejected proposal, when a similar proposal is later submitted, then the prior rejection and reason are surfaced; and given a rejection with no reason, then it cannot be submitted | Without this, agents regenerate rejected proposals indefinitely |
| FR-CUR-004 | Must | Review roles are scoped by subsystem and level; a reviewer may only accept content within their declared competence | Given a cardiovascular reviewer accepting a nervous-system L7 proposal, when submitted, then it is refused with the scope stated; and given in-scope content, then acceptance proceeds | Competence scoping is what makes "expert review" more than a checkbox |
| FR-CUR-005 | Must | Conflict adjudication requires two reviewers and preserves both original positions | Given a conflicted claim, when adjudicated, then a new adjudication claim is created citing both originals and both reviewers, and neither original is deleted; and given a single reviewer attempting adjudication, then it is refused | Erasing the losing position destroys the record of a real scientific disagreement |
| FR-CUR-006 | Must | Compilation and representation status promotions require review and record the reviewer | Given a promotion applied without review, when audited, then it is a defect; and given a reviewed promotion, then the reviewer, date, and evidence are recorded | Promotion is the moment prose becomes a model; it needs a name attached |
| FR-CUR-007 | Must | Write access to canonical content is deny-by-default; readers require no authentication for the reference model | Given an unauthenticated reader, when they browse the reference model, then access is granted; and given any write attempt without curator role, then it is refused | Open reading is a deliberate posture: the reference model is a public good |
| FR-CUR-008 | Should | Queue depth, review throughput, and blocked items are visible to operators | Given the operator view, when opened, then queue depth by subsystem, throughput, and blocked items with reasons are shown | Curation capacity is the real constraint on this project; hiding it hides the bottleneck |
| FR-CUR-009 | Should | Agents throttle when the queue exceeds review capacity | Given a queue beyond its configured depth for a subsystem, when agents run, then generation for that subsystem pauses; and given capacity restored, then it resumes | Generating faster than humans can check produces a backlog that becomes a rubber stamp |
| FR-CUR-010 | Should | Batch review is supported for mechanically similar proposals without collapsing them into one decision | Given fifty entities blocked by one upstream split, when reviewed as a batch, then one decision applies to all with each recorded individually | Batching is necessary at scale; recording one approval for fifty items is not |
| FR-CUR-011 | Could | Reviewer disagreement rates per subsystem are tracked as a quality signal | Given review history, when analyzed, then disagreement rates by subsystem and reviewer pair are reported | Rising disagreement usually means the content is genuinely uncertain, which is worth knowing |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| CurationTask | RW | the proposal queue |
| Review | RW | reviewer decisions, reasons, and scope |
| Approval | W | the record required for any canonical change |
| Entity | RW | on acceptance |
| Claim | RW | on acceptance |
| Relationship | RW | on acceptance, including retyping |
| Process | RW | on promotion |
| Agent | R | proposal attribution |

## States & Transitions
Task lifecycle: `queued` → `in_review` → (`accepted` | `rejected` | `blocked` |
`escalated`). `blocked` carries its blocking reason — an upstream split, a
missing source, an unresolved conflict — and is not a failure state. `escalated`
routes to the Biology Lead for scope or competence questions the reviewer cannot
settle.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: no pending proposals | the queue reports empty with throughput history, distinguishing "caught up" from "nothing generating" | FR-CUR-008 |
| Invalid input: a proposal missing its derivation | not reviewable; returned to the proposer | FR-CUR-002 |
| Permission denied: a reviewer acting outside their subsystem scope | refused with the scope stated and a re-routing option offered | FR-CUR-004 |
| Concurrency: two reviewers open the same proposal | soft lock with the second reviewer told who holds it; simultaneous acceptance is impossible | FR-CUR-001 |
| External dependency failure: an authority unreachable during review | the proposal is `blocked` rather than accepted on unverified identity | FR-CUR-002 |
| Scale extreme: an upstream release blocks hundreds of entities at once | batched into one review task with per-item records | FR-CUR-010 |
| A reviewer accepts content later found wrong | the acceptance stands in the record; the content is superseded with a new review, and the original decision is never edited | FR-CUR-005 |
| The only competent reviewer for a subsystem is unavailable | the queue holds; content is not admitted by a less-scoped reviewer, and the bottleneck is reported rather than routed around | FR-CUR-004 |

## Dependencies
- On other modules: PRD_FR_Agent_Definition (proposals), PRD_FR_Evidence
  (grading gates), PRD_FR_Ontology (admission), PRD_FR_Validation (findings on
  proposals), PRD_FR_Versioning (release gating), PRD_Security_Requirements
- On external integrations: identity provider for curator authentication

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Canonical changes carrying an Approval record with a named reviewer | G-05 | 100%, enforced |
| Rejections carrying a recorded reason | G-05 | 100% |
| Queue depth against review capacity by subsystem | G-01 | published; throttling engages before a backlog becomes a rubber stamp |
| Adjudications preserving both original positions | G-03 | 100% |

## Out of Scope for This Module
- Deciding biological truth by vote — reviewers judge whether the model
  represents the evidence, not whether the evidence is right
- Editing the reference model through a navigation surface
- Individual data review (PRD_FR_Personalization, Phase 7)
- Public contribution workflows

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| How is reviewer competence declared and kept current without becoming a credentialing bureaucracy? | Biology Lead | Phase 2 |
| What queue depth should trigger agent throttling, per subsystem? | Biology Lead | Phase 2 |
| Does batch review erode decision quality, and how would we detect it? | Model Reviewer | Phase 3 |
