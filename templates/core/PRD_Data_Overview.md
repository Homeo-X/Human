---
doc: PRD_Data_Overview
tier: standard+   # at Light, fold into TECH_Implementation_Notes
version: 0.0.0
status: template
owner: architect
last_updated: —
---

# Data Overview & Core Entities

_Brownfield runs: current-state facts cite their grounding source (tool +
date, per INTEGRATIONS.md); to-be-built content is explicitly marked._

_The single source of truth for entity names and attributes. FR modules
reference entities by the names defined here; they do not redefine
attributes. Applies to any storage model — relational, document, local
device store, vector index._

## Core Entities
| Entity | Purpose | Owned By (module) | Lifecycle (create → … → delete/archive) |
|---|---|---|---|

## Relationships
_Cardinality between entities, in plain language or a Mermaid ER sketch._

## Key Attributes per Entity
_Per entity: name, type, required?, notes. Only attributes with product
meaning — not framework columns like updated_at._

### <Entity>
| Attribute | Type | Required | Notes / Constraints |
|---|---|---|---|

## Data Classification & Retention
| Entity / Attribute | Classification (public/internal/PII/sensitive) | Retention | Deletion Path |
|---|---|---|---|

## Volumetrics (order of magnitude)
_Expected row counts / growth — drives indexing and NFR targets._
