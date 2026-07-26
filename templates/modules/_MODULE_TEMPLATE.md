---
doc: PRD_FR_<Module>
tier: any
version: 0.0.0
status: template
owner: pm        # UX adds the UX Considerations section in its review pass
last_updated: —
---

# Functional Requirements — <Module>

_This is the canonical skeleton for ANY module. When scoping produces a
module with no pre-filled library file (modules/common, /ecommerce, /saas,
/ai), instantiate this and rename <Module> and <AREA> throughout. Every FR
module file — library or not — must contain all sections below; write
"None" deliberately rather than deleting a section silently._

## Purpose & Scope
_What this module covers, and the boundary with adjacent modules (name
them). One sentence each._

## User Stories
| As a… | I want… | So that… |
|---|---|---|

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | UX Considerations |
|---|---|---|---|---|
| FR-<AREA>-001 | Must | | | |

## Data Touched
_Entities read/written — names must match PRD_Data_Overview. New entities
this module introduces get flagged for the Architect._
| Entity | Read/Write | Notes |
|---|---|---|

## States & Transitions
_If this module owns stateful objects: allowed states and transitions.
Otherwise "None"._

## Edge Cases & Error States
_Minimum coverage: empty states, invalid input, permission denied,
concurrency/conflict, external-dependency failure, scale extremes._
| Scenario | Expected Behavior | FR Ref |
|---|---|---|

## Dependencies
- On other modules:
- On external integrations:

## Success Metrics
_At least one metric tracing to a KPI in PRD_Executive_Summary (Standard/Full)
or Product_Brief §Success Criteria (Light)._
| Metric | Traces To (KPI id) | Target |
|---|---|---|

## Out of Scope for This Module
-

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
