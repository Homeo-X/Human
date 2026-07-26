---
doc: BIO_RUBRIC
tier: standard+   # bio profile — applied by UX pass A, dispositions in docs/BIO_Model_Review.md
version: 0.0.0
status: template
owner: ux
last_updated: —
---

# Biological Model Rubric

_Known failure modes of computational biological models, phrased as checks. This
is not a biology textbook and it does not check whether the biology is right —
domain experts and primary sources do that. It checks the ways a model **looks**
right on paper while being unsupported, overclaimed, or internally impossible.
**Protocol:** in UX pass A (Model Reviewer), every item gets a disposition —
**pass** (with one line of evidence: the document and the specific content that
satisfies the check), **flag** (becomes a punch-list item), or **N/A** (with the
reason) — recorded in `docs/BIO_Model_Review.md`. Silence is not a disposition.
Flags that survive the punch list become Decision Log entries: shipping a known
failure mode is allowed, but only on purpose._

## Representation honesty
| ID | Check | How to Verify |
|---|---|---|
| BRB-01 | A level is represented with no stated resolution limit — the model implies it knows more than it does | every `SCL` row's resolution-limit cell; empty or "as needed", flag |
| BRB-02 | A simplification is presented in the same voice as a fact | scan every quantitative claim for its `EVC` class; any bare number, flag |
| BRB-03 | `UNKNOWN` has nowhere to live — the schema can only express what is known | find the field that stores "we do not know"; if absent, flag |
| BRB-04 | Visual completeness implies knowledge completeness — a rendered structure reads as a validated one | name the surface that shows a structure's evidence class alongside it; if none, flag |
| BRB-05 | A coverage claim is stated without its denominator ("major organs covered") | every coverage KPI names what the whole is, and who defines it |

## Scale and cross-scale linkage
| ID | Check | How to Verify |
|---|---|---|
| BRB-06 | A cross-scale link asserts causation the evidence does not carry (molecule → symptom in one hop) | trace each cross-scale edge: name the intermediate levels it skips and why the skip is legitimate |
| BRB-07 | A mechanism is described at one scale and used as if it operated at another | for each `BPR`, its declared spatial scale vs the scale of the entities it consumes/produces |
| BRB-08 | Semantic zoom is conflated with physical zoom — changing magnification silently changes what the model claims | the zoom model distinguishes the two explicitly, with a named transition rule |
| BRB-09 | A declared depth has no populated content behind it | per subsystem: declared max level vs entities actually at that level; a declaration with zero entities, flag |
| BRB-10 | An entity claims a level deeper than its subsystem's scale-depth declaration | cross-check every entity's level against MANIFEST §Scale Depth |

## Evidence and provenance
| ID | Check | How to Verify |
|---|---|---|
| BRB-11 | Confidence exceeds evidence quality — a textbook statement graded as verified measurement | sample the highest-confidence claims; does the source type support the grade? |
| BRB-12 | Conflicting sources are silently resolved by picking one | find the conflict-representation mechanism; if resolution is implicit, flag |
| BRB-13 | Species provenance is unmarked — animal-derived data sits unlabelled in a human model | per claim: species field present and populated |
| BRB-14 | A source's licence permits less than the product does | every geometry and ontology source has a licence field and a stated downstream constraint |
| BRB-15 | Evidence is attached to entities but not to the relationships between them | sample relationships: do they carry their own provenance, or inherit it silently? |
| BRB-16 | A citation exists but does not actually support the specific claim it is attached to | spot-check three claims against their cited source's actual scope |

## Process and simulation
| ID | Check | How to Verify |
|---|---|---|
| BRB-17 | A process is named but not modelled, and the difference is not visible to a user | per `BPR`: are inputs, outputs, state variables, and timescale populated, or is it a label? |
| BRB-18 | A process consumes or produces entities the ontology does not define | every `BPR` input/output resolves to a defined entity |
| BRB-19 | Timescales are forced into one clock — nanosecond chemistry and decade-scale aging in one loop | the timescale model per process; a single global clock, flag |
| BRB-20 | A simulation claim exceeds what the underlying data supports | for each executable process, name the parameter source; parameters with no source, flag |
| BRB-21 | Feedback loops are drawn but never closed — no damping, no failure state | per `BPR` with feedback: the damping mechanism and the failure state are both named |

## Personalization and individual data
| ID | Check | How to Verify |
|---|---|---|
| BRB-22 | Individual data can reach the canonical model — the reference is mutable in practice | find the write path to reference entities; if a personalization path exists, flag |
| BRB-23 | A user-reported value is treated as equivalent to a clinical measurement | the measurement-method field is required and affects downstream confidence |
| BRB-24 | Stale individual data is presented as current | every individual value carries a timestamp and a staleness policy |
| BRB-25 | A personalized output implies clinical meaning the system cannot support | trace the most clinically-suggestive personalized surface to its stated boundary |

## Structural
| ID | Check | How to Verify |
|---|---|---|
| BRB-26 | An invariant exists in prose but has no executable check | every `INV` row names the check that enforces it and the failure it produces |
| BRB-27 | An AI surface can introduce biology the graph does not contain | trace the retrieval path: is every generated claim required to resolve to a graph node? |
| BRB-28 | The scale-depth lens's extra-depth docs are skeletal | per the declared depth, the lens's named docs are at real depth, not headings |
| BRB-29 | Narrative content is presented as though it were structured — compilation debt is invisible | sample content at each compilation status; is the status visible to a reader who did not go looking for it? |
| BRB-30 | An association is rendered as a mechanism, or a navigation hierarchy is rendered as biological structure | every `associated_with` edge and every tree view: does the surface state what it is, or does it let the reader infer causation and containment that were never asserted? |
