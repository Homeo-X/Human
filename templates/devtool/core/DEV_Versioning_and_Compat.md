---
doc: DEV_Versioning_and_Compat
tier: standard+
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Versioning & Compatibility

## Version Policy
Semver, interpreted for THIS tool: what counts as breaking (surface
removal, behavior change, error-type change, minimum-runtime bump —
decide each), what's minor, what's patch. Pre-1.0 policy stated if
applicable.

## Compatibility Matrix
| Dimension | Supported Range | Tested In CI? |
|---|---|---|
| Runtimes / language versions | | |
| OS / platforms | | |
| Peer/host frameworks (if plugin) | | |

## Deprecation Protocol
announce (release notes + in-code warning naming the replacement) →
grace ≥ <N> minor versions → removal in the next major. Every deprecation
row tracked:
| Symbol | Deprecated In | Replacement | Removal Target |
|---|---|---|---|

## Breaking-Change Protocol
A breaking change ships with: migration guide entry, codemod/migration
tool where feasible, and a Decision Log entry with `affects:` listing the
surface rows. Silent behavior change under the same major is a defect
class, not a judgment call.

## Support Windows
Which majors receive fixes, which receive security-only, for how long.

## Requirements
| ID | Priority | Requirement | Acceptance Criteria (Given/When/Then) | Notes |
|---|---|---|---|---|
| FR-VERS-001 | Must | Public-surface diff gate in CI: unapproved breaking diffs fail the release | Given a release build removing/changing a stable symbol, when CI runs, then it fails without an explicit approval artifact | |
| FR-VERS-002 | Must | Deprecation warnings per protocol, silenceable per site | Given a deprecated call, when executed, then one warning names the replacement and is suppressible | |
| FR-VERS-003 | Must | Compat matrix exercised in CI per its "tested" column | Given the matrix, when CI runs, then every tested-yes cell has a job | |
