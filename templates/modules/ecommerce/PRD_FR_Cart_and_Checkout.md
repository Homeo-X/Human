---
doc: PRD_FR_Cart_and_Checkout
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Cart & Checkout

## Purpose & Scope
From add-to-cart through order placement. Boundary: charging the money is
PRD_FR_Payments_and_Billing; post-order lifecycle is PRD_FR_Order_Management.

## User Stories
| As a… | I want… | So that… |
|---|---|---|
| shopper | to check out without creating an account | minimal friction |

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-CHK-001 | Must | Cart: add/remove/update, persistence (guest: N days device-scoped; account: cross-device) | Given items in a guest cart, when returning within N days on the same device, then the cart persists | |
| FR-CHK-002 | Must | Guest checkout + account checkout; post-purchase account offer | Given guest checkout completion, when offered an account, then declining still completes the order | |
| FR-CHK-003 | Must | Address + shipping method selection with priced options | Given an address, when shipping options load, then each shows its price before selection | |
| FR-CHK-004 | Must | Order review: itemized totals, tax, shipping — no surprise costs after this step | Given the review step, when displayed, then the total equals the final charge exactly | |
| FR-CHK-005 | Must | Order confirmation (screen + notification NTF ref) | Given payment success, when confirmed, then the order screen and notification show the order id | |
| FR-CHK-006 | Should | Promo/discount code entry (rules → Business Rules) | | |
| FR-CHK-007 | Could | Abandoned-cart recovery (consent rules apply) | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Cart / CartItem | RW | |
| Order | W (creates) | |

## States & Transitions
Cart: active → converted | expired. Order creation is atomic with inventory
reservation — define reservation window.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Item goes out of stock at checkout | explicit line-item error, not silent removal | FR-CHK-004 |
| Price changed between cart-add and review | show delta | FR-CHK-004 |
| Payment succeeds, order-write fails | idempotent creation; never charge without order | FR-CHK-005 |
| Guest cart merges into account cart at login | define merge policy | FR-CHK-001 |
| Double-click on Place Order | idempotency key | FR-CHK-005 |

## Dependencies
- Payments, Notifications, tax/shipping integrations

## Success Metrics
| Metric | Traces To | Target |
|---|---|---|
| Checkout completion rate | conversion KPI | |
| Checkout error rate | reliability KPI | |

## Out of Scope for This Module
-

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
