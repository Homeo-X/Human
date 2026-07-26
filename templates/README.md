# Templates

Three groups — see `../AGENTS.md` §1–2 for which files each tier uses and
the fold-into matrix:

- `core/` — fixed Standard/Full set, domain-neutral (14 PRD + 4 TECH)
- `light/` — Light-tier consolidated pair
- `gdd/` — the game profile's document set (concept, core loop &
  mechanics, systems, content & levels, player experience, narrative, art
  & audio, monetization, game AI & encounters, playtesting & telemetry,
  game technical architecture + a Light-tier prototype brief); tier sets,
  folds, production milestones, and the genre lens in `gdd/README.md`
- `research/`, `devtool/` — the research and devtool profiles' document
  sets; tier mappings and lenses in each directory's `README.md`
- `bio/` — the bio profile's document set (research charter, scale
  contract, anatomical ontology, physiological processes, cell &
  molecular model, evidence & provenance, validation framework,
  personalization model + a Light-tier model brief); tier sets, folds,
  the scale-depth lens, and the model rubric in `bio/README.md`
- `modules/` — FR module library; `_MODULE_TEMPLATE.md` is the canonical
  skeleton for any module not covered by the libraries: `common/` (8),
  `ecommerce/` (6), `saas/` (4), `ai/` (3), `mobile/` (2),
  `marketplace/` (3), `content/` (2), `games/` (6)

Every template carries YAML front-matter (`status: template`). Agents copy
into `docs/`, fill in, set status/version — never edit files here.
`MANIFEST.md` (repo-level, instantiated at every tier) is the authoritative
scoping record and AREA-code registry.

Front-matter `tier` vocabulary: `light` = Light-only file · `light+` =
copied at every tier · `standard+` = copied at Standard and Full (at Light
its content is covered by the Product Brief / Implementation Notes) ·
`any` = FR module, tier-independent.

## Filename convention

Letters, digits, underscores only. Human titles (with `&`, commas) live in
each file's H1, not the filename.
