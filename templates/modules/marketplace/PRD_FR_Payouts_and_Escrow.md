---
doc: PRD_FR_Payouts_and_Escrow
tier: any
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Functional Requirements — Payouts & Escrow

## Purpose & Scope
Money OUT to sellers: split payments, held funds, releases, refund
interplay. Boundary: buyer-side charging → ecommerce Payments patterns;
who gets restricted → Trust & Safety.

## Money Flow Definition (the core artifact)
Buyer pays → platform holds (escrow window: <trigger for release —
delivery confirmation / N days / milestone>) → fee split (platform %,
processing) → seller payout (schedule, minimums). Diagram this before
writing requirements; every arrow is a requirement.

## Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-PAYT-001 | Must | Seller payout account setup via payment partner (KYC owned by partner); payout blocked until verified | Given unverified payout details, when a payout is due, then it is held with the fix path shown | verification status always visible |
| FR-PAYT-002 | Must | Escrow: funds held until the release trigger; early-release and hold-extension rules stated (BR refs) | Given delivery confirmed, when the window closes, then release is automatic and logged | |
| FR-PAYT-003 | Must | Fee computation per Money Flow, itemized to the seller before listing and on every payout | Given any payout, when itemized, then fees match the published Money Flow exactly | no surprise fees — ever |
| FR-PAYT-004 | Must | Refund/dispute interplay: refunds pull from escrow first, then clawback policy for released funds | Given a refund with funds in escrow, when executed, then escrow is debited before any clawback | |
| FR-PAYT-005 | Must | Payout ledger: every cent traceable buyer→escrow→fees→seller; exportable | Given any payout, when audited, then it reconciles to orders exactly | |
| FR-PAYT-006 | Should | Payout schedule options (instant-for-fee / weekly) per seller tier | | |

## Data Touched
| Entity | Read/Write | Notes |
|---|---|---|
| EscrowEntry / Payout / LedgerLine | RW | partner is money source of truth; ledger reconciles |

## States & Transitions
Escrow entry: held → released | refunded | disputed(frozen) → resolved.
Payout: scheduled → processing → paid | failed → retried.

## Edge Cases & Error States
| Scenario | Expected Behavior | FR Ref |
|---|---|---|
| Payout fails (bad bank details) | funds re-held; seller notified with fix path | FR-PAYT-001 |
| Refund after payout released | clawback per policy; negative balance handling stated | FR-PAYT-004 |
| Partner webhook missed → ledger drift | reconciliation job; partner wins, drift alarmed | FR-PAYT-005 |
| Seller suspended with funds in escrow | funds follow Trust & Safety disposition rules, never limbo | FR-PAYT-002 |
| Currency conversion in cross-border payout | rate source + timing stated; itemized | FR-PAYT-003 |

## Dependencies
- Integrations: payment partner (Connect-style) · Modules: Listings, Trust & Safety, ecommerce Payments (buyer side)

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Payout success rate (first attempt) | G-0X | |
| Ledger reconciliation breaks | G-0X (trust) | 0 |

## Out of Scope for This Module
- Tax withholding/1099s unless Business Rules require at launch

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
