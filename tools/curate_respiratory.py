#!/usr/bin/env python3
"""Respiratory findings — the first content that is not a definition.

The substrate holds 423 claims. **414 of them are definitions** and 9 are
findings. That ratio is the project's real state: it knows what words mean and
almost nothing about what a body does. Every mechanism built for findings —
the evidence ladder, conflict representation, units, the population field, the
promotion gates — has been exercised against nine records, all of them
cardiovascular, all qualitative.

This script writes the other kind. One subsystem, real physiology, on the
evidence ladder (D-021's biological register), with quantities that carry UCUM
units and a population that actually discriminates.

**It is a test and it is allowed to fail.** The question is whether the claim
record can hold biology. If a value needs a field the schema lacks, or the
population field cannot separate two genuine measurements, that is the finding
— to be recorded, not worked around.

Three things are deliberate:

- **Nothing is graded above EVC-4.** BR-002 forbids an automated actor from
  assigning EVC-1 or EVC-2, and the ladder does not admit `reference textbook`
  at EVC-3 at all. Textbook physiology is APPROXIMATED or INFERRED, which is
  what it is.
- **The population field discriminates.** CH-05 found `"unspecified in source"`
  on 94% of seeded claims, making the field decorative. Total lung capacity
  differs by sex by about 30%; recording one number for "adults" would be the
  same failure with better prose.
- **One pair genuinely conflicts.** Alveolar surface area is ~70 m² by the
  classic estimate and ~130 m² by design-based stereology. That disagreement is
  methodological and unresolved, so it is EVC-7 on both sides with each
  pointing at the other. The system never picks (FR-EVID-006), and until now it
  never had a real chance not to.

No clinical framing anywhere (BR-019): these are reference values for a healthy
population, never an interpretation of anyone.

    PYTHONPATH=src python3 tools/curate_respiratory.py --write
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, 'src')

from homeo.agents import AgentRuntime                      # noqa: E402
from homeo.curation import CurationService                 # noqa: E402

GUYTON = {'citation': 'Hall JE & Hall ME, Guyton and Hall Textbook of Medical '
                      'Physiology, 14th ed.',
          'identifier': 'ISBN:9780323597128', 'licence_tier': 'T2'}
WEST = {'citation': "West JB & Luks AM, West's Respiratory Physiology: The "
                    'Essentials, 11th ed.',
        'identifier': 'ISBN:9781975139186', 'licence_tier': 'T2'}
OCHS = {'citation': 'Ochs M et al., The number of alveoli in the human lung, '
                    'Am J Respir Crit Care Med 169:120-124, 2004',
        'identifier': 'PMID:14512270', 'licence_tier': 'T2'}
# Added after the verification pass (D-033). The only openly licensed source
# here: CC BY 3.0, so a reader can actually open it and check. Guyton and West
# are T2 reference-only — citable, but nobody can follow the citation.
OPENSTAX = {'citation': 'OpenStax College, Anatomy & Physiology 1e, OpenStax '
                        'CNX (CC BY 3.0)',
            'identifier': 'https://github.com/philschatz/anatomy-book',
            'licence_tier': 'T0'}
GEHR = {'citation': 'Gehr P, Bachofen M, Weibel ER, The normal human lung: '
                    'ultrastructure and morphometric estimation of diffusion '
                    'capacity, Respir Physiol 32:121-140, 1978',
        'identifier': 'PMID:644146', 'licence_tier': 'T2'}

LUNG = 'UBERON:0002048'
DIAPHRAGM = 'UBERON:0001103'
TREE = 'UBERON:0007196'
BRONCHUS = 'UBERON:0002182'

ADULT = 'healthy adult, both sexes, at rest, sea level'
ADULT_M = 'healthy adult male, 20-40 years, at rest, sea level'
ADULT_F = 'healthy adult female, 20-40 years, at rest, sea level'

# (id, subject, predicate, object, unit, class, source_type, sources,
#  population, limitations, conflicts_with, conditions)
#
# `object` as a number makes it a quantity to INV-04, which then requires the
# unit — and INV-07 then requires measurement **conditions**. That column was
# absent from the first version of this table and the validator asked for it on
# all fifteen quantities. It was right to: "tidal volume is 500 mL" is not a
# fact about a body until it says at rest, upright, breathing air at sea level.
# The whole point of writing findings was to find out what the record demands
# that prose does not, and this is the answer.
FINDINGS = [
    ('CLM:lung-function-gas-exchange', LUNG, 'has_function',
     'Exchanges oxygen and carbon dioxide between alveolar gas and pulmonary '
     'capillary blood by passive diffusion across the blood-gas barrier',
     None, 'EVC-4', 'reference textbook', [WEST], ADULT,
     'A statement of the organ\'s principal function. Ventilation, perfusion '
     'and diffusion each have their own limiting conditions, none represented '
     'here.', ()),

    ('CLM:lung-tidal-volume', LUNG, 'has_quantity', 500, 'mL',
     'EVC-4', 'reference textbook', [OPENSTAX, GUYTON, WEST], ADULT,
     'A rounded reference value for quiet breathing. Tidal volume varies with '
     'body size, posture and metabolic demand; ~7 mL/kg is the size-scaled '
     'form and is not represented as a separate claim.', (),
     {'preparation': 'in vivo',
      'notes': 'quiet breathing, upright, breathing air at sea level'}),

    ('CLM:lung-respiratory-rate', LUNG, 'has_quantity', 15, '/min',
     'EVC-4', 'reference textbook', [OPENSTAX, GUYTON], ADULT,
     'Corrected by the verification pass (D-033). The first version recorded 14 '
     'as "the midpoint of the commonly cited 12-16 range"; OpenStax states '
     '"12 to 18 breaths per minute" for adults, so the range was wrong and the '
     'midpoint with it. Sources genuinely differ on the upper bound — Guyton '
     'gives 12-16, OpenStax 12-18 — and the recorded value is the midpoint of '
     'the wider, openly checkable range. The range is the honest form; a single '
     'value is a limitation of the claim record, not of the biology.',
     (),
     {'preparation': 'in vivo',
      'notes': 'awake, at rest, upright, normocapnic'}),

    ('CLM:lung-anatomical-dead-space', TREE, 'has_quantity', 150, 'mL',
     'EVC-4', 'reference textbook', [WEST], ADULT,
     'The conducting-airway volume that does not participate in gas exchange, '
     'approximated as 2.2 mL per kg body weight. Physiological dead space is a '
     'different quantity, measured by a different method, and is not this '
     'value.', (),
     {'preparation': 'in vivo',
      'notes': "Fowler's single-breath nitrogen washout; scales with body "
               'weight'}),

    ('CLM:lung-frc', LUNG, 'has_quantity', 2400, 'mL',
     'EVC-4', 'reference textbook', [GUYTON], ADULT,
     'Functional residual capacity: the volume remaining after a quiet '
     'expiration, where inward lung recoil balances outward chest-wall recoil. '
     'Posture-dependent; supine values are substantially lower and are not '
     'represented.', (),
     {'preparation': 'in vivo',
      'notes': 'upright, end of a quiet expiration; helium dilution or body plethysmography'}),

    # The population pair. Two claims, same predicate, same subject, different
    # populations — not a conflict. If `population` could not tell them apart
    # the model would have to call one of them wrong.
    ('CLM:lung-tlc-male', LUNG, 'has_quantity', 6000, 'mL',
     'EVC-4', 'reference textbook', [GUYTON], ADULT_M,
     'Total lung capacity for the stated population. Scales with standing '
     'height more strongly than with sex alone; height is not represented in '
     'the population field, which is a limit of this record.', (),
     {'preparation': 'in vivo',
      'notes': 'maximal inspiration, upright, body plethysmography'}),

    ('CLM:lung-tlc-female', LUNG, 'has_quantity', 4200, 'mL',
     'EVC-4', 'reference textbook', [GUYTON], ADULT_F,
     'Total lung capacity for the stated population. Differs from the male '
     'reference by roughly 30%, largely through body size. This is a different '
     'population, not a competing measurement.', (),
     {'preparation': 'in vivo',
      'notes': 'maximal inspiration, upright, body plethysmography'}),

    # The genuine conflict. Both retained, both EVC-7, each naming the other.
    ('CLM:lung-alveolar-surface-classic', LUNG, 'has_quantity', 70, 'm2',
     'EVC-7', 'reference textbook', [OPENSTAX, WEST, GUYTON], ADULT,
     'The classic textbook estimate of the alveolar gas-exchange surface. '
     'Design-based stereology gives roughly twice this figure; the '
     'disagreement is methodological and unresolved, so both are retained.',
     ('CLM:lung-alveolar-surface-stereology',),
     {'preparation': 'ex vivo',
      'notes': 'fixed lung, light-microscopic morphometry; the fixation and '
               'shrinkage assumptions are where this diverges from the '
               'stereological figure'}),

    ('CLM:lung-alveolar-surface-stereology', LUNG, 'has_quantity', 130, 'm2',
     'EVC-7', 'primary research', [GEHR, OCHS], ADULT,
     'Morphometric estimate from design-based stereology on fixed lungs. '
     'Depends on fixation and on the assumed shrinkage correction, which is '
     'the substance of the disagreement with the classic figure.',
     ('CLM:lung-alveolar-surface-classic',),
     {'preparation': 'ex vivo',
      'notes': 'perfusion-fixed lung, design-based stereology with shrinkage '
               'correction'}),

    ('CLM:lung-alveolar-number', LUNG, 'has_quantity', 480_000_000, '1',
     'EVC-5', 'primary research', [OCHS], ADULT,
     'Mean alveolar number from design-based stereology in six adult lungs '
     '(range 274-790 million). The mean is recorded because the record holds '
     'one value; the spread is wider than the mean is precise, and the value '
     'should not be read as a population constant.', (),
     {'preparation': 'ex vivo',
      'notes': 'perfusion-fixed lungs, design-based stereology, physical disector; n=6'}),

    ('CLM:diaphragm-function-inspiration', DIAPHRAGM, 'has_function',
     'The principal muscle of quiet inspiration: contraction flattens the dome, '
     'increasing thoracic volume and lowering intrapleural pressure',
     None, 'EVC-4', 'reference textbook', [WEST], ADULT,
     'Accessory muscles contribute increasingly with effort and are not '
     'represented. The claim is about quiet breathing only.', ()),

    ('CLM:diaphragm-tidal-contribution', DIAPHRAGM, 'has_quantity', 70, '%',
     'EVC-5', 'reference textbook', [WEST], ADULT,
     'Approximate share of resting tidal volume attributable to diaphragmatic '
     'descent. Inferred from the commonly cited 60-80% range; posture and '
     'abdominal compliance both move it.', (),
     {'preparation': 'in vivo',
      'notes': 'supine and upright quiet breathing; the share moves with posture'}),

    ('CLM:diaphragm-innervation-phrenic', DIAPHRAGM, 'has_property',
     'Innervated by the phrenic nerve, arising from cervical roots C3-C5',
     None, 'EVC-4', 'reference textbook', [GUYTON], ADULT,
     'A structural fact of gross anatomy stated at nerve-root resolution. '
     'Contributions from C3 and C5 vary between individuals.', ()),

    ('CLM:bronchial-tree-generations', TREE, 'has_quantity', 23, '1',
     'EVC-4', 'reference textbook', [WEST], ADULT,
     'Weibel symmetric-branching model: airway generations from trachea to '
     'alveolar sacs. Real branching is asymmetric, and the count is a property '
     'of the model rather than of any particular lung.', (),
     {'preparation': 'ex vivo',
      'notes': 'Weibel symmetric-branching model of a resin cast; a model property, not a measurement of one lung'}),

    ('CLM:bronchial-tree-conducting-generations', TREE, 'has_quantity', 16, '1',
     'EVC-4', 'reference textbook', [WEST], ADULT,
     'Generations 0-16 conduct without gas exchange; 17-23 are the respiratory '
     'zone. Same model dependence as the total generation count.', (),
     {'preparation': 'ex vivo',
      'notes': 'as above — the conducting/respiratory boundary is a feature of the same model'}),

    ('CLM:main-bronchus-asymmetry', BRONCHUS, 'has_property',
     'The right main bronchus is wider, shorter and more vertical than the '
     'left, which is why inhaled material reaches the right lung preferentially',
     None, 'EVC-4', 'reference textbook', [GUYTON], ADULT,
     'A structural asymmetry with a well-known consequence. Stated as anatomy; '
     'no clinical inference is drawn from it here.', ()),

    ('CLM:lung-diffusion-capacity-co', LUNG, 'has_quantity', 25,
     'mL/min/mmHg', 'EVC-4', 'reference textbook', [WEST], ADULT,
     'Diffusing capacity for carbon monoxide at rest — the standard proxy for '
     'the blood-gas barrier\'s conductance, because CO uptake is '
     'diffusion-limited. Rises severalfold with exercise; the resting value is '
     'not a maximum.', (),
     {'preparation': 'in vivo',
      'notes': 'single-breath carbon monoxide method, at rest, seated'}),

    ('CLM:lung-alveolar-ventilation', LUNG, 'has_quantity', 4200, 'mL/min',
     'EVC-5', 'reference textbook', [GUYTON], ADULT,
     'Derived as (tidal volume - dead space) x respiratory rate from the '
     'reference values above. Inferred rather than measured, and it inherits '
     'every approximation in its inputs — which is why it is EVC-5 and its '
     'components are EVC-4.', (),
     {'preparation': 'in vivo',
      'notes': 'derived, not measured: computed from the resting tidal volume, dead space and rate recorded here'}),

    ('CLM:blood-gas-barrier-thickness', LUNG, 'has_quantity', 0.3, 'um',
     'EVC-4', 'primary research', [GEHR], ADULT,
     'Harmonic mean thickness of the tissue barrier between alveolar gas and '
     'capillary blood in its thinnest regions. The barrier is not uniform, and '
     'a single thickness is a deliberate simplification of a distribution.',
     (),
     {'preparation': 'ex vivo',
      'notes': 'perfusion-fixed lung, electron-microscopic morphometry; harmonic mean over the thin portions of the barrier'}),

    ('CLM:lung-perfusion-cardiac-output', LUNG, 'has_property',
     'Receives the entire cardiac output, unlike any other organ, so pulmonary '
     'blood flow equals systemic blood flow in the steady state',
     None, 'EVC-4', 'reference textbook', [WEST], ADULT,
     'True in the steady state and at the whole-organ level. Bronchial '
     'circulation and physiological shunt are small exceptions not represented '
     'here.', ()),
]


def build(write: bool) -> int:
    curation = CurationService([], queue_ceiling=len(FINDINGS) * 2 + 32)
    runtime = AgentRuntime(curation)
    # AGT-2 is the Evidence agent. Claims about what a structure does are
    # evidence, not anatomy, so AGT-3 would be refused — the same contract that
    # refused curate_pancreas.py's first attempt to do both under one agent.
    run = runtime.start('AGT-2', 'record respiratory findings on the evidence '
                                 'ladder')

    tasks = []
    for (cid, subject, predicate, obj, unit, klass, source_type, sources,
         population, limitations, conflicts, *rest) in FINDINGS:
        conditions = rest[0] if rest else None
        claim = {
            'id': cid, 'subject': subject, 'predicate': predicate,
            'object': obj,
            # The register split (D-021). These are findings about a body, not
            # statements about what a word means, so they belong on the
            # evidence ladder and are citable as evidence.
            'kind': 'biological',
            'evidence_class': klass, 'source_type': source_type,
            'sources': sources, 'species': 'Homo sapiens',
            'population': population, 'date_asserted': '2026-07-28',
            'review_state': 'provisional', 'assigned_by': 'agent:physiology',
            'limitations': limitations,
        }
        if unit:
            claim['unit'] = unit
        if conflicts:
            claim['conflicts_with'] = list(conflicts)
        if conditions:
            claim['conditions'] = conditions
        tid = runtime.propose(
            run, kind='claim', subsystem='respiratory', level=3,
            payload={'claim': claim},
            sources=[s['identifier'] for s in sources],
            rationale=f'{predicate} of {subject}, graded {klass}.')
        tasks.append((tid, cid))

    print(f'proposed {len(tasks)} findings under {run.agent} ({run.id})')

    admitted = []
    for tid, label in tasks:
        try:
            admitted.append(curation.admit_provisional(
                tid, 'agent:physiology',
                'Reference physiology from standard texts and two morphometric '
                'papers. No human reviewer is available; admitted '
                'provisionally under D-017.'))
        except Exception as exc:                          # noqa: BLE001
            print(f'  REFUSED {label}: {exc}')

    quantities = sum(1 for f in FINDINGS if isinstance(f[3], (int, float)))
    conflicting = sum(1 for f in FINDINGS if f[10])
    populations = {f[8] for f in FINDINGS}
    print(f'admitted {len(admitted)} provisionally, 0 reviewed')
    print(f'  {quantities} quantities with units, {conflicting} in conflict, '
          f'{len(populations)} distinct populations')
    print(f'review deficit now: {curation.admission_summary()}')

    if not write:
        print('\ndry run — nothing written. Re-run with --write.')
        return 0

    claims = [p['payload']['claim'] for p in curation.provisional_payloads()
              if 'claim' in p['payload']]
    os.makedirs('ontology/respiratory', exist_ok=True)
    _dump('ontology/respiratory/claims.json', claims)
    _dump('ontology/respiratory/ADMISSIONS.json', {
        'note': ('The first findings this substrate holds that are not '
                 'definitions. Proposed by AGT-2, admitted by '
                 'agent:physiology, reviewed by nobody (D-017, D-030). '
                 'Reference values for a healthy population — never an '
                 'interpretation of any individual (BR-019).'),
        'run': run.id, 'reviewed': 0, 'provisional': len(admitted),
        'quantities': quantities, 'conflicting_pairs': conflicting // 2,
        'populations': sorted(populations),
        'admissions': [a.as_dict() for a in admitted]})
    print(f'\nwrote {len(claims)} claims — all provisional')
    return 0


def _dump(path: str, obj) -> None:
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    sys.exit(build('--write' in sys.argv))
