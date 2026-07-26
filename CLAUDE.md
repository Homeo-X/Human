@AGENTS.md

## Claude Code specifics

Claude Code is this framework's multi-agent-mode wiring (AGENTS.md §11);
other agents run the same standard natively or via `adapters/`.

This project ships first-class Claude Code support on top of the standard
above:

- `.claude/agents/prd-orchestrator.md`, `prd-pm.md`, `prd-architect.md`,
  `prd-ux.md`, `prd-redteam.md` — subagents matching the four roles in AGENTS.md (UX runs
  twice: review pass A, design pass B)
- `.claude/skills/prd-new/`, `prd-review/`, `prd-status/`, `prd-redteam/`,
  `prd-memcheck/` — slash commands

`/prd-new` forks straight into `prd-orchestrator`, which picks the tier,
runs the scoping checkpoint, then spawns `prd-pm`, `prd-ux` (pass A),
`prd-architect`, and `prd-ux` (pass B) per AGENTS.md §4. Prefer the slash
commands over natural-language asks — they pin the exact agent.

External tooling (codebase-memory-mcp, graphify, rtk, ponytail) is
detected and used per INTEGRATIONS.md — brownfield grounding, corpus
queries, token-efficient shell, and the implementation handoff.

Semantic validation: `python3 tools/specgraph.py docs/` derives the spec
graph (ids, references, KPI traces) and reports dangling refs, Musts
without acceptance criteria, and untraced requirements (`--trace src/`).

Write generated docs to `docs/` in the target project unless told
otherwise, including `docs/MANIFEST.md`. Never modify files under
`templates/` — those are the blank originals; copy, then fill.
