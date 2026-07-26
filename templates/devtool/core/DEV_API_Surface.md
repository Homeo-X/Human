---
doc: DEV_API_Surface
tier: standard+
version: 0.0.0
status: template
owner: ux
last_updated: —
---

# API Surface

_The public contract, exhaustively. If it's exported/reachable and not
here, that's drift (a cross-review finding). One table per surface kind —
delete unused kinds._

## Surface Inventory
### Functions / Methods / Endpoints / Commands
| Symbol / Route / Command | Purpose (one line) | Stability | Since | Notes |
|---|---|---|---|---|
Stability levels: `stable` (semver-protected) · `beta` (may change, minor)
· `experimental` (may vanish, flagged at use where possible) · `internal`
(exported by necessity, use forbidden — and marked so).

### Types / Schemas / Config Keys
| Name | Shape (or ref) | Stability |
|---|---|---|

## Design Conventions (the consistency contract)
- Naming grammar: verbs for actions, nouns for accessors; the ONE word per
  concept (create vs add vs new — pick, list forbidden synonyms)
- Argument order & options-object rules; sync/async convention; nullability
  and default rules
- Error contract: error type(s), machine-readable codes, and the rule that
  every thrown/returned error names its remedy (→ DX rubric)

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | DX Considerations |
|---|---|---|---|---|
| FR-API-001 | Must | Every stable symbol behaves per its inventory row and docs entry | Given any stable symbol's documented example, when executed against the release, then it behaves as documented | |
| FR-API-002 | Must | Errors follow the error contract with remedy included | Given any error path, when triggered, then the message carries code + remedy | |
| FR-API-003 | Must | `internal` surface unusable by accident | Given documented usage only, when following docs, then no internal symbol is required | |

## Edge Cases
| Scenario | Expected Behavior | Ref |
|---|---|---|
| Invalid input at the boundary | validated with the contract's error, never a stack trace from internals | FR-API-002 |
| Concurrent use (if applicable) | thread/async-safety per symbol stated in inventory notes | FR-API-001 |
