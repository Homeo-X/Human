---
doc: PRD_FR_Overview
tier: standard+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Functional Requirements — Overview

_Index of all FR module files. The module list was decided at scoping (D-001) and
is authoritative in `MANIFEST.md`._

## Modules
| Module | File | Area Code | Status | Cross-Cutting Concerns Folded In |
|---|---|---|---|---|
| Ontology | PRD_FR_Ontology.md | ONTO | draft | terminology localization |
| Relationship Graph | PRD_FR_Relationship_Graph.md | REL | draft | none |
| Evidence | PRD_FR_Evidence.md | EVID | draft | source licensing, species provenance, negative knowledge, audit lineage |
| Scale Bridging | PRD_FR_Scale_Bridging.md | SCAL | draft | none |
| Spatial Representation | PRD_FR_Spatial_Representation.md | SPAT | draft | asset licence tiering |
| Navigation | PRD_FR_Navigation.md | NAV | draft | none |
| Search | PRD_FR_Search.md | SRCH | draft | findability, negative-knowledge query |
| Process Models | PRD_FR_Process_Models.md | PHYS | draft | none |
| Simulation | PRD_FR_Simulation.md | SIM | draft | none |
| Personalization | PRD_FR_Personalization.md | PERS | draft | uncertainty representation |
| Validation | PRD_FR_Validation.md | VALD | draft | units and quantities |
| Knowledge Retrieval | PRD_FR_Knowledge_Retrieval.md | RETR | draft | AI behaviour, evals, cost |
| Agent Definition | PRD_FR_Agent_Definition.md | AGD | draft | AI autonomy limits |
| Curation | PRD_FR_Curation.md | CUR | draft | permissions, admin tooling |
| Versioning | PRD_FR_Versioning.md | VER | draft | audit trail, import/export, reproducibility |

## Cross-Cutting Concern Decisions
`MANIFEST.md` is authoritative — see its Cross-Cutting Concern Decisions table.
It is referenced rather than mirrored here, because a second copy is a second
thing to drift.

## Requirement ID Convention
`FR-<AREA>-<NNN>`, e.g. `FR-ONTO-001`. Area codes are 2–5 uppercase letters,
unique per module, listed above. IDs are never reused after deletion — retire,
don't recycle.

**Correction from the brief:** the brief proposed `FR-3D-NNN`. An AREA code
containing a digit is inadmissible under AGENTS.md §6 and invisible to
`validate.sh`'s AREA scan. Spatial requirements use `FR-SPAT-NNN`. The brief's
`FR-CELL` is covered by SCAL, and `FR-AI` by RETR and AGD.

## Priority Levels
- **Must** — required for the phase in which the module is built
- **Should** — important, not phase-blocking
- **Could** — nice to have

## Module Dependency Order
The build order is not arbitrary; each module depends on the one before it
holding.

```
ONTO ──> REL ──> SCAL ──┬──> SPAT ──> NAV
  │        │            │
  └──> EVID ────────────┼──> SRCH
         │              │
         └──> VALD      └──> PHYS ──> SIM
                │
   VER <────────┘            PERS (Phase 7, depends on all)
    │
   CUR ──> RETR ──> AGD
```

ONTO and EVID are the foundation: nothing else is meaningful before entities have
identity and claims have grades. VALD spans everything, because an invariant that
arrives after the data it governs is an invariant that will find violations it
cannot fix.
