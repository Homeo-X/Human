#!/usr/bin/env bash
# Install a framework adapter for a non-Claude agent. Run from project root.
# Usage: bash tools/adapt.sh <gemini|qwen|antigravity|copilot|cursor|windsurf|cline|aider|goose|list>
set -eu
A="$(dirname "$0")/../adapters"
put(){ mkdir -p "$(dirname "$2")"; cp "$A/$1" "$2"; echo "installed $2"; }
case "${1:-list}" in
  gemini)      put GEMINI.md GEMINI.md ;;
  qwen)        put GEMINI.md QWEN.md ;;
  antigravity) put GEMINI.md .gemini/GEMINI.md ;;
  copilot)     put copilot-instructions.md .github/copilot-instructions.md ;;
  cursor)      put cursor-rule.mdc .cursor/rules/prd-framework.mdc ;;
  windsurf)    put windsurf-rule.md .windsurf/rules/prd-framework.md ;;
  cline)       put clinerules.md .clinerules ;;
  aider)       put CONVENTIONS.md CONVENTIONS.md; echo "add 'read: CONVENTIONS.md' to .aider.conf.yml" ;;
  goose)       put goosehints .goosehints ;;
  list|*)      echo "agents: gemini qwen antigravity copilot cursor windsurf cline aider goose"
               echo "native AGENTS.md (no adapter): codex opencode zed amp factory devin kimi rovo vibe openclaw" ;;
esac
