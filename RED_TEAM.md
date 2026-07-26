# RED_TEAM.md — Adversarial Review Protocol

Cross-review checks that the spec agrees with itself. This layer checks
whether an internally consistent spec is **wrong** — the failure mode of
shared-context role work, where an upstream assumption propagates until
apparent consistency masks a shared error. Red team complements
cross-review; it never replaces it.

## Isolation rules (the point of the exercise)
- The red team reads ONLY: the original brief, `docs/`, and each role's
  declared "assumptions adopted" list (AGENTS.md §4). Never the working
  conversation, never the other roles' reasoning beyond what the docs say.
- Multi-agent mode: a fresh subagent (`prd-redteam`). Single-agent mode:
  the hardest fresh-eyes break in the framework — re-read everything from
  disk, adopt the attacker stance, and do not defend anything you wrote.
- The red team ATTACKS ONLY. It proposes no fixes — the moment it designs
  a remedy it becomes a collaborator and inherits the frame it was meant
  to test. Dispositions belong to the orchestrator.

## The question protocol (every question answered, per spec)
| # | Question | Typical Victims |
|---|---|---|
| Q1 | Which assumption, if wrong, invalidates the most? | market/user assumptions in Exec Summary; "users will…" claims |
| Q2 | Which requirement is impossible or self-undermining as written? | latency vs consistency; privacy vs the analytics it promises |
| Q3 | Which described user behavior is unrealistic? | FTUE patience, configuration diligence, honest self-reporting |
| Q4 | What single failure makes the whole system useless? | the unexamined dependency every module shares |
| Q5 | Which entity is underspecified enough to hide a design error? | the entity every module touches but none owns deeply |
| Q6 | Which metric can be gamed, and who gains by gaming it? | KPIs, EV bars, moderation SLAs, rubric evidence itself |
| Q7 | Which two requirements contradict under load or at scale? | pairs that only meet in production |
| Q8 | What happens under PARTIAL failure of each critical path? | half-completed agent runs, half-synced saves, half-released payouts |
| Q9 | (agentic specs) Which TOOL/autonomy cell would an attacker or a confused model exploit first? | injection paths, approval fatigue, compensation gaps |
| Q10 | (per profile) the profile rubric's most-likely-flag, re-derived independently — do the dispositions survive hostile reading? | evidence written to pass rather than to test |

## Output — the Challenge Register
Instantiate `templates/CHALLENGE_REGISTER.md` into
`docs/CHALLENGE_REGISTER.md`. One CH row per finding; severity honest
(S1 invalidates the spec's core claim · S2 breaks a module or a Must ·
S3 weakens confidence). No finding is also legal — stated explicitly with
what was probed hardest.

## Disposition (orchestrator, after)
Per CH: **accept** (spec changes, versions bump, Decision entry) ·
**refute** (evidence cited in the register — refutation without evidence
is denial) · **acknowledge** (true, tolerated on purpose — Decision entry
with the accepted risk). S1/S2 unresolved at report time are escalated to
the user verbatim, in the red team's words, not the orchestrator's
summary.
