---
doc: RES_Methodology
tier: standard+   # foldable into Charter §Methods for single-method studies
version: 0.0.0
status: template
owner: ux
last_updated: —
---

# Methodology

## Design
_Design type (per study-type lens) and why it fits the question — not why
it was convenient. State the causal ambition honestly: describing,
predicting, or explaining._

## Variables
| Variable | Role (independent/dependent/controlled/confound) | Levels / Range | Measured How |
|---|---|---|---|

## Causal Model & Estimands
_Only for studies making causal or mechanistic claims — descriptive
studies write "descriptive; no causal claims" and skip to threats.
Every confirmatory HYP names the mechanism that would explain it._
| ID | Mechanism Claim (X → Y via …) | Explains (HYP ref) | Intervention or Observation? | Adjustment Strategy (what's held fixed / conditioned on) |
|---|---|---|---|---|
| CM-1 | | HYP-1 | | |

**Estimand table** — the precise quantity each analysis targets, before
any model choice:
| Estimand (in words + symbol if useful) | For (CM/HYP) | Identified By (design feature that licenses it) |
|---|---|---|
A causal word ("causes", "drives", "improves") in any HYP without a CM
row and an estimand is a rubric flag (RRB-19).

## Power & Uncertainty
- **Power / precision analysis:** for each primary comparison — the
  smallest effect worth detecting, the assumed variance (source: pilot /
  prior work / stated guess), and the resulting run/sample count. This is
  where EXP "why that number" cells get their numbers.
- **Uncertainty reporting standard:** effect sizes with intervals
  (confidence/credible — pick and stay consistent), never bare point
  estimates or bare p-values; seeds/runs reported as distributions, not
  best-run anecdotes.

## Replication & Generalization
What internal replication the campaign includes (re-run of the key EXP
with fresh seeds at minimum), and the stated generalization boundary:
the regimes/parameter ranges the conclusions do NOT claim to cover.

## Validity Threat Register (the core artifact)
_One row per threat, dispositioned like risks. "We accept it" is a legal
answer; silence is not._
| Threat | Type (internal/external/construct/statistical) | Mitigation or Accepted (why) |
|---|---|---|
| selection / sampling bias | | |
| confounds (name candidates!) | | |
| measurement artifact / proxy gaming | | |
| experimenter degrees of freedom | | pre-registration in Analysis_Plan |
| generalization beyond tested regime | | |

## Randomization & Seed Policy
What is randomized, how seeds are chosen (never hand-picked after seeing
results), how many seeds constitute a claim, and where seeds are recorded
(→ Reproducibility).

## Controls & Baselines
| Baseline/Control | What It Isolates | Fairness Notes (tuned as hard as the treatment?) |
|---|---|---|

## Stopping & Exclusion Rules
Pre-stated: what ends a run early, what data may be excluded and why —
decided before data, logged when applied (Decision Log).

## Ethics & Compliance
Only what applies (human data → consent/IRB; scraped data → license;
none → say "none, because…").
