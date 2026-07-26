---
doc: PRD_Acceptance_Criteria_and_DoD
tier: light+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Acceptance Criteria & Definition of Done

## Acceptance Criteria Convention
Per-requirement criteria live in each FR module's requirements table, in
Given/When/Then form. This file defines the convention, the biological-claim
analog, and the release-level gates — it does not duplicate per-FR criteria.

- Format: **Given** [context], **when** [action], **then** [observable outcome].
- Every Must requirement has at least one criterion covering the happy path and
  at least one covering its most likely failure mode.

### The biological-claim analog
A biological assertion cannot be Given/When/Then'd — it is not a behaviour. The
bio profile's acceptance analog applies: **a biological claim is accepted when it
carries an evidence class, a complete provenance record, and passes the INV
invariants, with a named reviewer within their declared competence.**

Content that can be neither behaviourally specified nor evidence-graded is not
admissible. There is no third category, and in particular there is no "obviously
true, no source needed" category — that is precisely where inherited errors live.

## Release-Level Acceptance
| Gate | Evidence Required | Owner |
|---|---|---|
| All blocking invariants pass | `biocheck` run recorded in the release manifest, zero blocking failures | Research Engineer |
| Negative tests pass | `biocheck --selftest` detects every injected violation | Research Engineer |
| Spec graph is clean | `tools/validate.sh --docs docs/` and `specgraph --strict` exit zero | Research Engineer |
| Rubric pass complete | `docs/BIO_Model_Review.md` with all 30 BRB items dispositioned and no unresolved flags | Model Reviewer |
| Every Must has implementation trace | `specgraph --trace` reports no untraced Must for built modules | Research Engineer |
| Evidence completeness | 100% of claims carry complete records; UNKNOWN count published | Biology Lead |
| Licence manifest complete | every source verified, every asset tiered, no T1/T2 in T0 | Licence owner |
| Reproducibility | release rebuilds byte-identically from clean checkout | Research Engineer |
| Domain review complete | every new entity, EVC-1/EVC-2 claim, and mechanism reviewed within competence scope | Biology Lead |
| Non-diagnostic boundary present | every personalized and clinical-adjacent surface carries it | Model Reviewer |
| Red-team dispositioned | every CH accepted, refuted with evidence, or acknowledged by Decision; unresolved S1/S2 escalated | Orchestrator |

## Phase 0 Exit Criteria (this delivery)
- [ ] Every INV row has an executable check named in the row
- [ ] Every INV has a passing negative test in `--selftest`
- [ ] The cardiovascular vertical slice validates clean end to end, L0 to L10
- [ ] `bash tools/validate.sh` passes on the framework tree including `templates/bio/`
- [ ] `bash tools/validate.sh --docs docs/` passes
- [ ] `python3 tools/specgraph.py docs/ --strict` exits zero
- [ ] All 30 BRB items dispositioned with no unresolved flags
- [ ] The challenge register exists with every CH dispositioned
- [ ] MANIFEST is refreshed and matches the file set

## Definition of Done (per work item)
- [ ] Code reviewed
- [ ] Tests written and passing (unit plus the FR's acceptance criteria)
- [ ] Meets acceptance criteria as written, or criteria updated with PM sign-off
- [ ] For content: evidence class assigned, provenance complete, reviewer named
      within their competence scope
- [ ] For content: species field populated; units on every quantity
- [ ] For content: compilation status accurate — not promoted by reformatting
- [ ] Declared scale depth respected, even where the content is correct
- [ ] No new Must-severity accessibility or security findings
- [ ] Implementation and tests annotated with the FR ids they realize
      (AGENTS.md §10 traceability)
- [ ] Docs updated, including this spec: version bump and Decision entry where a
      decision changed
- [ ] Validators pass locally before commit

## What "Done" Explicitly Does Not Mean
A completed item is not a correct one. Passing every gate above establishes that
the model is internally consistent, properly graded, within its declared scope,
and reviewed by someone competent to review it. It does not establish that the
biology is right — the sources and the reviewers carry that, and both can be
wrong together.

This paragraph is part of the Definition of Done because the moment a team stops
believing it is the moment the checklist starts substituting for judgment.
