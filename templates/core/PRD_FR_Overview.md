---
doc: PRD_FR_Overview
tier: standard+   # at Light, the Product_Brief's FR table replaces this
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Overview

_Index of all FR module files. The module list is decided per product during
scoping (see AGENTS.md) — there is no default set._

## Modules
| Module | File | Area Code | Status | Cross-Cutting Concerns Folded In |
|---|---|---|---|---|
| | PRD_FR_<Module>.md | | | |

## Cross-Cutting Concern Decisions
_MANIFEST.md is authoritative. Either mirror its table here or simply
reference it ("see MANIFEST.md") — referencing avoids drift and is
preferred when the audiences are the same people._
| Concern | Decision | Location / Reason |
|---|---|---|

## Requirement ID Convention
`FR-<AREA>-<NNN>`, e.g. `FR-AUTH-001`. Area codes are 2–5 uppercase letters,
unique per module, listed in the Modules table above. IDs are never reused
after deletion — retire, don't recycle.

## Priority Levels
- **Must** — required for launch
- **Should** — important, not launch-blocking
- **Could** — nice to have
