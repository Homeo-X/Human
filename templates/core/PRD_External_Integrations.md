---
doc: PRD_External_Integrations
tier: standard+   # at Light or when few, fold into TECH_Implementation_Notes
version: 0.0.0
status: template
owner: architect
last_updated: —
---

# External Integrations

_One row per third-party system this product depends on. Categories below
are prompts, not requirements — a product with no payments has no payments
row._

## Integration Register
| System | Category | Purpose | Direction (in/out/both) | Criticality | Failure Behavior |
|---|---|---|---|---|---|

Category prompts: identity/SSO · payments/billing · communications
(email/SMS/push) · analytics/telemetry · AI/LLM providers · file storage ·
domain-specific (logistics, EHR, ERP, market data…) · internal systems.

## Per-Integration Notes
### <System>
- Auth method & credential ownership:
- Rate limits / quotas:
- Data exchanged (fields, PII flags):
- Sandbox/test story:
- Vendor lock-in / exit path:

## Webhooks & Callbacks Inbound
| Source | Event | Endpoint | Idempotency Strategy |
|---|---|---|---|
