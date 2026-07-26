# MEMORY.md — The Spec as a Memory System

The framework's files are a persistent institutional memory: what was
decided, why, what was excluded, what changed, what exists, what
implements it, and where reality diverged. This file names that model,
the query surface, and the test that keeps the memory honest.

## The seven questions and where they live
| Question | Lives In | Query |
|---|---|---|
| What was decided | Decision Log + MANIFEST | `--digest`, `--impact` |
| Why | decision schema (context, alternatives, consequences) | `--why <ID>` |
| What was excluded | non-goals, out-of-scope, exclusions-with-reason, folds, rejected_because | `--excluded <term>` |
| What changed | version bumps + git `-S` / CHANGE_LEDGER + supersede chains | `--history <ID>` |
| Which requirements exist | ID registers → typed IR | `--json`, `--brief` |
| What implements them | FR-id annotations in code/tests | `--trace <src>` (test-verified vs claimed) |
| Where reality diverged | §8 drift check + §10 reality-feedback Decisions | `/prd-review` |

## Memory integrity
- Append-only is enforced, not assumed: specgraph hashes Decision Log
  entries into `docs/INTEGRITY.json` each validation run and warns when a
  past entry mutates or disappears. Supersede; never edit.
- Compaction never deletes: superseded entries move to
  `PRD_Decision_Log_Archive.md`; `--digest` spans both.

## Staleness (memory that must be re-examined, not just recalled)
- Decisions carry `Valid while:`; `--stale [days]` surfaces conditional
  decisions, aged low/medium-reversibility decisions, and `[grounded: …]`
  markers older than the threshold. Run it inside `/prd-review`.

## The sufficiency probe (`prd-memcheck`)
Total memory is impossible; sufficient memory is testable. Protocol: an
ISOLATED fresh context (multi-agent: a fresh subagent; single-agent: the
hardest fresh-eyes break, no reliance on having written anything) reads
docs/ alone and answers the seven questions for a sampled set of targets
(2–3 requirements, 1 decision, 1 exclusion, 1 divergence if code exists).
Every answer must cite file:line. Questions unanswerable from disk are
findings: either the record has a gap (fix the docs, Decision entry) or
the question exceeds the record's stated scope (say so). Where a human
still remembers ground truth, spot-check reconstructions against it —
mismatches are the drift alarm.

## The event horizon (honest boundary)
The record cannot contain what was never written: pre-articulation
context, options discarded in conversation, a model's true (vs narrated)
reasoning. The framework's strategy is not total capture but cheap writes
at decision moments — punch lists, rejected_because, challenge registers —
pushing the horizon away from anything load-bearing.

## Deferred (build when the trigger fires)
Cross-spec memory (`LESSONS.md` — patterns harvested from superseded
decisions and repeated rubric flags, advisory-only): first multi-project
deployment where the same mistake demonstrably recurs. The trap is stale
or client-contaminated defaults; the governance question precedes the
code.
