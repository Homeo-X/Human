---
doc: PRD_FR_RAG_and_Knowledge
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — RAG & Knowledge

## Purpose & Scope
Retrieval-grounded answering over a managed corpus. Boundary: generation
behavior/evals → PRD_FR_AI_Behavior (grounding invariants live there as
INV/EV rows); corpus file handling → Files & Media if scoped.

## Corpus Definition
| Source | Ingestion (manual/sync/crawl) | Freshness Requirement | Permissioned? | Chunking/Indexing Notes |
|---|---|---|---|---|

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-RAG-001 | Must | Answers cite retrieved sources; every claim attributable to a citation or marked as general knowledge | Given an answer, when a citation is opened, then it resolves to the exact passage | citations inline, not footnote-buried |
| FR-RAG-002 | Must | Retrieval respects the caller's permissions at query time — no leakage via snippets or embeddings | Given a restricted document, when another user asks, then neither content nor existence leaks | |
| FR-RAG-003 | Must | "Not in the corpus" is an honest first-class answer, never filled by fabrication (→ INV row in AI Behavior) | Given a question outside the corpus, when answered, then the answer says so and fabricates nothing | offer scope-widening or source-adding path |
| FR-RAG-004 | Must | Corpus management: add/remove/update sources with visible ingestion status; deletions propagate to index within <N> | Given a removed source, when queried after <N>, then it is neither retrieved nor cited | |
| FR-RAG-005 | Should | Freshness per Corpus table: stale sources flagged; answers show source date where recency matters | | |
| FR-RAG-006 | Could | Answer feedback (wrong source / missing source) feeding the EV set | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Source / Chunk / Index | RW | embeddings inherit source permissions; deletion path incl. vectors |

## States & Transitions
Source: added → ingesting → indexed | failed → (re-ingesting) → removed
(index purge confirmed).

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Conflicting sources answer differently | surface the conflict with both citations, don't average | FR-RAG-001 |
| Permission change not yet in index (lag) | query-time check is the gate; index lag ≤ declared bound | FR-RAG-002 |
| Empty corpus / no relevant chunks | FR-RAG-003 path, plus guided source-adding | FR-RAG-003 |
| Very large document (scale) | chunking degrades gracefully; ingestion status honest | FR-RAG-004 |
| Index rebuild in progress (dependency) | degraded declared mode, not silent partial answers | FR-RAG-004 |

## Dependencies
- PRD_FR_AI_Behavior (EV rows: citation accuracy, unsupported-claim rate), Permissions, Search (if both scoped: define which surface answers what)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Citation accuracy at EV bar | G-0X | per EV row |
| "Not in corpus" honesty violations | G-0X (trust) | 0 |

## Out of Scope for This Module
- Model/provider choice; embedding tech (Architecture)

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
