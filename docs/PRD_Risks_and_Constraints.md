---
doc: PRD_Risks_and_Constraints
tier: standard+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Risks & Constraints

## Risk Register
| ID | Risk | Type | Likelihood | Impact | Mitigation | Owner | Trigger to Re-assess |
|---|---|---|---|---|---|---|---|
| RSK-01 | The stated user problem is asserted from the structure of available tools, not from research. If educators do not actually want evidence grading, the product's central differentiator is a cost with no benefit | adoption | medium | high — invalidates the value proposition, not a feature | validate with 5–8 medical educators before Phase 1 build; the Phase 1 gate depends on it | Biology Lead | before Phase 1 build |
| RSK-02 | Curation throughput is the binding constraint. Expert review cannot keep pace with what agents can propose, and the queue becomes a rubber stamp | delivery | **high** | high — the review gate is the correctness story; if it degrades, nothing else holds | BR-023 throttling; queue depth published; review capacity treated as the planning unit rather than agent capacity. **This is the project's principal risk (CH-02) and is not resolvable by specification:** reviewer-hours are an organizational fact. If capacity is inadequate, every gate degrades to a rubber stamp *while all fourteen invariants continue to pass green* — the validators cannot detect it | Biology Lead | continuously from Phase 2 |
| RSK-03 | External ontology dependency: upstream deprecations, splits, and merges create unbounded maintenance, or an authority becomes unmaintained or changes licence | tech | medium | high | authority pinning per release; splits block promotion rather than silently resolving; minted-id count tracked as a drift signal. **Named limitation (CH-12):** pinning protects against upstream *change*, not against an authority being abandoned, relicensed, or community-forked. That failure has no mitigation that preserves the interoperability D-002 was chosen for, and is accepted as residual | Research Engineer | each upstream release |
| RSK-04 | Honest coverage reporting makes the product look worse than competitors who report bare percentages against undisclosed denominators | business | **high** | medium | `n / declared_n` reporting is a rule (BR-021), not a preference; the denominator's visibility is positioned as the differentiator rather than defended as a limitation | Biology Lead | at each public release |
| RSK-05 | Share-alike geometry obligations propagate further than expected, or the quarantine leaks through a derived artifact | legal | medium | high | T0/T1/T2 tiering enforced by INV-11; per-asset licence metadata; exports refuse to cross tiers; legal review before the first public release including geometry | Licence owner | before any geometry release |
| RSK-06 | Domain reviewer availability per subsystem is assumed and may not exist, particularly for L7+ content | delivery | medium | high | declared depth is set to what review capacity supports, not to ambition; a subsystem without a reviewer stays at its current depth | Biology Lead | per phase gate |
| RSK-07 | The reference subject is anatomically male for sex-variant structures because most open geometry is male-derived. This encodes a known bias into the reference | ethical | **certain** | medium | recorded explicitly in BIO_Research_Charter rather than hidden; female-reference parity is a Phase 3 objective; variants are first-class entities, not exceptions | Biology Lead | Phase 3 |
| RSK-08 | The retrieval layer produces fluent, well-cited, subtly wrong explanations — grounded in real claims but composing them into a false picture | tech | medium | high — this is the failure the whole architecture is built against, and groundedness does not fully prevent it | EV-RETR-001 through EV-RETR-006; adversarial question sets; composition errors escalated as red-team findings rather than treated as prompt bugs | Research Engineer | every release |
| RSK-09 | Users read the 3D view as the model and ignore evidence grading entirely, making the honesty machinery decorative | adoption | medium | high | BRB-04 and the Model Reviewer role exist for this; evidence class is rendered on the entity, not in a panel; filtering by class is a first-class navigation control | Model Reviewer | Phase 2 usability testing |
| RSK-10 | The seed corpus's 157 narrative nodes are never compiled, so the model is permanently a well-formatted encyclopedia | delivery | medium | medium | compilation status is visible everywhere (BRB-29); the proportion still at `narrative` is published per release | Biology Lead | each release from Phase 1 |
| RSK-11 | Scope pressure to add a "which condition is this" feature, arriving as a reasonable-sounding user request | business | medium | **high** — it converts the product into a regulated medical device with obligations it is not built for | BR-019 has no exceptions; the boundary is in the charter, not in a settings page | Biology Lead | any time it is proposed |
| RSK-12 | Byte-identical rebuild (G-07) becomes impractical once geometry assets reach gigabytes | tech | medium | medium | hash manifests per asset rather than whole-artifact rebuild; the guarantee is re-scoped explicitly by Decision if it must weaken, never quietly dropped | Research Engineer | Phase 1 |
| RSK-13 | Phase 7 personal health data arrives before the privacy posture is genuinely ready, because the architecture "already supports it" | legal | low | high | Phase 7 is gated on a completed privacy review, not on architectural readiness; the two are explicitly different gates | Architect | before Phase 7 |
| RSK-14 | The framework fork diverges from upstream, and re-applying deltas becomes expensive enough to abandon | tech | medium | low | UPSTREAM.md records every delta with its rationale; the specgraph regex fix is offered upstream so the delta can collapse | Research Engineer | each upstream release |

## Hard Constraints
| Constraint | Source | Consequence If Violated |
|---|---|---|
| Not a medical device; no regulatory clearance sought | product decision, BIO_Research_Charter | any diagnostic capability makes the product a regulated device it was not built, tested, or staffed to be |
| No individual data before Phase 7 and a completed privacy review | D-004, PRD_Security_Requirements | handling health data without the posture in place is a legal and ethical failure, not a schedule slip |
| Declared scale depth is binding | D-001, BIO_Scale_Contract | a declaration that yields to good content is not a declaration, and the honesty claim collapses |
| Human review on every canonical change | BR-009 | the correctness story is entirely this gate; automating it removes the product's basis for trust |
| T0 layers hold no share-alike content | D-003 | share-alike obligations attach to the whole model and cannot be un-mixed afterwards |
| Every quantitative value carries a unit | INV-04 | unit-less quantities are the classic silent scientific error |
| Coverage reported against a declared denominator | BR-021 | bare percentages are gameable, and gaming them would make G-01 meaningless |

## Open Questions
| Question | Blocks | Owner | Needed By |
|---|---|---|---|
| Do medical educators actually want evidence grading, or is it a cost they will not pay for? | the value proposition (RSK-01) | Biology Lead | before Phase 1 build |
| What review capacity exists per subsystem, and does it support the declared depths? | Phase 4 depth declarations (RSK-06) | Biology Lead | Phase 3 |
| What is the admissible transfer justification for animal-derived mechanism data? | Phase 5 (BIO_Research_Charter) | Biology Lead | Phase 5 |
| Where does variation stop being a variant and become a separate entity? | Phase 3 (PRD_FR_Ontology) | Biology Lead | Phase 3 |
| Does a permissive-only build have enough coverage to be worth shipping? | Phase 1 asset strategy | Licence owner | Phase 1 |
| Can the groundedness guard run within the latency budget at full corpus size? | Phase 2 (RSK-08) | Research Engineer | Phase 2 |
