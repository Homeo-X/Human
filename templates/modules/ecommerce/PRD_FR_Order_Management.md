---
doc: PRD_FR_Order_Management
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Order Management & Fulfillment

## Purpose & Scope
Order lifecycle after placement: fulfillment, tracking, cancellations,
returns, and the automations that move orders between states. Boundary:
placement is Checkout; money movement is Payments.

## Order State Machine (the core artifact)
placed → confirmed → fulfilling → shipped → delivered → closed,
with branches: cancelled (until which state?), returned → refunded.
Define per transition: trigger (automation/operator/customer), notification
(→ NTF catalog), and inventory effect.

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-ORD-001 | Must | State machine enforced; illegal transitions rejected | Given an illegal transition request, when attempted, then it is rejected with the allowed transitions | |
| FR-ORD-002 | Must | Status automation from carrier/warehouse events | Given a carrier event, when received, then the order status updates without operator action | |
| FR-ORD-003 | Must | Customer cancellation within allowed window | Given an order inside its window, when the customer cancels, then it cancels and refund path starts | window shown up front |
| FR-ORD-004 | Should | Returns/RMA flow with reasons and refund linkage | | |
| FR-ORD-005 | Should | Shipment tracking surfaced to customer | | |
| FR-ORD-006 | Should | Inventory decrement/restock rules per transition | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| Order / Shipment / Return | RW | |
| InventoryLevel | RW | |

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Carrier event out of order (delivered before shipped) | reconcile rule | FR-ORD-002 |
| Partial shipment / split fulfillment | per-item states | FR-ORD-001 |
| Cancellation racing fulfillment | first committed state wins; refund path | FR-ORD-003 |
| Return received in damaged condition | operator disposition flow | FR-ORD-004 |

## Dependencies
- Integrations: carriers/3PL, warehouse · Modules: Payments, Notifications, Admin

## Success Metrics
| Metric | Traces To | Target |
|---|---|---|
| Orders auto-progressed without operator touch | ops-cost KPI | |
| WISMO ("where is my order") ticket rate | support-load KPI | |

## Out of Scope for This Module
-

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
