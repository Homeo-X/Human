---
doc: PRD_Security_Requirements
tier: standard+   # at Light, fold key rows into TECH_Implementation_Notes
version: 0.0.0
status: template
owner: architect
last_updated: —
---

# Security Requirements

## Threat Snapshot
_Top 3–5 realistic threats for THIS product (not a generic list): who
attacks, what they want, through which surface._
| Threat | Actor | Surface | Mitigation Ref |
|---|---|---|---|

## Authentication & Session Security
- Password/credential policy, MFA stance, session lifetime, token handling

## Authorization
- Enforcement point (API layer, DB row-level, both); deny-by-default statement;
  reference the Permissions model in the relevant FR module

## Data Protection
- In transit / at rest encryption; secrets management; PII handling per the
  classification table in PRD_Data_Overview

## Compliance
_Only regimes that actually apply (GDPR, HIPAA, PCI-DSS, SOC 2, local data
residency…). For each: which requirements bind, and where they're satisfied._

## Abuse Prevention
- Rate limiting, input validation stance, bot/fraud controls as applicable
- For AI surfaces: prompt-injection handling, output filtering, tool-call limits

## Audit Logging
| Event | Data Captured | Retention | Access |
|---|---|---|---|
