#!/usr/bin/env python3
"""The pancreas test — the smallest addition that can falsify the thesis.

"Biology is a graph, not a tree; the pancreas belongs to both the digestive and
the endocrine system" is the claim this project was founded on. The architecture
answers it: containment and membership are separate relations, and the
navigation tree is derived rather than stored, so it cannot be edited into
disagreeing with the graph.

None of which had ever met a case that could break it. Before this script the
substrate held **zero entities with more than one membership** and exactly one
`member_of` edge. The thesis was verified by unit tests over a structure
containing no instance of the thing being tested.

So: one organ with two memberships, and both of its lineages modelled deep
enough that the two branches genuinely diverge —

    Pancreas (L3, in the abdomen; member of digestive AND endocrine)
      ├─ exocrine: acinus (L5) → acinar cell (L7) → zymogen granule (L8)
      └─ endocrine: islet of Langerhans (L5) → beta cell (L7) → insulin (L9)

Everything is admitted provisionally (D-017): an agent proposes, no human
reviews, and every record says so.

    PYTHONPATH=src python3 tools/curate_pancreas.py --write
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, 'src')

from homeo.agents import AgentRuntime                      # noqa: E402
from homeo.curation import Competence, CurationService     # noqa: E402

# The representation mode each level actually offers (BIO_Scale_Contract).
MODE_BY_LEVEL = {3: 'enumerated', 5: 'typed', 7: 'typed', 8: 'typed',
                 9: 'exemplar'}

GRAY = {'citation': "Standring S (ed.), Gray's Anatomy, 42nd ed.",
        'identifier': 'ISBN:9780702077050', 'licence_tier': 'T2'}
GUYTON = {'citation': 'Hall JE & Hall ME, Guyton and Hall Textbook of Medical '
                      'Physiology, 14th ed.',
          'identifier': 'ISBN:9780323597128', 'licence_tier': 'T2'}

# (id, class, level, subsystem, term, part_of, definition, source)
ENTITIES = [
    ('UBERON:0001264', 'Organ', 3, 'digestive', 'Pancreas', 'UBERON:0000916',
     'A retroperitoneal gland lying transversely across the posterior abdominal '
     'wall, with an exocrine acinar mass secreting digestive enzymes into the '
     'duodenum and endocrine islets secreting hormones into the portal blood.',
     GRAY),
    ('UBERON:0001263', 'TissueType', 5, 'digestive', 'Pancreatic acinus',
     'UBERON:0001264',
     'The exocrine secretory unit: a cluster of pyramidal cells around a central '
     'lumen draining into an intercalated duct.', GRAY),
    ('CL:0002064', 'CellType', 7, 'digestive', 'Pancreatic acinar cell',
     'UBERON:0001263',
     'A polarized zymogen-secreting epithelial cell with basal rough '
     'endoplasmic reticulum and apical secretory granules.', GRAY),
    ('GO:0042589', 'Organelle', 8, 'digestive', 'Zymogen granule',
     'CL:0002064',
     'A membrane-bound apical granule storing digestive proenzymes until '
     'secretagogue-triggered exocytosis.', GUYTON),
    ('UBERON:0000006', 'TissueType', 5, 'endocrine', 'Islet of Langerhans',
     'UBERON:0001264',
     'A vascularized endocrine micro-organ dispersed through the exocrine mass, '
     'comprising several hormone-secreting cell types.', GRAY),
    ('CL:0000169', 'CellType', 7, 'endocrine', 'Type B pancreatic cell',
     'UBERON:0000006',
     'The insulin-secreting islet cell; the majority cell type in the human '
     'islet, though proportions vary between individuals and islet size.',
     GUYTON),
    ('CHEBI:145810', 'Biomolecule', 9, 'endocrine', 'Insulin',
     None,
     'A 51-residue peptide hormone of two chains linked by disulfide bonds, '
     'secreted by type B pancreatic cells in response to raised plasma glucose.',
     GUYTON),
]

# (id, source, target, type, prose) — the two memberships are the point.
RELATIONSHIPS = [
    ('REL:pancreas-member-digestive', 'UBERON:0001264', 'HOX:function:digestive',
     'member_of',
     'The exocrine mass secretes digestive enzymes into the duodenum. This '
     'membership is not more or less real than the endocrine one.'),
    ('REL:pancreas-member-endocrine', 'UBERON:0001264', 'HOX:function:endocrine',
     'member_of',
     'The islets secrete insulin and glucagon into the portal blood. Filing the '
     'pancreas under one system and cross-referencing the other would make the '
     'model disagree with the anatomy.'),
    ('REL:betacell-produces-insulin', 'CL:0000169', 'CHEBI:145810', 'produces',
     'Type B cells synthesize proinsulin, cleave it, and secrete insulin with '
     'C-peptide in equimolar amounts.'),
]

# A cell producing a molecule crosses L7 to L9 without an L8 step. The skip is
# real and must be named rather than assumed (FR-SCAL-004).
SKIPS = {'REL:betacell-produces-insulin':
         'L8 (organelle) is skipped deliberately. Insulin biosynthesis does '
         'traverse organelles — rough ER, Golgi, secretory granule — and none '
         'is modelled here. The claim is that the cell secretes the molecule, '
         'which holds at cell level; the organelle pathway is not represented '
         'and this edge does not imply it is.'}


def build(write: bool) -> int:
    curation = CurationService([
        # No human reviewer is declared, because none exists. Everything below
        # is admitted provisionally and says so (D-017).
    ], queue_ceiling=64)
    runtime = AgentRuntime(curation)
    run = runtime.start('AGT-3', 'model the pancreas and both of its lineages')

    tasks = []
    for uid, klass, level, subsystem, term, parent, definition, source in ENTITIES:
        entity = {
            'id': uid, 'minted': False, 'entity_class': klass, 'level': level,
            'subsystem': subsystem, 'preferred_term': term,
            'compilation_status': 'structured',
            # Taken from the level's contract rather than guessed. The first
            # version guessed, and INV-13 caught three wrong modes: L5 offers
            # `typed`, not `enumerated`, and L9 offers `exemplar`.
            'representation_mode': MODE_BY_LEVEL[level],
            'review_state': 'provisional', 'admitted_by': 'agent:anatomy',
            'xrefs': [{'authority': uid.split(':')[0], 'id': uid,
                       'pinned_version': '2026-01-15'}],
        }
        if parent:
            entity['part_of'] = parent
        claim = {
            'id': f'CLM:{term.lower().replace(" ", "-")}-definition',
            'subject': uid, 'predicate': 'has_definition', 'object': definition,
            # EVC-4: a textbook description is a deliberate simplification, and
            # EVC-3 or better is not available to an automated actor anyway
            # (BR-002, D-017).
            'evidence_class': 'EVC-4', 'source_type': 'reference textbook',
            'sources': [source], 'species': 'Homo sapiens',
            'population': 'adult, both sexes', 'date_asserted': '2026-07-27',
            'review_state': 'provisional', 'assigned_by': 'agent:anatomy',
            'limitations': (
                'A structural description at one level of detail. No human '
                'reviewer has examined this record.'),
        }
        tid = runtime.propose(
            run, kind='entity', subsystem=subsystem, level=level,
            payload={'entity': entity, 'claim': claim},
            sources=[source['identifier']],
            rationale=f'{term} is required to model both pancreatic lineages.')
        tasks.append((tid, term))

    # A second run under a different agent. AGT-3 (Anatomy) may propose
    # entities and nothing else; relationships carry claims and belong to
    # AGT-2 (Evidence). The runtime refused the first attempt to do both under
    # one agent, which is the contract working rather than an obstacle — the
    # fix is to use the permitted agent, never to widen the permission.
    rel_run = runtime.start('AGT-2', 'type the pancreatic relationships')
    for rid, src, tgt, rtype, prose in RELATIONSHIPS:
        rel = {
            'id': rid, 'source': src, 'target': tgt, 'type': rtype,
            'compilation_status': 'structured',
            'review_state': 'provisional',
            'prose_justification': prose,
            'provenance_claim': 'CLM:pancreas-definition',
        }
        if rid in SKIPS:
            rel['skip_justification'] = SKIPS[rid]
        tid = runtime.propose(
            rel_run, kind='relationship', subsystem='digestive', level=3,
            payload={'relationship': rel}, sources=[GRAY['identifier']],
            rationale=prose)
        tasks.append((tid, rid))

    print(f'proposed {len(tasks)} records: {run.agent} ({run.id}) entities, '
          f'{rel_run.agent} ({rel_run.id}) relationships')

    admitted = []
    for tid, label in tasks:
        try:
            admitted.append(curation.admit_provisional(
                tid, 'agent:anatomy',
                'Structural anatomy from two reference texts. No human reviewer '
                'is available; admitted provisionally under D-017.'))
        except Exception as exc:                          # noqa: BLE001
            print(f'  REFUSED {label}: {exc}')
    print(f'admitted {len(admitted)} provisionally, 0 reviewed')
    print(f'review deficit now: {curation.admission_summary()}')

    if not write:
        print('\ndry run — nothing written. Re-run with --write.')
        return 0

    payloads = curation.provisional_payloads()
    entities = [p['payload']['entity'] for p in payloads
                if 'entity' in p['payload']]
    claims = [p['payload']['claim'] for p in payloads if 'claim' in p['payload']]
    rels = [p['payload']['relationship'] for p in payloads
            if 'relationship' in p['payload']]

    os.makedirs('ontology/pancreas', exist_ok=True)
    _dump('ontology/pancreas/entities.json', entities)
    _dump('ontology/pancreas/claims.json', claims)
    _dump('ontology/pancreas/relationships.json', rels)
    _dump('ontology/pancreas/ADMISSIONS.json', {
        'note': ('Every record here was admitted provisionally: proposed by '
                 'AGT-3, admitted by agent:anatomy, reviewed by nobody. It is '
                 'in the substrate because absence would be its own '
                 'distortion, and it is marked unreviewed at every surface '
                 '(D-017).'),
        'runs': [run.id, rel_run.id], 'reviewed': 0,
        'provisional': len(admitted),
        'admissions': [a.as_dict() for a in admitted]})
    print(f'\nwrote {len(entities)} entities, {len(claims)} claims, '
          f'{len(rels)} relationships')
    return 0


def _dump(path: str, obj) -> None:
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    sys.exit(build('--write' in sys.argv))
