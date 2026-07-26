---
doc: BIO_Anatomical_Ontology
tier: standard+
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Anatomical Ontology

_What exists, how it is identified, and how it is classified. This document
defines the ontology's shape and rules; the instances live in the substrate
(`ontology/`), not here._

## Entity Classes
_The canonical classes and what distinguishes each from its neighbours. A class
whose boundary cannot be stated is a class that will accumulate misfiled
entities._

| Class | Level(s) | Definition | Boundary With Neighbour |
|---|---|---|---|

## Identity and Identifiers
_ID scheme, minting rules, stability guarantees, and cross-references to external
ontologies. State explicitly what happens when an external term is deprecated,
merged, or split upstream._

| Rule | Statement |
|---|---|
| Primary identifier | |
| External cross-references | |
| When to mint a local ID | |
| Stability guarantee | |
| Deprecation / merge / split handling | |

## Relationship Types
_Every typed relation the graph admits, its inverse, its cardinality, and the
levels between which it is admissible. An untyped edge is a claim nobody can
check._

| Relation | Inverse | Cardinality | Admissible Between | Semantics |
|---|---|---|---|---|

## Hierarchy Rules
_Containment vs part-of vs membership. Multiple parenthood: when it is legitimate
(an organ in a region AND a system) and when it signals an error._

## Naming and Terminology
_Preferred term, synonyms, eponyms, abbreviations, and the nomenclature authority
per level. How localization interacts with anatomical terminology._

## Anatomical Variation
_How variation is represented rather than averaged away: variant entities,
prevalence, and what the reference model shows by default._

| Variation Type | Representation | Prevalence Source | Default Behaviour |
|---|---|---|---|

## Diffuse and Non-Discrete Structures
_Systems that resist the organ abstraction (immune, endocrine, fascia, interstitium)
and how the ontology handles them without pretending they are discrete._

## Ontology Versioning
_How the ontology is released, what constitutes a breaking change, and how
downstream references survive one._

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
