---
doc: PRD_Non_Functional_Requirements
tier: standard+
version: 1.0.0
status: draft
owner: architect
last_updated: 2026-07-26
---

# Non-Functional Requirements

_Every target has a number and a measurement method. Targets are scaled to the
stated usage — an educational and research reference used by classes and
individuals, not a consumer product at internet scale._

## NFR Register
| ID | Category | Requirement (with number) | Measured By | Priority |
|---|---|---|---|---|
| NFR-001 | Performance | Entity view resolves in p95 ≤ 300 ms, p50 ≤ 100 ms, for an entity with ≤ 200 relations, excluding geometry download | server-side timing histogram per release | Must |
| NFR-002 | Performance | Graph query over ≤ 3 traversal hops returns p95 ≤ 800 ms at Phase 3 volumetrics | query benchmark suite in CI | Must |
| NFR-003 | Performance | Negative-space query returns p95 ≤ 1.5 s — it aggregates across levels and is expected to be slower, but must not be so slow that users stop asking | benchmark suite | Should |
| NFR-004 | Performance | Semantic zoom transition completes in ≤ 400 ms including the level announcement | client instrumentation | Must |
| NFR-005 | Rendering | L0–L3 whole-body scene sustains ≥ 30 fps on mid-range hardware (integrated GPU, 4-core CPU, 8 GB RAM, 2020-era baseline) | automated frame-time capture on the reference device profile | Must |
| NFR-006 | Rendering | Detail degrades before frame rate, and degradation is visible to the user, never silent | frame-time capture plus a UI assertion in the test suite | Must |
| NFR-007 | Rendering | Initial scene interactive within 5 s on a 10 Mbit connection; progressive geometry load thereafter | synthetic network test | Should |
| NFR-008 | Scalability | Graph and claim store support Phase 5 volumetrics (10⁵ entities, 10⁶ claims) without architectural change | load test at 10× Phase 3 volumes | Must |
| NFR-009 | Scalability | Validation harness completes a full run in ≤ 10 min at Phase 3 volumetrics | CI timing | Must |
| NFR-010 | Scalability | Commit-time partial validation completes in ≤ 5 s for a typical change | local timing; **if exceeded, curators disable the hook and the guarantee evaporates** (RSK, FR-VALD-008) | Must |
| NFR-011 | Availability | 99.5% monthly for the read surface; no availability target for curation, which tolerates downtime | uptime monitoring | Should |
| NFR-012 | Availability | Degraded mode: when the language model or index is unavailable, structured search and navigation continue, and the degradation is stated | chaos test per release | Must |
| NFR-013 | Offline | The full L0–L3 reference model plus geometry for one selected build tier runs offline after a one-time download of ≤ 2 GB | offline test on the reference device profile | Must |
| NFR-014 | Offline | An offline session pins its release and states which release it is running | functional test | Must |
| NFR-015 | Accessibility | WCAG 2.2 AA for all non-spatial surfaces | automated audit plus manual review per release | Must |
| NFR-016 | Accessibility | Every spatial surface has a non-spatial equivalent path: any entity reachable in 3D is reachable and fully described through keyboard navigation and screen reader | manual audit with an assistive-technology user per phase | Must |
| NFR-017 | Accessibility | Reduced-motion mode disables camera animation and process animation without loss of information | functional test | Must |
| NFR-018 | Accessibility | Colour is never the sole carrier of evidence class, compilation status, or representation kind | design audit per release | Must |
| NFR-019 | Platform | WebGL2 baseline; WebGPU used when available but never required | browser matrix test | Must |
| NFR-020 | Platform | Current and previous major versions of Chrome, Firefox, Safari, Edge | browser matrix test | Must |
| NFR-021 | i18n | Terminology localization resolves through nomenclature authorities, not string tables; a locale without an authority falls back to Latin, stated | functional test per locale | Should |
| NFR-022 | Observability | Every KPI (G-01…G-07) is computed from recorded data, never asserted; the computation is reproducible from a release | KPI recomputation from a release artifact | Must |
| NFR-023 | Observability | Validation findings, queue depth, review throughput, and EV results are recorded per release and queryable | operator view | Must |
| NFR-024 | Cost | Retrieval response ≤ 8000 tokens and ≤ 6 s p95 wall-clock; exceeding degrades to a shorter grounded answer, never a truncated one | per-response accounting | Must |
| NFR-025 | Cost | Agent run ceilings: ≤ 50 tool calls, ≤ 100 000 tokens, ≤ 10 min wall-clock per run; graceful stop at each | run record accounting | Must |
| NFR-026 | Cost | Storage: reference model excluding geometry ≤ 5 GB at Phase 5 | release artifact size | Should |
| NFR-027 | Reproducibility | A release rebuilds byte-identically from a clean checkout at its pinned inputs | release rebuild job every release | Must |
| NFR-028 | Reproducibility | The retrieval step of any response reproduces exactly given the same query and release; generation may vary, retrieval may not | response replay test | Must |
| NFR-029 | Maintainability | Framework deltas re-apply to a new upstream version in ≤ 1 day of work | tracked on each upstream update (UPSTREAM.md) | Should |
| NFR-030 | Privacy | Individual data is encrypted at rest and in transit; deletion completes within 24 h and is verifiable by the individual | deletion test; the reference release hash is unchanged after deletion | Must |
| NFR-031 | Security | No individual data appears in logs, traces, error reports, or agent run records | log audit per release | Must |

## Category Notes

**Performance targets are deliberately unambitious.** This is a reference tool
used in study sessions and classrooms, not a real-time application. Chasing
lower latency would trade against the thing that actually matters here —
resolving a claim's full provenance on every view, which is inherently more work
than rendering a label.

**NFR-010 is the one target where missing it destroys a guarantee rather than
degrading an experience.** A commit hook slower than about five seconds gets
disabled, and once disabled, invariant violations reach CI instead of the
author's editor, where they are an order of magnitude more expensive to fix.

**NFR-016 is not a compliance row.** A 3D anatomical explorer is close to the
worst case for assistive technology, and "we added ARIA labels" is not an answer.
The requirement is a genuinely equivalent non-spatial path — every entity
reachable, every relation traversable, every evidence class announced. This is
expensive and it is a Must, because a model of the human body that excludes
disabled users is a poor advertisement for its own subject matter.

**NFR-018 exists because evidence class is the product's core signal.** Encoding
it in colour alone would make the honesty machinery invisible to a substantial
fraction of users — which is RSK-09 arriving through an accessibility failure
rather than a design one.

**Cost budgets (NFR-024, NFR-025) are referenced from PRD_FR_Knowledge_Retrieval
and PRD_FR_Agent_Definition rather than duplicated there**, per AGENTS.md §3.
