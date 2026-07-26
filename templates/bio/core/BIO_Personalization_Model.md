---
doc: BIO_Personalization_Model
tier: standard+   # excluded with reason (not folded) when no individualization is in scope
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Personalization Model

_How individual data becomes an individual model without ever touching the
canonical reference. The reference model is immutable; personalization is an
overlay applied at read time._

    REFERENCE MODEL  ⊕  PERSONALIZATION OVERLAY  =  INDIVIDUAL MODEL

## The Immutability Guarantee
_The statement, and the mechanism that enforces it rather than requesting it.
Name the invariant (`INV`) and the check._

## Overlay Algebra
_What an overlay may do, precisely._

| Operation | Permitted | Applies To | Constraints |
|---|---|---|---|
| override a parameter value | | | |
| narrow a range | | | |
| add an individual-specific entity | | | |
| mark an entity absent | | | |
| replace geometry | | | |
| add an observation series | | | |
| change a relationship | | | |
| change a canonical biological fact | **never** | — | the reference is not a draft |

## Individual Data Classes
| Class | Examples | Typical Method | Default Confidence | Staleness Policy |
|---|---|---|---|---|

_Minimum coverage: demographics · age · biological sex where physiologically
relevant · anthropometrics · body composition · anatomical measurements ·
laboratory values · vital signs · imaging-derived anatomy · genetic information ·
medication exposure · disease states · lifestyle variables · longitudinal
observations._

## The Individual Value Record
_Every personalized value carries its provenance. A value without these fields
cannot enter an overlay._

| Field | Required | Notes |
|---|---|---|
| value | yes | |
| unit | yes | |
| measurement time | yes | |
| measurement method | yes | |
| device / instrument | if applicable | |
| source (self-reported / clinical / derived / inferred) | yes | |
| confidence | yes | |
| superseded by | if applicable | |

## Uncertainty Handling
| Situation | Representation | User-Visible Behaviour |
|---|---|---|
| measurement uncertainty | | |
| missing data | | |
| conflicting measurements | | |
| stale data | | |
| estimated value | | |
| inferred value | | |
| directly measured value | | |

## Source Hierarchy
_Self-reported data is not clinical measurement. State the ordering and what it
changes downstream._

## Propagation Rules
_When an individual value differs from the reference, what else changes — and
what explicitly does not. Uncontrolled propagation is how a single measured
number becomes a fabricated physiology._

| Overlay Value | Propagates To | Does NOT Propagate To | Basis |
|---|---|---|---|

## Temporal History
_How longitudinal data is held, how the model at time T is reconstructed, and
what "current" means._

## Boundaries
_What a personalized model must never be presented as: a diagnosis, a prediction
of an individual outcome, a substitute for measurement, or a validated clinical
tool. Each with the surface where the boundary is stated._

## Privacy Posture
_Reference to the Security Requirements. What individual data is stored, where,
under what control, and what the deletion path is._
