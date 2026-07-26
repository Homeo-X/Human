# PRD-Agent Framework

Turns a product brief into a **right-sized** PRD + TECH documentation set —
Light (~4–6 files), Standard (~12–16), or Full (~20+ incl. modules) — using
a four-role agent workflow — in four document profiles: **product**
(PRD/TECH), **game** (GDD), **research** (studies/experiments), and
**devtool** (libraries/SDKs/CLIs), inventoried in `PROFILES.md` — Orchestrator → PM → UX (review pass) →
Architect → UX (design pass) → cross-review.

## What's in here

```
AGENTS.md              the standard: tiers, roles, workflow, conventions
SPEC_MODEL.md          the canonical specification model (IR, node/edge kinds, renderers)
RED_TEAM.md            adversarial review protocol (challenge register, isolation rules)
MEMORY.md              the spec-as-memory model: query surface, integrity, sufficiency probe
PROFILES.md            profile inventory, extension contract, roadmap
adapters/              entry-file pointers for non-Claude agents (+ tools/adapt.sh)
INTEGRATIONS.md        optional external tooling: brownfield grounding + efficiency
CLAUDE.md              Claude Code entry point (imports AGENTS.md)
README.md              this file
templates/
  core/                18 domain-neutral fixed templates (14 PRD + 4 TECH)
  gdd/                 game profile: 11 GDD core docs + prototype brief + genre lens + design rubric
  research/            research profile: 6 core docs + study brief + methods rubric + study-type lens
  devtool/             devtool profile: API surface, versioning & compat, DX & docs
  light/               2 consolidated Light-tier templates
  modules/             FR module library:
    _MODULE_TEMPLATE.md   canonical skeleton for ANY module
    common/               auth, permissions, admin, notifications, search,
                          analytics, i18n, files-and-media (8)
    ecommerce/ saas/ ai/ mobile/ marketplace/ content/ games/
                          domain starting points (6 / 4 / 3 / 2 / 3 / 2 / 6)
.claude/agents/        5 subagents (orchestrator, pm, architect, ux, redteam)
.claude/skills/        5 commands (prd-new, prd-review, prd-status, prd-redteam, prd-memcheck)
tools/validate.sh      dependency-free static checker (run: bash tools/validate.sh)
tools/specgraph.py     semantic spec-graph validator + implementation tracer
```

## Use with Claude Code

1. Drop this folder's contents into your project root (or `--add-dir`).
2. `/prd-new <brief>` — the orchestrator picks a tier and module list,
   confirms them with you once (the scoping checkpoint), then generates the
   set into `docs/` plus a `MANIFEST.md` and a Decision Log.
   Variants: `/prd-new light <brief>` forces a tier; `/prd-new auto <brief>`
   skips the checkpoint.
3. `/prd-review` — cross-checks consistency, coverage, and conventions;
   findings are logged to the Decision Log.
4. `/prd-status` — reports tier and per-file version/status from MANIFEST.

## External tooling (optional)

Detected automatically, never required (see `INTEGRATIONS.md`):
**codebase-memory-mcp** grounds brownfield specs in an indexed codebase
graph; **graphify** grounds scoping and drafting in a knowledge graph of
existing docs/PDFs; **rtk** compresses every shell interaction; **ponytail**
is recommended at the spec→implementation handoff so Musts get built
minimally. Greenfield runs with none installed behave exactly as before.

## Use with any other coding agent

`AGENTS.md` is the canonical spec — Codex CLI, OpenCode, Zed, Amp, Factory
Droid, Devin and others load it natively. For agents with their own entry
file (Gemini, Qwen, Copilot, Cursor, Windsurf, Cline, Aider, Goose), run
`bash tools/adapt.sh <agent>` to install a pointer adapter — see
`adapters/README.md`. Runtimes without subagents use single-agent role
rotation (AGENTS.md §11): explicit role hats, files-as-handoff, fresh
re-read before cross-review. Claude Code's `.claude/` is just this
framework's multi-agent-mode wiring, not a privileged surface.
