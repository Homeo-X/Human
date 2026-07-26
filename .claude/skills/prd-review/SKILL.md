---
name: prd-review
description: Cross-check an already-generated PRD-Agent framework spec for contradictions, coverage gaps, and convention violations
disable-model-invocation: true
context: fork
agent: prd-orchestrator
---

Run only the cross-review step of the PRD-Agent workflow (the cross-review
step in your instructions) against the files already in docs/. Do not
regenerate files from scratch. Check at minimum: entity-name consistency
across Data Overview / FR modules / API spec / Data Design; FR→TECH
coverage; scope↔roadmap alignment; module metrics tracing to named KPIs;
folded content present in its fold target (per MANIFEST.md); front-matter
version/status hygiene; leftover placeholder dashes.

Fix small issues directly and bump the affected files' versions. Treat
MANIFEST.md as authoritative for scoping records: re-sync any copies (the
FR Overview cross-cutting table) FROM it, never the reverse. Record every
finding and its resolution as an entry in PRD_Decision_Log.md, and refresh
MANIFEST.md's file inventory. If a shell is available, also run `bash
tools/validate.sh` from the framework root (prefix with `rtk` when
installed). If MANIFEST §Tooling shows codebase-memory-mcp was used, run
the spec↔code drift check per AGENTS.md §8, applying the reality-feedback
rule of AGENTS.md §10: reality wins for current-state sections, the spec
wins for intent, and every reality-driven change gets a Decision entry.
Run `python3 tools/specgraph.py docs/` (add `--trace <src>` when
implementation exists) and act on its findings — including INTEGRITY
warnings (a mutated past decision is supersede-not-edit being violated)
and `--stale` output (decisions whose Valid-while conditions or grounding
age warrant re-examination; disposition each: still valid / supersede). If docs/ doesn't exist or is empty, tell the user to
run /prd-new first instead.
