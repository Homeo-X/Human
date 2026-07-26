---
doc: BIO_Cell_and_Molecular_Model
tier: standard+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Cell and Molecular Model

_Levels L6–L10: cell populations, cell types, subcellular structures, molecular
mechanisms, and biochemical processes. The level at which a model most easily
acquires false precision, so every section here carries its own limits._

**Scope reminder:** only the cardiovascular subsystem is declared below L5
(MANIFEST §Scale depth). Everything in this document that is not cardiovascular
is either a rule that will apply when other subsystems descend, or an explicit
statement that the content does not exist. Nothing here should be read as
implying cellular coverage the model does not have.

## Cell Type Taxonomy
| Rule | Statement |
|---|---|
| Authority and version | Cell Ontology (CL), pinned per release (D-002) |
| Definition basis | CL's classification mixes morphological, molecular, and functional criteria, and the bases disagree for some types. This model records **which basis** a given type assignment rests on, per entity, rather than inheriting the ambiguity silently |
| Handling of upstream revisions | a CL split blocks the affected entity from promotion until a reviewer assigns it (BIO_Anatomical_Ontology §Identity); a merge flags any claim that depended on the distinction |
| Handling of states vs types | a cell **state** (activated, senescent, hypertrophied) is not a type. States are modelled as properties of a population, never as new CellType entities. Where a source treats a state as a type, the claim records the source's usage and the model's disagreement |
| Unresolved | the definitional-basis question is an open item in BIO_Research_Charter and blocks Phase 4. It is recorded rather than resolved because resolving it requires domain expertise this project does not yet have on the team |

## Cell Types Represented
| Cell Type | Tissue / Organ | Level | Representation Mode | Species Provenance | Evidence Class |
|---|---|---|---|---|---|
| Cardiomyocyte (`CL:0000746`) | myocardium, heart | L7 | typed, one canonical exemplar | structure and function human-derived; most quantitative parameters rodent or isolated-preparation | EVC-2 structural, EVC-3 quantitative |

That is the entire table. One cell type, in the one subsystem declared to
cellular depth. A reader expecting pneumocytes, neurons, or hepatocytes will not
find them, and the model says so at the point of asking rather than rendering a
generic cell.

## Tissue Organization
Myocardium is represented at L5 as a composition — cardiomyocytes, fibroblasts,
capillary endothelium, and extracellular matrix — with the composition stated and
the *arrangement* explicitly not represented. Myocardial fibre orientation varies
transmurally and is functionally significant; the model records that this is
known and unrepresented (EVC-8 on the arrangement claim), rather than showing an
undirected block of tissue that implies isotropy.

This is the general rule for L5: **composition is represented, architecture is
represented only where a source supports the specific arrangement.**

## Subcellular Structures
| Structure | Present In | Function Represented | Spatial Representation | Evidence Class |
|---|---|---|---|---|
| Sarcomere (`GO:0030017`) | cardiomyocyte | contractile unit; the site of filament sliding | schematic, explicitly marked | EVC-2 |
| Sarcoplasmic reticulum (`GO:0016529`) | cardiomyocyte | Ca²⁺ store, release and reuptake | schematic | EVC-2 |
| T-tubule (`GO:0030315`) | cardiomyocyte | conducts depolarization into the cell interior | schematic | EVC-2 |
| Mitochondrion (`GO:0005739`) | cardiomyocyte | ATP supply for the cross-bridge cycle | schematic | EVC-2 |

All four are `typed` and schematic per SCL-08. Organelle morphology is dynamic
and cell-state dependent; these show one state, and the surface says so wherever
they are displayed (INV-13).

## Molecular Entities
| Class | Authority | Identifier Form | What Is Represented | What Is Not |
|---|---|---|---|---|
| Ions | ChEBI | `CHEBI:29108` (Ca²⁺) | identity, charge, role in represented mechanisms | concentration fields, spatial gradients within a cell |
| Metabolites | ChEBI | `CHEBI:15422` (ATP) | identity, role as substrate or product | full metabolic network context |
| Proteins | UniProt | `UniProt:P12883` (myosin heavy chain 7) | identity, role in represented mechanisms, isoform where it matters | structure, folding, post-translational state |
| Genes | HGNC | `HGNC:7577` (`MYH7`) | identity, the protein it encodes | expression levels, regulation, variants |

Represented molecular entities are limited to those participating in BPR-01. The
model holds a handful of molecules, not a molecular inventory of the cell, and
G-01 reports that against the declared scope rather than against biology.

## Molecular Mechanisms

### Cross-bridge cycle (`HOX:mechanism:cross-bridge-cycle`)
- **Chain:** ATP binds myosin → cross-bridge detaches from actin → ATP hydrolysis
  cocks the myosin head → head binds actin (permitted once Ca²⁺-troponin has
  moved tropomyosin) → phosphate release drives the power stroke → ADP release →
  the cycle repeats while Ca²⁺ and ATP are both present.
- **Cell-type specificity:** described here for cardiac muscle. Skeletal and
  smooth muscle differ — smooth muscle materially, through myosin light-chain
  phosphorylation rather than troponin-mediated regulation. **The cardiac
  mechanism is not transferable**, and the model does not present it as a general
  muscle mechanism.
- **Conditions under which it holds:** measured predominantly in vitro, in
  isolated preparations, frequently at sub-physiological temperature, and often
  in rodent tissue. Every rate constant inherits those conditions.
- **Quantities:**

  | Quantity | Value | Unit | Condition | Evidence class |
  |---|---|---|---|---|
  | cycle duration, approximate | order 10–100 | `ms` | isolated preparation, varies with load and temperature | EVC-4 |
  | ATP consumed per cycle | 1 | `1` (dimensionless count) | stoichiometric | EVC-2 |
  | Ca²⁺ required for actin site availability | threshold, not a single value | `umol/L` | see BPR-01 state table | EVC-3 |

  The cycle-duration row is EVC-4 — approximated — deliberately. Precise human
  in-vivo values do not exist, and giving one would be false precision with a
  citation attached, which is the most persuasive kind of wrong.
- **Boundary:** the model stops at the cycle's steps and stoichiometry. It does
  not represent myosin's structural conformations, the elastic properties of
  titin, or the cooperative behaviour of neighbouring cross-bridges — each of
  which is real, studied, and outside what this model claims.

## Species Provenance
| Claim Domain | Predominant Source Species | Transfer Justification | Flagged To User? |
|---|---|---|---|
| Cardiomyocyte gross structure and function | human | none required | not applicable |
| Excitation–contraction coupling mechanism structure | human, with rodent contribution | mechanism conserved across mammals with documented differences in calcium handling proportions; the differences are recorded on the affected quantities | yes, on quantities |
| Cross-bridge cycle kinetics | rabbit, rat, and other mammalian preparations | conserved mechanism; **rates are not conserved** and are therefore graded EVC-4, not transferred as human values | yes, prominently |
| Cytosolic calcium concentrations | rodent and isolated human preparations | partial; human in-vivo measurement at this resolution does not exist | yes |
| Sarcomere length ranges | human and mammalian | strongly conserved; supported by human tissue studies | yes, on the range |

A human model containing unlabelled animal data is wrong, not approximate
(INV-12). The transfer-justification rule that makes this table more than
paperwork is an open question in BIO_Research_Charter and blocks Phase 5 — until
it is answered, "conserved mechanism" is doing more work in this table than it
has earned.

## In Vitro to In Vivo Transfer
Most quantitative molecular data in this model — and in the field — comes from
preparations that are not a living human: isolated myocytes, skinned fibres,
reconstituted protein systems, often at 20–25 °C rather than 37 °C, at
non-physiological ionic strength, and without neurohumoral context.

The model's posture: such values enter at **EVC-3 (MODELLED) or EVC-4
(APPROXIMATED), never EVC-1 or EVC-2**, regardless of how well-established or how
frequently cited they are. The measurement-conditions field is mandatory for
every one of them (INV-07), and the conditions are displayed alongside the value
rather than hidden behind it.

## Known False-Precision Risks
_The specific places this document could mislead, named by its own authors._

| Risk | Where | Mitigation |
|---|---|---|
| A strongly-supported mechanism lends its credibility to the weak numbers inside it | BPR-01 and the cross-bridge cycle | mechanism and quantity are graded separately, and both grades are shown |
| Schematic organelle geometry reads as measured morphology | subcellular structures | INV-13 requires the schematic marker at every binding site |
| "Conserved mechanism" used as a blanket transfer justification | species provenance table | flagged as an open question that blocks Phase 5; the phrase is currently load-bearing without a rule behind it |
| One canonical cardiomyocyte read as representative of all myocardium | cell types table | SCL-07's `typed` mode is stated at the surface; transmural heterogeneity is recorded as EVC-8 |
| A single cell type present implies a cellular model exists | this document as a whole | the scope reminder at the top, and G-01 reporting against declared scope |
| Order-of-magnitude values presented with unit precision that implies measurement | cross-bridge quantities | EVC-4 grading and "order" wording retained rather than a spurious point value |
