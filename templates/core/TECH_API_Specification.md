---
doc: TECH_API_Specification
tier: standard+
version: 0.0.0
status: template
owner: architect
last_updated: —
---

# API Specification

_Brownfield runs: current-state facts cite their grounding source (tool +
date, per INTEGRATIONS.md); to-be-built content is explicitly marked._

_If the product has no API surface (pure client tool), state that and stop.
Coverage rule: every FR module must map to endpoints here or be explicitly
marked client-only._

## Conventions
- Style (REST/GraphQL/RPC), versioning scheme, pagination, timestamps, IDs

## Authentication & Authorization
- Scheme, token lifetime, how roles/permissions are enforced per endpoint

## Resources & Endpoints
_One subsection per resource (resources come from PRD_Data_Overview
entities — same names)._

### <Resource>
| Method | Path | Description | Auth (role) | FR Refs |
|---|---|---|---|---|

## Error Handling
- Standard error shape (code, message, correlation ID); table of shared
  error codes and when each is returned

## Rate Limits & Idempotency
- Limits per client class; which mutating endpoints require idempotency keys

## FR → API Coverage Check
| FR Module | Covered By (resources) or Client-Only |
|---|---|
