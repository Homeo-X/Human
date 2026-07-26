---
doc: TECH_API_Specification
tier: standard+
version: 1.0.0
status: draft
owner: architect
last_updated: 2026-07-26
---

# API Specification

_Greenfield: all endpoints are to be built. The read API is the product's
integration surface and is designed to be stable, cacheable, and citable._

## Conventions
- **Style:** REST over HTTP/JSON. Read endpoints are stateless and release-pinned.
- **Versioning:** `/v1/` in the path for the API contract; the *content* version
  is the release id, which is orthogonal. A response always states both.
- **Release pinning:** every read accepts `?release={id}`. Without it, the current
  release is used **and its id is returned in the response**, so a caller never
  has to guess what answered them.
- **Pagination:** cursor-based, `?cursor=&limit=` with `limit` capped at 200.
- **Timestamps:** RFC 3339, UTC.
- **IDs:** entity ids are external ontology terms or `HOX:` locals and appear
  verbatim in paths, percent-encoded.
- **Every response carrying a claim carries its evidence class.** There is no
  "compact" representation that omits it — the grade is not optional metadata.

## Authentication & Authorization
| Surface | Auth |
|---|---|
| Read API | **none.** The reference model is public (FR-CUR-007) |
| Curation API | bearer token from the identity provider; role and competence scope enforced per request |
| Personal API (Phase 7) | bearer token scoped to one individual; no cross-individual read exists at any role |

The read API has no authentication because it has no privileged data. Adding auth
would be theatre and would break the public-good posture that makes citation
useful.

## Resources & Endpoints

### Entity
| Method | Path | Description | Auth | FR Refs |
|---|---|---|---|---|
| GET | `/v1/entities/{id}` | entity with class, level, mode, compilation status, spatial identity, and claim summary | none | FR-ONTO-001, FR-ONTO-006 |
| GET | `/v1/entities/{id}/relations` | typed relations; `?type=&direction=&level=` | none | FR-REL-010 |
| GET | `/v1/entities/{id}/claims` | claims; `?class=&predicate=` | none | FR-EVID-002 |
| GET | `/v1/entities/{id}/unknowns` | recorded UNKNOWN claims and unrepresented aspects | none | FR-EVID-005, FR-SRCH-004 |
| GET | `/v1/entities/{id}/geometry` | geometry references by level and licence tier | none | FR-SPAT-001, FR-SPAT-010 |
| GET | `/v1/entities/{id}/lineage` | history across releases | none | FR-VER-008 |

A retired id returns **HTTP 301** to its successor with a tombstone body — not
404, because the caller's reference was valid and deserves an answer
(FR-ONTO-004, FR-VER-007).

### Claim
| Method | Path | Description | Auth | FR Refs |
|---|---|---|---|---|
| GET | `/v1/claims/{id}` | the claim | none | FR-EVID-001 |
| GET | `/v1/claims/{id}/provenance` | the complete provenance record | none | FR-EVID-010 |
| GET | `/v1/claims/{id}/conflicts` | conflicting claims with their sources | none | FR-EVID-006 |

### Scale
| Method | Path | Description | Auth | FR Refs |
|---|---|---|---|---|
| GET | `/v1/levels` | all eleven SCL contracts | none | FR-SCAL-001 |
| GET | `/v1/levels/{n}` | one level contract including its resolution limit | none | FR-SCAL-001 |
| GET | `/v1/coverage` | declared versus populated per subsystem per level | none | FR-SCAL-010 |
| GET | `/v1/entities/{id}/descend` | the next level down, **or the terminal answer** | none | FR-SCAL-003 |

`/descend` past declared depth returns **HTTP 200 with a terminal-answer body**,
not 404. The model has an answer — "this is not represented, and here is why" —
and an error status would misrepresent a designed response as a fault.

### Process
| Method | Path | Description | Auth | FR Refs |
|---|---|---|---|---|
| GET | `/v1/processes` | the BPR register with representation status | none | FR-PHYS-001 |
| GET | `/v1/processes/{id}` | full specification | none | FR-PHYS-002 |
| GET | `/v1/processes/unmodelled` | named-but-not-modelled, with reasons | none | FR-PHYS-010 |
| POST | `/v1/processes/{id}/runs` | execute (Phase 6; executable processes only) | none | FR-SIM-001 |
| GET | `/v1/runs/{id}` | run record with parameters, limits, and release | none | FR-SIM-003 |

A run request against a non-executable process returns **HTTP 409** with the
unmet gate conditions listed (FR-SIM-001).

### Search and retrieval
| Method | Path | Description | Auth | FR Refs |
|---|---|---|---|---|
| GET | `/v1/search` | `?q=&mode=name\|function\|clinical\|spatial\|negative` | none | FR-SRCH-001…004 |
| POST | `/v1/query` | structured graph query | none | FR-SRCH-005 |
| POST | `/v1/ask` | grounded natural-language response | none | FR-RETR-001 |
| GET | `/v1/export` | scoped export with provenance and licence manifest | none | FR-SRCH-009, FR-VER-009 |

`/ask` returns per-assertion claim ids and classes. When the groundedness guard
refuses, the response is **HTTP 200 with a refusal body** stating why — a refusal
is a valid answer, and 4xx would imply the caller erred.

### Release
| Method | Path | Description | Auth | FR Refs |
|---|---|---|---|---|
| GET | `/v1/releases` | published releases | none | FR-VER-001 |
| GET | `/v1/releases/{id}/manifest` | sources, licences, tiers, authority pins, validation result | none | FR-VER-003, FR-VER-004 |
| GET | `/v1/releases/{a}/diff/{b}` | additions, removals, retypings, class changes | none | FR-VER-011 |

### Curation (authenticated)
| Method | Path | Description | Auth | FR Refs |
|---|---|---|---|---|
| GET | `/v1/curation/queue` | proposals within the caller's competence scope | curator | FR-CUR-002, FR-CUR-004 |
| POST | `/v1/curation/tasks/{id}/review` | accept or reject with a reason | curator | FR-CUR-001, FR-CUR-003 |
| POST | `/v1/curation/tasks/{id}/adjudicate` | conflict adjudication (two reviewers) | reviewer | FR-CUR-005 |
| POST | `/v1/releases` | publish (re-authentication required) | operator | FR-VER-005 |

### Personal (Phase 7, authenticated)
| Method | Path | Description | Auth | FR Refs |
|---|---|---|---|---|
| GET | `/v1/me/overlay` | the overlay and its pinned release | individual | FR-PERS-002 |
| POST | `/v1/me/overlay/values` | add a value with full provenance | individual | FR-PERS-003 |
| GET | `/v1/me/model/{entity-id}` | reference ⊕ overlay, with propagation stated | individual | FR-PERS-005 |
| DELETE | `/v1/me` | complete deletion, verifiable | individual | FR-PERS-008 |

`POST /v1/me/overlay/values` returns **HTTP 422** listing missing provenance
fields when incomplete (INV-09), and **HTTP 403** if the target path resolves
outside the overlay namespace (INV-08).

## Error Handling
Standard shape:

```json
{ "error": { "code": "DEPTH_EXCEEDED", "message": "…",
             "detail": { "subsystem": "endocrine", "declared_level": 3,
                         "requested_level": 7 },
             "correlation_id": "…", "release": "…" } }
```

| Code | HTTP | When |
|---|---|---|
| `ENTITY_RETIRED` | 301 | retired id, successor supplied |
| `NOT_REPRESENTED` | 200 | descend past declared depth — a designed answer, not an error |
| `UNGROUNDED_REFUSED` | 200 | the groundedness guard refused; body states why |
| `DEPTH_EXCEEDED` | 422 | a write targeting a level beyond declared depth |
| `INCOMPLETE_PROVENANCE` | 422 | claim or overlay value missing required fields |
| `UNIT_REQUIRED` | 422 | a quantity submitted without a UCUM unit |
| `PROCESS_NOT_EXECUTABLE` | 409 | run requested on a non-executable process; unmet conditions listed |
| `TIER_VIOLATION` | 409 | an export or reference crossing licence tiers |
| `EVIDENCE_CLASS_FORBIDDEN` | 403 | a non-human actor attempting EVC-1 or EVC-2 |
| `REFERENCE_WRITE_REFUSED` | 403 | an overlay operation targeting the reference |
| `OUT_OF_COMPETENCE_SCOPE` | 403 | a reviewer acting outside their declared scope |
| `DEGRADED` | 206 | partial results with the degradation stated (NFR-012) |

The status-code choices encode the product's posture: **the model's limits are
200s, and only genuine caller errors are 4xx.** A system that returns 404 for "we
do not model that" teaches users that its honesty is a malfunction.

## Rate Limits & Idempotency
- Read: 600 requests/minute per IP; `/ask` 20/minute per IP (it is expensive).
- Curation and personal: 120/minute per token.
- Mutating endpoints require an `Idempotency-Key`. Proposal submission, review
  decisions, overlay value writes, and release publication are all idempotent by
  key — a retried review must never double-apply.

## FR → API Coverage Check
| FR Module | Covered By |
|---|---|
| ONTO | `/entities/*`, tombstone 301 behaviour |
| REL | `/entities/{id}/relations` |
| EVID | `/claims/*`, `/entities/{id}/unknowns` |
| SCAL | `/levels/*`, `/coverage`, `/descend` |
| SPAT | `/entities/{id}/geometry` |
| NAV | **client-only** — navigation state is a viewer concern; every state maps to an addressable read call |
| SRCH | `/search`, `/query`, `/export` |
| PHYS | `/processes/*` |
| SIM | `/processes/{id}/runs`, `/runs/{id}` |
| PERS | `/me/*` (Phase 7) |
| VALD | **no public surface** — validation runs in the build pipeline; results are exposed through `/releases/{id}/manifest` |
| RETR | `/ask` |
| AGD | **internal only** — agents act through the curation API as service identities; no public agent endpoint exists, deliberately |
| CUR | `/curation/*` |
| VER | `/releases/*` |

Every module is covered, client-only, or explicitly internal. None is unaccounted
for.
