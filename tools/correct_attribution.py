#!/usr/bin/env python3
"""Correct eighteen claims that name a human reviewer who does not exist.

D-013 recorded the seed corpus being attributed to a fabricated
`human:reviewer-seed-01`, and fixed it. Three days later this project shipped
nine cardiovascular claims attributed to `human:reviewer-cardio-01` and nine
regional claims attributed to `human:anatomy-reviewer-01`. Neither reviewer
exists. Thirteen of those claims sit at EVC-2 — a class
`BIO_Evidence_and_Provenance` says the canonical graph never admits unreviewed,
and that BR-002 forbids any automated actor from assigning.

So the same defect was committed twice, the second time by the process that
wrote the rule. It is corrected here rather than quietly, and the audit file
this produces is the record.

**What the correction does not do** is claim the biology is weaker than it is.
`CLM:heart-function-pump` cites Gray's and Guyton; the evidence really does
support EVC-2. What was missing is a curator, not a source. So each claim keeps
the agent's assessment in `proposed_class` and drops its asserted
`evidence_class` to what an automated actor may assert. The gap between the two
columns is the review backlog, per claim — the first time RSK-02 has been
expressible as a list rather than a worry.

    python3 tools/correct_attribution.py            # dry run
    python3 tools/correct_attribution.py --write
"""
from __future__ import annotations

import json
import os
import sys

CARDIO = 'ontology/cardiovascular/claims.json'
REGIONS = 'ontology/regions/claims.json'
AUDIT = 'ontology/ATTRIBUTION_CORRECTION.json'

# The actor each set is honestly attributable to. These are the agents that
# actually produced the content; no human is named because none was involved.
ACTORS = {CARDIO: 'agent:evidence', REGIONS: 'agent:anatomy'}

FABRICATED = ('human:reviewer-cardio-01', 'human:anatomy-reviewer-01')

# Where an EVC-2 assessment lands once it is capped. EVC-4 (APPROXIMATED) is
# chosen per claim rather than by rule, and it fits every one of these: each is
# a deliberate simplification of something known to be more complex, which is
# the ladder's own wording, and each claim's `limitations` field already says
# so. `reference textbook` and `primary research` are both admissible at EVC-4,
# so no claim needs its source type changed.
CAPPED = 'EVC-4'
CAP_REASON = (
    'Assessed at EVC-2 by an automated actor from two independent admissible '
    'sources. BR-002 forbids an agent assigning EVC-1 or EVC-2, and '
    'BIO_Evidence_and_Provenance §Pipeline says the canonical graph admits '
    'nothing unreviewed at those classes. Asserted at EVC-4 (a deliberate '
    'simplification, which each claim\'s limitations field already states) '
    'with the EVC-2 assessment retained as proposed_class pending curator '
    'review.')


def correct(write: bool) -> int:
    changes = []
    for path in (CARDIO, REGIONS):
        actor = ACTORS[path]
        with open(path, encoding='utf-8') as fh:
            claims = json.load(fh)
        for claim in claims:
            before = dict(claim)
            if claim.get('assigned_by') not in FABRICATED:
                continue
            claim['assigned_by'] = actor
            claim['review_state'] = 'provisional'
            if claim['evidence_class'] in ('EVC-1', 'EVC-2'):
                claim['proposed_class'] = claim['evidence_class']
                claim['evidence_class'] = CAPPED
            changes.append({
                'claim': claim['id'], 'file': path,
                'was_assigned_by': before['assigned_by'],
                'now_assigned_by': claim['assigned_by'],
                'was_class': before['evidence_class'],
                'now_class': claim['evidence_class'],
                'proposed_class': claim.get('proposed_class'),
                'reason': (CAP_REASON if before['evidence_class']
                           in ('EVC-1', 'EVC-2') else
                           'Class unchanged — already within the class an '
                           'automated actor may assert. Only the fabricated '
                           'reviewer attribution was corrected.'),
            })
        if write:
            _dump(path, claims)

    capped = [c for c in changes if c['proposed_class']]
    print(f'{len(changes)} claims corrected, {len(capped)} capped from '
          f'EVC-2 to {CAPPED}')
    for row in changes:
        arrow = (f"{row['was_class']} -> {row['now_class']}"
                 if row['was_class'] != row['now_class'] else row['now_class'])
        print(f"  {row['claim']:<52} {arrow:<16} {row['now_assigned_by']}")

    if not write:
        print('\ndry run — nothing written. Re-run with --write.')
        return 0

    _dump(AUDIT, {
        'note': ('Eighteen claims named a human reviewer who does not exist. '
                 'This file records every field changed and why (D-017). It is '
                 'append-only in spirit: a later correction adds a record, it '
                 'does not edit this one.'),
        'decision': 'D-017',
        'corrected_on': '2026-07-27',
        'claims_corrected': len(changes),
        'claims_capped': len(capped),
        'review_backlog': [
            {'claim': c['claim'], 'asserted': c['now_class'],
             'assessed': c['proposed_class']} for c in capped],
        'changes': changes,
    })
    print(f'\nwrote {AUDIT} with {len(changes)} records')
    return 0


def _dump(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    sys.exit(correct('--write' in sys.argv))
