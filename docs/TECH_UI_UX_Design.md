---
doc: TECH_UI_UX_Design
tier: standard+
version: 1.0.0
status: draft
owner: ux
last_updated: 2026-07-26
---

# UI/UX Design

_The product is a spatial and semantic explorer. Its hardest design problem is not
rendering the body — it is making epistemic status legible without burying the
anatomy under caveats._

## Design Principles for This Product

1. **Evidence class is part of what a thing is, not metadata about it.** It is
   rendered with the entity, at the same visual priority as its name. Demoting it
   to a panel makes the honesty machinery decorative, which is RSK-09.
2. **The model's limits are answers, not errors.** The terminal surface, the
   negative-space result, and the retrieval refusal are designed states with real
   layouts — never empty viewports or error styling.
3. **Semantic zoom is a declared act.** Changing the level of biological
   abstraction is never a side effect of a scroll wheel. Users must be able to
   feel the difference between moving closer and changing what kind of claim they
   are looking at.
4. **A tree is drawn as a view, a graph as the model.** Every hierarchy
   presentation is visually marked as one path through a graph, and
   multi-membership is reachable from anywhere within it.
5. **Nothing important is carried by colour alone.** Evidence class, compilation
   status, and representation kind each have a non-colour encoding, because
   colour-only would make the product's core signal invisible to a large minority
   of users (NFR-018).

## Design System
- **Colour:** a restrained anatomical palette for geometry; a separate,
  deliberately non-anatomical accent family for epistemic signals so the two are
  never confused. Evidence class uses a monochrome weight ramp plus glyph, not a
  traffic-light hue ramp — red-for-weak-evidence would read as "wrong", and
  `HYPOTHESIZED` is not wrong.
- **Typography:** one serif family for definitional and claim text, one sans for
  interface chrome and identifiers. Anatomical Latin terms are never italicized
  by default — they are the preferred term, not a foreign phrase.
- **Spacing scale:** 4 px base. Dense by default; this is a reference tool used
  for long sessions, not a marketing page.
- **Source:** a custom minimal system rather than an existing component library.
  The epistemic components below have no equivalents to borrow.

## Component Inventory
| Component | Used By (FR refs) | States (empty/loading/error included) |
|---|---|---|
| Evidence badge | FR-EVID-002, FR-SRCH-002 | eight classes; unknown; conflicted; loading; **never absent** |
| Compilation-status chip | FR-ONTO-006, FR-RETR-008 | four statuses; blocked-from-promotion |
| Level indicator | FR-NAV-002, FR-SCAL-001 | level, mode, resolution limit; persistent, not transient |
| Lineage breadcrumb | FR-NAV-010 | 1–11 deep; truncated-with-expand; spanning-process variant |
| Membership switcher | FR-NAV-005, FR-REL-003 | single membership; multi-membership (equal weight, no primary) |
| Relation list | FR-REL-010 | grouped by class; **association rows visually distinct**; empty; paginated |
| Claim record panel | FR-EVID-010 | full record; conflicted pair; UNKNOWN; source unresolvable |
| Terminal surface | FR-SCAL-003, FR-NAV-003 | declared-depth reached; with external resources; without |
| Coverage matrix | FR-SCAL-010 | subsystem × level, declared vs populated; unmet declaration highlighted |
| Geometry viewport | FR-SPAT-002 | rendered; schematic-marked; described-not-depicted; load-failed (distinct from absent); degraded LOD |
| Process chain | FR-PHYS-002 | ordered steps; per-step spatial anchor; failure-state branch; narrative-only variant |
| Negative-space result | FR-SRCH-004 | gaps enumerated; no-gaps-assessed; never-assessed |
| Grounded response | FR-RETR-001 | per-assertion citations; refusal; gap statement; degraded |
| Reference comparison (Phase 7) | FR-PERS-005 | in-range; out-of-range; stale; conflicting; **see PUNCH-03 below** |
| Review card | FR-CUR-002 | proposal with derivation; blocked with reason; conflict pair |

## Key Screens

### Explorer (the primary surface)
- **Purpose:** navigate structure and meaning together.
- **Primary action:** move — laterally through relations, vertically through levels.
- **Always visible (IA layer 1):** entity name, level indicator with mode and
  resolution limit, compilation-status chip, evidence badges on every displayed
  claim, lineage breadcrumb.
- **Empty:** an entity with no geometry renders the described-not-depicted state —
  position, neighbours, and relations laid out as the primary content rather than
  as consolation for a missing mesh.
- **Loading:** geometry streams progressively; the semantic layer renders first,
  because the text is the model and the mesh is a projection of it.
- **Error:** geometry load failure is visually distinct from genuine absence
  (FR-SPAT-002). Conflating them would teach users that the model is incomplete
  when it is merely offline.

### Terminal surface
- **Purpose:** answer "what is below this?" when the answer is "nothing, here".
- **Layout:** full-width, composed, typographically equal to any other view. It
  states the level reached, the representation mode, the declared depth for that
  subsystem, and that this is a statement about the model, not about biology.
  Where external resources hold what we do not, they are named.
- **The design rule:** this must not use error styling, muted text, or an empty
  illustration. A user reaching the model's edge has been served correctly, and
  the surface should feel like an answer.

### Coverage
- **Purpose:** the model's honest account of itself.
- **Layout:** subsystem × level matrix, populated count over declared count in
  every cell. A cell that is declared with zero content is **highlighted, not
  hidden** — the unmet promise is the most important information on the screen
  (PUNCH-01, FR-SCAL-010).
- **Empty state:** does not exist; a model with no content still has declarations,
  and showing them is the point.

### Ask
- **Purpose:** natural-language access with every assertion traceable.
- **Per-assertion citation:** each assertion carries its own evidence badge
  inline. There is deliberately **no single overall confidence score** — averaging
  an EVC-2 mechanism with an EVC-4 quantity destroys exactly the distinction the
  user needs.
- **Refusal state:** styled as an answer. "I have no claims supporting this" is
  information, and it renders as prose, not as a warning.

### Curation review
- **Purpose:** let a reviewer judge without reconstructing.
- **Layout:** proposal, its full derivation (agent, sources, tool calls),
  validation findings, and the accept/reject action with a mandatory reason field.
- **Blocked state:** shows the blocking reason and the path to resolution
  (Scope Reopen request, split assignment) rather than a dead end.

### Onboarding and first run
Folded here per the MANIFEST cross-cutting record. The L0 entry states what the
model is, what it holds, and what it does not, with Coverage one action away. The
honest empty state — "we do not model this" — is introduced early and
deliberately, because a user who meets it first at depth will read it as a
failure.

## Interaction & Feedback Patterns
- **Semantic vs physical zoom:** separate controls, separate feedback. Physical
  zoom is continuous and silent. Semantic zoom is discrete, announced, and
  reversible with a single action.
- **Validation timing:** curation forms validate on blur for shape and on submit
  for cross-record rules, so a reviewer is not fighting the form mid-thought.
- **Destructive actions:** publication and personal-data deletion both require
  re-authentication and an explicit typed confirmation. Nothing else in the
  product is destructive, because nothing else can be — releases are immutable.
- **Undo:** not offered on canonical content, because there is nothing to undo;
  proposals are voided, claims are superseded, and both are recorded.
- **Reduced motion:** camera transitions and process animation become instant
  state changes with no information loss (NFR-017). Process chains remain
  readable as ordered steps without motion.

## Responsive / Platform Behavior
| Class | Behaviour |
|---|---|
| Desktop (primary) | full explorer, side-by-side semantic and spatial panes |
| Tablet | panes stack; semantic pane takes priority when both cannot fit — the text is the model |
| Phone | semantic-first; the viewport becomes a summonable overlay rather than the default |
| Offline bundle | identical to desktop, release pinned and stated persistently (NFR-014) |

The stacking priority is a deliberate inversion of the norm for 3D products: when
space is scarce, the anatomy view yields to the claims, not the other way around.

## Accessibility Implementation
Meeting NFR-015 through NFR-018 on a spatial product requires more than labelling.

- **The equivalent path (NFR-016) is a first-class interface, not a fallback.**
  Every entity reachable in 3D is reachable through a keyboard-navigable
  structural tree plus relation lists; every level transition, resolution limit,
  and evidence class is announced; every spatial relationship (containment,
  adjacency, laterality) is available as text because it lives in the spatial
  identity, not in the mesh (FR-SPAT-008). This is why D-008's indirection matters
  for accessibility and not only for licensing.
- **Announcements:** level transitions announce level, mode, and resolution limit
  through a live region. Evidence class is announced with each claim, not batched.
- **Non-colour encodings:** evidence class carries a glyph and a text label;
  compilation status carries a label; schematic geometry carries a persistent
  textual marker. Removing all colour must lose no information (NFR-018).
- **Focus management:** semantic zoom moves focus to the new level's heading;
  lineage breadcrumb is a landmark; the terminal surface takes focus when reached.
- **Testing:** manual audit with an assistive-technology user each phase, not only
  automated checks — automated auditing cannot evaluate whether a 3D explorer is
  actually usable without sight.

## PUNCH-03 — The out-of-range comparison (design decision, Phase 7)
Carried from BIO_Model_Review as a required design decision rather than closed
with disclaimer text.

**The problem:** a user sees their measured value plotted outside a reference
range. Regardless of any adjacent disclaimer, the visual grammar of "outside the
band" reads as a finding — that grammar is inherited from every lab report they
have ever seen. BR-019 forbids the product from making that claim, and BRB-25
observes that wording alone will not stop the inference.

**The decision:** the reference comparison component does not use the lab-report
grammar at all.

1. **No band-with-outlier layout.** Reference ranges are shown as a distribution
   the individual value sits within, not as a pass/fail interval with a boundary
   to fall outside of.
2. **No threshold colour.** Out-of-range values receive no red, no amber, no
   warning glyph. Distance from the population centre is shown as position, which
   is descriptive, rather than as status, which is interpretive.
3. **Provenance is co-equal with the value.** Method, device, source rank, and
   time render at the same visual weight as the number itself, so a self-reported
   value never looks like a clinical measurement (FR-PERS-006).
4. **Propagation is shown as explicitly bounded.** Adjacent to any comparison,
   the component states what this value does and does not change in the model
   (FR-PERS-005) — the default being "nothing else".
5. **The population is named on every comparison.** "Outside the reference range"
   is meaningless without knowing whose range; the reference subject's declared
   population (BIO_Research_Charter) appears with the comparison.

**What this costs:** the component will feel less immediately informative than a
lab report, and some users will want the familiar grammar. That is the trade —
the familiar grammar communicates a clinical judgment this product is not
entitled to make, and adopting it would be RSK-11 arriving through visual design
rather than through a feature request.

This decision is recorded here and referenced from BIO_Model_Review; it binds the
Phase 7 implementation and is not re-litigable without a Decision entry.
