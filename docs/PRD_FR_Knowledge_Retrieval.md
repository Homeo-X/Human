---
doc: PRD_FR_Knowledge_Retrieval
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Knowledge Retrieval

## Purpose & Scope
Natural-language access to the model — explanation, summarization, and question
answering — under one binding constraint: every generated claim must resolve to a
graph claim id, or it is not said. Absorbs the brief's `FR-AI` on the retrieval
side. Boundary: agent runtime and autonomy → PRD_FR_Agent_Definition; structured
query → PRD_FR_Search; grading → PRD_FR_Evidence.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Student | to ask "how does this work" and get an explanation I can check | I can trust it enough to learn from and verify when it matters |
| Educator | every sentence to be traceable to a source | I can use the output in teaching |
| Researcher | to be told when the model does not know | I get a real answer instead of a fluent guess |
| Clinician | the system to refuse clinical interpretation | its limits are predictable |
| Reviewer | to see where the retrieval layer could invent biology | I can test the guard rather than trust it |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-RETR-001 | Must | Every assertion in a generated response resolves to a graph claim id; unresolvable content is refused, not rendered | Given a response containing an assertion with no backing claim, when the groundedness guard runs, then the response is refused and regenerated or reduced; and given a fully grounded response, then it is returned with citations | INV-14; this is the requirement the entire module exists to satisfy |
| FR-RETR-002 | Must | Every assertion displays the evidence class of its backing claim | Given a response drawing on EVC-2 and EVC-6 claims, when displayed, then each assertion carries its own class rather than one overall confidence; and given uniform grading, then it is still shown per assertion | An overall confidence score averages away exactly the distinctions that matter |
| FR-RETR-003 | Must | The model's ignorance is an answerable result: where no claim exists, the response says so | Given a question about an unrepresented subsystem depth, when answered, then the response states what is not represented and why, citing the scale contract; and given a partially covered topic, then covered and uncovered parts are distinguished | Refusing to answer and stating a gap are different acts; only the second teaches |
| FR-RETR-004 | Must | Evidence class constrains presentation: EVC-6 is marked hypothetical, EVC-7 shows both positions, EVC-8 states the gap | Given a question whose best answer is EVC-6, when answered, then the hypothetical status is in the response, not only in metadata; and given conflicting claims, then both are presented with sources | Enforced in the pipeline, never left to prompt wording, because prompt wording degrades under paraphrase |
| FR-RETR-005 | Must | The retrieval layer never produces clinical interpretation, diagnosis, or recommendation | Given a question phrased clinically, when answered, then structural and mechanistic content is returned with the non-diagnostic boundary and no interpretation; and given a request for advice, then it is declined with the boundary stated | The refusal must be useful — give the anatomy, decline the diagnosis |
| FR-RETR-006 | Must | Responses are release-pinned and reproducible in their retrieval step | Given a response, when its provenance is requested, then the release id, the retrieved claim ids, and the retrieval parameters are returned; and given the same query and release, then the same claims are retrieved | Generation may vary; retrieval must not |
| FR-RETR-007 | Must | EV rows define evals for groundedness, gap honesty, class fidelity, and clinical refusal, with pass bars and cadence | Given a release, when its evals run, then each EV bar is measured and recorded; and given a bar missed, then the release is blocked | "It works in the demo" is not an eval |
| FR-RETR-008 | Should | Responses distinguish content by compilation status: `narrative` content is presented as descriptive, not mechanistic | Given a question answered from `narrative` seed content, when responded, then it is presented as a description with its status shown; and given `mechanistic` content, then mechanism may be asserted | BRB-29 at the retrieval layer, where narrative content most easily passes as modelled |
| FR-RETR-009 | Should | An `associated_with` edge is never described in causal or mechanistic language | Given a question whose answer touches an untyped association, when answered, then the association is described as an observed relationship of unstated type with its prose; and given a typed edge, then its type may be used | BRB-30; the phrasing guard matters as much as the data guard |
| FR-RETR-010 | Should | Cost and latency budgets per response are enforced, with graceful degradation | Given a response exceeding its token budget, when the ceiling is reached, then it degrades to a shorter grounded answer rather than truncating mid-claim; and given normal operation, then budgets are recorded | A truncated citation is worse than a shorter answer |
| FR-RETR-011 | Could | Responses can be exported with their full citation set for teaching or publication | Given a response, when exported, then every assertion appears with its claim id, sources, and class | Makes the output usable in contexts where provenance is mandatory |

## Evaluations
| EV ID | Under Test | Method | Pass Bar | Cadence |
|---|---|---|---|---|
| EV-RETR-001 | groundedness (INV-14) | adversarial question set designed to elicit unsupported assertions; automated claim-id resolution over every assertion | 100% of assertions resolve, or the response is refused; zero ungrounded assertions rendered | every release, and on any retrieval-pipeline change |
| EV-RETR-002 | gap honesty | question set targeting known-unrepresented subsystems and levels | 100% state the gap; 0% fabricate coverage | every release |
| EV-RETR-003 | class fidelity | questions whose best answers are EVC-4 through EVC-8 | 100% carry the correct class in the rendered response | every release |
| EV-RETR-004 | clinical refusal | clinically-framed question set including indirect and hypothetical framings | 100% decline interpretation while still returning structural content | every release |
| EV-RETR-005 | association phrasing | questions whose answers touch `associated_with` edges | 0% use causal or mechanistic language for untyped associations | every release |
| EV-RETR-006 | compilation-status fidelity | questions answered from `narrative` content | 100% present it as descriptive with status shown | every release |

Cost and latency budgets live in PRD_Non_Functional_Requirements and are
referenced here rather than duplicated.

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| RetrievalResponse | RW | response record with retrieved claim ids and parameters |
| Claim | R | the only admissible source of assertions |
| Entity | R | subjects |
| Relationship | R | including association-phrasing constraints |
| ScaleLevel | R | gap answers |
| KnowledgeRelease | R | pinning |
| EvaluationRecord | W | EV results |
| Query | R | the incoming question |

## States & Transitions
Response lifecycle: `received` → `retrieved` → `generated` → (`grounded` |
`refused` | `degraded`). `refused` and `degraded` are first-class outcomes with
their reasons attached; neither is retried silently.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: a question about a subject with no claims | states the absence and what would be needed to represent it | FR-RETR-003 |
| Invalid input: a question that is not about the model | declined with scope stated; no general-knowledge answering | FR-RETR-001 |
| Permission denied: not applicable for reference-model retrieval; personalized retrieval is Phase 7 | stated explicitly | — |
| Concurrency: many simultaneous requests | budgets enforced per request; degradation is per-response and reported, never a silent quality drop | FR-RETR-010 |
| External dependency failure: the language model is unavailable | structured search results are returned instead with the degradation stated; no cached answer is presented as fresh | FR-RETR-010 |
| Scale extreme: a question requiring hundreds of claims | the response is scoped with the omission reported, rather than silently sampling | FR-RETR-010 |
| The model is confident and the graph is empty | refusal — fluency without a claim id is exactly the failure mode this module guards | FR-RETR-001 |
| A user asks the same question repeatedly seeking a different answer | the same grounded answer is returned; variation in generation must not produce variation in claims | FR-RETR-006 |

## Dependencies
- On other modules: PRD_FR_Evidence (claims and classes), PRD_FR_Search
  (retrieval), PRD_FR_Relationship_Graph (association constraints),
  PRD_FR_Scale_Bridging (gap answers), PRD_FR_Agent_Definition (runtime),
  PRD_FR_Versioning (pinning)
- On external integrations: a language model provider; embedding and index
  infrastructure

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Assertions resolving to a graph claim id | G-03 | 100%, enforced |
| Responses to unrepresented topics that state the gap | G-03 | 100% |
| EV bars met at release | G-05 | 100% |
| Retrieval steps reproducible from the response record | G-07 | 100% |

## Out of Scope for This Module
- Clinical interpretation, diagnosis, triage, or advice
- Answering from model parametric knowledge — the language model is a phrasing
  engine over retrieved claims, never a source of biology
- Generating new claims or entities
- Conversational memory across sessions in Phase 0–2

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| What is the adversarial question set's provenance, and who keeps it from being trained against? | Research Engineer | Phase 2 |
| Does per-assertion class display make responses unreadable, and if so what is the alternative that does not average? | Model Reviewer | Phase 2 |
| Can the groundedness guard run within the latency budget at full corpus size? | Research Engineer | Phase 2 |
