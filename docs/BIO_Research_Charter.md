---
doc: BIO_Research_Charter
tier: standard+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Biological Research Charter

_What this model exists to answer, whose body it represents, and the boundary of
what it may claim. Written before the ontology, because the ontology's shape
follows from the question._

## The Modelling Question
A user should be able to start at any anatomical structure and move continuously
in two directions that existing tools keep apart: *inward* through the scale
ladder to the tissues, cells, and mechanisms that constitute it, and *sideways*
into what it does, what depends on it, and what happens when it fails — with
every step carrying the evidence that supports it and an honest marker where
evidence runs out.

The question is not "what does the body look like" and not "how does the body
work", but: **for any part of the body, what do we actually know, how do we know
it, and where does knowing stop?**

## The Reference Subject
The reference is never "a human". It is one declared configuration, and every
number in the model inherits its population.

| Property | Reference Value | Basis | Known Limitation |
|---|---|---|---|
| Species | Homo sapiens | scope definition | claims sourced from other species are marked and justified per INV-12 |
| Developmental stage | adult | scope definition | pediatric and geriatric anatomy differ structurally, not just in scale; neither is represented |
| Age range | 20–40 years | the range most reference physiology data describes | values drift with age; a claim's population field records the source's actual range, which is often narrower or unstated |
| Sex | anatomically male reference for sex-variant structures, with female variants recorded as declared variants rather than omissions | most open reference geometry is male-derived; recording the asymmetry is preferable to hiding it | this is a limitation of available source data, not a modelling choice we endorse. Female-reference parity is a Phase 3 objective, tracked as RSK-07 |
| Health state | no diagnosed pathology | scope definition | "healthy" is a source convention, not a measured state; sources define it differently and the claim record preserves each source's definition |
| Body habitus | values reported as population ranges, not a single body | avoids inventing a fictional individual | a user cannot ask "how tall is the reference model"; the model answers with a range and its source |

**Why this table matters:** a model that silently averages populations produces a
body that does not exist and reports its measurements with unearned precision.
The reference is a stated position, contestable and revisable, recorded here so
that it can be argued with.

## Scope of Represented Biology
| Subsystem | In / Out | Max Level (L0–L10) | Rationale |
|---|---|---|---|
| Cardiovascular | in | L10 | the designated vertical slice; cardiac excitation–contraction coupling is among the best-characterized human mechanisms, so it tests the substrate against strong evidence rather than weak |
| Respiratory | in | L5 | gas exchange requires tissue-level structure to be meaningful |
| Nervous | in | L5 | needed for L3 content elsewhere to cohere; deeper representation would be a research programme, not curation |
| Urinary | in | L5 | nephron function is tissue-level; transporter kinetics deferred |
| Musculoskeletal | in | L4 | highest-value enumerated content; bone remodelling deferred |
| Digestive | in | L3 | organ-level structure and function |
| Endocrine | in | L3 | organ-level; the system is diffuse and needs the non-discrete handling in the ontology |
| Immune | in | L3 | diffuse and largely cellular; representing it at L3 only is a deliberate under-claim, since its real biology lives at L6–L9 |
| Lymphatic | in | L3 | organ and vessel level |
| Integumentary | in | L3 | organ-level |
| Reproductive | in | L3 | organ-level; sex-variant structures per the reference subject note |
| Development, aging, pathology | out | — | each multiplies every entity by a state dimension; the reference is one state |
| Microbiome | out | — | not a human tissue; a legitimate future scope, but a different ontology |
| Psychological and behavioural states | out | — | no admissible representation at the levels this model works in |

## What This Model May Claim
| Goal | Claim the system may make | Claim it may NOT make |
|---|---|---|
| **A — Knowledge representation** | "this is what the sources say about this structure, graded and cited, and here is what is not represented" | "this is everything known about this structure", or that the absence of a claim means the absence of a fact |
| **B — Visualization** | "this is a reference geometry for this structure, at this level, in this representation mode" | that the geometry is any particular person's anatomy, that visual fidelity indicates evidential strength, or that a schematic is a measurement |
| **C — Simulation** | "this process, under these declared parameters and conditions, behaves this way in this model" | that the model predicts what a real body will do, or that a validated process implies a validated physiology |
| **D — Personalization** | "your measured value differs from the reference range in this direction, and here is what the model does and does not propagate from it" | any diagnosis, any prediction of an individual outcome, any recommendation, or that a personalized model is clinically validated |

The distinction that must survive contact with a demo: **having a 3D model does
not constitute a physiological simulation, and having a knowledge graph does not
constitute the ability to predict an individual person's health.** Both
inferences are tempting and both are false.

## Non-Diagnostic Boundary
> This system is an educational and research reference. It does not diagnose,
> treat, or offer medical advice, and it is not a medical device. Individual data
> shown here has not been clinically validated and must not be used for clinical
> decisions.

Placements — each is a requirement, not a suggestion:

| Surface | Placement |
|---|---|
| Any personalized view | persistent, not dismissible |
| Any comparison of an individual value to a reference range | inline with the comparison |
| Any simulation output | inline with the output, alongside its capability limits |
| Retrieval responses touching clinical terms | appended to the response |
| Exported data and API responses | in the response envelope and the export manifest |
| Product landing and about surfaces | prominent |

## Authorities and Vocabularies
| Level / Domain | Authority | Version | Conflict Resolution |
|---|---|---|---|
| Anatomical terminology (L1–L4) | Terminologia Anatomica | current edition, pinned per release | TA is authoritative for the preferred term; where TA and UBERON disagree on structure, UBERON governs the graph relation and TA governs the label, with the divergence recorded |
| Anatomical structure (L1–L5) | UBERON | pinned release | primary xref; FMA consulted where UBERON is coarse |
| Detailed anatomy | FMA | pinned release | used where UBERON lacks the granularity; never used to contradict UBERON without a recorded adjudication |
| Cell types (L6–L7) | Cell Ontology (CL) | pinned release | CL is authoritative; where a source uses a cell-type name CL does not carry, the claim records the source's term and flags the mapping gap |
| Molecular function (L9) | Gene Ontology (GO) | pinned release | GO for function terms |
| Chemical entities | ChEBI | pinned release | ChEBI for metabolites and ions |
| Genes and proteins | HGNC, UniProt | pinned release | HGNC for gene symbols, UniProt for proteins |
| Physiological quantities | primary literature, then reference texts | per claim | primary measurement outranks textbook restatement; disagreement becomes EVC-7, never a silent pick |
| Units | UCUM | current | mandatory; a value without a UCUM unit does not enter (INV-04) |

Version pinning is per release and recorded in the release manifest
(PRD_FR_Versioning), so a claim can always be re-evaluated against the authority
version that was current when it was made.

## Expert Review Model
| Reviewer | Gate | Sign-off Binds |
|---|---|---|
| Domain reviewer (per subsystem) | new entity admission, EVC-1/EVC-2 assignment, mechanism admission | that the content is correct as represented at its declared level |
| Two domain reviewers | conflict adjudication | a recorded adjudication that preserves both original positions |
| Reviewer plus Research Engineer | a process becoming `executable` | that parameters have sources and that simulation claims do not exceed them |
| Biology Lead | content release | the release as a whole, including the rubric pass |

Reviewers sign off on *representation*, not on the underlying science: the
question at every gate is "does the model say what the evidence supports, at the
level it claims", not "is this biology true". No reviewer, and no agent, is the
final authority on biological truth — the sources are, and the provenance chain
is what makes that checkable.

## Open Biological Questions
| Question | Why It Matters | Blocking? | Owner |
|---|---|---|---|
| Which cell-type definition basis does the model adopt where CL's molecular and morphological definitions diverge? | determines whether L7 content is stable or churns with every atlas release | blocks Phase 4 | Biology Lead |
| How are diffuse systems (immune, endocrine, fascia, interstitium) represented without forcing them into the organ abstraction? | forcing them produces confidently wrong anatomy | blocks those subsystems at L3 | Biology Lead |
| What is the admissible transfer justification for rodent-derived mechanism data at L9? | most molecular mechanism data is not human in vivo; without a stated rule, INV-12 becomes a rubber stamp | blocks Phase 5 | Biology Lead + domain reviewer |
| Where does anatomical variation stop being a variant and start being a separate entity? | determines whether the variation model scales or explodes | blocks Phase 3 | Biology Lead |
| Which physiological quantities are genuinely population-invariant, and which have been treated as such by convention only? | a convention presented as a constant is false precision with a citation | not blocking; continuous | Biology Lead |
