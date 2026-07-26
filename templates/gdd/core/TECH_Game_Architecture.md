---
doc: TECH_Game_Architecture
tier: standard+   # game profile: use INSTEAD of TECH_System_Architecture (online services may still add it)
version: 0.0.0
status: template
owner: architect
last_updated: —
---

# Game Technical Architecture

_Brownfield runs: current-state facts cite their grounding source (tool +
date, per INTEGRATIONS.md); to-be-built content is explicitly marked._

## Engine & Platform Decision
| Question | Decision | Rationale (→ Decision Log entry) |
|---|---|---|
| Engine (Unity/Unreal/Godot/custom) | | team skill × genre needs × platform targets × license |
| Language/scripting split | | |
| Target platforms + min spec | | |
| Store/platform certification path (TRC/XR/cert) | | |

## Frame Budget (the load-bearing table)
_Per platform, per target frame rate. The art direction and content scope
are constrained by this table, not vice versa._
| Platform | Target | Frame Budget | Sim/Logic | Render | Physics | Audio | Headroom |
|---|---|---|---|---|---|---|---|
| | 60fps | 16.6ms | | | | | ≥10% |

## Runtime Architecture
- Main loop structure: update order, fixed-vs-variable timestep, where
  determinism matters (replays/netcode → games/Multiplayer sync model)
- State management: game state machine (boot → menu → loading → play →
  pause), scene/level streaming strategy
- Data-driven design: where tuning values live (→ FR-SYS-002), hot-reload
  in dev builds

## Asset Pipeline
| Stage | Tool | Output | Validation Gate |
|---|---|---|---|
| Source → import | | | naming/budget lint |
| Build → cook/pack | | | size budget per platform |
- Build size budgets: initial download / full install / patch delta per
  platform (store rules constrain these — cross-check mobile/App_Store_
  Release if scoped)

## Save, Config & Platform Services Interfaces
Pointers, not duplication: save model → games/Save_and_Progression;
platform services → games/Platform_Services; remote config →
games/LiveOps. This doc owns the INTERFACES those modules bind to.

## Performance Strategy
- Content budgets derived from frame budget (poly/texture/draw-call
  ceilings per asset class → feeds Art §technical constraints)
- Profiling cadence: per-milestone on min-spec hardware, gate in DoD
- Loading targets: cold boot ≤ <N>s, level load ≤ <N>s (NFR rows)

## Environments, Build & Patch
- Build flavors (dev/profiling/release), CI per platform, patch strategy
  and cadence, version-compatibility window (→ version-window rules in mobile/App_Store_Release if scoped)

## Consistency Checks
Every tuning value named in GDD_Systems_Design resolves to a data asset;
every frame-budget row has a profiling report per milestone; every
platform target has a cert-requirements checklist started.
