# Devtool Profile — Library / SDK / CLI / API-as-Product

Specification of the **devtool** profile (PROFILES.md). For software whose
users are developers and whose UI is an API surface. Deliberately lean:
it REUSES the product core and replaces only what maps badly.

## What changes vs the product profile
| Product doc | Devtool replacement |
|---|---|
| PRD_Information_Architecture | DEV_API_Surface (the surface IS the IA) |
| PRD_User_Flows_and_Use_Cases | DEV_DX_and_Docs §Golden Paths (a use case is a code sample that compiles) |
| TECH_UI_UX_Design | DEV_DX_and_Docs (docs, examples, and error messages ARE the UX) |
| — (new) | DEV_Versioning_and_Compat |
Everything else — Executive Summary, Scope & Roadmap, Business Rules
(rare), FR Overview + modules, Data/NFR/Security/Risks/DoD/Decision Log,
TECH System Architecture / API Specification (internal services) /
Data Design — is the product core, unchanged. **Light tier:** reuse
`light/PRD_Product_Brief.md` + `light/TECH_Implementation_Notes.md`; the
brief's Primary Flow is written as the getting-started code sample.

## Role mapping
| Framework Role | Acts As | Owns |
|---|---|---|
| PM | API Product Owner | Exec Summary, Scope, FR modules, DEV_Versioning_and_Compat policy decisions |
| UX | DX Designer | DEV_API_Surface ergonomics review (pass A: naming, consistency, error contracts — the punch list is API-shape feedback BEFORE implementation lock), DEV_DX_and_Docs |
| Architect | same | internals, TECH files, NFRs (perf, binary/bundle size budgets) |

## Checklist additions (AGENTS.md §5 applies, plus)
supported runtimes/platforms matrix · packaging & distribution (registry,
signing, supply-chain posture) · semver & deprecation policy · docs
build/publish pipeline · telemetry in a dev tool (consent! opt-in default)
· licensing (of the tool AND its dependencies) · migration tooling for
breaking changes · benchmark honesty (vs whom, on what).

## DX failure modes (dispositioned in pass A — lean rubric, recorded in
the punch list itself rather than a separate review file)
- getting-started exceeds <15> minutes or requires undocumented state
- an error message without a remedy in it
- a breaking change without a migration path AND a codemod/tool where feasible
- public surface drift: exported-but-undocumented or documented-but-gone
  (specgraph --trace over the surface table catches this)
- inconsistent naming across the surface (same concept, two names —
  the Glossary rule applied to identifiers)
- silent behavior change under the same version (semver violation)

## No new ID registers
FR areas: API (surface), VERS (compat), DX (docs/experience).
