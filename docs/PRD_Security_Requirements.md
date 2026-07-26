---
doc: PRD_Security_Requirements
tier: standard+
version: 1.0.0
status: draft
owner: architect
last_updated: 2026-07-26
---

# Security Requirements

_This product has an unusual security shape: the primary asset is public and
should stay public, the primary threat is corruption rather than exfiltration,
and the one genuinely sensitive dataset does not exist until Phase 7._

## Threat Snapshot
| Threat | Actor | Surface | Mitigation Ref |
|---|---|---|---|
| **Silent corruption of canonical content** — an incorrect claim, relation, or grade admitted and then trusted | a compromised curator account, a confused agent, or a well-meaning contributor | curation queue, agent proposal path | BR-009 human approval, competence scoping (FR-CUR-004), append-only lineage (FR-VER-008), sampled source-aptness gate |
| **Prompt injection through source material** — a document containing instruction-shaped text read by an agent | anyone who can get a document into an ingest path | TOOL-02 source fetch, retrieval corpus | FR-AGD-005 tool outputs are data; EV-AGD-003 injection resistance; autonomy enforced by the runtime, not the prompt |
| **Individual health data exposure** (Phase 7) | external attacker, or an insider with database access | overlay store, logs, agent run records, exports | NFR-030, NFR-031, structural separation (D-004), deny-by-default access scoped to the individual |
| **Licence-obligation leak** — share-alike content escaping its tier into a build or export that does not carry the obligation | no attacker required; this is an accident | asset pipeline, export path | INV-11, D-003 tiering, FR-VER-009 tier-split-or-refuse |
| **Reference-model tampering via overlay** (Phase 7) | a compromised personalization path | overlay resolver | INV-08, AGT-9 holds no credential that could write to the reference, EV-AGD-004 adversarial test |

Note what is *not* on this list: data exfiltration of the reference model. It is
published deliberately, and treating it as a secret would be security theatre.

## Authentication & Session Security
- **Readers are unauthenticated.** The reference model is a public good and
  requires no account (FR-CUR-007). This is a deliberate posture, not an
  oversight.
- **Curators and operators authenticate** via an external identity provider with
  MFA required. Session lifetime 8 hours; re-authentication required for
  publication (TOOL-08) regardless of session age.
- **Individuals (Phase 7)** authenticate with MFA available and strongly
  encouraged; session lifetime 1 hour for any surface exposing overlay data.
- **Agents** hold service identities with no interactive credential and no
  ability to authenticate as a person.

## Authorization
Enforcement at the API layer **and** in the store — the two are not redundant,
because the store-level constraint is what makes INV-08 structural rather than
procedural.

Deny-by-default. Every role's permissions are enumerated; there is no
"administrator" role that can bypass BR-007 (overlay-to-reference writes) or
BR-002 (agent EVC-1/EVC-2 assignment). The absence of a superuser override is a
security property here, not an inconvenience: the guarantees this product sells
are exactly the ones a superuser would be able to break.

| Role | May | May Not |
|---|---|---|
| Reader (anonymous) | read the reference model, query, export within licence tier | write anything |
| Curator | propose, review and accept within competence scope | publish releases, assign outside scope, write overlays |
| Reviewer (domain) | assign EVC-1/EVC-2 within scope, adjudicate | publish, alter lineage |
| Operator | publish releases, manage queues and throttles | assign evidence classes, alter claims |
| Agent (service) | read, propose; per-agent tool cells in FR-AGD Facet 5 | anything at confirm or forbidden autonomy |
| Individual (Phase 7) | read and write own overlay, delete own data | read others' overlays, write the reference |

## Data Protection
- TLS 1.3 in transit; encryption at rest for all stores.
- Individual data (Phase 7) is stored in a **physically separate store** from the
  reference model with separate credentials, so that reference-model read access
  conveys no path to individual data.
- Secrets in a managed secret store, never in configuration files, never in agent
  run records.
- PII and health-data handling follows the classification table in
  PRD_Data_Overview: `Individual`, `Overlay`, and `OverlayValue` are the only
  sensitive classes and are treated as health data regardless of deployment
  jurisdiction.

## Compliance
| Regime | Applies? | What binds | Where satisfied |
|---|---|---|---|
| GDPR (and equivalents) | **yes, from Phase 7** | lawful basis, data minimization, right of access, right of erasure, portability | deletion path (FR-PERS-008), export (FR-PERS-012), consent per BR-008 |
| HIPAA | **only if deployed by a covered entity** — not by default | BAA, safeguards, audit | not assumed; a covered-entity deployment is a separate scope decision with its own review |
| Medical device regulation (FDA, MDR) | **no — by construction** | would bind if the product made diagnostic or treatment claims | BR-019 has no exceptions; RSK-11 tracks the pressure to add one |
| Source licence obligations | **yes, now** | attribution, share-alike propagation | D-003 tiering, INV-11, release manifests |

The medical-device row is the load-bearing one. A single "which condition is
this" feature would move this product into a regulatory regime it is not built,
tested, staffed, or funded for. That is why BR-019 is a hard constraint rather
than a policy.

## Abuse Prevention
- Rate limiting per client class on read, query, and retrieval surfaces.
- Input validation at every ingest boundary; malformed content is rejected, never
  partially admitted.
- **For AI surfaces:** prompt-injection handling per FR-AGD-005 — tool outputs are
  data and cannot escalate autonomy. Output filtering is not the primary control;
  the primary control is that ungrounded assertions are refused (INV-14), which
  means an injection that produces fluent text still produces nothing renderable.
- Tool-call limits per agent run (NFR-025), with graceful stop rather than silent
  truncation.
- Curation queue throttling (BR-023) — an attacker who could flood the proposal
  queue would be attacking reviewer attention, which is the scarcest resource
  here.

## Audit Logging
Knowledge lineage *is* the audit trail for content (MANIFEST fold record); this
section covers what lineage does not.

| Event | Data Captured | Retention | Access |
|---|---|---|---|
| Canonical content change | Approval record: reviewer, scope, proposal derivation, timestamp | permanent, append-only | curators, operators |
| Release publication | operator, release id, validation result, manifest hash | permanent | public |
| Evidence class assignment or change | claim id, old and new class, evidence cited, reviewer | permanent | public |
| Agent run | Steps, ToolCalls, Observations, Failures | 180 days, then aggregated | operators |
| Authentication and authorization failure | actor, surface, timestamp — never the attempted payload | 90 days | operators |
| Individual data access (Phase 7) | who, what, when — **never the values** | 1 year | the individual, and operators on request |
| Individual data deletion | request, completion, reference-hash verification | permanent — the fact, never the data | the individual |

Two rules govern the whole table: **no individual data ever appears in a log**
(NFR-031), and **audit records are append-only** — an audit trail that can be
edited by the people it audits is decorative.
