---
doc: BIO_Scale_Contract
tier: light+   # never omitted at any tier — this is what stops the model overclaiming
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Scale Contract — L0 to L10

_One `SCL` row per represented level. A level with an unfilled representation
mode, evidence model, or resolution limit is a validation error, not a to-do:
an undeclared level is exactly how a model claims more than it holds._

## Level Contracts
| ID | Level | Represents | Representation Mode | Data Model | Spatial Model | Functional Model | Evidence Model | Uncertainty Model | Computational Cost | Resolution Limit |
|---|---|---|---|---|---|---|---|---|---|---|
| SCL-00 | L0 | whole organism | | | | | | | | |
| SCL-01 | L1 | anatomical regions | | | | | | | | |
| SCL-02 | L2 | organ systems | | | | | | | | |
| SCL-03 | L3 | organs | | | | | | | | |
| SCL-04 | L4 | sub-organ structures | | | | | | | | |
| SCL-05 | L5 | tissues | | | | | | | | |
| SCL-06 | L6 | cell populations | | | | | | | | |
| SCL-07 | L7 | individual cell types | | | | | | | | |
| SCL-08 | L8 | subcellular structures | | | | | | | | |
| SCL-09 | L9 | molecular mechanisms | | | | | | | | |
| SCL-10 | L10 | biochemical / physical processes | | | | | | | | |

_Representation mode vocabulary: `enumerated` (every instance named) ·
`typed` (types named, instances not) · `statistical` (populations, distributions)
· `exemplar` (one representative case stands for a class) · `referenced`
(pointed at an external resource, not held) · `absent` (declared out of scope)._

## Declared Depth per Subsystem
_The scale-depth lens binding from MANIFEST §Product, restated with its
justification. An entity deeper than its subsystem's declared level is a
cross-review finding._

| Subsystem | Max Level | Representation Mode at Max | Why This Depth |
|---|---|---|---|

## Semantic Zoom vs Physical Zoom
_The transition rules. Changing magnification and changing level of biological
abstraction are different operations; state how each is triggered, what changes,
and what the user is told when the model's claim changes underneath them._

## Cross-Scale Linkage Rules
_Which level may link to which, what an edge that skips levels means, and when
skipping is inadmissible._

| From Level | To Level | Allowed Edge Types | Skip Permitted? | Justification Required |
|---|---|---|---|---|

## What Happens Below the Deepest Declared Level
_The honest terminal answer the system gives when a user keeps zooming._
