---
doc: PRD_FR_Payments_and_Billing
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Payments & Billing

## Purpose & Scope
Money movement: capture, refunds, receipts. Boundary: checkout UX is
PRD_FR_Cart_and_Checkout; recurring subscriptions → saas/PRD_FR_Subscription_Billing.

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-PAY-001 | Must | Supported methods per market (cards, wallets, local methods — enumerate) | Given a market from the matrix, when paying, then its listed methods are offered and work | |
| FR-PAY-002 | Must | Gateway integration; card data never touches our servers (tokenized) | Given a card payment, when processed, then only the gateway token is stored server-side | |
| FR-PAY-003 | Must | Refunds: full + partial; who may issue (→ Admin/Permissions) | Given an authorized partial refund, when issued, then the exact amount returns and is ledgered | |
| FR-PAY-004 | Must | Receipts/invoices with legally required fields per market | Given a completed payment, when the receipt renders, then all legally required fields are present | |
| FR-PAY-005 | Should | Chargeback/dispute handling workflow + evidence capture | | |
| FR-PAY-006 | Should | Payment retry / failure recovery messaging | | actionable, non-alarming copy |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Payment / Transaction | RW | gateway token only, PCI scope minimized |
| Refund / Dispute | RW | |

## States & Transitions
Payment: pending → authorized → captured → (partially_refunded ⇄) refunded | failed | disputed. Reconciliation source of truth: gateway.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Webhook arrives before redirect (or never) | state from webhook wins; polling fallback | FR-PAY-002 |
| Duplicate webhook delivery | idempotent processing | FR-PAY-002 |
| Refund exceeds remaining captured amount | blocked with reason | FR-PAY-003 |
| Currency rounding across gateway/tax/display | single rounding rule documented | FR-PAY-004 |

## Dependencies
- Integrations: payment gateway, tax engine · Modules: Checkout, Order Management, Notifications

## Success Metrics
| Metric | Traces To | Target |
|---|---|---|
| Payment success rate (by method) | revenue KPI | |
| Chargeback rate | risk KPI | below network thresholds |

## Out of Scope for This Module
-

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
