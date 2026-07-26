---
doc: RES_Experiment_Designs
tier: standard+
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Experiment Designs

_One EXP subsection per experiment. Full-tier programs may split each into
its own file (RES_EXP_<slug>.md); the register stays here either way._

## Experiment Register
| ID | Name | Tests (HYP refs) | Status | Depends On |
|---|---|---|---|---|
| EXP-01 | | HYP-1 | planned | — |

## EXP-01 — <name>
### Purpose
Which HYPs, and the specific prediction: "if HYP-1, we expect <pattern> in
<metric>."
### Setup & Conditions
| Condition | Parameters (named, valued) | Runs/Samples per Condition | Seeds |
|---|---|---|---|
_Parameter sweeps: state the grid and WHY those ranges — "defaults" is not
a reason. Sample sizes: the justification can be rough (pilot variance,
convention, budget) but must exist._
### Procedure
Numbered, executable by someone else: setup → run → collect. Anything
manual is flagged (manual steps are where reproduction dies).
### Metrics
| Metric | Definition (formula/measurement) | Baseline Value | Collected When |
|---|---|---|---|
_Metrics defined BEFORE runs — especially emergence/qualitative metrics:
if "interesting behavior" isn't operationalized here, it will be
cherry-picked later._
### Expected Outcomes & Interpretation Map
| If We Observe | It Supports / Undermines | Notes |
|---|---|---|
_Include the boring branch: what a null result looks like and what it
means. Every row here must have a matching decision criterion in the
Analysis_Plan._
### Resource Budget
Compute/time per condition × grid = total; fits the NFR run budget or the
grid shrinks now, not mid-campaign.

## Cross-Experiment Rules
Shared codebase version per EXP recorded; changes between EXPs are
Decision Log entries (a tweaked simulator between two experiments is a
confound unless declared).
