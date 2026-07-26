---
name: prd-memcheck
description: Memory-sufficiency probe — an isolated pass answering the seven memory questions from docs/ alone (MEMORY.md protocol); unanswerable questions become findings
disable-model-invocation: true
context: fork
argument-hint: [optional focus, e.g. a module or ID to center the sample on]
---

Run the MEMORY.md sufficiency probe against docs/. Focus (optional):
$ARGUMENTS

Isolation: reason ONLY from the files in docs/ (plus tools/specgraph.py
queries) — no conversation history, no memory of authorship. Sample per
protocol: 2–3 requirements, 1 decision, 1 exclusion, 1 divergence when
implementation exists. Answer each of the seven questions with file:line
citations; use `python3 tools/specgraph.py docs/ --why/--impact/
--excluded/--history` where they help, and say plainly when a question
cannot be answered from disk. Report: answered (with citations) /
unanswerable (record gap → recommend the fix) / out of stated scope.
If docs/ is missing or empty, tell the user to run /prd-new first.
