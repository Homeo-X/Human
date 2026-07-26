---
doc: PRD_FR_Content_Authoring
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Content Authoring & Publishing

## Purpose & Scope
Creating, editing, and publishing structured content (articles, pages,
posts, courses — type per product). Boundary: reader-side discovery →
Search/feeds; UGC policing → Moderation; media files → Files & Media.

## Content Model
| Content Type | Structure (fields/blocks) | Workflow (direct / draft-review-publish) | Versioned? |
|---|---|---|---|

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-CONT-001 | Must | Editor per content model (rich text/blocks), autosave with visible save state | Given a crash mid-edit, when reopening, then work within <N>s is recovered | never lose a paragraph |
| FR-CONT-002 | Must | Draft → publish lifecycle per workflow column; scheduled publishing if scoped | Given a scheduled publish, when its time arrives, then the item publishes or fails safe with notice | |
| FR-CONT-003 | Must | Revision history: view, diff, restore; published versions immutable snapshots | Given a restore, when confirmed, then a new revision is created, history intact | |
| FR-CONT-004 | Should | Collaborative editing policy: locking OR concurrent (pick; concurrent needs conflict UX) | | |
| FR-CONT-005 | Should | Preview: exact reader-rendering before publish, per surface (web/mobile) | | |
| FR-CONT-006 | Could | Templates/reusable blocks | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| ContentItem / ContentRevision | RW | revisions append-only |

## States & Transitions
ContentItem: draft → in_review? → scheduled? → published → updated
(new revision) → unpublished | archived. Who may trigger each → Permissions.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Publish with broken embeds/links | pre-publish check warns; publish not silently degraded | FR-CONT-002 |
| Two editors, lock policy (conflict) | lock visible with holder + takeover rule | FR-CONT-004 |
| Scheduled publish while author loses permission | fails safe: unpublished + author notified | FR-CONT-002 |
| Very long document (scale) | editor stays responsive; autosave chunked | FR-CONT-001 |
| Unpublish of widely-linked content | reader-side 410/redirect policy stated | FR-CONT-002 |

## Dependencies
- Files & Media, Permissions, Moderation (if UGC), Search (index on publish)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Draft → publish completion rate | G-0X | |
| Autosave data-loss reports | G-0X (trust) | 0 |

## Out of Scope for This Module
- Comments/community features unless scoped separately

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
