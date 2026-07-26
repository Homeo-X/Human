---
doc: PRD_FR_Listings_and_Sellers
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Listings & Sellers

## Purpose & Scope
The supply side of a two-sided market: seller onboarding and the listing
lifecycle. Boundary: buying → ecommerce cart/checkout patterns; money out
→ Payouts & Escrow; disputes/quality → Trust & Safety.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| new seller | to list quickly with the minimum viable listing | supply exists before polish |
| marketplace | quality gates on listings | buyers trust search results |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-LIST-001 | Must | Seller onboarding: identity/eligibility per Business Rules (KYC tier if payouts), seller profile | Given incomplete KYC where required, when publishing, then blocked with named steps | |
| FR-LIST-002 | Must | Listing CRUD with required-field policy per category; draft → published lifecycle | Given required fields missing, when publishing, then publish is blocked with the fields named | |
| FR-LIST-003 | Must | Listing quality gates: media minimums, prohibited-content rules (→ Moderation if scoped) | Given a prohibited term/category, when publishing, then rejected with the rule cited | rejection is educational, not punitive |
| FR-LIST-004 | Must | Availability truth: stock/calendar/capacity model per listing type; overselling policy | Given zero availability, when a buyer views the listing, then purchase is blocked honestly | |
| FR-LIST-005 | Should | Seller dashboard: views, conversion, pending actions | | |
| FR-LIST-006 | Could | Bulk listing tools / import | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Seller / Listing | RW | listing carries category-typed attributes |

## States & Transitions
Listing: draft → in_review? → published → paused | sold_out → archived |
removed (policy). Seller: onboarding → active → restricted → suspended.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Seller suspended with live listings | listings paused, open orders honored per Trust rules | FR-LIST-001 |
| Category recategorized under a listing | attributes migrate or listing flagged for edit | FR-LIST-002 |
| Two buyers race the last unit (conflict) | first committed wins; second gets honest sold-out | FR-LIST-004 |
| Empty marketplace (cold start) | seller-side empty states + supply-seeding plan (Risks) | FR-LIST-002 |

## Dependencies
- Payouts & Escrow, Trust & Safety, Search (listing discovery), Files & Media (listing media)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Time from signup to first published listing | G-0X | |
| Listing rejection rate (quality gate) | G-0X | trending ↓ |

## Out of Scope for This Module
- Pricing strategy tooling; ads/promotion products

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
