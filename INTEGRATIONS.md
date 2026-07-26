# INTEGRATIONS.md — External Tooling

The framework runs self-contained, but detects and uses four external tools
when present. All are optional; every workflow degrades gracefully without
them. Facts below are taken from each project's own documentation.

## 1. codebase-memory-mcp — brownfield ground truth
**What:** MCP server (single static binary, macOS/Linux/Windows; MIT).
Indexes a codebase into a persistent knowledge graph via tree-sitter
(158 languages, Hybrid LSP for 12) and serves 15 MCP tools — among them
`index_repository`, `get_architecture`, `get_graph_schema`, `search_graph`,
`trace_path`, `detect_changes`, `query_graph`, `get_code_snippet`,
`manage_adr`. Repo: github.com/DeusData/codebase-memory-mcp.
**Install:** download the release binary, run its `install` (auto-configures
detected agent clients), restart the agent.
**Framework use (brownfield runs — see AGENTS.md §8):**
- Orchestrator, intake: `index_repository` on the target repo, then
  `get_architecture` + `get_graph_schema` to ground scoping in what exists.
- Architect: query the graph (`search_graph`, `trace_path`) instead of
  file-reading to write current-state sections of Data Overview,
  System Architecture, and the API spec; ground every current-state claim.
- Cross-review / `/prd-review`: `detect_changes` and `search_graph` to
  check spec↔code drift (entities, routes, components named in TECH docs
  must exist in the graph or be marked as *to be built*).
- Optional: mirror Decision Log entries into `manage_adr` so decisions
  persist next to the code across sessions.

## 2. graphify — source-document ground truth
**What:** CLI + agent skill (Python, `uv tool install graphifyy`, then
`graphify install`; invoked as `/graphify <path>`). Maps code AND
docs/PDFs/images into a queryable knowledge graph; every edge tagged
`EXTRACTED` (explicit in source) or `INFERRED`. Code parsing is local and
deterministic (tree-sitter); non-code uses the assistant's model. Repo:
github.com/Graphify-Labs/graphify.
**Framework use:**
- Orchestrator, intake: when the brief arrives with sibling material
  (legacy specs, notes, PDFs), `/graphify` that corpus; scoping questions
  are answered by graph queries before they are asked of the user.
- PM: query the corpus graph while drafting; prefer `EXTRACTED` edges as
  citable facts, treat `INFERRED` edges as assumptions to list in the
  MANIFEST's assumptions section.
- Division of labor vs codebase-memory-mcp: cbm owns *code* ground truth;
  graphify owns *document/mixed-media* ground truth. Both may run in one
  brownfield generation.

## 3. rtk — token-efficient shell
**What:** Rust CLI proxy (`brew install rtk`; Apache-2.0) that filters and
compresses command output 60–90% before it reaches agent context; 100+
commands with passthrough support, <10ms overhead. Verify with
`rtk --version` and `rtk gain` (a same-named "Rust Type Kit" exists — if
`rtk gain` fails, the wrong tool is installed). Repo: github.com/rtk-ai/rtk.
**Framework use:** every role, every tier. When `rtk` is on PATH, prefix
shell commands with it — including `rtk bash tools/validate.sh` in
cross-review and `/prd-review`. Spec generation is markdown-heavy but its
shell moments (git, file listings, validators, test runs in brownfield
inspection) are exactly what rtk compresses.

## 4. ponytail — minimal-code implementation handoff
**What:** an agent skill/plugin ("the lazy senior dev": ~54% less code on
average, up to 94%, with trust-boundary, data-loss, security, and
accessibility guards never dropped; MIT). Claude Code install:
`/plugin marketplace add DietrichGebert/ponytail` then
`/plugin install ponytail@ponytail`; 20 agent surfaces supported. Repo:
github.com/DietrichGebert/ponytail.
**Framework use:** ponytail shapes *code*, not specs — it is deliberately
NOT wired into generation. Its place is the handoff: when the same repo
proceeds from spec to implementation, install ponytail so the implementing
agent builds the Musts minimally. The orchestrator's final report
recommends it for the implementation phase; the DoD's "meets acceptance
criteria as written" pairs with ponytail's bias against over-building.

## Detection & recording
At intake the orchestrator detects each tool (MCP tool list for cbm;
`graphify`, `rtk` on PATH; ponytail is handoff-only) and records the result
in `docs/MANIFEST.md` §Tooling. Grounded facts in generated docs name their
source ("per codebase-memory-mcp `get_architecture`, <date>"). A run with
zero tools detected is a normal greenfield run — no behavior is lost, only
grounding and token efficiency.
