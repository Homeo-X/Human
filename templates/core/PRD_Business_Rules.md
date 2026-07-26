---
doc: PRD_Business_Rules
tier: standard+   # at Light, fold essential rules into Product_Brief
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Business Rules

_Domain policies that are true regardless of UI: rules the system must
enforce even if every screen changed. Write each rule so it is testable.
Populate only the categories that apply to this product; delete the rest._

## Rule Register
| ID | Rule | Applies To (entity/module) | Source (law, policy, stakeholder) | Exceptions |
|---|---|---|---|---|
| BR-001 | | | | |

## Category prompts (delete unused)
- **Monetization / pricing** — pricing logic, discounts, trials, refunds, quotas
- **Eligibility & entitlement** — who may access what, under which plan/role/region
- **Lifecycle & state rules** — allowed state transitions for core entities (draft→published, open→resolved…), retention and archival policy
- **Limits & quotas** — rate limits, storage caps, seat counts, fair-use rules
- **Compliance & regulatory** — tax, data residency, industry regulation, age gates
- **Temporal rules** — deadlines, expirations, grace periods, timezone handling

## Conflicts & Precedence
_When two rules can collide (e.g., a discount vs. a regional price floor),
state which wins._
