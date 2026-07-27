# UPSTREAM.md — Vendored Framework and Applied Deltas

This repository vendors the **PRD-Agent Framework** at its root, because the
project extends it with a new document profile (`bio`), and a profile is not a
profile unless its validators ship with it (PROFILES.md §"The profile contract",
clause 5). Referencing the framework externally would leave the bio documents
structurally unvalidated.

## Vendored

- **Source:** `prd-agent-framework` (uploaded archive `prdagentframework.zip`)
- **Vendored:** 2026-07-26
- **Baseline:** `bash tools/validate.sh` → `ALL CHECKS PASSED` on the untouched tree
- **Files:** `AGENTS.md`, `CLAUDE.md`, `PROFILES.md`, `SPEC_MODEL.md`,
  `RED_TEAM.md`, `MEMORY.md`, `INTEGRATIONS.md`, `templates/`, `tools/`,
  `adapters/`, `.claude/`. The framework's own `README.md` was moved to
  `FRAMEWORK.md` so the repository root README describes the project;
  `validate.sh`'s required-root-doc check only asserts that `README.md` exists,
  which it still does.

## Deltas applied

Every change to a vendored file is listed here. Files under `templates/` other
than the new `templates/bio/` tree are untouched, per AGENTS.md §2.

### D1 — New `bio` profile (additive)
`templates/bio/` — profile README, 8 core `BIO_` documents, a Light-tier brief,
`BIO_RUBRIC.md`, and `BIO_Model_Review.md`. Registered in `PROFILES.md`
(shipped-profiles table), `AGENTS.md` §2 and §6 (ID registers), and
`templates/README.md`.

### D2 — `tools/specgraph.py`: bio ID registers
`ID_DEF` and `ID_REF` extended with `SCL`, `BPR`, `EVC`, `INV`, `BRB`.
`kind()` extended to map them to the node kinds declared for the profile.

### D3 — `tools/specgraph.py`: **upstream defect fix** — unparsed declared registers
`SPEC_MODEL.md` declares `AGT-N` (agent), `TOOL-NN` (tool), `CH-NN` (challenge),
and `CM-N` (causal-mechanism) as node kinds, and `specgraph.kind()` already maps
all four — but neither `ID_DEF` nor `ID_REF` ever matched them. Consequence in
upstream: in any spec containing agents, tools, a challenge register, or a
research causal-mechanism table, those IDs are invisible to the graph — duplicate
`AGT-1` definitions are not reported, and a reference to an undefined `TOOL-07`
or `CH-12` passes validation silently. The research profile's own trace chain
(research/README.md §"The research trace chain") names `CM-n` as a required link,
yet no `CM` id can ever be resolved.

Fixed here by adding all four to both regexes. **This is a defect in the upstream
framework, not a project-specific need** — it should be reported and, once fixed
upstream, this delta collapses into D2.

### D4 — `tools/specgraph.py`: bio semantic checks
Added alongside the existing semantic checks, in the same finding style:
- every `SCL` row declares a representation mode, an evidence model, and a
  resolution limit (an undeclared level is how a spec overclaims silently);
- every claim-bearing row in a `BIO_` document carries an `EVC` class;
- every quantitative row carries a unit (AGENTS.md-adjacent; the bio profile's
  unit-consistency rule);
- `BPR` defined but referenced nowhere warns — same shape as the existing
  `HYP`/`DC` broken-chain check.

### D5 — `tools/validate.sh`: bio profile registration
- `BIO` added to the doc-prefix scan (dead-template-reference check);
- `templates/bio/` added to the AREA-code uniqueness scan;
- a bio-profile block mirroring the game-profile block: when `BIO_*.md` exist in
  a docs set, `MANIFEST.md` must carry a scale-depth declaration and
  `BIO_Model_Review.md` must exist with every `BRB` item dispositioned.

### D6 — `tools/biocheck.py` (new, project-owned)
Not a framework file. Executes the `INV-NN` invariants from
`docs/BIO_Validation_Framework.md` against `ontology/`. Written in specgraph's
idiom (finding levels, `--strict`, exit codes) so both validators behave
identically, and carries `--selftest` negative tests.

### D7 — `tools/specgraph.py`: **upstream defect fix** — `affects:` outside the doc set
The `affects:` check warns for any token ending in `.md` that is not in the docs
directory. AGENTS.md §3 defines `affects:` as "files or IDs", and decisions
routinely affect Markdown that lives beside `docs/` rather than in it —
`README.md`, `AGENTS.md`, a profile README. Upstream reports every one of those
as a missing file, which trains authors to delete true entries from `affects:`
to get a clean run. Since `affects:` is precisely what makes a changed decision
re-reviewable ("whatever it lists is what gets re-read"), a checker that
penalizes completeness is worse than no checker.

Fixed here by also accepting a file that exists one level above the docs
directory before warning. Non-existent files still warn, verified both ways.
**Defect in the upstream framework, not a project-specific need** (D-022).

## Re-applying an upstream update

1. Diff the new upstream tree against the vendored baseline.
2. Re-apply D1–D5 and D7 (D3 and D7 first — check whether upstream fixed them;
   if so, drop them).
3. Re-run `bash tools/validate.sh` and `bash tools/validate.sh --docs docs/`.
4. Record the new vendored date and baseline above.
