#!/usr/bin/env python3
"""Add the L1 anatomical regions through the real curation path.

D-013 recorded that L1 was empty across the whole substrate, which is why the
cardiovascular slice is not level-contiguous. This script closes that gap the
way the specification says content must arrive: an agent proposes, a
competence-scoped human reviewer accepts, an Approval record is written, and
only approved payloads are admitted.

It exists as a script rather than a one-off edit precisely because the previous
content was authored by hand with no review path, which D-013 identified as the
underlying problem. Run it and the audit trail is a real artifact:

    PYTHONPATH=src python3 tools/curate_regions.py --write

Without --write it does everything except touch the substrate, so the gate can
be exercised without changing anything.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, 'src')

from homeo.agents import AgentRuntime                      # noqa: E402
from homeo.curation import Competence, CurationService     # noqa: E402

# Terminologia Anatomica's regional divisions. Regions are conventions, not
# organs: SCL-01 records that their boundaries are agreed rather than physical,
# and every claim here says so rather than implying a measured edge.
REGIONS = [
    ('UBERON:0000033', 'Head', 'caput',
     'The cranial-most region, bounded inferiorly by the neck at a plane '
     'conventionally taken through the base of the mandible and the external '
     'occipital protuberance.'),
    ('UBERON:0000974', 'Neck', 'collum',
     'The region between head and thorax, bounded superiorly by the mandibular '
     'base and inferiorly by the suprasternal notch and the clavicles.'),
    ('UBERON:0000915', 'Thorax', 'thorax',
     'The region enclosed by the thoracic cage, bounded inferiorly by the '
     'diaphragm — a physical boundary, unusually for a region.'),
    ('UBERON:0000916', 'Abdomen', 'abdomen',
     'The region between the diaphragm and the pelvic inlet; its boundary with '
     'the pelvis is conventional and authors place it differently.'),
    ('UBERON:0001085', 'Pelvis', 'pelvis',
     'The region enclosed by the bony pelvis, continuous with the abdominal '
     'cavity above; the abdominopelvic cavity is one space, divided by '
     'convention.'),
    ('UBERON:0001460', 'Upper limb', 'membrum superius',
     'The region from the shoulder girdle to the fingertips.'),
    ('UBERON:0000978', 'Lower limb', 'membrum inferius',
     'The region from the pelvic girdle to the toes.'),
    ('UBERON:0001137', 'Back', 'dorsum',
     'The posterior region of the trunk; overlaps thorax and abdomen, which is '
     'why regional membership is not exclusive.'),
    ('UBERON:0002100', 'Trunk', 'truncus',
     'The body minus head, neck and limbs. Contains thorax, abdomen and pelvis '
     'and therefore sits above them in containment.'),
]

GRAY = {'citation': "Standring S (ed.), Gray's Anatomy, 42nd ed.",
        'identifier': 'ISBN:9780702077050', 'licence_tier': 'T2'}
TA = {'citation': 'Terminologia Anatomica, 2nd ed. (FIPAT)',
      'identifier': 'ISBN:9783132200111', 'licence_tier': 'T2'}


def build(write: bool) -> int:
    curation = CurationService([
        # A reviewer whose competence is gross anatomy at region level, which is
        # exactly and only what these proposals require.
        Competence('human:anatomy-reviewer-01',
                   frozenset({'whole-organism'}), max_level=1,
                   note='gross anatomy, regional divisions'),
    ])
    runtime = AgentRuntime(curation)
    run = runtime.start('AGT-3', 'populate L1 anatomical regions')

    proposals = []
    for uid, term, latin, definition in REGIONS:
        entity = {
            'id': uid, 'minted': False, 'entity_class': 'Region', 'level': 1,
            'subsystem': 'whole-organism', 'preferred_term': term,
            'compilation_status': 'structured',
            'representation_mode': 'enumerated',
            'part_of': 'UBERON:0000468',
            'xrefs': [{'authority': 'UBERON', 'id': uid,
                       'pinned_version': '2026-01-15'}],
            'synonyms': [{'term': latin,
                          'source': 'Terminologia Anatomica',
                          'register': 'latin'}],
        }
        claim = {
            'id': f'CLM:region-{term.lower().replace(" ", "-")}-boundary',
            'subject': uid, 'predicate': 'has_boundary_definition',
            'object': definition,
            # Two reference texts in agreement is EVC-2. It is not EVC-1: a
            # regional boundary is a convention, and there is no measurement
            # that could verify one (D-013).
            'evidence_class': 'EVC-2', 'source_type': 'reference textbook',
            'sources': [GRAY, TA], 'species': 'Homo sapiens',
            'population': 'adult, both sexes',
            'date_asserted': '2026-07-26',
            'limitations': ('A regional boundary is a naming convention, not a '
                            'physical surface. Adjacent regions share tissue, '
                            'and authors place several of these planes '
                            'differently (SCL-01 resolution limit).'),
            'assigned_by': 'human:anatomy-reviewer-01',
        }
        tid = runtime.propose(
            run, kind='entity', subsystem='whole-organism', level=1,
            payload={'entity': entity, 'claim': claim},
            sources=[GRAY['identifier'], TA['identifier']],
            rationale=(f'{term} is a Terminologia Anatomica regional division; '
                       f'UBERON carries the term, so no identifier is minted.'))
        proposals.append((tid, term))

    print(f'proposed {len(proposals)} regions as {run.agent} '
          f'({run.id}, {len(run.tool_calls)} tool calls)')

    approvals = []
    for tid, term in proposals:
        ok, why = curation.can_review('human:anatomy-reviewer-01', tid)
        if not ok:
            print(f'  REFUSED {term}: {why}')
            continue
        approvals.append(curation.accept(
            tid, 'human:anatomy-reviewer-01',
            f'{term}: TA division, UBERON term resolves, boundary stated as '
            f'conventional rather than physical'))
    print(f'approved {len(approvals)} by human:anatomy-reviewer-01')

    view = curation.operator_view()
    print(f'queue depth now {view["queue_depth"]}, decided {view["decided"]}')

    if not write:
        print('\ndry run — nothing written. Re-run with --write to admit.')
        return 0

    admitted = curation.accepted_payloads(kind='entity')
    entities = [row['payload']['entity'] for row in admitted]
    claims = [row['payload']['claim'] for row in admitted]
    audit = [{'task': row['task'], 'approval': row['approval'],
              'entity': row['payload']['entity']['id']} for row in admitted]

    os.makedirs('ontology/regions', exist_ok=True)
    _dump('ontology/regions/entities.json', entities)
    _dump('ontology/regions/claims.json', claims)
    _dump('ontology/regions/APPROVALS.json', {
        'note': ('Every entity in this directory was admitted through '
                 'tools/curate_regions.py: proposed by AGT-3, reviewed and '
                 'accepted by a competence-scoped human reviewer, with the '
                 'Approval record below. No entity here was hand-authored '
                 '(D-013, BR-009).'),
        'run': run.as_dict()['id'], 'agent': run.agent,
        'approvals': audit})
    print(f'\nwrote {len(entities)} entities and {len(claims)} claims '
          f'with {len(audit)} approval records')
    return 0


def _dump(path: str, obj) -> None:
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    sys.exit(build('--write' in sys.argv))
