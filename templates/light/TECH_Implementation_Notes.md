---
doc: TECH_Implementation_Notes
tier: light   # Light tier only — replaces all four TECH files + Data Overview,
              # Integrations, NFR, Security for small scopes
version: 0.0.0
status: template
owner: architect
last_updated: —
---

# Implementation Notes — <Name>

## Approach
_A few sentences: where this lives (new service? feature in existing app?),
stack, and why. Link Decision Log entries for anything contested._

## Data
| Entity | Storage | Key Fields | PII? | Retention |
|---|---|---|---|---|

## API / Interfaces
_Endpoints, commands, or component props this exposes or consumes. Skip if
purely internal to an existing surface._
| Method/Type | Path/Name | Purpose | Auth |
|---|---|---|---|

## Integrations
| System | Purpose | Failure Behavior |
|---|---|---|

## Non-Functional Notes
_Only targets that actually bind: expected load, latency needs, availability
expectations, platform support. Numbers, not adjectives._

## Security Notes
- AuthN/AuthZ approach, data protection, audit needs — proportional to the
  data classification above

## Rollout
- Feature flag? Migration? Rollback path?
