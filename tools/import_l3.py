#!/usr/bin/env python3
"""Import major organs at L3 from the pinned UBERON snapshot.

This is the first content that arrives by rule rather than by hand, and the
rule tables below are the artifact a reviewer would actually judge. That is the
point: RSK-02 says expert review cannot keep pace with generation, and the
answer is not to review two hundred organs one at a time but to review *how*
two hundred organs were placed, once.

**Placement comes from UBERON's own assertions, not from opinion.** Walking a
term's `part_of`/`is_a` closure reaches the organ systems the ontology says it
belongs to; `SYSTEM_MAP` translates the ones that mean something into this
project's subsystems. Terms reaching only abstractions like "anatomical system"
are refused — reaching *a* system places nothing.

Two things this produces that hand-authoring would not:

- **29 of 195 organs belong to more than one system** — the liver to digestive
  and endocrine, the pituitary to endocrine, nervous and reproductive, the
  tongue to digestive and nervous. Each becomes real `member_of` edges, which
  is the multi-membership case (D-019) at seventy times the scale it was fixed
  against.
- **Honest refusals.** 28 organs reach no mapped system, `lymphatic` has no L2
  anchor in this substrate at all, and terms with no human warrant are declined
  rather than quietly filed as human.

    PYTHONPATH=src python3 tools/import_l3.py            # dry run
    PYTHONPATH=src python3 tools/import_l3.py --write
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

sys.path.insert(0, 'src')

from homeo.agents import AgentRuntime                          # noqa: E402
from homeo.curation import CurationService                     # noqa: E402
from homeo.importers.obo import (OBO_IS_A, OBO_PART_OF,         # noqa: E402
                                 OboImporter, load_snapshot)

# ---- the reviewable artifact, part one: which UBERON system means which -----
#
# Only systems that name something this project models. UBERON's "anatomical
# system" and "non-connected functional system" are true of every organ and
# therefore locate none of them.
SYSTEM_MAP = {
    'cardiovascular system': 'cardiovascular',
    'circulatory system': 'cardiovascular',
    'respiratory system': 'respiratory',
    'nervous system': 'nervous',
    'central nervous system': 'nervous',
    'peripheral nervous system': 'nervous',
    'sensory system': 'nervous',
    'renal system': 'urinary',
    'excretory system': 'urinary',
    'musculoskeletal system': 'musculoskeletal',
    'skeletal system': 'musculoskeletal',
    'muscular system': 'musculoskeletal',
    'digestive system': 'digestive',
    'alimentary part of gastrointestinal system': 'digestive',
    'endocrine system': 'endocrine',
    'immune system': 'immune',
    'hemolymphoid system': 'immune',
    'lymphatic system': 'lymphatic',
    'integumental system': 'integumentary',
    'reproductive system': 'reproductive',
    'male reproductive system': 'reproductive',
    'female reproductive system': 'reproductive',
}

# ---- the reviewable artifact, part two: what a membership edge points at ----
#
# `lymphatic` is deliberately absent: this substrate has no L2 lymphatic entity,
# so a lymphatic organ has nothing to be a member of and is refused rather than
# attached to an invented anchor.
#
# Nine of these are narrative seed nodes rather than proper System entities —
# a known inconsistency recorded with the run, not hidden by it.
ANCHORS = {
    'cardiovascular': 'UBERON:0004535',
    'respiratory': 'HOX:function:respiratory',
    'nervous': 'HOX:function:nervous',
    'urinary': 'HOX:function:urinary',
    'musculoskeletal': 'HOX:function:skeletal',
    'digestive': 'HOX:function:digestive',
    'endocrine': 'HOX:function:endocrine',
    'immune': 'HOX:function:lymphimmune',
    'integumentary': 'HOX:function:integumentary',
    'reproductive': 'HOX:function:reproductive',
}

CLOSURE_LIMIT = 14


class Placement:
    """Decides where an imported term belongs, from the ontology's own edges."""

    def __init__(self, terms):
        self.terms = terms
        self.systems = {t.id: t.label for t in terms.values()
                        if t.label.endswith(' system')}
        self.refusals: dict[str, str] = {}

    def _closure(self, term_id: str) -> set[str]:
        seen, frontier = {term_id}, [term_id]
        for _ in range(CLOSURE_LIMIT):
            nxt = []
            for current in frontier:
                term = self.terms.get(current)
                if term is None:
                    continue
                for pred, target in term.parents:
                    if pred in (OBO_PART_OF, OBO_IS_A) and target not in seen:
                        seen.add(target)
                        nxt.append(target)
            frontier = nxt
            if not frontier:
                break
        return seen

    def systems_for(self, term) -> list[str]:
        """Every subsystem this term belongs to, per UBERON, with an anchor."""
        reached = {SYSTEM_MAP[self.systems[s]]
                   for s in self._closure(term.id)
                   if s in self.systems and self.systems[s] in SYSTEM_MAP}
        return sorted(s for s in reached if s in ANCHORS)

    def __call__(self, term) -> str | None:
        """The primary filing, or None to refuse.

        `Entity.subsystem` is the primary filing and the `member_of` edges carry
        the whole truth (D-019), so which of several systems is named here does
        not decide what the model knows. It is taken alphabetically to be
        deterministic — a reproducible arbitrary choice, rather than an
        undocumented one.
        """
        if term.human_warrant is None:
            self.refusals[term.id] = (
                'non-human: no FMA cross-reference and not in the human '
                'reference atlas, so this vertebrate-general class has no '
                'warrant for a human reference model')
            return None
        found = self.systems_for(term)
        if not found:
            unanchored = {SYSTEM_MAP[self.systems[s]]
                          for s in self._closure(term.id)
                          if s in self.systems and self.systems[s] in SYSTEM_MAP}
            if unanchored:
                self.refusals[term.id] = (
                    f'unanchored: belongs to {sorted(unanchored)}, which has no '
                    f'L2 entity in this substrate to be a member of')
            else:
                self.refusals[term.id] = (
                    'unplaced: UBERON puts this term under no system this '
                    'project models — it reaches only abstractions like '
                    '"anatomical system", which locate nothing')
            return None
        return found[0]


def build(write: bool) -> int:
    terms, version = load_snapshot('UBERON')
    placement = Placement(terms)
    # What the substrate already holds. Without this the import overwrites
    # curation: the first run replaced the curated heart with the raw UBERON
    # term, and the loader's last-file-wins made it invisible.
    from homeo.substrate import load as load_substrate
    existing = {e.id for e in load_substrate('ontology').entities
                if not e.provenance_source
                or 'UBERON 2026' not in str(e.provenance_source)}
    importer = OboImporter(terms, pinned_version=version,
                           placement=placement, existing=existing,
                           agent='agent:anatomy')
    selected = importer.select('organ_slim')
    result = importer.build(selected)

    # Membership edges, from the same closure that decided placement.
    memberships = []
    for entity in result.entities:
        term = terms[entity['id']]
        for subsystem in placement.systems_for(term):
            rid = (f'REL:{entity["id"].replace(":", "-").lower()}'
                   f'-member-{subsystem}')
            claim_id = f'CLM:{rid[4:]}-assertion'
            memberships.append(({
                'id': rid, 'source': entity['id'],
                'target': ANCHORS[subsystem], 'type': 'member_of',
                'compilation_status': 'structured',
                'review_state': 'provisional',
                'provenance_claim': claim_id,
                'prose_justification': (
                    f'UBERON places {entity["id"]} under the {subsystem} '
                    f'system through its own part_of/is_a closure.'),
            }, {
                'id': claim_id, 'subject': entity['id'],
                'predicate': 'asserted_member_of', 'object': ANCHORS[subsystem],
                'kind': 'terminological', 'evidence_class': 'TRM-1',
                'authority': 'UBERON',
                'definition_source': f'UBERON {version}',
                'source_type': 'curated database', 'species': 'Homo sapiens',
                'population': 'not applicable', 'date_asserted': '2026-07-27',
                'review_state': 'provisional', 'assigned_by': 'agent:anatomy',
                'limitations': (
                    'Derived from the source ontology\'s own hierarchy. That a '
                    'system membership is asserted is not that a curator has '
                    'checked it.'),
            }))
    result.relationships.extend(r for r, _ in memberships)
    result.claims.extend(c for _, c in memberships)

    multi = Counter()
    for entity in result.entities:
        multi[len(placement.systems_for(terms[entity['id']]))] += 1

    print(f'UBERON {version}: {len(selected)} organ_slim terms selected')
    print(json.dumps(result.summary(), indent=1))
    print(f'\nmembership edges: {len(memberships)}')
    print(f'organs by system count: {dict(sorted(multi.items()))}')
    print(f'  → {sum(n for k, n in multi.items() if k > 1)} organs belong to '
          f'more than one system')
    reasons = Counter(r.split(':')[0] for r in placement.refusals.values())
    print(f'\nplacement refusals: {dict(reasons)}')
    for tid, why in list(placement.refusals.items())[:4]:
        print(f'  {terms[tid].label:<30} {why[:70]}')

    if not write:
        print('\ndry run — nothing written. Re-run with --write.')
        return 0

    # Everything goes through the curation plane, provisionally (D-017).
    curation = CurationService([], queue_ceiling=len(result.entities) * 4 + 64)
    runtime = AgentRuntime(curation)
    ents = runtime.start('AGT-3', 'import L3 organs from UBERON')
    rels = runtime.start('AGT-2', 'import the ontology assertions behind them')
    budget = {'steps': 10_000, 'tool_calls': 10_000}
    ents.budget = dict(budget)
    rels.budget = dict(budget)

    admitted = 0
    for entity in result.entities:
        tid = runtime.propose(
            ents, kind='entity', subsystem=entity['subsystem'],
            level=entity['level'], payload={'entity': entity},
            sources=[f'UBERON {version}'],
            rationale=f'{entity["preferred_term"]} is in UBERON organ_slim.')
        curation.admit_provisional(
            tid, 'agent:anatomy',
            'Imported from a pinned UBERON snapshot by a stated rule. No human '
            'reviewer has examined it (D-017).')
        admitted += 1

    _dump('ontology/imported/entities.json', result.entities)
    _dump('ontology/imported/claims.json', result.claims)
    _dump('ontology/imported/relationships.json', result.relationships)
    _dump('ontology/imported/IMPORT_REPORT.json', {
        'note': ('Imported from a pinned UBERON snapshot by the rule tables in '
                 'tools/import_l3.py. Nothing here is reviewed. The refusals '
                 'are as much the result as the imports (D-017, D-019).'),
        'source': f'UBERON {version}', 'agent': 'agent:anatomy',
        'runs': [ents.id, rels.id], 'reviewed': 0, 'provisional': admitted,
        'summary': result.summary(),
        'multi_system_organs': sum(n for k, n in multi.items() if k > 1),
        'refusals': [r.as_dict() for r in result.refusals],
        'placement_refusals': placement.refusals,
        'known_inconsistency': (
            'Nine of the ten system anchors are narrative seed topic nodes '
            'rather than System entities. Membership edges point at them '
            'because that is what the substrate has; importing the eleven '
            'UBERON system terms properly is outstanding work.'),
    })
    print(f'\nwrote {len(result.entities)} entities, {len(result.claims)} '
          f'claims, {len(result.relationships)} relationships — all provisional')
    return 0


def _dump(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    sys.exit(build('--write' in sys.argv))
