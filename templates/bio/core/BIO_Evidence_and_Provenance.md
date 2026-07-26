---
doc: BIO_Evidence_and_Provenance
tier: light+   # never omitted at any tier — a model without provenance is an assertion with an interface
version: 0.0.0
status: template
owner: architect
last_updated: —
---

# Evidence and Provenance

_How every assertion in the model is graded, sourced, and constrained. The grade
is a data field with consequences, not a citation style._

## Evidence Classes
_The `EVC` ladder. Each class states what admits a claim to it, and — critically —
the promotions that are forbidden._

| ID | Class | Admits | Typical Sources | Forbidden Promotion |
|---|---|---|---|---|
| EVC-1 | VERIFIED | | | |
| EVC-2 | STRONGLY_SUPPORTED | | | |
| EVC-3 | MODELLED | | | |
| EVC-4 | APPROXIMATED | | | |
| EVC-5 | INFERRED | | | |
| EVC-6 | HYPOTHESIZED | | | |
| EVC-7 | CONFLICTING_EVIDENCE | | | |
| EVC-8 | UNKNOWN | | | |

## The Claim Record
_The mandatory shape of any assertion the system stores or displays._

| Field | Required | Notes |
|---|---|---|
| subject (entity id) | yes | |
| predicate | yes | |
| object / value | yes | |
| unit | if quantitative | |
| evidence class | yes | |
| source(s) | unless UNKNOWN | |
| source type | yes | |
| species | yes | |
| population / context | yes | |
| measurement conditions | if quantitative | |
| date asserted | yes | |
| known limitations | yes | |
| conflicting claims | if any | |

## Source Register
| Source | Type | Authority Basis | Licence | Attribution Requirement | Downstream Constraint |
|---|---|---|---|---|---|

_Source type vocabulary: primary research · systematic review · reference
textbook · anatomical atlas · imaging dataset · curated database · derived model
· expert assertion._

## Licensing Tiers
_Sources segregated by what they permit downstream, so a future relicensing does
not require re-deriving the model._

| Tier | Permits | Sources | Segregation Mechanism |
|---|---|---|---|

## Conflict Handling
_What the system does when sources disagree. Silent resolution is forbidden;
state the visible behaviour._

| Conflict Type | Representation | User-Visible Behaviour |
|---|---|---|

## The Evidence Pipeline
_Source → extraction → entity resolution → claim extraction → classification →
conflict detection → expert review → canonical graph. Per stage: who or what
performs it, what it may change, and what it may not._

| Stage | Performed By | May Change | May NOT Change | Output |
|---|---|---|---|---|

## Traceability Guarantee
_The statement of what "traceable" means operationally, and the query that
demonstrates it for any given claim._

## Negative Knowledge
_Where `UNKNOWN` is stored, how it is surfaced, and how it is counted. A model
that cannot express ignorance will manufacture confidence._
