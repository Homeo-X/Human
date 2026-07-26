---
name: prd-new
description: Generate a right-sized PRD/TECH spec for a new product or feature using the PRD-Agent framework (tiered — Light, Standard, or Full)
disable-model-invocation: true
context: fork
agent: prd-orchestrator
argument-hint: [tier?] [auto?] [product brief]
---

Product brief: $ARGUMENTS

Run the full PRD-Agent framework workflow for this brief per your
instructions and AGENTS.md at the project root.

Argument handling — flags are LEADING TOKENS ONLY, matched as whole words,
case-insensitive; everything after the flags is the brief verbatim:
- If the first token is exactly `game`, `research`, `devtool`, or `bio`, force
  that profile (PROFILES.md); otherwise infer the profile from the brief
  and confirm at the checkpoint.
- If the next token is exactly `light`, `standard`, or `full`, treat it as
  a user-mandated tier — skip tier selection but still run module scoping.
- If the first token (or the token right after a tier flag) is exactly
  `auto`, skip the interactive scoping checkpoint and proceed on your best
  scoping, logging all decisions in the Decision Log and MANIFEST instead.
- A flag word appearing anywhere INSIDE the brief text is content, not a
  flag: "auto repair shop manager" has no flags; "Lighting design tool"
  mandates no tier. When a leading token is ambiguous (the brief could
  plausibly start with that word, e.g. "light table configurator"), ask
  one clarifying question rather than guessing.
- If no brief remains after flags, ask the user for one before proceeding.
