---
doc: BIO_Validation_Framework
tier: standard+   # never omitted at Standard+ — invariants that live only in prose are not invariants
version: 0.0.0
status: template
owner: architect
last_updated: —
---

# Validation Framework

_The model's integrity rules as executable checks. Every `INV` row names the
check that enforces it and the failure it produces; a rule with no check is a
finding (BRB-26), not a rule._

## Integrity Invariants
| ID | Invariant | Rule | Enforced By | Failure Produced | Severity |
|---|---|---|---|---|---|
| INV-01 | | | | | |

_Minimum coverage — each of these gets at least one `INV`: biological
consistency · hierarchical consistency · functional consistency · unit
consistency · scale consistency · temporal consistency · evidence consistency ·
personalization consistency · identifier integrity · licence integrity._

## Validation Layers
| Layer | Runs When | Scope | Blocking? |
|---|---|---|---|

## Check Specifications
_Per check: the exact condition, the data it reads, and a worked example of both
a pass and a failure. A check whose failure case was never written is a check
nobody has confirmed can fail._

### <Check name> — enforces INV-NN
- **Condition:**
- **Reads:**
- **Passes when:**
- **Fails when:**
- **Failure message:**

## Negative Testing
_Every invariant is deliberately violated in a self-test. A validator that cannot
fail is not a validator._

| INV | Violation Injected | Expected Detection |
|---|---|---|

## Expert Review Gates
_Where human biological review is required, what it reviews, and what its
sign-off binds. Automated checks establish consistency, never correctness._

| Gate | Reviewer | Reviews | Binds |
|---|---|---|---|

## What Validation Does Not Establish
_The honest boundary. Consistency is not truth; coverage is not completeness;
passing checks is not expert endorsement._
