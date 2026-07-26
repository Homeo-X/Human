---
doc: PRD_Information_Architecture
tier: standard+
version: 1.0.0
status: draft
owner: ux
last_updated: 2026-07-26
---

# Information Architecture, Sitemap & Navigation

_The product's primary surface is a spatial and semantic explorer, not a document
site. Its information architecture is therefore two-dimensional: a **level axis**
(L0–L10, semantic zoom) and a **relation axis** (the typed graph). The navigation
tree is a third, derived, convenience — and the IA must never let it read as the
structure (D-006, BRB-30)._

## Surface Map
- **Explorer** — the primary surface; everything else is reached from it
  - Entity view (any level): structure, function, relations, evidence, geometry
  - Level transition surface: announces mode and resolution limit
  - Terminal surface: reached at declared depth — a designed answer, not an empty state
  - Evidence panel: the claim record behind anything displayed
  - Relations panel: typed edges, grouped by class, associations marked
  - Process view: mechanism as an ordered chain, in its spatial context
- **Search**
  - Name, function, clinical term, spatial predicate
  - Structured graph query
  - **Negative-space query** — what is unknown, unrepresented, unmodelled
- **Ask** — natural-language retrieval, every assertion cited
- **Coverage** — what the model holds against what it declared; the honest map of itself
- **Releases** — versions, manifests, licences, diffs
- **Curation** (authenticated) — queues, review, adjudication, operator view
- **My model** (Phase 7, authenticated) — overlay values, provenance, deletion

## Primary Navigation
Four items earn permanent placement, because each answers a question a user has
continuously rather than occasionally:

| Item | Question it answers | Why permanent |
|---|---|---|
| Explore | "where am I and what is here" | the product's core loop |
| Search | "where is the thing I want" | entry point for every task that does not start with browsing |
| Ask | "explain this to me" | the surface most users will reach for first |
| Coverage | "what does this model actually hold" | **the honesty surface must be permanent, not buried.** If it lives in a footer, the model's limits become discoverable only by the diligent, and BRB-05 fails |

Curation and My model appear only when authenticated, and are visually distinct
from the reference surfaces — the boundary between reading the canonical model
and altering anything must be unmistakable.

## Secondary / Contextual Navigation
- **Lineage breadcrumb** — the L0-to-current path, always visible, each ancestor
  one action away. This is the antidote to the standard failure of deep zoom
  interfaces, where users lose the thread at three levels down (FR-NAV-010).
- **Level indicator** — current level, its representation mode, and its
  resolution limit, persistently visible rather than announced once at transition.
  A user who arrives by link never saw the transition.
- **Membership switcher** — for multi-system entities, the other systems this
  entity belongs to, presented as equals. The pancreas must never look like a
  digestive organ with an endocrine footnote (FR-NAV-005).
- **Evidence-class filter** — a first-class control, not a settings item.
- **Related-by-type** — relations grouped by class, with `associated_with`
  visually distinct from typed relations.

## URL / Route / Deep-Link Structure
Every navigation state is addressable, because deep exploration that cannot be
shared is worthless to an educator (FR-NAV-006).

```
/e/{entity-id}                      entity at its default level
/e/{entity-id}@L{n}                 entity at an explicit level
/e/{entity-id}/evidence/{claim-id}  a specific claim
/e/{entity-id}/relations?type=...   filtered relations
/process/{bpr-id}                   a process specification
/search?q=...&mode=...              a query, including negative-space mode
/coverage?subsystem=...             coverage against declared scope
/release/{release-id}               a pinned release
/e/{entity-id}?release={id}         any view, pinned
```

Canonicalization: an entity resolves by any of its identifiers — external term,
minted id, or a retired id, which resolves to a tombstone (FR-VER-007). Shared
links pin their release by default, so a link handed to a student in September
still shows what it showed in September.

## Entry Points
Each must land on a state that makes sense with no prior context:

| Entry | Lands on | Must carry |
|---|---|---|
| Direct navigation | Explorer at L0 | orientation, and Coverage within reach |
| Shared deep link | the exact state, release-pinned | full lineage breadcrumb, level indicator, and the release it is pinned to |
| Search result | entity at the level that matched | why it matched, its compilation status, and the class of the matching claim |
| Ask response citation | the claim in its entity context | the claim record, not just the entity |
| Coverage view | a declared-but-unpopulated level | the terminal answer explaining what is declared and what exists |
| External ontology reference | the entity, via its external id | which authority resolved it and at what pinned version |
| Retired identifier | tombstone | what replaced it and why |

## Information Layering
The brief requires structural → functional → quantitative → clinical layering
that never overwhelms the spatial view. The IA's rule:

1. **Always visible:** what this is, where it is, its level and mode, its
   compilation status, and the evidence class of anything asserted.
2. **One action away:** function, typed relations, the claim record, geometry
   provenance.
3. **Two actions away:** mechanism detail, full source citations, conflicting
   claims, variation.
4. **Never hidden:** the resolution limit, the terminal answer, the
   non-diagnostic boundary, and the distinction between a typed relation and an
   association.

Layer 1 is deliberately larger than a conventional anatomy viewer's, because
evidence class and compilation status belong to what a thing *is* here, not to
its metadata. Demoting them to layer 2 would make the honesty machinery
decorative — which is RSK-09, the risk this IA exists to mitigate.
