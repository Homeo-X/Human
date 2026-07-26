---
doc: RES_Analysis_Plan
tier: standard+
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Analysis Plan (pre-registered)

_Frozen before main runs begin — the freeze is a Decision Log entry, and
any post-freeze change is a new Decision marked as such. This document is
what makes conclusions credible: it proves the criteria predate the data._

## Decision Criteria (the acceptance analog)
_One row per confirmatory HYP minimum. "Supports" thresholds stated
numerically where possible; where judgment is unavoidable, the judgment
procedure is stated (who, blind to what)._
| ID | For (HYP/EXP) | If the Data Shows | We Conclude / Update | Threshold / Test |
|---|---|---|---|---|
| DC-1 | HYP-1 / EXP-01 | | | |

## Statistical / Analytical Methods
Per metric: the analysis (test, model, or descriptive method), assumptions
and their checks, and the multiple-comparisons posture (corrections, or
the honest "exploratory, uncorrected, labeled as such").

## Exploratory Analysis Charter
Exploration is allowed and expected — in a separate, labeled section of
the writeup. Rule: nothing found in exploration is reported as
confirmatory; it becomes a HYP for the next study.

## Negative & Null Results
Where they are reported (same writeup, same prominence). A campaign that
only reports hits is a filter, not a study.

## Robustness Checks
| Check | Varies What | Conclusion Survives If |
|---|---|---|
| seed sensitivity | seeds | effect direction stable across all reported seeds |
| parameter perturbation | ±<N>% on key params | |
| ablation (if applicable) | components | |

## Figures & Claims Plan
The 3–6 figures the writeup needs, each named with the DC it evidences —
planned now so runs collect what the figures require, not vice versa.
