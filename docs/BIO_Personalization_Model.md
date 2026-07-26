---
doc: BIO_Personalization_Model
tier: standard+
version: 1.0.0
status: draft
owner: pm
last_updated: 2026-07-26
---

# Personalization Model

_How individual data becomes an individual model without ever touching the
canonical reference. The reference model is immutable; personalization is an
overlay applied at read time (D-004)._

    REFERENCE MODEL  ⊕  PERSONALIZATION OVERLAY  =  INDIVIDUAL MODEL

**Phase status:** nothing in this document is built. Personalization is Phase 7.
It is specified now so that the substrate, schemas, and APIs do not have to
change when it arrives — which is the brief's requirement, and the reason a
document about unbuilt functionality is load-bearing today.

## The Immutability Guarantee
The reference model has no write path from an overlay. This is enforced, not
requested:

- **Structural:** reference entities and overlay documents live in separate
  stores with separate write paths. The overlay resolver has read-only access to
  the reference.
- **Checked:** INV-08 fails any overlay operation whose target path resolves to
  a reference entity's canonical fields. `biocheck --selftest` injects exactly
  this violation and requires the check to fail.
- **Pinned:** every overlay names the reference release it resolves against. An
  overlay cannot float across reference versions and silently change meaning.

The distinction that matters under pressure: a convention is what a team intends,
a review rule is what a team notices, and an enforced property is what holds when
neither happens. This is the third.

## Overlay Algebra
| Operation | Permitted | Applies To | Constraints |
|---|---|---|---|
| override a parameter value | yes | quantitative properties of reference entities | the reference value remains visible alongside; an override never erases what it replaces |
| narrow a range | yes | population ranges | the individual value must fall within a plausibility bound or be flagged, never silently accepted |
| add an individual-specific entity | yes | overlay-owned entity space | e.g. an implanted device, a surgically absent organ; carries its own provenance |
| mark a reference entity absent | yes | overlay annotation on a reference id | the entity remains in the reference; the overlay records its absence in this individual |
| replace geometry | yes | spatial identities (D-008) | imaging-derived mesh binds to the spatial identity, not the entity; reference geometry is untouched |
| add an observation series | yes | overlay-owned time series | longitudinal values with per-point provenance |
| change a relationship | **restricted** | overlay-owned relations only | an individual may have an anatomical variant relationship; the reference relation is never rewritten |
| change a canonical biological fact | **never** | — | the reference is not a draft. No privilege level permits this, including administrative |
| change an evidence grade | **never** | — | grades belong to claims, and claims belong to the reference |

## Individual Data Classes
| Class | Examples | Typical Method | Default Confidence | Staleness Policy |
|---|---|---|---|---|
| Demographics | age, recorded sex | self-reported or record-derived | high for age, contextual for sex | age recomputed, not stored as a fixed number |
| Anthropometrics | height, mass | measured or self-reported | measured high, self-reported moderate | 12 months |
| Body composition | fat mass, lean mass | DXA, bioimpedance, estimate | varies by method by an order of magnitude | 6 months |
| Anatomical measurements | chamber dimensions, organ volumes | imaging-derived | high, method-dependent | 12 months, or on any relevant clinical event |
| Laboratory values | electrolytes, metabolic panel | clinical laboratory | high | class-specific: hours for electrolytes, months for structural markers |
| Vital signs | heart rate, blood pressure | clinical device, consumer wearable, manual | high to low across that range — the spread is the point | minutes to days by class |
| Imaging-derived anatomy | segmented meshes | imaging plus segmentation | high for geometry, method-dependent for derived quantities | per study |
| Genetic information | variants | sequencing | high for the call, **low for interpretation** | call is stable; interpretation is not, and is re-evaluated against current knowledge |
| Medication exposure | current medicines, doses | record-derived or self-reported | moderate | continuous |
| Disease states | diagnoses | record-derived | moderate | continuous |
| Lifestyle variables | activity, sleep, diet | self-reported or wearable-derived | low to moderate | continuous |
| Longitudinal observations | any of the above over time | mixed | inherits per point | not applicable; the series is the record |

## The Individual Value Record
_A value without these fields cannot enter an overlay (INV-09)._

| Field | Required | Notes |
|---|---|---|
| value | yes | |
| unit | yes | UCUM; INV-04 applies to overlays exactly as to the reference |
| measurement time | yes | when measured, not when entered |
| measurement method | yes | from a controlled vocabulary per data class |
| device / instrument | if applicable | a consumer wearable and a clinical monitor are not the same measurement |
| source | yes | self-reported, clinical, device, derived, or inferred |
| confidence | yes | derived from method and source, not asserted independently |
| superseded by | if applicable | supersession, not overwrite — the series is append-only |

## Uncertainty Handling
| Situation | Representation | User-Visible Behaviour |
|---|---|---|
| Measurement uncertainty | interval or distribution, with method-derived spread | value shown with its interval; a point value is never shown for an interval-valued measurement |
| Missing data | absent, explicitly | the reference range is shown as the reference range, never as the individual's value |
| Conflicting measurements | both retained with their methods and times | both shown, ordered by method quality, with the disagreement stated |
| Stale data | retained with its age and the class staleness policy | age displayed; past the policy threshold the value is shown as historical, not current |
| Estimated value | flagged with the estimator | shown as estimated, with what it was estimated from |
| Inferred value | flagged with the inference and its basis | shown as inferred; distinguished from measured at every surface |
| Directly measured | flagged with method | the only class shown without a qualifier, and only when method quality supports it |

## Source Hierarchy
Self-reported data is not clinical measurement, and treating them as equivalent
is the fastest route to a confidently wrong individual model.

Ordering, strongest first: clinical measurement with a documented method →
validated clinical device → consumer device with known characteristics →
consumer device without → derived or estimated → self-reported → inferred by the
system.

Downstream consequences: a lower-ranked source cannot supersede a higher-ranked
one for the same quantity without an explicit user action; propagation (below) is
gated on source rank; and any surface comparing an individual value to a
reference range shows the source rank alongside.

## Propagation Rules
When an individual value differs from the reference, what else changes — and,
more importantly, what does not. **Uncontrolled propagation is how a single
measured number becomes a fabricated physiology**, and it is the most likely way
this feature could mislead someone.

| Overlay Value | Propagates To | Does NOT Propagate To | Basis |
|---|---|---|---|
| Height, mass | allometrically-scaled reference geometry, where an allometric relationship exists with a source | organ-level function, physiological parameters, cellular content | scaling geometry is supported; scaling function is not |
| Measured chamber dimension | that chamber's spatial identity | derived haemodynamic quantities, unless the derivation is itself sourced and its assumptions hold for this individual | a measured dimension is a measurement; a derived output is a model result and is graded as one |
| Resting heart rate | display of cardiac cycle timing at organism level | BPR-01's cellular or molecular parameters | the mechanism does not scale with the rate in a way this model can represent |
| Laboratory value | comparison against reference range | any mechanism, any structure, any cellular parameter | a serum concentration is not a cellular concentration |
| Genetic variant | annotation on the relevant entity, with interpretation confidence | protein behaviour, mechanism rates, phenotype | genotype-to-phenotype inference is out of scope and would be the most dangerous overreach available here |
| Imaging-derived mesh | the spatial identity it binds to | tissue composition, cellular content, function | geometry is measured; what is inside it is not |

**Default: no propagation.** A propagation path exists only where it is listed
above with a stated basis. Anything not listed does not propagate, and the
individual model shows the reference value with an explicit note that the
individual value does not inform it.

## Temporal History
Overlays are append-only series. The model at time *T* is reconstructed by
resolving each quantity to its most recent non-superseded value at or before *T*,
subject to its staleness policy. "Current" means "most recent within policy" —
where nothing falls within policy, the answer is that there is no current value,
not the most recent stale one.

## Boundaries
A personalized model must never be presented as a diagnosis, a prediction of an
individual outcome, a substitute for measurement, or a validated clinical tool.

| Boundary | Surface Where Stated |
|---|---|
| Not a diagnosis | persistent on every personalized view |
| Not a prediction | inline with any projected or derived quantity |
| Not clinically validated | inline with every comparison to a reference range |
| Not a substitute for measurement | wherever an estimated or inferred value is shown |
| Derived quantities are model outputs | inline with each derived quantity, with its inputs and assumptions reachable |

The BRB-25 rubric check exists for this section specifically: it asks which
personalized surface most implies clinical meaning, and requires that surface to
be traced to its stated boundary.

## Privacy Posture
Detail lives in PRD_Security_Requirements. The commitments this document makes:

- Individual data is **health data**, treated as the most sensitive class the
  system holds, regardless of whether a given deployment falls under a specific
  regulatory regime.
- Overlays are separable and individually deletable; deleting an overlay leaves
  the reference model bit-identical, which is a direct consequence of D-004
  rather than a separate feature.
- No individual data enters the reference model, any published release, any
  training corpus, or any aggregate without a separate, explicit, and revocable
  authorization — and aggregate use is out of scope in Phase 7 rather than
  quietly permitted.
- The deletion path is a hard requirement, tested, not a policy statement.
