---
doc: PRD_Non_Functional_Requirements
tier: standard+   # at Light, fold the applicable rows into TECH_Implementation_Notes
version: 0.0.0
status: template
owner: architect
last_updated: —
---

# Non-Functional Requirements

_Every target needs a number and a measurement method; "fast" and "scalable"
are not requirements. Scale targets to the product's actual stated usage —
an internal tool for 40 support agents does not need 99.99% uptime._

## NFR Register
| ID | Category | Requirement (with number) | Measured By | Priority |
|---|---|---|---|---|
| NFR-001 | Performance | | | |

## Category prompts (delete unused)
- **Performance** — latency percentiles (p50/p95) per key action, cold start, payload budgets
- **Scalability** — concurrent users, data volume growth, burst behavior
- **Availability** — uptime target, maintenance windows, degradation modes
- **Accessibility** — WCAG level, screen-reader and keyboard coverage
- **Platform support** — browsers/OS versions/device classes actually required
- **Localization / i18n** — languages, RTL, locale formats (if scoped in)
- **Offline / connectivity** — behavior on loss, sync/conflict policy (mobile especially)
- **Observability** — logging, tracing, alerting expectations
- **Cost** — infra or per-request cost ceilings (AI products especially: token budgets)
- **Maintainability** — deploy frequency, rollback time
