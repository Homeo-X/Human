---
doc: BIO_Anatomical_Ontology
tier: standard+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Anatomical Ontology

_What exists, how it is identified, and how it is classified. This document
defines the ontology's shape and rules; the instances live in the substrate
(`ontology/`), not here._

## The Tree Is a View; the Graph Is the Model
The single most consequential structural decision in this project (D-006).

A hierarchy is how people navigate anatomy and how nearly every anatomical
resource is organized. It is also, as a model of biology, false — not
approximate, false. Biology is a graph, and the tree is one spanning presentation
of it.

**The pancreas is the standing counterexample.** In a tree it must be filed under
exactly one system, and whichever is chosen, the choice is wrong:

```
pancreas
├── part_of        → abdominal cavity           (containment: single-parent)
├── member_of      → digestive system           (functional membership)
├── member_of      → endocrine system           (functional membership)
├── produces       → pancreatic enzymes          (exocrine output)
├── produces       → insulin                     (endocrine output)
├── produces       → glucagon                    (endocrine output)
├── responds_to    → blood glucose concentration (regulatory input)
├── affects        → cellular glucose uptake     (downstream effect)
├── vascularized_by→ splenic, superior mesenteric arteries
└── innervated_by  → vagus nerve, coeliac plexus
```

Nine of those ten relationships cannot exist in a tree. The exocrine and
endocrine roles are not a primary fact plus a footnote; they are two equally real
participations in different systems, and the model represents them as such.

Accordingly:

| Structure | Status | Role |
|---|---|---|
| **Graph** | canonical | typed, multi-participation, carries spatial, functional, causal, regulatory, temporal, developmental, and evidential relations |
| **Navigation tree** | derived view | a chosen spanning presentation, computed from the graph, recomputable, and labelled as a view wherever a user might read it as structure |

`part_of` stays single-parent (INV-02) because *containment* genuinely is single:
the pancreas is inside the abdomen and nowhere else. Every other participation is
a separate typed relation. This is what lets multi-system membership be expressed
without corrupting the containment hierarchy that spatial reasoning depends on.

## Entity Classes
| Class | Level(s) | Definition | Boundary With Neighbour |
|---|---|---|---|
| Organism | L0 | the whole reference subject | vs Region: the organism is one entity, regions partition it |
| Region | L1 | a conventionally bounded division of the body | vs Organ: regions are spatial conveniences with no function of their own |
| System | L2 | a functional grouping of organs, not spatially contiguous | vs Region: a system is functional and may be diffuse; a region is spatial and always contiguous |
| Organ | L3 | a discrete structure with a characteristic composition and function | vs Structure: an organ is nameable in its own right; a structure is a named part of one |
| Structure | L4 | a named division of an organ | vs Tissue: a structure has a location and boundary; a tissue is a composition |
| TissueType | L5 | a class of tissue by composition and architecture | vs CellType: tissue is an arrangement of cells plus matrix, not a cell |
| CellPopulation | L6 | a statistical population of one cell type within a host tissue | vs CellType: a population has abundance and turnover; a type has neither |
| CellType | L7 | a class of cell by definitional basis (see below) | vs CellPopulation: the type is the class, the population is its occurrence |
| Organelle | L8 | a subcellular structure | vs Biomolecule: an organelle is an assembly with an architecture, not a molecule |
| Biomolecule | L9 | a molecular entity — gene, protein, metabolite, ion | vs Mechanism: a molecule is a participant; a mechanism is a chain |
| Mechanism | L9 | an ordered causal chain of molecular events | vs Process: a mechanism explains how; a process is the parameterized rate |
| Process | L10, spanning | a physiological or biochemical process with inputs, outputs, and state | vs Function: a function is what a thing is for; a process is what happens |
| Function | any | a teleological statement about what a structure does | vs Process: functions are ascribed, processes are enacted; a function without a process behind it is a label |
| Claim | n/a | a graded, sourced assertion (BIO_Evidence_and_Provenance) | not a biological entity; the unit of what is known |

## Identity and Identifiers
| Rule | Statement |
|---|---|
| Primary identifier | the external ontology term where one exists — `UBERON:0000948`, `CL:0000746`, `CHEBI:29101`. This is the identity, not a mapping to it (D-002) |
| Local identifier form | `HOX:<class>:<slug>` — e.g. `HOX:process:excitation-contraction-coupling` |
| When to mint a local ID | only when no suitable external term exists, or when the entity is a project construct (a scale contract, a spatial identity). Minted ids carry `minted: true` and a `minted_reason`, and INV-10 fails on an unflagged one |
| Stability guarantee | identifiers are never reused after retirement, never renumbered, and never repurposed. A retired id resolves to a tombstone naming its successor |
| Deprecation upstream | an upstream deprecation does not silently rewrite our graph. The old term is retained with `deprecated_upstream` and the replacement recorded; the swap is a reviewed change with a release note |
| Merge upstream | when upstream merges two terms we reference, both are retained pointing to the merged term, and any claim that distinguished them is flagged for review — the distinction may have been load-bearing for us |
| Split upstream | when upstream splits a term we reference, our entity is flagged as ambiguous and **blocked from promotion** until a reviewer assigns it to one side or declares it to span both |
| Minted-term budget | the count of minted ids is published per release. A rising count means the project is drifting away from community vocabulary and is treated as a signal, not a statistic |

## Relationship Types
Every edge is typed. An untyped edge is a claim nobody can check, and the seed
corpus's cross-links are the reason this table exists (D-007).

| Relation | Inverse | Cardinality | Admissible Between | Semantics |
|---|---|---|---|---|
| `part_of` | `has_part` | many-to-**one** | L1→L0, L3→L1, L4→L3, L8→L7 | physical containment; single-parent, acyclic (INV-02) |
| `member_of` | `has_member` | many-to-many | L3→L2, L7→L6 | functional membership; the pancreas relation |
| `located_in` | `location_of` | many-to-many | any structural level → L1 | spatial presence without containment semantics |
| `adjacent_to` | `adjacent_to` | many-to-many, symmetric | same level | shares a boundary |
| `connected_to` | `connected_to` | many-to-many, symmetric | L3–L4 | continuous lumen or physical continuity |
| `composed_of` | `constitutes` | many-to-many | L3/L4→L5, L5→L6 | composition, not containment |
| `innervated_by` | `innervates` | many-to-many | L3/L4→L3/L4 | neural supply |
| `vascularized_by` | `vascularizes` | many-to-many | L3/L4→L3/L4 | arterial supply |
| `drained_by` | `drains` | many-to-many | L3/L4→L3/L4 | venous or lymphatic drainage |
| `produces` | `produced_by` | many-to-many | L3/L7→L9 | synthesis or secretion of a molecular entity |
| `consumes` | `consumed_by` | many-to-many | L10→L9 | substrate consumption |
| `transports` | `transported_by` | many-to-many | L8/L9→L9 | movement across a boundary |
| `converts` | `converted_by` | many-to-many | L9/L10→L9 | chemical transformation |
| `responds_to` | `signals_to` | many-to-many | any→L9 or a state variable | regulatory input |
| `regulated_by` | `regulates` | many-to-many | any→any | control relationship |
| `activates` / `inhibits` | `activated_by` / `inhibited_by` | many-to-many | L9/L10→L9/L10 | directional modulation with a sign |
| `differentiates_into` | `differentiates_from` | many-to-many | L7→L7 | developmental transition |
| `originates_from` | `gives_rise_to` | many-to-many | L7→L7, L3→embryonic structure | developmental origin |
| `realizes` | `realized_by` | many-to-many | L9→L10 | a mechanism realizing a process |
| `participates_in` | `has_participant` | many-to-many | any→L10 | an entity taking part in a process |
| `causes` | `caused_by` | many-to-many | any→any | **restricted**: requires an evidence class of EVC-2 or better and, if it spans more than one level, a skip justification (INV-05) |
| `contributes_to` | `contributed_to_by` | many-to-many | any→any | partial causation; the honest form when `causes` is too strong |
| `associated_with` | `associated_with` | many-to-many, symmetric | any→any | **an observed relationship of unstated type.** The seed corpus's cross-links land here. Carries its prose justification. Never rendered as a mechanism, never promoted without a curator choosing a type (BRB-30) |
| `is_a` | `subsumes` | many-to-many | same level | **subsumption, and explicitly not containment.** A cardiomyocyte *is a* muscle cell; neither contains the other and both sit at the same granularity. Excluded from the containment ladder, from `lineage()`, and from the navigation tree — an imported ontology's `is_a` hierarchy is full of abstractions like "thoracic segment organ", and admitting them as structure would make the body navigable into concepts (D-023) |

**The `associated_with` rule is the compilation discipline in one line:** knowing
*that* two things are related is not knowing *how*. The corpus tells us the
parathyroid and bone remodelling are connected; typing that as
`regulates` — with parathyroid hormone driving osteoclast activity — is curation
work with a source, not a rename.

## Hierarchy Rules
- **Containment** (`part_of`) is single-parent and acyclic. Enforced by INV-02.
- **Membership** (`member_of`) is many-to-many and carries no spatial meaning.
- **Location** (`located_in`) relates a structure to a region without asserting
  that the region contains it in the part-whole sense.
- **Multiple parenthood is legitimate** only through membership and location.
  Where an entity genuinely appears to need two containment parents, that is a
  modelling error or a genuine anatomical ambiguity — and the second case is
  recorded as an explicit `containment_ambiguity` with its sources, not resolved
  by picking.

## Naming and Terminology
| Field | Rule |
|---|---|
| Preferred term | Terminologia Anatomica where it defines one; otherwise the authority for that level |
| Synonyms | retained with their source and register (clinical, historical, colloquial) |
| Eponyms | retained as synonyms, never as the preferred term — an eponym encodes attribution, not anatomy |
| Abbreviations | retained with expansion; never the preferred term |
| Localization | anatomical terminology is nomenclature-anchored, so a translation is a **term record with its own authority**, not a string in a translation file. A locale without an authoritative nomenclature falls back to the Latin term rather than to a machine translation, because a plausible mistranslation of an anatomical term is worse than an untranslated one |

This is why internationalization is folded into the ontology rather than treated
as a presentation concern (MANIFEST cross-cutting table).

## Anatomical Variation
| Variation Type | Representation | Prevalence Source | Default Behaviour |
|---|---|---|---|
| Presence or absence (e.g. palmaris longus) | variant entity linked by `variant_of` with a prevalence claim | population anatomy literature | reference shows the majority form, labelled as such, with variants one step away |
| Branching pattern (vascular, neural) | variant relationship set, not a variant entity | population anatomy literature | reference shows the modal pattern with prevalence stated |
| Morphometric range | a distribution on the property, never a point value | population studies | ranges shown; a single number is never displayed for a varying quantity |
| Sex-variant structures | distinct entities, both first-class | anatomical reference | per the reference-subject declaration in BIO_Research_Charter, with its stated asymmetry and RSK-07 |
| Positional variation (situs) | variant of the whole spatial identity | clinical literature | not represented in the reference; recorded as a known unrepresented case |

**The open question this table does not settle** — where variation stops being a
variant and becomes a separate entity — is recorded in BIO_Research_Charter and
blocks Phase 3. It is a real modelling boundary, not a detail.

## Diffuse and Non-Discrete Structures
Several systems resist the organ abstraction, and forcing them into it produces
confidently wrong anatomy:

| System / Structure | Why It Resists | Handling |
|---|---|---|
| Immune | largely a distributed cell population, not organs | represented as populations (L6) with `located_in` many tissues; the organ-level entities (thymus, spleen, nodes) are real but are not the system |
| Endocrine | glands plus scattered endocrine cells in non-endocrine organs | organ entities plus `member_of` from organs whose endocrine role is partial — the pancreas case, generalized |
| Fascia | continuous throughout the body with conventional rather than physical divisions | one continuous entity with named regions as `located_in` divisions, not `part_of` subdivisions |
| Interstitium | fluid-filled spaces whose status as a structure is recent and contested | represented at EVC-6 with the contested status explicit; the corpus's own frontier framing is preserved |
| Microbiome | not human tissue | out of scope (BIO_Research_Charter), recorded as a deliberate exclusion rather than an omission |

## Compilation Status
Every entity and relation carries the ladder from D-007, and it is visible
wherever the content is:

| Status | Means | May Be Used For |
|---|---|---|
| `narrative` | prose as received; machine-readable, not machine-usable | display with its source; never for reasoning, traversal-based inference, or simulation |
| `structured` | entity, class, level, and typed relations assigned and reviewed | navigation, search, cross-scale traversal |
| `mechanistic` | inputs, outputs, state variables, participants, timescale defined | mechanism display, dependency and failure analysis |
| `parameterized` | quantities attached with units, sources, and conditions | simulation, quantitative comparison |

Promotion requires the work, not a reformat. A `narrative` entity rendered
alongside a `mechanistic` one without the distinction being visible is BRB-29.

## Ontology Versioning
- The ontology is released as a versioned, addressable artifact (PRD_FR_Versioning).
- **Breaking:** removing an entity, changing an identifier, changing a relation's
  semantics, narrowing a declared scale depth.
- **Non-breaking:** adding entities or relations, promoting compilation status,
  adding claims, correcting prose.
- Every release pins the version of every external authority it references, so a
  claim can be re-evaluated against the vocabulary that was current when it was
  made.
- Downstream references survive a breaking change through tombstones: a retired
  identifier resolves, and says what replaced it and why.

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
| Which of the 31 seed cross-links can be typed from their existing sources, and which need new sourcing? | Biology Lead | Phase 1 |
| Does `associated_with` need a sub-vocabulary (co-location, co-regulation, shared-dependency) or does typing always resolve it? | Biology Lead | Phase 2 |
| How is a containment ambiguity displayed without implying the model is confused rather than the anatomy? | Model Reviewer | Phase 2 |
| What is the review cost per entity to move `narrative` to `structured`, and does it scale to 157 seed nodes? | Biology Lead | Phase 1 |
