---
name: prd-redteam
description: Run the adversarial review pass against an existing generated spec (RED_TEAM.md protocol) — attacks assumptions and failure modes; complements /prd-review, never replaces it
disable-model-invocation: true
context: fork
agent: prd-redteam
argument-hint: [path to brief or brief text, optional]
---

Run the RED_TEAM.md protocol against docs/. Brief context (if provided):
$ARGUMENTS

If docs/ doesn't exist or is empty, tell the user to run /prd-new first.
After writing docs/CHALLENGE_REGISTER.md, report the S1/S2 findings
verbatim and remind the user that dispositions are done by /prd-review or
the orchestrator, not by you.
