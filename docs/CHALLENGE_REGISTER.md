---
doc: CHALLENGE_REGISTER
tier: standard+
version: 1.0.0
status: draft
owner: redteam
last_updated: 2026-07-26
---

# Challenge Register — Adversarial Review

_Produced under RED_TEAM.md isolation rules: the brief and `docs/` only, attacker
stance, **no fixes proposed**. Dispositions belong to the orchestrator and appear
in the final section, written after the attacks._

**What was probed hardest:** the gap between what this spec's honesty machinery
*checks* and what it *claims*; the assumption that curation capacity exists; and
every place where a rule's enforcement is weaker than its wording.

## Challenges

| ID | Sev | Class | Challenge |
|---|---|---|---|
| CH-01 | S1 | Q1 assumption | **The entire product rests on an unvalidated market assumption, and the spec knows it.** PRD_Executive_Summary marks the problem statement as asserted "from the structure of available tools, not from user research", and RSK-01 rates it medium/high. But every other document proceeds as though it were settled: the scale contract, the evidence ladder, the rubric, fourteen invariants, and a fifteen-module architecture are all built on top of "educators want evidence grading". If they do not — if they want a fast, pretty atlas and treat EVC badges as clutter — then the honesty machinery is not a differentiator but the reason the product is slower and emptier than its competitors. Nothing in the roadmap gates Phase 1 *build* on RSK-01's resolution; it gates it on the same phase's exit criteria. The validation is scheduled to happen alongside the work it would invalidate. |
| CH-02 | S1 | Q4 single failure | **Curation capacity is the single dependency every module shares, and it has no owner outside the spec.** BR-009 requires a human Approval on every canonical change; FR-CUR-004 requires reviewer competence scoped by subsystem and level; the new sampled source-aptness gate adds ≥5% re-review per release; conflict adjudication requires two reviewers. RSK-02 rates this high/high. But the spec never states how many reviewer-hours exist, and it declares depths (cardiovascular L10) that imply molecular-level review competence. If that capacity is one part-time domain expert, every gate degrades to a rubber stamp and the product's correctness story — which is *entirely* the review gate, by BIO_Validation_Framework's own admission — evaporates while all fourteen invariants continue to pass green. |
| CH-03 | S2 | Q6 gameable metric | **G-01's denominator is protected by a rule that the same people can change.** BR-021 says the declared scope narrows "only by Scope Reopen with a Decision entry", and D-001 grants reopen authority to the orchestrator. The orchestrator is on the team whose coverage number is being measured. A Scope Reopen that narrows the endocrine declaration from L3 to L2 improves G-01 and is fully compliant with every rule in the spec. The Decision entry documents it, but documentation is not a constraint — it is a record of an unconstrained act. |
| CH-04 | S2 | Q7 contradiction at scale | **BR-023 (throttle agents to review capacity) and the roadmap's coverage targets are incompatible, and the spec resolves the conflict in the wrong direction for its own schedule.** Phase 3 requires G-01 at 90% of declared L0–L3 scope and G-02 at 95%. Throttling caps content generation at review throughput. If review throughput is the binding constraint (CH-02), the Phase 3 targets are unreachable without either lifting the throttle or lowering the target — and BR-023's precedence ordering says throttling wins. The spec has therefore already decided it will miss its own roadmap, without saying so in the roadmap. |
| CH-05 | S2 | Q5 underspecified entity | **`Claim` is the entity every module touches, and its most consequential field is the least specified.** Fourteen fields are enumerated, but `population` accepts the free-text value `"unspecified in source"` — which BIO_Evidence_and_Provenance calls "valid and informative". In the seeded substrate, 140 of 149 claims carry `"adult, unspecified in source"`. The field that is supposed to prevent conflating populations (FR-EVID-006's stated mechanism for distinguishing genuine conflicts from population differences) is, in practice, a constant. The invariant checks that the field is non-empty, not that it discriminates. |
| CH-06 | S2 | Q2 self-undermining requirement | **INV-14 and FR-RETR-002 cannot both hold as written.** INV-14 requires every assertion in a response to resolve to a graph claim id. FR-RETR-002 requires every assertion to display "the evidence class of its backing claim", singular. But a useful natural-language sentence routinely composes two or more claims ("the left ventricle pumps oxygenated blood into the aorta" draws on structure, function, and connectivity claims). Either the response is decomposed into one-claim assertions — which produces unreadable prose, exactly the objection FR-RETR-002's own Open Questions raises — or an assertion carries several classes and the "per-assertion class" requirement quietly becomes an aggregate, which is the averaging the spec explicitly forbids. |
| CH-07 | S2 | Q8 partial failure | **The three-plane architecture has no specified behaviour for a partially-published release.** TECH_System_Architecture describes build → validate → hash → publish, and FR-VER-001 makes releases immutable. But a release comprises a graph, claim set, asset bundles across licence tiers, and a manifest. If asset bundle publication fails after the graph is published, readers see entities whose geometry 404s — which FR-SPAT-002 handles visually, but the *release* is now in a state the spec does not name: published, immutable, and incomplete. There is no `partially_published` state, no rollback path (releases cannot be withdrawn, per BR-020), and no invariant covering manifest-to-artifact correspondence. |
| CH-08 | S2 | Q9 agentic autonomy | **AGT-12's isolation is asserted but structurally unenforced, and it has the most dangerous write scope in the system.** TOOL-12 lets the Red-Team Biology agent write findings; Facet 6 says agents hold fewer permissions than curators; EV-AGD-007 tests its output for proposed fixes. But a challenge register entry *is* free text that reviewers act on. An agent that writes "CH-NN: the myocardium entity should be split into three transmural layers" has proposed a fix in the grammar of a finding, and no runtime check can distinguish that from a legitimate attack. The one agent explicitly forbidden from designing remedies is the one whose output format cannot be constrained to exclude them. |
| CH-09 | S3 | Q3 unrealistic behaviour | **The spec assumes users will read a terminal answer as information rather than as failure.** BIO_Scale_Contract, FR-SCAL-003, FR-NAV-003, and TECH_UI_UX_Design all invest heavily in the terminal surface, and TECH_API_Specification goes as far as returning HTTP 200 for "not represented". This is intellectually correct and behaviourally optimistic. A student mid-revision who zooms and is told "this model holds nothing below here" has been served correctly and will experience it as the product being incomplete. No evidence is offered that the framing changes the reaction; the design decision is asserted, not tested, and BRB-04's disposition cites requirements rather than user evidence. |
| CH-10 | S3 | Q6 gameable metric | **G-03's UNKNOWN count is presented as an anti-gaming mechanism but is gameable in the opposite direction.** The spec publishes the absolute UNKNOWN count "so completeness cannot be raised by deleting the things we do not know". But nothing sets a floor or an expectation for the count, so a team under pressure to look thorough can inflate it — asserting UNKNOWN claims for facts nobody would ask about is cheap, raises no invariant, and makes the model look scrupulous. The metric detects deletion and rewards padding. |
| CH-11 | S3 | Q10 rubric hostile re-read | **BRB-16's disposition was upgraded from a flag to a mitigated flag by adding a review gate that the same document admits cannot scale.** The sampled source-aptness gate (≥5%, min 20 claims, different reviewer) is the fix for citations that look apt but are not. It is also net-new recurring reviewer work landing on the capacity constrained in CH-02, reviewed by a *second* reviewer per sample. At 149 claims the sample is 20; at Phase 3's 10⁵ claims it is 5,000 per release. The gate is specified at a rate that is either trivial now or impossible later, and no phase-dependent rate is given. |
| CH-12 | S3 | Q1 assumption | **D-002 is marked reversibility "low" and treated as settled, but its failure mode is not in the risk register with the severity the Decision itself assigns.** The Decision says identifiers "propagate into every downstream artifact, including published releases and any third-party consumer", and PRD_External_Integrations calls it "the project's deepest dependency" with an exit path that "is not clean". RSK-03 rates it medium/high and mitigates with pinning — but pinning protects against upstream *change*, not against an authority being abandoned, relicensed, or forked by its community. The mitigation addresses the frequent failure, not the fatal one. |
| CH-13 | S3 | Q5 underspecified | **`compilation_status` is enforced as a label but not as a capability constraint.** D-007 and FR-ONTO-006 require the status to be visible; FR-RETR-008 requires narrative content to be presented as descriptive. But no invariant prevents a `narrative` entity from being an endpoint of a `mechanistic` relationship, or from being consumed by a process specification. In the seeded substrate all 140 seed entities are `narrative` and 26 relationships between them carry `compilation_status: narrative` — consistent today, but nothing in `biocheck` would catch the mixed case, and the mixed case is what will occur the moment compilation begins on part of a subsystem. |

## No-finding areas
Probed and found sound, stated explicitly so the silence is not mistaken for
inattention: the reference-immutability chain (D-004 → INV-08 → schema
`target_path` pattern → selftest) is enforced at four independent layers, and I
could not construct a path from an overlay to a reference field. The licence
tiering (D-003 → INV-11 → tier-split export) similarly holds. The negative-test
discipline is real — every invariant demonstrably fails when violated, which is
rarer than it should be.

---

## Dispositions (orchestrator, after the attacks)

| Challenge | Disposition | Basis |
|---|---|---|
| re CH-01 | **accept** | Correct and material. Phase 1 exit criteria do not gate the *build* on RSK-01. Roadmap amended: educator validation moves from a milestone to a **Phase 1 entry gate** — build does not start until it resolves. Recorded as D-010. |
| re CH-02 | **acknowledge** | True, and not resolvable inside a specification. Reviewer capacity is an organizational fact this project does not control. Accepted as a named residual risk with the consequence stated plainly in the roadmap rather than mitigated on paper. D-010. |
| re CH-03 | **accept** | The conflict of interest is real. Narrowing a declared depth now requires the Decision entry to state the coverage delta it produces, and coverage is reported against **both** the current and the original scoping denominator whenever they differ. D-010. |
| re CH-04 | **accept** | The contradiction is genuine and the spec had resolved it silently. Phase 3 targets are now stated as conditional on review capacity, with BR-023's precedence made explicit in the roadmap. D-010. |
| re CH-05 | **accept** | The strongest finding in the register. `"unspecified in source"` on 94% of seeded claims makes the population field decorative. Accepted; the seed ingest's population value is a known limitation now recorded on the seed manifest, and a population-discrimination requirement is added to the compilation ladder's `narrative → structured` promotion. D-010. |
| re CH-06 | **acknowledge** | Real tension, correctly identified, and not resolvable without user testing. Recorded as an open question already present in PRD_FR_Knowledge_Retrieval; the register's framing is sharper than the spec's and is adopted verbatim into that document's Open Questions. |
| re CH-07 | **accept** | A genuine gap. Release publication is specified as atomic but composed of separately-publishable parts. Requires a manifest-to-artifact correspondence check before a release leaves `validated`. D-010. |
| re CH-08 | **refute, with evidence** | The attack is well-aimed but the control exists: RED_TEAM.md's isolation rule is procedural for human red-teamers too, and EV-AGD-007 inspects output for remedies. More decisively, AGT-12 writes only to `CHALLENGE_REGISTER.md`, which per RED_TEAM.md is dispositioned by the orchestrator before any content changes — a fix smuggled into a finding still cannot reach canonical content without passing the same human gate as any proposal. The finding identifies a real ambiguity in *format*, not an escalation path. |
| re CH-09 | **acknowledge** | Correct that it is asserted rather than tested. It is a design bet, made deliberately, and it is the product's thesis in miniature. Added to Phase 2 usability testing as a named hypothesis rather than defended. |
| re CH-10 | **accept** | Sharp and correct. G-03's UNKNOWN count is now reported alongside the count of UNKNOWN claims that were *asked for* — a gap recorded in response to a query or review is distinguished from one asserted unprompted. D-010. |
| re CH-11 | **accept** | The rate is unscaled. The gate is respecified as a phase-dependent sample: fixed minimum now, statistically-sized sample later, with the size stated per release rather than fixed in the document. D-010. |
| re CH-12 | **acknowledge** | Correct that pinning does not address abandonment or relicensing. No mitigation is available that does not cost the interoperability D-002 was chosen for. Accepted as residual risk with the fatal failure mode named in RSK-03 rather than left implied. |
| re CH-13 | **accept** | Correct, and it will bite as soon as compilation begins. A mixed-status check is added to the invariant set. D-010. |

**Unresolved S1/S2 escalated to the user, in the red team's words:**

> **CH-01:** "The validation is scheduled to happen alongside the work it would
> invalidate."
>
> **CH-02:** "If that capacity is one part-time domain expert, every gate degrades
> to a rubber stamp and the product's correctness story — which is *entirely* the
> review gate, by BIO_Validation_Framework's own admission — evaporates while all
> fourteen invariants continue to pass green."

Both are accepted rather than refuted. CH-01 is fixed by a gate change; CH-02
cannot be fixed by a document and is the project's principal risk.
