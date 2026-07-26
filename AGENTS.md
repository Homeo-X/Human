# AGENTS.md — PRD-Agent Framework

This file tells any AI coding agent how to turn a product brief into a
right-sized product spec — a PRD + TECH documentation set — using a tiered
document standard and a four-role workflow. It is the single source of
truth; the templates and the Claude Code agents implement what is written
here.

## 1. Tiers — size the spec to the product

Do NOT produce the full document set for every brief. Choose a tier during
intake and confirm it at the scoping checkpoint (§4).

| Tier | When | Document set |
|---|---|---|
| **Light** | Small feature, internal tool, single-purpose utility; one implementer or small team; ≲2–3 weeks of build; low compliance risk | Both files in `templates/light/` + the two `light+` files from `core/` (`PRD_Decision_Log`, `PRD_Acceptance_Criteria_and_DoD`) (+ 1–3 `PRD_FR_<Module>` files only if an area exceeds ~10 requirements) |
| **Standard** | A typical single product or major feature; one team; external users OR meaningful data sensitivity | Core set below minus files folded per the matrix; usually 12–16 files |
| **Full** | Multi-team, marketplace/platform, regulated or compliance-heavy, or explicit stakeholder sign-off culture | Everything in `templates/core/` + all scoped FR modules |

Tier signals that push UP: money movement, PII/regulated data, multiple user
classes, external integrations users depend on, >1 team. Signals that push
DOWN: internal audience, single workflow, existing platform doing the heavy
lifting. When torn between two tiers, propose the lower one and say why —
the user can raise it at the checkpoint. "Internal admin tool for support
agents" is Light or small-Standard, never Full.

### Fold-into matrix (Standard tier)
Any core file may be omitted at Standard **only** by folding its essential
content into the named target and recording the fold in `MANIFEST.md`:

| File | Fold into (when omitted) |
|---|---|
| PRD_Business_Rules | Product Brief §Rules, or the owning FR module |
| PRD_Information_Architecture | TECH_UI_UX_Design §Key Screens |
| PRD_External_Integrations | TECH_System_Architecture |
| PRD_Security_Requirements | PRD_Non_Functional_Requirements (only when data is low-sensitivity) |
| PRD_Risks_and_Constraints | PRD_Scope_and_Roadmap |
| PRD_Glossary_and_References | PRD_FR_Overview |
| TECH_API_Specification | TECH_System_Architecture (client-only products) |

Folded content lands in the target as a clearly titled section (e.g.
"## Glossary (folded)") — adding such sections to a target is the one
sanctioned deviation from its template structure. `docs/MANIFEST.md` is the
authoritative record of tier, folds, modules, AREA codes, and cross-cutting
decisions; any copy elsewhere is re-synced FROM it at cross-review.

Never omitted at any tier: `docs/MANIFEST.md`, Decision Log, Acceptance
Criteria & DoD, and at least one place where requirements live with IDs.

## 2. Document set

**Profiles.** The framework ships document profiles sharing the same
tiers, roles, workflow, IDs, and validation — **product** (default),
**game**, **research**, **devtool**, **bio** — inventoried with their specs and the
extension contract in `PROFILES.md`. The orchestrator
selects the profile at intake from the brief (a game brief gets the game
profile) and confirms it at the scoping checkpoint; MANIFEST records it.
Profile-agnostic docs (Scope & Roadmap, Risks, NFR, Security, Acceptance &
DoD, Decision Log, MANIFEST, the TECH files, and the FR module library)
are shared — a game's multiplayer feature uses the same `_MODULE_TEMPLATE`
discipline as any other module.

Templates live in `templates/` in three groups (product profile):

- `templates/core/` — the fixed Standard/Full files (14 PRD + 4 TECH). All
  domain-neutral; nothing in them assumes e-commerce or any other domain.
- `templates/light/` — `PRD_Product_Brief.md`, `TECH_Implementation_Notes.md`.
- `templates/modules/` — Functional Requirements module library:
  - `_MODULE_TEMPLATE.md` — the canonical skeleton for ANY module. If a
    scoped module has no library file, instantiate this. Never invent a
    looser structure.
  - `common/` — Authentication, Permissions, Admin_Panel, Notifications,
    Search, Analytics_and_Reporting, Internationalization, Files_and_Media
    (domain-agnostic).
  - `ecommerce/`, `saas/`, `ai/`, `mobile/`, `marketplace/`, `content/` —
    domain starting points. These are
    LIBRARIES, not defaults. Use a library file only when the brief's domain
    matches; otherwise instantiate `_MODULE_TEMPLATE.md` with the product's
    own vocabulary.

A real run copies the tier-appropriate files into the target project's
`docs/` and fills them in. Never edit files under `templates/`.

## 3. Depth conventions (apply to every generated file)

- **Front-matter** — every doc keeps its YAML front-matter: bump `version`
  (semver: patch = wording, minor = new/changed requirements, major =
  scope change), set `status` (draft → in-review → approved), `owner`,
  `last_updated`. `status: template` means untouched.
- **FR module structure** — every FR file, library or instantiated,
  contains every `_MODULE_TEMPLATE` section. Write "None" deliberately
  rather than deleting a section.
- **Data models** — entities and attributes are defined once, in
  PRD_Data_Overview (physical detail in TECH_Data_Design). FR modules
  reference entity names only and flag new entities for the Architect.
- **Edge cases** — every FR module's Edge Cases table covers at minimum:
  empty states, invalid input, permission denied, concurrency/conflict,
  external-dependency failure, scale extremes. "N/A" is allowed per row,
  silence is not.
- **Success metrics** — every FR module carries ≥1 metric tracing to a
  named KPI in PRD_Executive_Summary (or Product_Brief §Success Criteria).
  A module whose metrics trace to nothing is a scope smell — flag it.
- **Acceptance criteria** — Given/When/Then, attached to requirements in
  the FR tables. Every Must has a happy-path criterion and a failure-mode
  criterion.
- **NFRs** — numbers and a measurement method, scaled to stated usage.
- No placeholder dashes in finished output.
- **Decisions** — Decision Log entries use the structured schema in the
  template: status, context, decision, alternatives (with
  `rejected_because`), consequences (positive AND negative),
  reversibility (high/medium/low), `affects:` (files or IDs), and
  `supersedes:`. The `affects:` links are what make a changed decision
  re-reviewable: whatever it lists is what gets re-read.
- **AI evaluation** — any module with Must-priority AI behavior defines
  eval rows (`EV-<AREA>-NNN`): method, dataset, pass bar, regression
  cadence. "Works in the demo" never substitutes for an EV row. Cost and
  latency budgets for AI live in the NFR register and are referenced from
  the AI module, not duplicated there.
- **Grounding (brownfield)** — when a target codebase or source-document
  corpus exists, current-state claims in generated docs cite how they were
  obtained using the marker `[grounded: <tool>, YYYY-MM-DD]` (per
  INTEGRATIONS.md; `specgraph --stale` flags aged grounding); designed-anew content needs
  no citation. Never present a queried fact and an invented one in the
  same voice.

## 4. Workflow

Roles: **Orchestrator**, **PM**, **Architect**, **UX**.

| Role | Owns |
|---|---|
| Orchestrator | Intake, tier + module scoping, cross-cutting decisions, `MANIFEST.md`, Decision Log entries for scoping, sequencing, final cross-review |
| PM | Executive Summary, Scope & Roadmap, Business Rules, FR Overview, all FR module files, Risks & Constraints, Acceptance Criteria & DoD, Glossary |
| Architect | Data Overview, External Integrations, NFRs, Security Requirements, TECH_System_Architecture, TECH_API_Specification, TECH_Data_Design |
| UX | Information Architecture, User Flows & Use Cases, TECH_UI_UX_Design, and the UX review of PM's FR files |

At Light tier the PM absorbs the UX role and the Architect writes only
TECH_Implementation_Notes.

Steps:

1. **Intake.** Establish what the product is, who it's for, what it does,
   and the tier signals (§1). If these can't be answered from the brief,
   ask — don't guess a domain.
2. **Scope.** Pick tier, FR module list, and walk the cross-cutting
   checklist (§5). Apply module-naming rules (§6).
3. **Scoping checkpoint (the one interactive gate).** Present to the user:
   tier + rationale, module list with one-line purposes, cross-cutting
   decisions, folds, and assumptions made. Ask for corrections. Skip this
   only if the user pre-authorized (e.g. brief contains "auto"). After
   approval, do not stop again until cross-review.
4. **Setup.** Create `docs/`, copy tier files + module files (instantiating
   `_MODULE_TEMPLATE` where needed), write `MANIFEST.md` and Decision Log
   entry D-001 recording the scoping.
5. **PM pass** — all PM-owned files.
6. **UX pass A** — UX drafts Information Architecture + User Flows, and
   reviews every FR file: fills the "UX Considerations" column, adds
   missing interaction edge cases, and returns a punch list of FR changes.
   PM applies or contests the punch list (disagreements → Decision Log).
7. **Architect pass** — reads PM + UX output; drafts all Architect files.
   Runs the built-in consistency checks (FR→API coverage, entity match).
8. **UX pass B** — TECH_UI_UX_Design, grounded in the now-stable FRs and
   architecture.
9. Every drafting role's completion report names the top assumptions it
   ADOPTED from upstream docs (not its own new ones) — this list is the
   red team's attack surface and the antidote to silent inheritance.
10. **Cross-review.** Orchestrator reads everything: entity-name mismatches,
   FR modules without TECH coverage, roadmap/scope drift, metrics that
   trace to no KPI, folds that lost content. Fix small issues (bump
   versions), log findings + resolutions in the Decision Log, flag large
   issues to the user with file + section.
11. **Red-team pass** (Standard/Full; Light on request): an adversarial
    review under RED_TEAM.md's isolation rules — fresh context, docs
    only, attacks without fixes — producing `docs/CHALLENGE_REGISTER.md`.
    The orchestrator dispositions every CH (accept / refute-with-evidence
    / acknowledge-by-Decision); unresolved S1/S2 go to the user verbatim.
12. **Report.** Files generated, tier + modules chosen and why, review
    findings, open questions needing the user.

## 5. Cross-cutting concerns checklist (mandatory at scoping)

Briefs rarely mention these; missing them is the most common scoping
failure. For EACH, record one of: **own module** / **folded into one or more named
locations** / **excluded — <reason>**, in `MANIFEST.md` and the FR Overview:

Search & findability · Permissions/roles/sharing · Analytics & telemetry
(KPI instrumentation) · Notifications · Internationalization/localization ·
Accessibility (goes to NFR at minimum) · Audit & compliance logging ·
Import/export & data portability · Offline/degraded connectivity (mobile
especially) · AI behavior, evals & cost (any LLM surface) · Admin/operator
tooling · Onboarding & empty states.

"Excluded — not mentioned in brief" is not a valid reason; the reason must
be about the product ("single-user tool, no permissions needed").

## 6. Naming and ID conventions

- **Filenames**: letters, digits, underscores only — no spaces, `&`,
  commas, or slashes. `PRD_<Name>.md`, `TECH_<Name>.md`,
  `PRD_FR_<Module>.md`. Human-readable titles (with `&`) live in the H1.
- **Modules**: named in the product's own vocabulary from the brief
  ("Case Triage", not "Order Management" for a support tool); 1–3 words;
  nouns; one module = one coherent capability a user could point at. If a
  proposed module can't be described in one sentence without "and also",
  split it. Reserved module names (collide with fixed files): "Overview".
- **Requirement IDs**: `FR-<AREA>-<NNN>`; AREA = 2–5 uppercase letters,
  unique per module, registered in the FR Overview table. Other registers:
  `BR-` (business rules), `NFR-`, `RSK-`, `UC-`, `NTF-`, `D-` (decisions),
  `EV-<AREA>-NNN` (evaluations), `G-NN` (KPIs); game profile adds
  `PIL-N` (design pillars), `MECH-NN` (mechanics), and `ARCH-NN` (AI
  archetypes); research profile adds `HYP-N` (hypotheses), `EXP-NN`
  (experiments), `DC-N` (decision criteria), and `CM-N` (causal
  mechanisms); bio profile adds `SCL-NN` (scale-level contracts), `BPR-NN`
  (biological processes), `EVC-N` (evidence classes), and `INV-NN`
  (integrity invariants); agentic specs add `AGT-N` (agents) and `TOOL-NN`
  (tools); the red-team pass adds `CH-NN` (challenges); rubric items use
  `RUB-NN` (game), `RRB-NN` (research), `BRB-NN` (bio).
  IDs are never reused after deletion.
- **Priority**: Must / Should / Could.

## 7. Versioning & history

- Per-doc history: front-matter `version`/`status`/`last_updated`, bumped
  by whichever role edits (rules in §3).
- Set-level inventory: `docs/MANIFEST.md` — product, brief digest, tier,
  module list + rationale, cross-cutting decisions, fold record, and a file
  table (file / owner / version / status). Orchestrator creates it at setup
  and refreshes it at cross-review; `/prd-status` reads it.
- Change history below the version bump: prefer `git log -S<ID>` when the
  spec lives in git; otherwise instantiate `templates/CHANGE_LEDGER.md`
  and append one line per minor/major bump (patch exempt).
  `specgraph --history <ID>` reads whichever exists.
- Compaction: when the Decision Log exceeds ~40 active-plus-superseded
  entries, MOVE superseded entries to `PRD_Decision_Log_Archive.md`
  (never delete — specgraph reads both) and generate the one-line view
  with `specgraph --digest --write`. Append-only integrity is checked
  automatically: specgraph hashes entries into `docs/INTEGRITY.json` and
  warns when a past entry changes or vanishes.
- Decision history: `PRD_Decision_Log.md`, append-only, supersede-not-edit.
  Scoping, contested trade-offs, review findings, and later scope changes
  all get entries. This replaces the old Glossary change-log as the audit
  trail.

## 8. Brownfield inputs

A run is **brownfield** when the spec targets an existing codebase and/or
arrives with a corpus of prior documents. The workflow (§4) is unchanged;
three steps gain a grounding duty, executed with the tools in
INTEGRATIONS.md when detected and by direct reading otherwise:

- **Intake:** index the codebase (codebase-memory-mcp) and/or graph the
  document corpus (graphify) before scoping; module candidates and
  cross-cutting decisions start from what exists, not from the brief alone.
- **Architect pass:** current-state sections of Data Overview, System
  Architecture, and the API spec are written from graph queries and cited
  as such; to-be-built content is explicitly marked.
- **Cross-review:** spec↔code drift check — names in TECH docs must exist
  in the graph or be marked *to be built*; findings go to the Decision Log.

Record tool detection and use in `docs/MANIFEST.md` §Tooling.

## 9. Scope lifecycle: locked scope, reopening, resolution

After the scoping checkpoint (§4 step 3), scope is **locked**. Discovered
problems are handled at the lowest sufficient level — never by silently
absorbing them and never by re-interviewing the user for every wrinkle:

1. **Minor change** (wording, a requirement added/split within a scoped
   module, a fold adjusted): make it, bump versions, Decision Log entry.
2. **Scope Reopen** (a module must be added/removed/renamed, a
   cross-cutting decision reversed, tier proven wrong): the orchestrator
   declares a reopen — a delta-checkpoint presented to the user showing
   only what changes and why, MANIFEST updated on approval, a Decision
   entry with `supersedes:` pointing at the original scoping decision.
   Only the orchestrator may reopen; other roles request it with evidence.
3. **Escalation** (two requirements are fundamentally incompatible, or a
   constraint makes a Must infeasible): halt work on the affected modules
   only, present the contradiction to the user with the options each role
   sees, continue everywhere else.

**Resolution Loop (cross-review):** when cross-review finds a cross-role
contradiction (e.g. a UX requirement implying synchronous behavior the
architecture makes async), run at most ONE structured round: each affected
role states its binding constraint in one or two sentences → the
orchestrator proposes a resolution → affected docs are updated and the
round is logged as a Decision with `affects:` links. If one round doesn't
resolve it, it is by definition level 2 or 3 above — reopen or escalate,
don't loop.

## 10. Spec graph, traceability, and reality feedback

**The framework is a specification compiler** (model, IR, and renderers
defined in `SPEC_MODEL.md`). **Files are the canonical serialization of
the spec model; the spec graph/IR is derived and disposable.** The entities of the model — requirements,
business rules, entities, decisions, risks, use cases, evals, KPIs — live
in the files as IDs and named references (§6). `tools/specgraph.py`
extracts them into a typed IR, validates it semantically, and answers
memory queries (`--why`, `--impact`, `--excluded`, `--context`,
`--digest`, `--stale`, `--history` — see MEMORY.md). Validation covers: dangling ID
references, duplicate IDs, Musts without acceptance criteria, Data Touched
entities absent from the Data Overview, metrics tracing to no KPI,
decisions affecting files that don't exist. Drift between graph and files
is a validation failure, never a merge problem — nothing is ever edited in
the graph.

**KPI ids:** goals in the Executive Summary / Product Brief carry ids
(`G-01`, `G-02`, …); Success Metrics cells trace by id so the trace is
machine-checkable, not prose-matched.

**Implementation traceability:** implementation artifacts carry the FR ids
they realize — in commit/PR messages, code comments at the entry point,
and test names or tags (`[FR-AUTH-001]`). `specgraph.py --trace <src-dir>`
reports Must requirements with zero implementation references; in
brownfield runs with codebase-memory-mcp, `search_code` over the FR-id
pattern is the faster equivalent. The DoD includes the annotation duty.

**Reality feedback (the loop back):** once implementation exists, the spec
is not finished — it is either true or drifting. On every `/prd-review` of
a repo with code: current-state claims are re-checked against the code
graph; where reality and spec disagree, reality wins for *current-state*
sections (update the doc, cite the grounding) and the spec wins for
*intent* (file the gap as a finding — code that contradicts a Must is a
defect, not a spec update). Every reality-driven spec change gets a
Decision entry so intent changes are never smuggled in as corrections.

## 11. Running on any agent

This file is the canonical, agent-neutral specification — many agents
(Codex CLI, OpenCode, Zed, Amp, Factory Droid, Devin, and others) load
`AGENTS.md` natively; for agents with their own entry file, thin pointer
adapters ship in `adapters/` (installed by `tools/adapt.sh <agent>`).
Nothing in §1–§10 assumes any particular agent product.

### Execution modes
- **Multi-agent mode** — an orchestrator that can spawn role agents runs
  §4 as written, one context per role. (In Claude Code this is wired via
  `.claude/`; any subagent-capable runtime can replicate it from §4.)
- **Single-agent mode (role rotation)** — one agent plays all four roles
  sequentially. Rules that make this sound: declare the active role
  explicitly before each pass ("acting as PM"); never blend roles in one
  pass; write all files and update MANIFEST **before** switching roles —
  the files are the handoff, not your memory; and before cross-review,
  take a deliberate fresh-eyes break: re-read every file from disk and
  audit it as written, not as remembered. The UX punch list still happens:
  the agent-as-UX reviews the agent-as-PM's files and records the punch
  list in writing before the agent-as-PM responds to it.

### Portable commands
These invocations are plain text and work on any agent (slash-command
wrappers, where they exist, map to the same procedures):
- `prd-new [game|research|devtool] [light|standard|full] [auto] <brief>`
  — run §4 from intake; a leading profile token forces that profile
  (otherwise inferred from the brief and confirmed at the checkpoint).
  Flag grammar: leading tokens only, exact whole-word match; a flag word
  inside the brief text is content, not a flag.
- `prd-redteam` — run the adversarial pass (RED_TEAM.md) against docs/;
  attacks only, dispositions belong to the orchestrator or `prd-review`.
- `prd-review` — run only the cross-review step against docs/: consistency,
  coverage, conventions, semantic checks (`tools/specgraph.py`), the §8
  drift check and §10 reality-feedback rule when code exists; findings to
  the Decision Log, MANIFEST refreshed.
- `prd-status` — report tier, modules, and per-file version/status from
  `docs/MANIFEST.md`; infer from the file set if the manifest is missing.
- `prd-memcheck` — memory-sufficiency probe (MEMORY.md): an isolated
  fresh context answers the seven memory questions from docs/ alone;
  gaps become findings.

### Validation tooling
`tools/validate.sh` (dependency-free bash) checks the framework tree, and
`--docs <dir>` checks a generated spec; it invokes `tools/specgraph.py`
(python3, stdlib-only) for semantic checks when available. Cross-review
runs both when a shell is available. In **Claude Code**,
this repo ships subagents for the four roles and `/prd-new`, `/prd-review`,
`/prd-status` commands — see `CLAUDE.md` and `.claude/`.
