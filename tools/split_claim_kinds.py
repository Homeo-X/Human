#!/usr/bin/env python3
"""Separate definitions from findings across the whole substrate (D-021).

156 of 165 claims — 94% — were definitions graded on the biological evidence
ladder. "The heart is a myogenic muscular circulatory organ" was carried as
APPROXIMATED *evidence*, on the same register as a measured sarcomere length.

That is a category error, and it is the one this project is least able to
afford: the whole product claim is that a grade means something. It also could
not survive the ontology import, which would have added 16,000 more definitions
graded the same way and drowned the nine real findings entirely.

So claims split into two registers:

- **biological** — an assertion about the body, graded EVC-1…EVC-8 by evidence;
- **terminological** — an assertion about what a term denotes, graded
  TRM-1…TRM-4 by the authority behind it and whether that authority's stated
  source resolves.

The grading here is by provenance, and each rule is stated rather than applied
silently:

- Seed-corpus definitions restate prose from one narrative document with no
  resolvable definition source → **TRM-3 DERIVED**.
- Region and pancreas definitions come from Gray's / Terminologia Anatomica /
  Guyton, which are naming authorities with resolvable ISBNs → **TRM-1**.

    python3 tools/split_claim_kinds.py            # dry run
    python3 tools/split_claim_kinds.py --write
"""
from __future__ import annotations

import json
import os
import sys

AUDIT = 'ontology/CLAIM_KIND_SPLIT.json'

# Predicates that assert what a term means rather than what the body does.
DEFINITIONAL = ('has_definition', 'has_boundary_definition')

# Authorities whose definitions carry a resolvable source, by the identifier
# already recorded on the claim's sources.
TRACEABLE_AUTHORITIES = {
    'ISBN:9780702077050': "Standring S (ed.), Gray's Anatomy, 42nd ed.",
    'ISBN:9783132200111': 'Terminologia Anatomica, 2nd ed. (FIPAT)',
    'ISBN:9780323597128': 'Hall JE & Hall ME, Guyton and Hall, 14th ed.',
}


def split(write: bool) -> int:
    changes: list[dict] = []
    for root, _, files in os.walk('ontology'):
        if 'claims.json' not in files:
            continue
        path = os.path.join(root, 'claims.json')
        with open(path, encoding='utf-8') as fh:
            claims = json.load(fh)
        for claim in claims:
            if claim.get('predicate') not in DEFINITIONAL:
                continue
            was = claim.get('evidence_class')
            identifiers = {s.get('identifier') for s in claim.get('sources', [])}
            traceable = identifiers & set(TRACEABLE_AUTHORITIES)
            if traceable:
                grade, authority = 'TRM-1', ', '.join(
                    TRACEABLE_AUTHORITIES[i] for i in sorted(traceable))
                source = ', '.join(sorted(traceable))
                why = ('a naming authority with a resolvable identifier')
            else:
                grade, authority = 'TRM-3', (claim.get('provenance_source')
                                             or 'seed corpus')
                source = None
                why = ('restated from one narrative document with no resolvable '
                       'definition source')
            claim['kind'] = 'terminological'
            claim['evidence_class'] = grade
            claim['authority'] = authority
            claim['definition_source'] = source
            claim.pop('proposed_class', None)
            changes.append({'claim': claim['id'], 'file': path,
                            'was': was, 'now': grade, 'authority': authority,
                            'reason': why})
        if write:
            _dump(path, claims)

    by_grade: dict = {}
    for row in changes:
        by_grade[row['now']] = by_grade.get(row['now'], 0) + 1
    print(f'{len(changes)} definitional claims moved to the terminological '
          f'register: {by_grade}')
    for row in changes[:6]:
        print(f"  {row['claim']:<52} {row['was']} -> {row['now']}")
    if len(changes) > 6:
        print(f'  … and {len(changes) - 6} more')

    if not write:
        print('\ndry run — nothing written. Re-run with --write.')
        return 0

    _dump(AUDIT, {
        'note': ('94% of this substrate\'s claims were definitions graded on '
                 'the biological evidence ladder. This file records every one '
                 'moved to the terminological register, and why (D-021). What '
                 'remains on the evidence ladder is what the model actually '
                 'found out about a body.'),
        'decision': 'D-021', 'corrected_on': '2026-07-27',
        'claims_moved': len(changes), 'by_grade': by_grade,
        'changes': changes})
    print(f'\nwrote {AUDIT}')
    return 0


def _dump(path: str, obj) -> None:
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    sys.exit(split('--write' in sys.argv))
