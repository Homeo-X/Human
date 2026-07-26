---
doc: BIO_Scale_Contract
tier: light+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Scale Contract — L0 to L10

_One `SCL` row per represented level. A level with an unfilled representation
mode, evidence model, or resolution limit is a validation error, not a to-do: an
undeclared level is exactly how a model claims more than it holds._

## Level Contracts
| ID | Level | Represents | Representation Mode | Data Model | Spatial Model | Functional Model | Evidence Model | Uncertainty Model | Computational Cost | Resolution Limit |
|---|---|---|---|---|---|---|---|---|---|---|
| SCL-00 | L0 | whole organism | enumerated | single Organism entity carrying reference-population parameters | one root coordinate frame, standard anatomical position | whole-body homeostatic set points only | reference physiology texts, population survey data | population ranges, never a single true value | negligible | one declared population; not any individual, and not an average of individuals |
| SCL-01 | L1 | anatomical regions | enumerated | ~9 Region entities with containment to L2 and L3 | bounding volumes, not surfaces | none — regions locate, they do not function | anatomical nomenclature authority (TA) | boundary ambiguity recorded per region pair | negligible | region boundaries are conventions, not physical surfaces; adjacent regions share tissue |
| SCL-02 | L2 | organ systems | enumerated | 11 System entities; membership is many-to-many with organs | none — systems are not spatially contiguous | system-level function statements with EVC grades | reference physiology texts | overlapping membership recorded explicitly | negligible | systems are functional groupings, not spatial objects; the immune and endocrine systems are diffuse and the model says so |
| SCL-03 | L3 | organs | enumerated | Organ entities, external xref primary (UBERON/FMA) | surface mesh per organ, one canonical pose | organ-level function, plus supply, drainage, innervation relations | anatomical atlases, imaging-derived reference geometry | geometry is one exemplar; inter-individual variation is not represented at this level | low — hundreds of meshes | a single reference geometry; organ shape and volume vary by tens of percent between individuals |
| SCL-04 | L4 | sub-organ structures | enumerated | Structure entities, part-of an Organ | surface mesh where the structure has a discrete boundary; otherwise a labelled region within the parent | structure-specific function | anatomical atlases, surgical and histological reference | structures without discrete boundaries flagged as region-labelled, not meshed | low | many sub-organ divisions are gradients (renal cortex to medulla); the model marks these rather than drawing a false boundary |
| SCL-05 | L5 | tissues | typed | TissueType entities; an Organ references its composition, not its instances | none — tissue is a composition property, not a located object at this level | tissue-level mechanical, transport, and metabolic properties | histology reference, tissue-property literature | property ranges with measurement conditions | low | composition only; the model states what tissue an organ contains, not where each portion of tissue is |
| SCL-06 | L6 | cell populations | statistical | CellPopulation entities: cell type, host tissue, abundance distribution | none | population-level function and turnover | quantitative histology, single-cell atlases | abundance as a distribution with its source population; never a point count | low | population statistics only; no individual cell is located or instantiated |
| SCL-07 | L7 | individual cell types | typed | CellType entities, external xref primary (CL) | canonical schematic geometry, explicitly non-spatial-in-body | cell-type function, its inputs and outputs | cell-ontology authority, primary cell-biology literature | cell type versus cell state distinguished; ambiguous cases flagged | low | one canonical exemplar per type; real cells vary continuously and type boundaries are contested upstream |
| SCL-08 | L8 | subcellular structures | typed | Organelle entities, part-of a CellType | canonical schematic geometry only | organelle function within its cell type | cell-biology reference, electron-microscopy literature | schematic geometry marked as schematic wherever displayed | low | schematic; organelle morphology is dynamic and cell-state dependent, and this model shows one state |
| SCL-09 | L9 | molecular mechanisms | exemplar | Biomolecule entities (xref ChEBI/HGNC/UniProt) plus Mechanism entities | none | mechanism steps as an ordered causal chain | primary molecular-biology literature, curated pathway databases | each step graded independently; the chain is only as strong as its weakest step | medium — curation cost, not compute | one exemplar mechanism per phenomenon; mechanisms are cell-type-specific and condition-dependent, and alternatives are not enumerated |
| SCL-10 | L10 | biochemical and physical processes | exemplar | Process entities with rate parameters, state variables, and conditions | none | quantitative process specification, executable only when parameterized | primary literature with measurement conditions attached | every rate carries its measurement conditions; in-vitro origin is flagged | high when executed; medium as specification | rate constants are condition-specific and predominantly in-vitro; transfer to living human tissue is an assumption, marked as one |

_Representation mode vocabulary: `enumerated` (every instance named) · `typed`
(types named, instances not) · `statistical` (populations, distributions) ·
`exemplar` (one representative case stands for a class) · `referenced` (pointed
at an external resource, not held) · `absent` (declared out of scope)._

## Declared Depth per Subsystem
_The scale-depth lens binding from MANIFEST §Product, restated with its
justification. An entity deeper than its subsystem's declared level is a
cross-review finding, not a stretch goal._

| Subsystem | Max Level | Representation Mode at Max | Why This Depth |
|---|---|---|---|
| Cardiovascular | L10 | exemplar | the designated vertical slice: one system taken to the bottom proves the substrate carries every level, and cardiac excitation–contraction coupling is among the best-characterized mechanisms in human physiology |
| Respiratory | L5 | typed | alveolar gas exchange needs tissue-level structure to be meaningful; the molecular level adds curation cost without changing what a user can learn at this phase |
| Nervous | L5 | typed | neural tissue types are needed for L3 organ content to make sense; L7–L9 neuroscience is a research programme, not a curation task, and declaring it would be the clearest possible overclaim |
| Urinary | L5 | typed | the nephron is a sub-organ structure whose function is tissue-level; filtration mechanism is specified at L5 without descending to transporter kinetics |
| Musculoskeletal | L4 | enumerated | bones and muscles are the highest-value enumerated content; tissue-level bone remodelling is deferred |
| Digestive, Endocrine, Immune, Lymphatic, Integumentary, Reproductive | L3 | enumerated | organ-level structure and function only. The immune and lymphatic systems are additionally diffuse, so even L3 requires the non-discrete-structure handling in BIO_Anatomical_Ontology |

**What this table costs us, stated plainly:** ten of eleven systems stop at or
above L5. A user who zooms into the pancreas expecting islet-cell molecular
biology will not find it, and the system will say so rather than render something
plausible. That is the intended behaviour.

## Entities Spanning Several Levels
A process is frequently not *at* a level — it is realized across several. Cardiac
contraction is simultaneously an organism-level event, an organ-level mechanical
one, a cellular one, and a molecular one. Forcing such an entity to a single
level would be a scale error of exactly the kind INV-05 exists to catch.

Rule: an entity declares `level` (a single value) when it is a located structure,
and `spatial_scale` (an ordered list of levels) when it is a process or mechanism
that spans them. A spanning entity must:

1. list every level at which it has a defined input, output, or state variable;
2. name, per level, what it contributes there — the same process does different
   work at L3 than at L9;
3. respect the declared depth of its subsystem at *every* listed level, not just
   the shallowest.

The third clause matters: a process cannot reach L9 in a subsystem declared to
L5 by describing itself as spanning. Spanning is a description of where a process
acts, never a route around the depth declaration.

## Level Vocabulary Reconciliation
The seed corpus (D-007) and much of the teaching literature use an eight-level
scheme. It is not wrong, it is coarser, and it omits two levels this model needs.
Mapping it explicitly prevents silent renumbering:

| Common 8-Level Scheme | This Model | Note |
|---|---|---|
| 1 Whole body | L0 | same |
| — | **L1 anatomical regions** | absent from the common scheme; needed because regions are how users navigate and how imaging is bounded |
| 2 Systems | L2 | same |
| 3 Organs | L3 | same |
| 4 Structures | L4 | same |
| 5 Tissue | L5 | same |
| — | **L6 cell populations** | absent from the common scheme; needed because abundance is statistical and a population is not a cell type |
| 6 Cells | L7 | same |
| 7 Subcellular | L8 | same |
| 8 Mechanism | L9 | the common scheme merges mechanism and process |
| — | **L10 biochemical / physical processes** | separated from L9 because a mechanism is a causal chain while a process is a parameterized rate; conflating them is how a described mechanism gets mistaken for a runnable model |

Content arriving under the eight-level scheme is mapped on ingest and the mapping
is recorded, so a later reader can tell whether a level assignment was chosen or
inherited.

## Semantic Zoom vs Physical Zoom
These are different operations and the model never conflates them.

- **Physical zoom** changes magnification within one level. Nothing about the
  model's claim changes; more of the same representation becomes visible.
- **Semantic zoom** changes the level of biological abstraction. The claim
  changes, the evidence basis changes, and often the representation mode changes
  (from `enumerated` geometry to `typed` schematic, for instance).

Transition rules:

1. Semantic zoom is always an explicit action, never a side effect of scrolling.
2. Crossing a level boundary announces the new level, its representation mode,
   and its resolution limit from the row above.
3. Crossing into a `typed`, `statistical`, or `exemplar` level states that what
   is now shown is not a located object in this body.
4. Attempting to descend past a subsystem's declared depth produces the terminal
   answer below — never a rendered guess.

## Cross-Scale Linkage Rules
| From Level | To Level | Allowed Edge Types | Skip Permitted? | Justification Required |
|---|---|---|---|---|
| L0 → L1 | adjacent | contains | no | none — containment is total |
| L1 → L2 | non-adjacent classes | contains (region to organ), member-of (organ to system) | yes, by design | systems are not contained in regions; the edge is membership, and the model records both |
| L2 → L3 | adjacent | contains, member-of | no | none |
| L3 → L4 | adjacent | contains, part-of | no | none |
| L4 → L5 | adjacent | composed-of | no | none — composition, not containment |
| L5 → L6 | adjacent | composed-of, populated-by | no | none |
| L6 → L7 | adjacent | instance-of | no | none |
| L7 → L8 | adjacent | contains | no | none |
| L8 → L9 | adjacent | contains, hosts-mechanism | no | none |
| L9 → L10 | adjacent | realizes | no | none |
| any → any, skipping ≥1 level | non-adjacent | causes, contributes-to, regulated-by | **only with recorded justification** | the skipped levels must be named, and the edge must state why the intermediate steps are not required for the claim to hold. This is checked by INV-05 |

**Why the skip rule exists:** a single edge from a molecule to a symptom is the
characteristic false-causation move in biological modelling (BRB-06). Such edges
are sometimes legitimate — a well-established pharmacological relationship, for
example — but they must be declared as compressions of a longer chain, not
presented as direct mechanism.

## What Happens Below the Deepest Declared Level
The system returns an explicit terminal answer, not an empty view and not a
generic rendering:

> **Not represented at this level.** This subsystem is modelled to L<n>
> (<mode>). Below that, this model holds nothing — that is a statement about the
> model, not about the biology. <Where relevant: the external resources that do
> hold it.>

This response is a designed surface (TECH_UI_UX_Design §Key Screens), is counted
in G-03's UNKNOWN tally, and is queryable — a user can ask what the model does
not represent and receive a real answer.
