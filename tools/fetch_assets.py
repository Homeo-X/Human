#!/usr/bin/env python3
"""Pin the geometry assets this project binds to entities.

The same discipline as `tools/fetch_authorities.py` (D-024), for the same
reason: a release that references a live URL is not reproducible, and G-07 asks
for a byte-identical rebuild. What is committed is the **manifest** — url,
sha256, byte size, licence, tier, attribution — and the bytes live in a
gitignored cache.

**The bytes are deliberately not vendored.** A mesh carries licence obligations
(attribution always, share-alike sometimes), and committing one into a
repository whose own licence posture is undecided would create an obligation
nobody agreed to. The manifest is the artifact; the asset is fetched.

Two things this records that a hash alone would not, and both matter more here
than in the ontology case:

- **`representation_kind`**, per FR-SPAT-004. The heart mesh below is an
  artist's model, not a measured dataset. It is bound as `reference_exemplar`
  and must never be presented as a measurement. A beautiful mesh labelled
  `measured` is exactly the failure this project exists to prevent — the whole
  problem statement is that a well-rendered guess is indistinguishable from a
  well-rendered measurement.
- **Attribution text**, because CC-BY is only satisfied if the credit travels
  with the asset. It goes in the manifest so the release pipeline can ship it.

    python3 tools/fetch_assets.py            # fetch what is missing
    python3 tools/fetch_assets.py --verify   # re-hash, change nothing
    python3 tools/fetch_assets.py --force    # re-fetch everything
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

CACHE = os.path.join('vendor', 'assets')
MANIFEST = os.path.join('ontology', 'assets', 'ASSETS.json')

ASSETS = {
    'ASSET:heart-exemplar-001': {
        'entity': 'UBERON:0000948',
        'spatial_identity': 'SPI:heart',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/d/d2/'
               '3D_model_of_a_human_heart.stl',
        'file': 'heart-exemplar-001.stl',
        'format': 'stl',
        'licence': 'CC BY 4.0',
        'licence_tier': 'T0',
        'representation_kind': 'reference_exemplar',
        'level': 3,
        'attribution': (
            '"Realistic Human Heart" by neshallads, licensed CC BY 4.0, via '
            'Wikimedia Commons.'),
        'source': 'https://commons.wikimedia.org/wiki/File:'
                  '3D_model_of_a_human_heart.stl',
        'note': (
            'An artist-authored exemplar, not a measurement of any individual '
            'and not derived from imaging. Bound as `reference_exemplar` so '
            'that no surface can present its shape as evidence: the model '
            'knows the heart is in the thorax and roughly this shape, and it '
            'does not know any dimension from this file.'),
    },
}


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def load_manifest() -> dict:
    if not os.path.isfile(MANIFEST):
        return {}
    with open(MANIFEST, encoding='utf-8') as fh:
        return json.load(fh).get('assets', {})


def available() -> set[str]:
    """Asset ids whose bytes are present and hash as pinned.

    This is what `ProjectionService` needs to tell `depicted` from
    `asset_unavailable`. Availability is a fact about a deployment, not about
    the model, so it is computed here and passed in rather than assumed.
    """
    present = set()
    for asset_id, record in load_manifest().items():
        path = os.path.join(CACHE, record['file'])
        if os.path.isfile(path) and sha256(path) == record['sha256']:
            present.add(asset_id)
    return present


def verify() -> int:
    manifest = load_manifest()
    if not manifest:
        print(f'no manifest at {MANIFEST}; nothing has been pinned yet')
        return 1
    failed = 0
    for asset_id, record in sorted(manifest.items()):
        path = os.path.join(CACHE, record['file'])
        if not os.path.isfile(path):
            print(f'  MISSING  {asset_id}: {path} — the binding stays valid, '
                  f'and the projection reports asset_unavailable rather than '
                  f'pretending the entity has no geometry')
            failed += 1
            continue
        actual = sha256(path)
        if actual != record['sha256']:
            print(f'  CHANGED  {asset_id}: cache hashes {actual[:16]}…, '
                  f'manifest pins {record["sha256"][:16]}…')
            failed += 1
        else:
            print(f'  OK       {asset_id}  {record["licence"]} '
                  f'({record["licence_tier"]})  {record["sha256"][:16]}…')
    print(f'\n{len(manifest) - failed} of {len(manifest)} assets verified')
    return 1 if failed else 0


def fetch(force: bool) -> int:
    os.makedirs(CACHE, exist_ok=True)
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    manifest = load_manifest()
    for asset_id, spec in sorted(ASSETS.items()):
        path = os.path.join(CACHE, spec['file'])
        if os.path.isfile(path) and not force:
            print(f'  cached   {asset_id}')
        else:
            print(f'  fetching {asset_id} … ', end='', flush=True)
            request = urllib.request.Request(
                spec['url'], headers={'User-Agent': 'project-human-organism/0.1'})
            with urllib.request.urlopen(request, timeout=120) as response:
                data = response.read()
            with open(path, 'wb') as fh:
                fh.write(data)
            print(f'{len(data) / 1e6:.1f} MB')
        record = {k: v for k, v in spec.items() if k != 'url'}
        record.update({
            'url': spec['url'], 'sha256': sha256(path),
            'bytes': os.path.getsize(path),
            'fetched': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        })
        manifest[asset_id] = record
    with open(MANIFEST, 'w', encoding='utf-8') as fh:
        json.dump({
            'note': ('Pinned geometry assets. The bytes are NOT in this '
                     'repository — they are fetched into a gitignored cache '
                     'and verified against these hashes. Every asset declares '
                     'its representation kind, and none of them is `measured`: '
                     'this project holds no measured geometry at all.'),
            'cache': CACHE, 'assets': manifest}, fh, indent=1,
            ensure_ascii=False)
    print(f'\nwrote {MANIFEST} — {len(manifest)} asset(s) pinned')
    return 0


def main(argv: list[str]) -> int:
    if '--verify' in argv:
        return verify()
    return fetch('--force' in argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
