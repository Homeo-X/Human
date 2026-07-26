---
name: prd-status
description: Show the state of a PRD-Agent framework spec — tier, per-file version/status, and what's still untouched template
---

Read docs/MANIFEST.md first; if present, report from it: tier, module list,
cross-cutting decisions, and the file table (file / owner / version /
status), verifying each listed file actually exists on disk and flagging
drift (file changed but MANIFEST stale, or vice versa). If MANIFEST.md is
missing, infer the tier from what exists (PRD_Product_Brief.md ⇒ Light;
PRD_Executive_Summary.md ⇒ Standard/Full; distinguish those two by whether
the fold-eligible files are present) and compare docs/ against that tier's
set in templates/ (see AGENTS.md §1–2), using each file's front-matter: `status:
template` or absent file = not started; otherwise report its status and
version. Keep the report to a short table grouped by owner role, plus one
line naming the tier and anything missing for that tier.
