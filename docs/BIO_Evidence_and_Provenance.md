---
doc: BIO_Evidence_and_Provenance
tier: light+
version: 1.0.0
status: draft
owner: architect
last_updated: 2026-07-26
---

# Evidence and Provenance

_How every assertion in the model is graded, sourced, and constrained. The grade
is a data field with consequences, not a citation style._

## Evidence Classes
_The `EVC` ladder. Each class states what admits a claim to it and, critically,
the promotions that are forbidden._

| ID | Class | Admits | Admissible Source Types | Min Independent Sources | Forbidden Promotion |
|---|---|---|---|---|---|
| EVC-1 | VERIFIED | direct measurement in living humans, reproduced independently, with stated conditions | `primary research`, `systematic review` | 2 | nothing may be promoted TO this class by inference, aggregation, or consensus of textbooks. Only a qualifying measurement admits — **a reference textbook can never support EVC-1**, however authoritative |
| EVC-2 | STRONGLY_SUPPORTED | multiple independent sources agree, but reproduction conditions differ or the measurement is indirect | `primary research`, `systematic review`, `reference textbook`, `anatomical atlas`, `curated database` | 2 | EVC-3 through EVC-8 may never be promoted here by adding another source of the same type; independence is the requirement, not count |
| EVC-3 | MODELLED | computed or derived from known biology through a stated model, not measured | `primary research`, `derived model`, `curated database` | 1 | a modelled value may never be presented as measured, and the model that produced it must be named |
| EVC-4 | APPROXIMATED | a deliberate simplification of something known to be more complex | `primary research`, `reference textbook`, `derived model`, `anatomical atlas` | 1 | an approximation may never be promoted by removing the note that says it is one. This is the single most likely silent failure in the system |
| EVC-5 | INFERRED | reasoned from adjacent established facts, without direct evidence for this specific claim | `primary research`, `reference textbook`, `derived model`, `expert assertion` | 1 | inference may never be promoted to EVC-2 by finding a source that repeats the same inference |
| EVC-6 | HYPOTHESIZED | scientifically plausible, proposed in the literature, not established | `primary research`, `reference textbook`, `expert assertion` | 1 | may never be displayed without its hypothetical status; may never become the default answer to a user question |
| EVC-7 | CONFLICTING_EVIDENCE | credible sources disagree and the disagreement is not resolved | `primary research`, `systematic review`, `reference textbook`, `anatomical atlas`, `curated database`, `derived model`, `expert assertion` | 2 | may never be resolved by the system choosing one side. Resolution requires either new evidence or an expert-reviewed adjudication recorded as such |
| EVC-8 | UNKNOWN | no reliable representation currently exists | none — an UNKNOWN claim carries no sources | 0 | **UNKNOWN never becomes an assumption.** It may only leave this class when a qualifying source is added. An empty field is not UNKNOWN; UNKNOWN is asserted deliberately |

_The `Admissible Source Types` and `Min Independent Sources` columns are
machine-read: `tools/biocheck.py` derives its class rules from this table rather
than holding a second copy, and errors if its built-in fallback ever diverges
from what is written here. That check exists because the first version of this
project had exactly that divergence — the prose forbade textbook-sourced EVC-1
and the checker permitted it (D-013)._

**The promotion rule, stated once:** a claim's class may only change when its
*evidence* changes. Reformatting, re-hosting, re-citing, aggregating, or
repeating a claim changes nothing. Every class change is recorded with the
evidence that caused it and the reviewer who accepted it (PRD_FR_Curation).

## Terminological Claims — a definition is not a finding

The ladder above grades **biological evidence**: what was measured, modelled, or
approximated about a body. A definition is a different kind of statement. "The
heart is a myogenic muscular circulatory organ" asserts what a term denotes
according to some authority; no measurement could confirm or refute it, and
grading it APPROXIMATED puts it on a register where it can be mistaken for a
finding.

This project made exactly that error at scale: **156 of 165 claims — 94% — were
definitions carried on the evidence ladder** until D-021 separated them. The
error would have been multiplied by the ontology import, which supplies
definitions by the tens of thousands.

Terminological claims are graded by the authority behind them and whether that
authority's stated source resolves.

| Class | Name | Admission Rule | Requires |
|---|---|---|---|
| TRM-1 | AUTHORITATIVE_TRACEABLE | a recognised naming authority states the definition, and its own cited source resolves to a retrievable identifier | `authority`, `definition_source` |
| TRM-2 | AUTHORITATIVE_UNTRACEABLE | a recognised naming authority states it, but its cited source cannot be resolved | `authority` |
| TRM-3 | DERIVED | restated or paraphrased from prose, with no resolvable definition source of its own | `authority` (the document restated) |
| TRM-4 | UNSOURCED | a label with no authority behind it — admissible only as a placeholder, never displayed as a definition | `authority` = none, stated |

**The separation rule, stated once:** a terminological claim may never be cited
as evidence for a biological assertion, and a biological claim may never be
graded on the TRM register. `INV-18` enforces both directions, and the
groundedness guard refuses an assertion about the body grounded only in
definitions — a model that answered "what does the heart do?" from a dictionary
would be fluent and empty.

A terminological claim is **not weaker** than a biological one; it is about
something else. TRM-1 is a fully satisfactory grade for a definition, in the way
EVC-1 is for a measurement.

## The Claim Record
_The mandatory shape of any assertion the system stores or displays._

| Field | Required | Notes |
|---|---|---|
| subject (entity id) | yes | resolves to a defined ontology entity |
| predicate | yes | drawn from the typed relation vocabulary or the property vocabulary |
| object / value | yes | entity reference, categorical value, or quantity |
| unit | if quantitative | UCUM code; a quantitative claim without a unit is rejected at ingest (INV-04) |
| evidence class | yes | one of EVC-1 through EVC-8 |
| source(s) | unless EVC-8 | full citation with a resolvable identifier (DOI, ISBN, accession) |
| source type | yes | from the vocabulary below |
| species | yes | `Homo sapiens` or the actual species; `not applicable` for purely structural conventions |
| population / context | yes | the population the claim holds for — age range, sex, health state, or `unspecified in source`, which is itself informative |
| measurement conditions | if quantitative | in vivo / in vitro / ex vivo, temperature, pH, preparation |
| date asserted | yes | when this claim entered the model |
| known limitations | yes | what this claim does not cover; `none identified` must be a deliberate entry |
| conflicting claims | if any | references to the competing claim records |

## Source Register
| Source | Type | Authority Basis | Licence | Attribution Requirement | Downstream Constraint |
|---|---|---|---|---|---|
| UBERON | curated database | community anatomy ontology, actively maintained | CC-BY 3.0 | cite ontology and version | none beyond attribution |
| Foundational Model of Anatomy (FMA) | curated database | structured anatomical reference | CC-BY 3.0 | cite ontology and version | none beyond attribution |
| Cell Ontology (CL) | curated database | community cell-type ontology | CC-BY 4.0 | cite ontology and version | none beyond attribution |
| Gene Ontology (GO) | curated database | community function ontology | CC-BY 4.0 | cite ontology and version | none beyond attribution |
| ChEBI | curated database | chemical entity reference | CC-BY 4.0 | cite database and release | none beyond attribution |
| HGNC / UniProt | curated database | gene and protein nomenclature | CC-BY 4.0 / CC-BY 4.0 | cite database and release | none beyond attribution |
| Terminologia Anatomica | reference textbook | international anatomical nomenclature authority | proprietary | terminology use, no redistribution of the work | terms may be used; the publication may not be reproduced |
| Standard physiology and anatomy reference texts | reference textbook | established teaching authority | proprietary | citation only | claims may be sourced; text may not be reproduced |
| Primary research literature | primary research | peer review | varies per publisher | full citation | quotation limits; data extraction generally permitted, verified per source |
| BodyParts3D | imaging dataset | derived from Visible Human-class imaging | CC-BY-SA 2.1 JP | attribution plus share-alike | **share-alike: quarantined asset tier per D-003** |
| Z-Anatomy | anatomical atlas | community-derived anatomical geometry | CC-BY-SA 4.0 | attribution plus share-alike | **share-alike: quarantined asset tier per D-003** |

_Source type vocabulary: primary research · systematic review · reference
textbook · anatomical atlas · imaging dataset · curated database · derived model
· expert assertion._

Each row is a starting register, not a completed audit. Every source's licence is
re-verified at ingest by the Provenance Agent (AGT-11) and at each release
(PRD_FR_Versioning); a source whose licence cannot be verified does not enter.

## Licensing Tiers
_Sources segregated by what they permit downstream, so a future relicensing does
not require re-deriving the model (D-003)._

| Tier | Permits | Sources | Segregation Mechanism |
|---|---|---|---|
| **T0 — core** | any downstream use with attribution | ontology terms, project-authored content, project-derived geometry | the ontology and evidence layers are T0 only, always. No T1 or T2 content is ever embedded in a claim record or entity |
| **T1 — share-alike** | use with attribution, derivatives inherit share-alike | BodyParts3D, Z-Anatomy and comparable geometry | separate asset package, per-asset licence metadata, referenced by entity id from T0 rather than embedded. A build selects tiers; T1 can be excluded without touching T0 |
| **T2 — reference-only** | citation, no redistribution | proprietary texts, Terminologia Anatomica | never stored as content. Only citations and the terms themselves enter the model |

The consequence worth stating: a permissive-only build is a configuration, and it
will have less geometry. Coverage in such a build is reported against the same
declared denominator, so the reduction is visible rather than hidden.

## Conflict Handling
_The system never silently resolves a disagreement._

| Conflict Type | Representation | User-Visible Behaviour |
|---|---|---|
| Two sources give different quantitative values | both claim records retained, each with its own conditions; the pair linked as conflicting | both values shown with their conditions and sources; if the conditions explain the difference, that explanation is shown instead of a range |
| Two sources give incompatible structural claims | both retained, class set to EVC-7 on both | the structural claim is presented as contested, with both positions attributed |
| A source contradicts a claim already in the model | the new claim enters as a conflict, never as an overwrite | contested marker appears on the entity; the curation queue receives a review item |
| Sources disagree because they describe different populations | not a conflict — a scoping error in the claim | both claims retained with their populations made explicit; INV-07 requires the population field, which is what surfaces this case |
| An expert adjudicates a conflict | adjudication recorded as its own claim, citing both originals and the reviewer | resolved claim shown, with the conflict and its adjudication one click away — never erased |

## Imported Evidence — the ECO mapping

Open biological databases annotate their assertions with **ECO**, the Evidence
and Conclusion Ontology (CC0). ECO says *how a conclusion was reached*, which is
the same question the EVC ladder asks, so imported claims arrive with their
evidence already characterised rather than needing it invented.

The mapping below is the authority; `tools/biocheck.py` derives from it, and a
divergence between the two is an error under INV-16 exactly as for the ladder.

| ECO | Meaning | Maps To | Note |
|---|---|---|---|
| ECO:0000006 | experimental evidence | EVC-2 | the strongest an import can *propose*; a curator decides whether it holds |
| ECO:0000033 | author statement supported by traceable reference | EVC-5 | a stated conclusion whose source resolves — inference, not measurement |
| ECO:0000034 | author statement without traceable support | EVC-6 | asserted in the literature, not established |
| ECO:0000205 | curator inference | EVC-5 | a database curator's reasoning from adjacent facts |
| ECO:0000203 | automatic assertion | EVC-6 | produced by a pipeline with no human in it |
| ECO:0000501 | evidence used in automatic assertion | EVC-6 | as above |

**A mapped class is a proposal, never an assertion.** BR-002 does not relax for
imported data: the mapping populates `proposed_class`, and the claim's asserted
`evidence_class` stays capped at what an automated actor may assign until a
curator confirms it (D-017). ECO:0000006 mapping to EVC-2 therefore means "a
reviewer is being asked to confirm EVC-2", not "this claim is EVC-2".

Terminological claims imported from an ontology are graded on the TRM register
and never touch this table — a definition's provenance is an authority, not an
experiment (D-021).

## The Evidence Pipeline
| Stage | Performed By | May Change | May NOT Change | Output |
|---|---|---|---|---|
| Source acquisition | Evidence Agent (AGT-2) | nothing; it collects | any existing claim | candidate source with licence verified |
| Extraction | Evidence Agent | proposes claim text | evidence class | extracted candidate claims |
| Entity resolution | Ontology Agent (AGT-1) | links claims to entity ids; proposes new entities | existing entity identity | resolved candidates, plus a new-entity queue |
| Claim extraction | Evidence Agent | structures the claim into the record shape | assign a class above EVC-5 | structured candidate claims |
| Evidence classification | Evidence Agent proposes; **curator decides** | proposed class | final class — an agent may never set EVC-1 or EVC-2 | classified candidates |
| Conflict detection | Validation Agent (AGT-10) | flags conflicts | resolve them | conflict set |
| Expert review | human domain reviewer | class, wording, limitations, acceptance | provenance history — it is append-only | reviewed claims |
| Canonical graph | Curation (PRD_FR_Curation) | admits the reviewed claim | anything unreviewed at EVC-1 or EVC-2 | canonical knowledge graph |

The rule that makes the pipeline meaningful: **no agent may set EVC-1 or EVC-2.**
The two classes that carry the most weight require a human reviewer, because
those are exactly the classes a confident language model would over-assign.

## Traceability Guarantee
For any claim in the model, the system can return, without human interpretation:
its evidence class, every source with a resolvable identifier, the species and
population, the measurement conditions where quantitative, the date, the stated
limitations, any conflicting claims, and the review history including who
accepted it and when.

Operationally: `GET /claims/{id}/provenance` returns this record; the same data
backs the evidence panel in every user surface. A claim that cannot produce this
record is not a claim — it fails INV-07 and does not enter the graph.

## Negative Knowledge
`UNKNOWN` (EVC-8) is stored as an asserted claim, not as an absent one. It is:

- **queryable** — a user or agent can ask what the model does not know about an
  entity, a subsystem, or a level, and receive an enumerated answer;
- **counted** — the absolute UNKNOWN count is published alongside G-03's
  completeness figure, specifically so completeness cannot be improved by
  deleting inconvenient claims;
- **displayed** — an entity with UNKNOWN claims shows them, rather than showing
  a shorter list that reads as complete.

A model that cannot express ignorance will manufacture confidence. This section
is the mechanism that stops it.
