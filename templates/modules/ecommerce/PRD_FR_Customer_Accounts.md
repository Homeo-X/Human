---
doc: PRD_FR_Customer_Accounts
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Customer Accounts

## Purpose & Scope
Authenticated shopper self-service area. Boundary: credentials/sessions are
PRD_FR_Authentication; order state itself is PRD_FR_Order_Management.

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-ACCT-001 | Must | Profile management (contact info, communication prefs → Notifications) | Given profile edits, when saved, then changes persist and communication prefs propagate to Notifications | |
| FR-ACCT-002 | Must | Order history with status, detail view, reorder | Given past orders, when history opens, then each shows current status and a working reorder action | |
| FR-ACCT-003 | Should | Saved addresses; validation per market | | |
| FR-ACCT-004 | Should | Saved payment methods (gateway-tokenized) | | |
| FR-ACCT-005 | Could | Wishlist / saved items | | |
| FR-ACCT-006 | Could | Loyalty/rewards (rules → Business Rules) | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Customer profile / Address / SavedPaymentMethod | RW | |
| Order | R | |

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Guest orders claimed after account creation | match policy (email verification) | FR-ACCT-002 |
| Saved card expired | prompt at next checkout, not nag | FR-ACCT-004 |
| Account deletion with open orders | block or define handling | FR-ACCT-001 |

## Dependencies
- Authentication, Order Management, Payments

## Success Metrics
| Metric | Traces To | Target |
|---|---|---|
| Repeat-purchase rate for account holders | retention KPI | |

## Out of Scope for This Module
-

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
