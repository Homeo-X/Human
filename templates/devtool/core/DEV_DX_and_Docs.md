---
doc: DEV_DX_and_Docs
tier: standard+
version: 0.0.0
status: template
owner: ux
last_updated: —
---

# Developer Experience & Documentation

## Getting Started (the load-bearing artifact)
The path from nothing to first success, as the literal commands/code —
target ≤ <15> minutes on a clean machine. Every prerequisite explicit.
This section is executed, not just read: it runs in CI against releases.

## Golden Paths (use cases as code)
_One per primary use case — the User Flows analog. Each is a complete,
compiling sample._
| Path | Sample (link/inline) | Exercises (FR-API refs) |
|---|---|---|

## Documentation Map
| Doc Kind | Covers | Generated or Authored | Drift Guard |
|---|---|---|---|
| Reference | every non-internal surface row | generated from source where possible | surface⇄docs diff in CI |
| Guides | golden paths + concepts | authored | samples compiled in CI |
| Migration guides | per breaking change | authored | required by FR-VERS protocol |
| Changelog | every release | authored/conventional | release gate |

## Error Message Style
Shape: what happened → why (best known) → the remedy → a docs link.
Written for the developer at 2am; no blame, no jargon walls, machine-
readable code included (FR-API-002).

## Feedback & Support Surface
Where issues go, response expectations, how API pain feeds the punch list
(DX findings are design input, not support noise).

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | Notes |
|---|---|---|---|---|
| FR-DX-001 | Must | Getting-started executes green in CI on the compat matrix's primary cell | Given a clean CI environment, when the getting-started commands run verbatim, then first success is reached | |
| FR-DX-002 | Must | Every golden-path sample compiles/runs in CI per release | Given a release candidate, when samples build, then zero failures | |
| FR-DX-003 | Must | Reference covers 100% of non-internal surface (drift gate) | Given the surface inventory, when diffed against reference docs, then no undocumented or ghost entries | |
