# Adapters — running the framework on non-Claude agents

`AGENTS.md` is the canonical spec and is loaded **natively** (no adapter
needed) by, among others: Codex CLI, OpenCode, Zed, Amp, Factory Droid,
Devin CLI, Kimi Code CLI, Rovo Dev CLI, Mistral Vibe, OpenClaw.

For agents with their own entry-file convention, install the matching
pointer with `bash tools/adapt.sh <agent>` from the project root, or copy
manually:

| Agent | Adapter file | Installs to |
|---|---|---|
| Gemini CLI | GEMINI.md | ./GEMINI.md |
| Qwen Code | GEMINI.md | ./QWEN.md |
| Antigravity | GEMINI.md | .gemini/GEMINI.md |
| GitHub Copilot | copilot-instructions.md | .github/copilot-instructions.md |
| Cursor | cursor-rule.mdc | .cursor/rules/prd-framework.mdc |
| Windsurf | windsurf-rule.md | .windsurf/rules/prd-framework.md |
| Cline / Roo Code | clinerules.md | ./.clinerules |
| Aider | CONVENTIONS.md | ./CONVENTIONS.md (add `read: CONVENTIONS.md` to .aider.conf.yml) |
| Goose | goosehints | ./.goosehints |

All adapters carry the same short pointer: read AGENTS.md in full, then
run in single-agent role-rotation mode (AGENTS.md §11) unless the runtime
supports subagents. Entry-file names above follow each tool's documented
project-level convention; if a tool doesn't pick the file up, check its
current docs — the adapter content is tool-agnostic and safe to relocate.
The Claude Code integration (`.claude/`) is simply this framework's
multi-agent-mode wiring, not a privileged surface.
