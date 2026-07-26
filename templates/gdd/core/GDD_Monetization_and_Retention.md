---
doc: GDD_Monetization_and_Retention
tier: standard+   # excluded (with reason) for premium games per profile folds
version: 0.0.0
status: template
owner: pm
last_updated: —
---

# Monetization & Retention

## Model
Premium / F2P+cosmetics / F2P+progression / subscription / ads / DLC —
pick, and state how it serves rather than fights the pillars.

## Ethical Constraints (binding, not aspirational)
- No pay-to-win where skill is a pillar; no dark patterns (fake scarcity,
  confusion pricing); real-money price always visible in local currency
- Minors: spend limits, no targeted FOMO; loot-box stance per age-rating
  law exposure (→ compliance checklist decision — jurisdictions differ)
- Everything purchasable is previewable; refund posture stated

## Offer Surface
| Surface (store/season/bundle) | What's Sold | When Shown | Never Shown When |
|---|---|---|---|
_"Never shown when" is the anti-dark-pattern column: e.g. never after a
loss, never interrupting play._

## Platform & Legal Compliance
_Store rules bind the model: platform cut, IAP disclosure, loot-box odds
publication where law requires, regional restrictions. Cross-check the
compliance checklist decision and mobile/App_Store_Release if scoped._

## Retention Design
- Session hooks: why come back tomorrow (dailies? progression? social?) —
  each hook must serve a pillar, not just a DAU metric
- Churn re-entry: returning after a month must feel welcome, not punished
  (catch-up policy for seasonal content)

## Testable Requirements
| ID | Priority | Requirement | Acceptance Criteria | UX Considerations |
|---|---|---|---|---|
| FR-MON-001 | Must | Store per Offer Surface incl. every "never shown when" rule | Given a loss/failure moment, when it ends, then no offer is shown | |
| FR-MON-002 | Must | Ethical constraints enforced mechanically (spend limits, preview, local pricing) | Given a purchase flow, when audited, then preview, local pricing, and spend limits are enforced mechanically | |
| FR-MON-003 | Should | Retention hooks per design; absence-tolerant (no punishment stacking) | | |

## Edge Cases
| Scenario | Expected Behavior | Ref |
|---|---|---|
| Purchase interrupted (payment fails mid-grant) | idempotent grant; never charge-without-grant | FR-MON-001 |
| Refunded purchase already consumed | disposition policy stated | FR-MON-002 |
| Price change while store open | truth at confirm; no bait | FR-MON-002 |

## Success Metrics
| Metric | Traces To (KPI id) | Target |
|---|---|---|
| Conversion without dark-pattern surfaces | G-0X | |
| D1/D7/D30 retention | G-0X | |

## Open Questions
| Question | Owner | Needed By |
|---|---|---|
