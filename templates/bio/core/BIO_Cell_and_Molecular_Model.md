---
doc: BIO_Cell_and_Molecular_Model
tier: standard+   # foldable into BIO_Anatomical_Ontology only when max declared depth ≤ L5 everywhere
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Cell and Molecular Model

_Levels L6–L10: cell populations, cell types, subcellular structures, molecular
mechanisms, and biochemical processes. The level at which a model most easily
acquires false precision, so every section here carries its own limits._

## Cell Type Taxonomy
_Which taxonomy is authoritative, at which version, and what happens when it
revises. Cell type is not a settled category; say which definition is in use._

| Rule | Statement |
|---|---|
| Authority and version | |
| Definition basis (morphological / molecular / functional) | |
| Handling of upstream revisions | |
| Handling of states vs types | |

## Cell Types Represented
| Cell Type | Tissue / Organ | Level | Representation Mode | Species Provenance | Evidence Class |
|---|---|---|---|---|---|

## Tissue Organization
_How cells are arranged into tissues: composition, architecture, and where the
model represents arrangement versus merely composition._

## Subcellular Structures
| Structure | Present In | Function Represented | Spatial Representation | Evidence Class |
|---|---|---|---|---|

## Molecular Entities
_Genes, proteins, metabolites, ions. Identity via external authority; state which._

| Class | Authority | Identifier Form | What Is Represented | What Is Not |
|---|---|---|---|---|

## Molecular Mechanisms
_Per mechanism: the chain, its cell-type specificity, its conditions, and its
boundary. A mechanism stated without its conditions is a mechanism stated wrongly._

### <Mechanism>
- **Chain:**
- **Cell-type specificity:**
- **Conditions under which it holds:** (in vivo / in vitro, temperature, pH, species)
- **Quantities:** value, unit, condition, source
- **Boundary:** where this mechanism's description stops and why

## Species Provenance
_Human-derived vs animal-derived data, per claim. A human model containing
unlabelled mouse data is wrong, not approximate._

| Claim Domain | Predominant Source Species | Transfer Justification | Flagged To User? |
|---|---|---|---|

## In Vitro to In Vivo Transfer
_Where measured values come from preparations that are not a living human, and
what that costs in confidence._

## Known False-Precision Risks
_The specific places this document could mislead, named by its own authors._

| Risk | Where | Mitigation |
|---|---|---|
