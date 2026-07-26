This project uses the PRD-Agent framework: a tiered PRD/TECH specification
system with four roles (Orchestrator, PM, UX, Architect) and portable
commands `prd-new`, `prd-review`, `prd-status`.

**Read `AGENTS.md` at the project root in full before any framework task.**
It is the canonical specification: tiers and fold rules (§1), templates
(§2), depth conventions (§3), workflow (§4), cross-cutting checklist (§5),
naming (§6), versioning (§7), brownfield grounding (§8), scope lifecycle
(§9), spec graph and traceability (§10), and execution modes (§11).

Unless this runtime can spawn role subagents, use single-agent role
rotation per AGENTS.md §11: one role at a time, declared explicitly, files
and MANIFEST written before every role switch, fresh re-read before
cross-review. Validate with `bash tools/validate.sh --docs docs/`.
