---
doc: TECH_Data_Design
tier: standard+
version: 0.0.0
status: template
owner: architect
last_updated: —
---

# Data Design

_Physical realization of PRD_Data_Overview: same entity names, now with
storage-level decisions. Any storage model — tables, collections, device
stores, caches, vector indexes._

## Storage Overview
| Store | Technology | Holds | Why This Store |
|---|---|---|---|

## Schemas
_One subsection per entity/table/collection._
### <entity>
| Field | Type | Constraints | Notes |
|---|---|---|---|

## Relationships & Integrity
- Foreign keys / reference strategy; what enforces integrity (DB vs app)

## Indexing Strategy
_Derive from actual query patterns in the FR modules — list the query, then
the index that serves it._
| Query Pattern (FR ref) | Index |
|---|---|

## Migration & Versioning Strategy
- Migration tooling, backward compatibility rules, seed/fixture data

## Consistency Check
_Confirm every entity in PRD_Data_Overview appears here, and no schema here
lacks a PRD-level entity. List exceptions deliberately._
