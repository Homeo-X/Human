#!/usr/bin/env python3
"""Check every finding against an open textbook, and record what was found.

**This produces verification, not review.** The distinction is the whole point.
BR-002 forbids any automated actor from assigning EVC-1 or EVC-2, and D-017 and
INV-17 exist because this project has twice caught itself recording review that
never happened. So nothing here sets `review_state: reviewed`, nothing rises
above EVC-3, and the register this writes says so in its own header.

What it buys is D-026's idea done honestly: the machine checks all of them
against a retrievable source and shows its working, so that a domain reviewer
confirms a *method and a sample* instead of re-deriving every value.

**The source.** `philschatz/anatomy-book` — OpenStax *Anatomy and Physiology*
1e, **CC BY 3.0**, per-chapter markdown. Chosen over the official
`openstax/osbooks-anatomy-physiology` deliberately: the official repo carries A&P
**2e** under **CC BY-NC-SA**, and NonCommercial sits outside this project's tier
scheme entirely — it forecloses the commercially-licensed build D-003 exists to
keep possible. 2e remains usable as T2 *reference-only* corroboration, because
checking a number against a book is not making a derivative work.

Editions differ, so every record says which edition answered it. A value
confirmed in 1e is not thereby confirmed in 2e.

    PYTHONPATH=src python3 tools/verify_findings.py           # run and report
    python3 tools/verify_findings.py --verify                 # re-hash, no fetch
    PYTHONPATH=src python3 tools/verify_findings.py --write   # write the register
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, 'src')

CACHE = os.path.join('vendor', 'textbooks')
REGISTER = os.path.join('ontology', 'VERIFICATION.json')

SOURCE = {
    'name': 'OpenStax Anatomy and Physiology 1e',
    'repo': 'philschatz/anatomy-book',
    'ref': 'master',
    'base': 'https://raw.githubusercontent.com/philschatz/anatomy-book/master',
    'path': 'contents/{module}.md',
    'edition': '1e (2014)',
    'licence': 'CC BY 3.0',
    'licence_tier': 'T0',
    'attribution': ('OpenStax College, Anatomy & Physiology. OpenStax CNX, '
                    'licensed CC BY 3.0.'),
}

# The second edition, admitted under D-034. Its licence is **CC BY-NC-SA**, so
# it sits at T1N: usable as content because this project is non-commercial and
# educational by commitment, segregated anyway because share-alike propagates to
# whoever reuses our output regardless of what we intend for it.
#
# It is here because it is *more complete*. 1e alone left ten of thirteen values
# uncovered, and the earlier refusal of NC material was costing real coverage
# for a restriction that does not bind this project.
SOURCE_2E = {
    'name': 'OpenStax Anatomy and Physiology 2e',
    'repo': 'openstax/osbooks-anatomy-physiology',
    'ref': 'main',
    'base': ('https://raw.githubusercontent.com/openstax/'
             'osbooks-anatomy-physiology/main'),
    'path': 'modules/{module}/index.cnxml',
    'edition': '2e',
    'licence': 'CC BY-NC-SA 4.0',
    'licence_tier': 'T1N',
    'attribution': ('OpenStax, Anatomy and Physiology 2e, licensed '
                    'CC BY-NC-SA 4.0.'),
}

SOURCES = (SOURCE, SOURCE_2E)

# Chapters that plausibly carry our findings. Listed rather than crawled: the
# book is 240 sections and a targeted read is honest about what was consulted.
CHAPTERS = {
    'm46549': 'The Process of Breathing',
    'm46551': 'The Lungs',
    'm46548': 'Organs and Structures of the Respiratory System',
    'm46521': 'Gas Exchange',
    'm46672': 'Cardiac Physiology',
    'm46676': 'Heart Anatomy',
    'm46661': 'Cardiac Cycle',
    'm46635': 'Blood Flow, Blood Pressure, and Resistance',
    'm46404': 'Cardiac Muscle Tissue',
}

# What to look for, per claim. A pattern is a *probe*, not an oracle: it finds
# the sentence, and the sentence is recorded verbatim so a human can disagree
# with the reading rather than only with the verdict.
PROBES = {
    'CLM:lung-tidal-volume': (r'tidal volume', 500, 'mL'),
    'CLM:lung-respiratory-rate': (r'respiratory rate|breaths per minute', 15, '/min'),
    'CLM:lung-anatomical-dead-space': (r'dead space', 150, 'mL'),
    'CLM:lung-frc': (r'functional residual capacity', 2400, 'mL'),
    'CLM:lung-tlc-male': (r'total lung capacity', 6000, 'mL'),
    'CLM:lung-tlc-female': (r'total lung capacity', 4200, 'mL'),
    'CLM:lung-alveolar-surface-classic': (r'surface area', 70, 'm2'),
    'CLM:lung-alveolar-number': (r'alveoli', 480_000_000, '1'),
    'CLM:diaphragm-tidal-contribution': (r'diaphragm', 70, '%'),
    'CLM:bronchial-tree-generations': (r'branch|generation', 23, '1'),
    'CLM:lung-diffusion-capacity-co': (r'diffusion|diffusing', 25, None),
    'CLM:lung-alveolar-ventilation': (r'alveolar ventilation', 4200, 'mL/min'),
    'CLM:blood-gas-barrier-thickness': (r'respiratory membrane|barrier', 0.3, 'um'),
}

NUMBER = re.compile(r'(\d[\d,]*(?:\.\d+)?)')


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_chapter(module: str, source: dict) -> tuple[str, str] | None:
    """Chapter text and its hash, from cache when present, or None if absent.

    Module ids do not line up between editions — 1e's `m46549` is not
    guaranteed to exist in 2e — so a 404 is an ordinary outcome, not an error.
    """
    os.makedirs(CACHE, exist_ok=True)
    tag = source['edition'].split()[0]
    path = os.path.join(CACHE, f'{tag}-{module}.txt')
    if not os.path.isfile(path):
        url = f'{source["base"]}/{source["path"].format(module=module)}'
        request = urllib.request.Request(
            url, headers={'User-Agent': 'project-human-organism/0.1'})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = response.read()
        except Exception:                                  # noqa: BLE001
            return None
        with open(path, 'wb') as fh:
            fh.write(data)
    with open(path, 'rb') as fh:
        raw = fh.read()
    return raw.decode('utf-8', 'replace'), sha256_bytes(raw)


# Lines that carry digits and no biology: image references and link targets.
# Rejected outright — the first version of this matcher accepted them and
# reported the diaphragm's tidal contribution as "disputed" on the strength of
# the numbers inside `2301_Major_Respiratory_Organs.jpg`.
NOISE = re.compile(r'!\[|\]\(|\.jpg|\.png|http')

# Markup that must be *stripped* rather than rejected. OpenStax tags every
# defined term with `{: data-type="term"}`, so rejecting sentences containing it
# threw away precisely the sentences that define the quantities — the second
# version of this matcher confirmed 2 of 13 for that reason alone.
MARKUP = re.compile(r'\{:[^}]*\}|</?[a-z][^>]*>|\*\*|\[|\]')

# A number only counts as a candidate value when a unit is attached to it. This
# is what separates "the book states 500 mL" from "the book contains a 500".
UNIT_ALTERNATIVES = (
    r'ml|millilit(?:er|re)s?|l\b|lit(?:er|re)s?|m2|m<sup>2</sup>|square met|'
    r'%|percent|per minute|breaths per minute|/min|micromet|\u03bcm|\u00b5m|um\b|'
    r'mmhg|million|billion|generations?')
VALUE = re.compile(r'(\d[\d,]*(?:\.\d+)?)\s*(?:to\s*\d[\d,]*\s*)?'
                   r'(' + UNIT_ALTERNATIVES + r')', re.I)


def sentences_about(text: str, pattern: str) -> list[str]:
    """Prose sentences on the topic that state a number **with a unit**.

    Three filters, each earned by a false positive in the first run: prose only
    (an image filename is not a claim), the topic within the same sentence, and
    a unit attached to the number. Without the last one the matcher found
    `blood-brain barrier` for a blood-gas barrier probe and called it a
    disagreement.
    """
    found = []
    for chunk in re.split(r'(?<=[.;])\s+', text):
        if NOISE.search(chunk):
            continue
        flat = re.sub(r'\s+', ' ', MARKUP.sub('', chunk)).strip()
        if not flat or len(flat) > 400:
            continue
        if re.search(pattern, flat, re.I) and VALUE.search(flat):
            found.append(flat)
    return found[:4]


# Which source units can answer which recorded unit. Comparing a count against
# a percentage is a category error, not a disagreement — "97 percent of the
# alveolar surface area" is not a rival figure for the *number* of alveoli, and
# the third version of this matcher called it one.
UNIT_FAMILY = {
    'mL': ('ml', 'millilit', 'lit', 'l'),
    'mL/min': ('ml', 'millilit', 'lit', 'per minute', '/min'),
    '/min': ('per minute', '/min', 'breaths per minute'),
    'm2': ('m2', 'square met', 'm<sup>2</sup>'),
    '%': ('%', 'percent'),
    'um': ('micromet', '\u03bcm', '\u00b5m', 'um'),
    '1': ('million', 'billion', 'generations', 'generation'),
}


def numbers_in(sentences: list[str], recorded_unit: str | None
               ) -> list[tuple[float, str]]:
    """Unit-bearing numbers whose unit could answer ours. A bare digit is not a
    stated value, and a value in the wrong dimension is not a rival."""
    allowed = UNIT_FAMILY.get(recorded_unit or '', ())
    values = []
    for sentence in sentences:
        for raw, unit in VALUE.findall(sentence):
            if allowed and not any(a in unit.lower() for a in allowed):
                continue
            try:
                values.append((float(raw.replace(',', '')), unit))
            except ValueError:
                continue
    return values


def verify(claims: dict) -> list[dict]:
    """One record per finding: what we hold, what the books say, the verdict.

    Both editions are read. They are separate sources with separate licences and
    separate module ids, and a value present in one is routinely absent from the
    other — so each record names the edition that answered it.
    """
    chapters = {}
    hashes = {}
    editions = {}
    for source in SOURCES:
        for module in CHAPTERS:
            got = fetch_chapter(module, source)
            if got is None:
                continue
            key = f'{source["edition"].split()[0]}:{module}'
            chapters[key], hashes[key] = got
            editions[key] = source

    records = []
    for claim_id, (pattern, recorded, unit) in sorted(PROBES.items()):
        claim = claims.get(claim_id)
        if claim is None:
            continue
        # Every chapter, not the first that matches anything. The first version
        # broke out on the earliest chapter containing the keyword, so lung
        # claims were answered from whichever section happened to come first in
        # dict order and the cardiac chapters were never read at all.
        hits, where = [], None
        for key, text in chapters.items():
            found = sentences_about(text, pattern)
            if not found:
                continue
            hits.extend(found)
            # Prefer the section that actually yields a comparable value, not
            # merely the first that mentions the words.
            if where is None or (not numbers_in(
                    sentences_about(chapters[where], pattern), unit)
                    and numbers_in(found, unit)):
                where = key
        if not hits:
            records.append({
                'claim': claim_id, 'recorded': recorded, 'unit': unit,
                'outcome': 'not covered',
                'note': ('No sentence in the consulted chapters of either '
                         'edition states this with a number. Not a refutation '
                         '— an absence of coverage in these sources.'),
                'consulted': sorted(CHAPTERS.values()),
                'editions_read': [s['edition'] for s in SOURCES]})
            continue
        values = numbers_in(hits, unit)
        # Purely relative, with no absolute floor. The floor was `max(1.0, 5%)`,
        # which for a value of 0.3 µm admitted anything within ±1.0 — so the
        # book's 0.5 µm was reported as *confirming* our 0.3, a false
        # confirmation, which is the single worst thing this register can
        # contain. It also let a child's respiratory rate of 14 confirm an
        # adult value of 15. A tolerance must scale with the quantity or it
        # stops being a tolerance.
        matched = any(abs(v - float(recorded)) <= 0.05 * abs(float(recorded))
                      for v, _u in values)
        # Three outcomes, and the third one is the important one. A keyword
        # match cannot tell "the number of alveoli" from "97 percent of the
        # alveolar surface area", so where the tool has found comparable
        # sentences but cannot establish they are about the same quantity, it
        # withholds rather than accusing. A false "disputed" in this register
        # would be worse than no register at all.
        if matched:
            outcome = 'confirmed'
        elif values:
            outcome = 'candidate evidence, verdict withheld'
        else:
            outcome = 'not covered'
        records.append({
            'claim': claim_id, 'recorded': recorded, 'unit': unit,
            'outcome': outcome,
            'edition': editions[where]['edition'],
            'licence_tier': editions[where]['licence_tier'],
            'section': f'{where} — {CHAPTERS[where.split(":", 1)[1]]}',
            'section_sha256': hashes[where],
            'values_in_source': [f'{v} {u}' for v, u in values[:8]],
            'sentences': hits,
        })
    return records


def main(argv: list[str]) -> int:
    from homeo.evidence import EvidenceService                # noqa: PLC0415
    from homeo.graph import Graph                              # noqa: PLC0415
    from homeo.scale import ScaleService                       # noqa: PLC0415
    from homeo.substrate import load                           # noqa: PLC0415

    graph = Graph(load('ontology'))
    evidence = EvidenceService(graph, ScaleService(graph))
    claims = {c.id: c for c in evidence.all_claims() if c.is_evidence}
    records = verify(claims)

    by_outcome: dict[str, int] = {}
    for record in records:
        by_outcome[record['outcome']] = by_outcome.get(record['outcome'], 0) + 1
    print(f'{len(claims)} findings in the substrate; {len(records)} probed')
    for outcome, count in sorted(by_outcome.items()):
        print(f'  {outcome:<12} {count}')
    for record in records:
        if record['outcome'] != 'confirmed' and record.get('sentences'):
            print(f'\n  {record["outcome"].upper()} — {record["claim"]}: '
                  f'we hold {record["recorded"]} {record["unit"] or ""}; '
                  f'comparable values found: '
                  f'{record["values_in_source"] or "none"}')
            print(f'    "{record["sentences"][0][:150]}"')

    if '--write' not in argv:
        print('\nnot written — re-run with --write')
        return 0

    with open(REGISTER, 'w', encoding='utf-8') as fh:
        json.dump({
            'note': (
                'VERIFICATION IS NOT REVIEW. Every record here was produced by '
                'an automated actor checking a value against an openly licensed '
                'textbook. It does not approve anything, it does not change any '
                'review state, and the review deficit is exactly what it was '
                'before this ran. No claim may rise above EVC-3 on the strength '
                'of it (BR-002, D-017, D-033).'),
            'verified_on': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'sources': list(SOURCES),
            'chapters_consulted': CHAPTERS,
            'summary': by_outcome,
            'records': records}, fh, indent=1, ensure_ascii=False)
    print(f'\nwrote {REGISTER}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
