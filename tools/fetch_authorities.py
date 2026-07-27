#!/usr/bin/env python3
"""Pin the external ontologies this project imports from.

An import is only reproducible if the source it read is pinned. G-07 requires a
byte-identical rebuild of a release, and the classroom NFR requires the whole
thing to work offline — both mean the importer must read a *snapshot* with a
recorded hash, never a live URL.

Three sources, all openly licensed and therefore admissible at tier T0, which is
what makes them usable at all where Gray's and Terminologia Anatomica are not:

    UBERON  basic.json     CC-BY 3.0   anatomy across vertebrates
    CL      cl-basic.obo   CC-BY 4.0   cell types
    ECO     eco.obo        CC0         evidence and conclusion codes

The manifest is written to `ontology/vocabularies/SNAPSHOTS.json`.
`authorities.json` is deliberately left alone: it is a flat list that
`tools/biocheck.py` reads as the registry INV-10 checks xrefs against, and
adding version fields there would break that invariant. One file answers "which
authorities may be cited", this one answers "which snapshot was pinned".

    python3 tools/fetch_authorities.py            # fetch what is missing
    python3 tools/fetch_authorities.py --verify   # re-hash, change nothing
    python3 tools/fetch_authorities.py --force    # re-fetch everything
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

CACHE = os.path.join('vendor', 'ontologies')
MANIFEST = os.path.join('ontology', 'vocabularies', 'SNAPSHOTS.json')

SOURCES = {
    'UBERON': {
        'url': 'https://purl.obolibrary.org/obo/uberon/basic.json',
        'file': 'uberon-basic.json', 'format': 'obo-json',
        'licence': 'CC-BY 3.0', 'licence_tier': 'T0',
        'note': 'Anatomy across vertebrates. Human applicability is a warrant '
                'each term must carry, never an assumption (INV-12).',
    },
    'CL': {
        'url': 'https://purl.obolibrary.org/obo/cl/cl-basic.obo',
        'file': 'cl-basic.obo', 'format': 'obo',
        'licence': 'CC-BY 4.0', 'licence_tier': 'T0',
        'note': 'Cell types.',
    },
    'ECO': {
        'url': 'https://purl.obolibrary.org/obo/eco.obo',
        'file': 'eco.obo', 'format': 'obo',
        'licence': 'CC0', 'licence_tier': 'T0',
        'note': 'Evidence codes, mapped to the EVC ladder by the table in '
                'BIO_Evidence_and_Provenance.',
    },
}


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def data_version(path: str, fmt: str) -> str | None:
    """The ontology's own version stamp, whatever it calls it.

    Recorded alongside our hash because the two answer different questions:
    the hash says "this is the same bytes", the version says "this is the
    release the publisher named".
    """
    try:
        if fmt == 'obo-json':
            with open(path, encoding='utf-8') as fh:
                meta = json.load(fh)['graphs'][0].get('meta', {})
            for prop in meta.get('basicPropertyValues', []):
                if prop.get('pred', '').endswith('versionInfo'):
                    return prop.get('val')
            return meta.get('version')
        with open(path, encoding='utf-8') as fh:
            for line in fh:
                if line.startswith('data-version:'):
                    return line.split(':', 1)[1].strip()
                if line.startswith('[Term]'):
                    break
    except (OSError, ValueError, KeyError, IndexError):
        return None
    return None


def load_manifest() -> dict:
    if not os.path.isfile(MANIFEST):
        return {}
    with open(MANIFEST, encoding='utf-8') as fh:
        return json.load(fh).get('snapshots', {})


def verify() -> int:
    """Re-hash the cache against the manifest. Changes nothing."""
    manifest = load_manifest()
    if not manifest:
        print(f'no manifest at {MANIFEST}; nothing has been pinned yet')
        return 1
    failed = 0
    for name, record in sorted(manifest.items()):
        path = os.path.join(CACHE, record['file'])
        if not os.path.isfile(path):
            print(f'  MISSING  {name}: {path} — re-fetch before importing')
            failed += 1
            continue
        actual = sha256(path)
        if actual != record['sha256']:
            print(f'  CHANGED  {name}: cache hashes {actual[:16]}…, manifest '
                  f'pins {record["sha256"][:16]}… — the snapshot moved under '
                  f'us, and an import against it would not be reproducible')
            failed += 1
        else:
            print(f'  OK       {name}  {record.get("data_version") or "—"}  '
                  f'{record["sha256"][:16]}…')
    print(f'\n{len(manifest) - failed} of {len(manifest)} snapshots verified')
    return 1 if failed else 0


def fetch(force: bool) -> int:
    os.makedirs(CACHE, exist_ok=True)
    manifest = load_manifest()
    for name, source in sorted(SOURCES.items()):
        path = os.path.join(CACHE, source['file'])
        if os.path.isfile(path) and not force:
            print(f'  cached   {name}  ({os.path.getsize(path):,} bytes)')
        else:
            print(f'  fetching {name} … ', end='', flush=True)
            try:
                with urllib.request.urlopen(source['url'], timeout=300) as r, \
                        open(path, 'wb') as out:
                    out.write(r.read())
            except OSError as exc:
                print(f'FAILED ({exc})')
                print(f'  {name} is unavailable. The importer runs offline '
                      f'against the cache; nothing is fetched at import time.')
                continue
            print(f'{os.path.getsize(path):,} bytes')
        manifest[name] = {
            'url': source['url'], 'file': source['file'],
            'format': source['format'], 'licence': source['licence'],
            'licence_tier': source['licence_tier'], 'note': source['note'],
            'bytes': os.path.getsize(path), 'sha256': sha256(path),
            'data_version': data_version(path, source['format']),
            'fetched': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        }

    with open(MANIFEST, 'w', encoding='utf-8') as fh:
        json.dump({
            'note': ('Pinned snapshots of the external ontologies this project '
                     'imports from. The importer reads the cache under '
                     f'{CACHE}/ and refuses to run if a hash here does not '
                     'match, because an import against a moving source is not '
                     'reproducible (G-07). Separate from authorities.json, '
                     'which is the flat registry INV-10 checks xrefs against '
                     'and must keep its shape.'),
            'cache': CACHE,
            'snapshots': manifest,
        }, fh, indent=1, ensure_ascii=False)
    print(f'\npinned {len(manifest)} snapshots in {MANIFEST}')
    return 0


def main(argv: list[str]) -> int:
    if '--verify' in argv:
        return verify()
    return fetch('--force' in argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
