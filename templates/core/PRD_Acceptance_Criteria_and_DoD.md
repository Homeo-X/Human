---
doc: PRD_Acceptance_Criteria_and_DoD
tier: light+
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Acceptance Criteria & Definition of Done

## Acceptance Criteria Convention
Per-requirement criteria live in each FR module's requirements table, in
Given/When/Then form. This file defines the convention and release-level
gates — it does not duplicate per-FR criteria.

- Format: **Given** [context], **when** [action], **then** [observable outcome].
- Every Must requirement has ≥1 criterion covering the happy path and ≥1
  covering its most likely failure mode.

## Release-Level Acceptance
_Conditions for the release as a whole (not per-feature): e.g., all Must FRs
pass, NFR targets met on staging, security review closed._
| Gate | Evidence Required | Owner |
|---|---|---|

## Definition of Done (per work item)
- [ ] Code reviewed
- [ ] Tests written & passing (unit + the FR's acceptance criteria)
- [ ] Meets acceptance criteria as written, or criteria updated with PM sign-off
- [ ] No new Must-severity accessibility or security findings
- [ ] Implementation and tests annotated with the FR ids they realize
      (AGENTS.md §10 traceability)
- [ ] Docs updated (including this spec: version bump + change note)
- [ ] QA sign-off
