---
doc: PRD_FR_Validation
tier: any
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Validation

## Purpose & Scope
Turning the integrity rules of BIO_Validation_Framework into executable checks
that run automatically and can demonstrably fail: the invariant harness, its
layers, its negative tests, and the honest reporting of what validation does and
does not establish. Boundary: the invariants themselves → BIO_Validation_Framework;
the document-level spec graph → `tools/specgraph.py`; expert review →
PRD_FR_Curation.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| Curator | to be stopped at commit time rather than at release | I fix a violation while I still remember the context |
| Research Engineer | every invariant to have a test proving it can fail | I know the harness is real |
| Reviewer | violations reported in biological terms | I can judge whether the rule or the content is wrong |
| Integrator | to know a release passed every blocking invariant | I can rely on structural guarantees |
| Anyone | to know what validation does not check | I do not mistake consistency for correctness |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-VALD-001 | Must | Every INV row in BIO_Validation_Framework has an executable check named in that row | Given an INV row with no named check, when the harness starts, then it errors on the unimplemented invariant; and given all rows implemented, then it runs | An invariant in prose only is BRB-26 |
| FR-VALD-002 | Must | Every invariant has a negative test that injects a violation and requires detection | Given `biocheck --selftest`, when run, then each invariant's injected violation is detected; and given an invariant whose injected violation is not detected, then the self-test fails loudly | A validator that cannot fail is not a validator |
| FR-VALD-003 | Must | Blocking invariants prevent the write or release; advisory invariants report without blocking | Given content violating a blocking invariant, when committed, then the write is refused; and given an advisory violation, then it is recorded and reported without blocking | The blocking/advisory split must be visible, or advisory findings become noise |
| FR-VALD-004 | Must | Validation runs at commit, in CI, and before every release | Given a commit touching `ontology/`, when hooks run, then the harness runs on the affected scope; and given a release, then the full harness runs and its result is recorded in the manifest | Fast at commit, exhaustive at release; a slow commit check gets disabled |
| FR-VALD-005 | Must | Violation messages name the biological problem, not only the schema fault | Given an inadmissible relation, when reported, then the message names the relation, both entities, and both levels; and given a missing unit, then it names the quantity and its path | A curator debugging a schema message learns nothing about the model |
| FR-VALD-006 | Must | Validation results are recorded per release and are queryable | Given a release, when its validation record is requested, then per-invariant pass/fail counts and any advisory findings are returned | G-05 is computed from this record, not asserted |
| FR-VALD-007 | Must | The harness reports what it does not establish, alongside its results | Given a passing validation run, when its report is produced, then the report states that consistency is not correctness and names the expert gates that carry correctness | Passing checks are exactly when overconfidence sets in |
| FR-VALD-008 | Should | The harness runs on a partial scope for fast local iteration and on full scope in CI | Given a changed subtree, when run locally, then only affected invariants execute; and given CI, then the full set executes regardless | Local speed determines whether the tool is used at all |
| FR-VALD-009 | Should | The harness and the spec-graph validator share finding levels, flags, and exit codes | Given either tool run with `--strict`, when warnings exist, then both exit non-zero; and given clean runs, then both exit zero | Two validators with different conventions is one validator people misread |
| FR-VALD-010 | Could | Validation history is trended so that a rising advisory count is visible before it becomes a blocker | Given several releases, when trends are requested, then per-invariant finding counts over time are returned | Slow degradation is invisible in a pass/fail view |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Entity | R | subject of most invariants |
| Relationship | R | admissibility and hierarchy checks |
| Claim | R | evidence, unit, species checks |
| Process | R | functional and temporal checks |
| Overlay | R | personalization checks |
| SpatialIdentity | R | licence tier and binding checks |
| GeometryAsset | R | licence tier checks |
| ScaleLevel | R | depth and mode checks |
| KnowledgeRelease | RW | validation record per release |

## States & Transitions
A validation run is `pending` → `running` → (`passed` | `failed` |
`passed_with_advisories`). A release cannot leave `draft` unless its run is
`passed` or `passed_with_advisories` with every advisory dispositioned.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Empty: an empty ontology directory | passes with zero entities checked and reports the zero explicitly rather than a bare success | FR-VALD-006 |
| Invalid input: malformed JSON in the substrate | schema layer fails first with file and position; invariant checks do not run on unparseable input | FR-VALD-003 |
| Permission denied: not applicable — validation is read-only | stated explicitly | — |
| Concurrency: two commits validating simultaneously | independent runs on their own scopes; the release-level run is serialized | FR-VALD-004 |
| External dependency failure: an authority unreachable during an identifier check | that check reports `indeterminate`, distinct from pass and from fail, and blocks release but not local commit | FR-VALD-005 |
| Scale extreme: the substrate grows to millions of claims | partial-scope runs stay within the commit-time budget in PRD_Non_Functional_Requirements; full runs move to CI-only | FR-VALD-008 |
| An invariant is found to be wrong rather than the content | the invariant is changed through a Decision entry, never silently relaxed, and the self-test is updated with it | FR-VALD-002 |
| A blocking invariant would reject a large amount of legitimate legacy content | the content is quarantined and reported, not admitted; a Scope Reopen is the path, not a suppression flag | FR-VALD-003 |

## Dependencies
- On other modules: every module that writes to the substrate; PRD_FR_Versioning
  (release gating), PRD_FR_Curation (disposition of advisories)
- On external integrations: identifier resolvers for INV-10

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| INV rows with an implemented check | G-05 | 100%, enforced at harness startup |
| Invariants with a passing negative test | G-05 | 100% |
| Releases passing all blocking invariants | G-05 | 100% |
| Mean time from violation introduced to detected | G-05 | at commit time for in-scope invariants |

## Out of Scope for This Module
- Establishing biological correctness — the harness checks consistency only, and
  says so in every report
- Expert review (PRD_FR_Curation)
- Document-set validation, which `tools/specgraph.py` owns
- Automatically repairing violations

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| What is the commit-time budget beyond which curators will disable the hook? | Research Engineer | Phase 1 |
| Should `indeterminate` block a release, or only warn, when an authority is down? | Research Engineer | Phase 2 |
| How are advisory findings prevented from accumulating into permanent background noise? | Research Engineer | Phase 3 |
