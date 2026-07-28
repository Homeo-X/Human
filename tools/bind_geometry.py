#!/usr/bin/env python3
"""Mint spatial identities for organs that have a mesh, and bind it.

`tools/fetch_assets.py` resolves BodyParts3D meshes to organs by FMA id. Most
organs are refused — BodyParts3D models them as composites — but fourteen
resolve to a single file. Those fourteen could still not be bound, for a reason
worth stating plainly: **geometry binds to a spatial identity, never to an
entity** (FR-SPAT-001), and none of the imported organs had one. Only three
entities in the whole substrate did, all hand-seeded.

So this mints the missing spatial identities. What it asserts is deliberately
almost nothing:

    id, entity, coordinate_frame

and no more. `anatomical_position` is prose about where a structure sits, which
is a claim and needs a source; `laterality`, `contained_in`, `adjacent_to` and
`landmarks` are curation judgements nobody has made. Leaving them absent is not
laziness — an empty field is a field nobody filled, and a *guessed* field is
indistinguishable from a checked one once it is in the graph. The mesh gives us
a shape to show; it does not tell us any of the rest.

Everything goes through the curation plane provisionally (D-017), like every
other record this project has added.

    PYTHONPATH=src python3 tools/bind_geometry.py --write
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, 'src')
sys.path.insert(0, 'tools')

from fetch_assets import resolve_bodyparts3d                 # noqa: E402
from homeo.agents import AgentRuntime                        # noqa: E402
from homeo.curation import CurationService                   # noqa: E402
from homeo.substrate import load                             # noqa: E402

# The one frame the substrate declares. Stated rather than invented: it is what
# the existing spatial identities use.
FRAME = 'HOX-REF-ADULT-2026'
OUT = os.path.join('ontology', 'geometry')


def _slug(entity_id: str) -> str:
    return entity_id.replace(':', '-').lower()


def build(write: bool) -> int:
    assets, refusals = resolve_bodyparts3d()
    substrate = load('ontology')
    placed = {si.entity for si in substrate.spatial_identities}

    bindable = [(aid, spec) for aid, spec in sorted(assets.items())
                if spec.get('entity') and spec.get('level') == 3]
    print(f'{len(bindable)} mesh(es) resolved, {len(refusals)} refused by the '
          f'source rule')

    curation = CurationService([], queue_ceiling=len(bindable) * 4 + 32)
    runtime = AgentRuntime(curation)
    run = runtime.start('AGT-3', 'mint spatial identities for organs with a '
                                 'resolvable mesh')

    tasks, minted, already = [], [], []
    for asset_id, spec in bindable:
        entity = spec['entity']
        if entity in placed:
            already.append(entity)
            continue
        identity = {
            'id': f'SPI:{_slug(entity)}',
            'entity': entity,
            'coordinate_frame': FRAME,
            'geometry': [{
                'asset_id': asset_id,
                'representation_kind': spec['representation_kind'],
                'level': spec['level'],
                'licence': spec['licence'],
                'licence_tier': spec['licence_tier'],
                'attribution': spec['attribution'],
                'source': spec['source'],
            }],
        }
        tid = runtime.propose(
            run, kind='spatial_identity', subsystem='foundational', level=3,
            payload={'spatial_identity': identity},
            sources=[spec['source']],
            rationale=(
                f'{spec["note"].split(".")[0]} has a single mesh in the pinned '
                f'source; a spatial identity is required before it can be '
                f'bound (FR-SPAT-001). Only the coordinate frame is asserted.'))
        tasks.append((tid, identity['id']))
        minted.append(identity)

    for tid, label in tasks:
        try:
            curation.admit_provisional(
                tid, 'agent:anatomy',
                'Minimal spatial identity: coordinate frame only, so that a '
                'pinned mesh can bind. No position, laterality or containment '
                'is asserted. Admitted provisionally under D-017.')
        except Exception as exc:                              # noqa: BLE001
            print(f'  REFUSED {label}: {exc}')

    print(f'minted {len(minted)} spatial identities, {len(already)} already '
          f'placed, 0 reviewed')
    if not write:
        print('\ndry run — nothing written. Re-run with --write.')
        return 0

    os.makedirs(OUT, exist_ok=True)
    _dump(os.path.join(OUT, 'spatial_identities.json'), minted)
    _dump(os.path.join(OUT, 'BINDINGS.json'), {
        'note': ('Spatial identities minted so that pinned meshes could bind '
                 '(FR-SPAT-001, D-032). Each asserts a coordinate frame and '
                 'nothing else: position, laterality and containment are '
                 'curation nobody has done, and are absent rather than '
                 'guessed. Every asset here is T1 share-alike and quarantined '
                 '(D-003, BR-013) — the bytes are not in this repository.'),
        'run': run.id, 'reviewed': 0, 'provisional': len(minted),
        'bound': [{'entity': i['entity'],
                   'asset': i['geometry'][0]['asset_id'],
                   'tier': i['geometry'][0]['licence_tier']} for i in minted],
        'refused_by_source_rule': refusals,
    })
    print(f'\nwrote {len(minted)} spatial identities with geometry')
    return 0


def _dump(path: str, obj) -> None:
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    sys.exit(build('--write' in sys.argv))
