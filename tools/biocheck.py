#!/usr/bin/env python3
"""biocheck.py — execute the BIO_Validation_Framework invariants against ontology/.

Files are the canonical serialization (TECH_Data_Design); indexes are derived.
This harness reads the substrate and checks the INV-01..INV-14 rules defined in
docs/BIO_Validation_Framework.md. Nothing is ever repaired here — a violation is
a finding, not a merge.

Usage:
  python3 tools/biocheck.py <ontology-dir> [--strict] [--json OUT]
  python3 tools/biocheck.py <ontology-dir> --coverage      declared vs populated
  python3 tools/biocheck.py <ontology-dir> --ladder PATH   override the EVC doc
  python3 tools/biocheck.py <ontology-dir> --relations PATH override the relation doc
  python3 tools/biocheck.py --selftest                     negative tests

Severity: blocking invariants produce errors; advisory ones produce warnings.
Exit: 0 clean, 1 errors (or warnings under --strict), 2 usage.

Realizes the Validation module in full: FR-VALD-001 (every INV has a check here),
FR-VALD-002 (--selftest), FR-VALD-003 (blocking vs advisory), FR-VALD-004 (runs
at commit, in CI, and pre-release), FR-VALD-005 (messages name the biological
problem), FR-VALD-006 (results recorded per release by tools/release.py),
FR-VALD-007 (the closing note on what validation does not establish),
FR-VALD-008 (scoped runs), FR-VALD-009 (shares specgraph's idiom).
Also enforces, on behalf of their owning modules: FR-REL-004 (relation
admissibility), FR-REL-005 (causal gating), FR-SCAL-004 (skip justification),
FR-SCAL-007 (representation mode), FR-SPAT-003/FR-SPAT-004/FR-SPAT-005 (geometry
binding, kind, licence tier), FR-EVID-009 (tier integrity), FR-PHYS-003
(input/output resolution), FR-PHYS-004 (timescale domain), FR-PHYS-005 (spanning
declarations).

Written in specgraph.py's idiom deliberately — two validators with different
conventions is one validator people misread (FR-VALD-009).

Stdlib only.
"""
import json, os, re, sys

# Levels at which each relation type may hold. None = any level pair.
# Mirrors BIO_Anatomical_Ontology's relationship table (INV-01).
ADMISSIBLE = {
    'part_of':          [(1, 0), (2, 0), (3, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7)],
    'member_of':        [(3, 2), (7, 6)],
    'composed_of':      [(3, 5), (4, 5), (5, 6), (4, 4)],
    'located_in':       None,
    'adjacent_to':      'same-level',
    'connected_to':     'same-level',
    'innervated_by':    [(3, 3), (4, 3), (4, 4), (3, 4)],
    'vascularized_by':  [(3, 3), (4, 3), (4, 4), (3, 4)],
    'drained_by':       [(3, 3), (4, 3), (4, 4), (3, 4)],
    'produces':         [(3, 9), (7, 9), (4, 9)],
    'consumes':         None,
    'transports':       None,
    'converts':         None,
    'responds_to':      None,
    'regulated_by':     None,
    'activates':        None,
    'inhibits':         None,
    'differentiates_into': [(7, 7)],
    'originates_from':  None,
    'realizes':         [(9, 10)],
    'participates_in':  None,
    'causes':           None,
    'contributes_to':   None,
    'associated_with':  None,
    # A class and its superclass describe the same kind of thing at the same
    # granularity. A cross-level `is_a` is a classification error (D-023).
    'is_a':             'same-level',
}
HUMAN = ('Homo sapiens', 'not applicable')
STRONG = ('EVC-1', 'EVC-2')

# Which source types may support which classes, and how many independent sources
# each requires (INV-07).
#
# This is a FALLBACK. The authority is the table in
# docs/BIO_Evidence_and_Provenance.md, which is parsed by load_ladder() and used
# in preference; when both are available and they disagree, that divergence is
# itself an error (INV-16).
#
# The check exists because this project shipped exactly that divergence: the
# ladder forbade textbook-sourced EVC-1 in prose while this table permitted it,
# and two claims were graded VERIFIED on textbooks as a result. A rule stated in
# one place and enforced in another will drift, and the drift is invisible
# precisely because both halves look correct on their own (D-013).
CLASS_SOURCE = {
    'EVC-1': ('primary research', 'systematic review'),
    'EVC-2': ('anatomical atlas', 'curated database', 'primary research',
              'reference textbook', 'systematic review'),
    'EVC-3': ('curated database', 'derived model', 'primary research'),
    'EVC-4': ('anatomical atlas', 'derived model', 'primary research',
              'reference textbook'),
    'EVC-5': ('derived model', 'expert assertion', 'primary research',
              'reference textbook'),
    'EVC-6': ('expert assertion', 'primary research', 'reference textbook'),
    'EVC-7': ('anatomical atlas', 'curated database', 'derived model',
              'expert assertion', 'primary research', 'reference textbook',
              'systematic review'),
}
MIN_SOURCES = {'EVC-1': 2, 'EVC-2': 2, 'EVC-3': 1, 'EVC-4': 1, 'EVC-5': 1,
               'EVC-6': 1, 'EVC-7': 2, 'EVC-8': 0}

# ECO -> EVC, for claims imported from databases that annotate their evidence.
# A FALLBACK, exactly like CLASS_SOURCE above: the authority is the mapping
# table in the ladder document, and a divergence between the two is an INV-16
# error. The same trap, guarded the same way (D-013).
ECO_TO_EVC = {
    'ECO:0000006': 'EVC-2',   # experimental evidence
    'ECO:0000033': 'EVC-5',   # author statement, traceable reference
    'ECO:0000034': 'EVC-6',   # author statement, no traceable support
    'ECO:0000203': 'EVC-6',   # automatic assertion
    'ECO:0000205': 'EVC-5',   # curator inference
    'ECO:0000501': 'EVC-6',   # evidence used in automatic assertion
}
LADDER_DOC = os.path.join('docs', 'BIO_Evidence_and_Provenance.md')
ONTOLOGY_DOC = os.path.join('docs', 'BIO_Anatomical_Ontology.md')
UCUM_OK = re.compile(r'^[A-Za-z0-9%\[\]/*.\-^{}()]+$')


def load_relations(path=ONTOLOGY_DOC):
    """Parse the relation vocabulary from the document that defines it.

    Returns {relation: inverse} or None when unreachable. Rows naming two
    relations at once (`activates` / `inhibits`) are split, because the document
    pairs them for readability and the code holds them separately.
    """
    if not os.path.isfile(path):
        return None
    out = {}
    for line in open(path, encoding='utf-8'):
        if not line.startswith('| `'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 5:
            continue
        rels = [r.strip(' `') for r in cells[0].split('/')]
        invs = [i.strip(' `') for i in cells[1].split('/')]
        if len(rels) != len(invs):
            continue
        for rel, inv in zip(rels, invs):
            if rel and inv:
                out[rel] = inv
    return out or None


def relation_divergence(doc_relations, code_inverses=None,
                        path=ONTOLOGY_DOC):
    """INV-19: the documented relation vocabulary and the code must agree.

    The check exists because its absence let a defect through. `is_a` was added
    to INVERSES and ADMISSIBLE in code and not to the document — the same
    doc/code divergence D-013 recorded for the evidence ladder, committed again
    inside the change whose purpose was to add a relation. INV-16 guards the
    ladder; nothing guarded this table, so nothing noticed.

    `code_inverses` is injectable so the negative tests can diverge it without
    editing the module under test.
    """
    out = []
    if doc_relations is None:
        out.append(('warn', 'INV-19',
                    f'{path} not found; the relation vocabulary is '
                    f'unverified. The document is the authority'))
        return out
    try:
        if code_inverses is None:
            sys.path.insert(0, 'src')
            from homeo.substrate import INVERSES as code_inverses  # noqa: PLC0415
    except ImportError:
        out.append(('warn', 'INV-19',
                    'src/homeo/substrate.py not importable; the relation '
                    'vocabulary could not be cross-checked'))
        return out
    for rel in sorted(set(doc_relations) | set(code_inverses)):
        mine, theirs = code_inverses.get(rel), doc_relations.get(rel)
        if theirs is None:
            out.append(('error', 'INV-19',
                        f'{rel}: in the code vocabulary but absent from '
                        f'{path} — a relation the document does not '
                        f'define is a relation nobody agreed to'))
        elif mine is None:
            out.append(('error', 'INV-19',
                        f'{rel}: defined in {path} but absent from the '
                        f'code vocabulary — edges of this type cannot be typed'))
        elif mine != theirs:
            out.append(('error', 'INV-19',
                        f'{rel}: code says the inverse is {mine!r}, '
                        f'{path} says {theirs!r} — the document is the '
                        f'authority'))
    for rel in sorted(set(ADMISSIBLE) - set(doc_relations)):
        out.append(('error', 'INV-19',
                    f'{rel}: has an admissibility rule in the checker but no '
                    f'row in {path}'))
    return out


def load_ladder(path=LADDER_DOC):
    """Parse the EVC ladder from the document that defines it.

    Returns (class_source, min_sources) or (None, None) when the document is not
    reachable — biocheck must remain runnable against a bare substrate.
    """
    if not os.path.isfile(path):
        return None, None
    sources, minimums = {}, {}
    for line in open(path, encoding='utf-8'):
        if not line.startswith('| EVC-'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 6:
            continue
        evc = cells[0]
        types = tuple(sorted(t.strip(' `') for t in cells[3].split(',')
                             if t.strip(' `') and not t.strip().startswith('none')))
        try:
            minimums[evc] = int(cells[4])
        except ValueError:
            continue
        if types:
            sources[evc] = types
    return (sources or None), (minimums or None)


def load_eco_mapping(path=LADDER_DOC):
    """Parse the ECO mapping from the document that defines it.

    Same shape as load_ladder, and for the same reason: a rule stated in one
    place and enforced in another will drift, invisibly, because both halves
    look correct on their own.
    """
    if not os.path.isfile(path):
        return None
    mapping = {}
    for line in open(path, encoding='utf-8'):
        if not line.startswith('| ECO:'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 3:
            continue
        target = cells[2]
        if target.startswith('EVC-'):
            mapping[cells[0]] = target
    return mapping or None


def eco_divergence(doc_mapping, path=LADDER_DOC):
    """INV-16, extended to the ECO table."""
    out = []
    if doc_mapping is None:
        out.append(('warn', 'INV-16',
                    f'{path} carries no ECO mapping; the built-in table '
                    f'is unverified. The document is the authority'))
        return out
    for eco in sorted(set(ECO_TO_EVC) | set(doc_mapping)):
        mine, theirs = ECO_TO_EVC.get(eco), doc_mapping.get(eco)
        if mine != theirs:
            out.append(('error', 'INV-16',
                        f'{eco}: checker maps to {mine}, {path} maps to '
                        f'{theirs} — the document is the authority'))
    return out


def ladder_divergence(doc_sources, doc_minimums):
    """INV-16: the checker's fallback must agree with the document.

    Reported as errors rather than warnings. A checker that silently disagrees
    with the rule it enforces is worse than no checker, because it produces
    green runs that mean nothing.
    """
    out = []
    if doc_sources is None:
        out.append(('warn', 'INV-16',
                    f'{LADDER_DOC} not found; using the built-in class table '
                    f'unverified. The document is the authority'))
        return out
    for evc in sorted(set(CLASS_SOURCE) | set(doc_sources)):
        mine = tuple(sorted(CLASS_SOURCE.get(evc, ())))
        theirs = tuple(sorted(doc_sources.get(evc, ())))
        if mine != theirs:
            out.append(('error', 'INV-16',
                        f'{evc}: checker admits {mine or "()"} but '
                        f'{LADDER_DOC} admits {theirs or "()"} — the document '
                        f'is the authority and the checker must match it'))
    for evc in sorted(set(MIN_SOURCES) | set(doc_minimums or {})):
        mine = MIN_SOURCES.get(evc)
        theirs = (doc_minimums or {}).get(evc)
        if mine != theirs:
            out.append(('error', 'INV-16',
                        f'{evc}: checker requires {mine} independent source(s), '
                        f'{LADDER_DOC} requires {theirs}'))
    return out


def load(root):
    """Read every JSON file under root, keyed by its basename stem."""
    data = {}
    for dp, _, fns in os.walk(root):
        for fn in sorted(fns):
            if not fn.endswith('.json'):
                continue
            path = os.path.join(dp, fn)
            try:
                obj = json.load(open(path, encoding='utf-8'))
            except (OSError, ValueError) as e:
                data.setdefault('_errors', []).append((path, str(e)))
                continue
            data.setdefault(fn[:-5], []).extend(obj if isinstance(obj, list) else [obj])
    return data


def levels_of(entities):
    """entity id -> level; a spanning entity maps to its shallowest listed level."""
    out = {}
    for e in entities:
        if 'level' in e:
            out[e['id']] = e['level']
        elif e.get('spatial_scale'):
            out[e['id']] = min(e['spatial_scale'])
    return out


def is_quantity(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return True
    if isinstance(v, dict):
        return any(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v.values())
    return False


def check(data, ladder=None, minimums=None):
    """Run every invariant. Returns a list of (level, inv, message).

    `ladder`/`minimums` come from the document when available (load_ladder);
    the module constants are the fallback, and INV-16 checks they agree.
    """
    f = []
    class_source = ladder or CLASS_SOURCE
    min_sources = minimums or MIN_SOURCES
    ents = data.get('entities', [])
    rels = data.get('relationships', [])
    claims = data.get('claims', [])
    procs = data.get('processes', [])
    spatials = data.get('spatial_identities', [])
    scls = data.get('scale_contracts', [])
    declared = (data.get('declared_depth') or [{}])[0]
    # authorities.json is a flat list, so load() has already spread it
    authorities = set(data.get('authorities') or [])

    by_id = {e['id']: e for e in ents}
    lvl = levels_of(ents)
    claim_ids = {c['id'] for c in claims}
    scl_by_level = {s['level']: s for s in scls}

    for path, msg in data.get('_errors', []):
        f.append(('error', 'SCHEMA', f'{path}: unparseable ({msg})'))

    # INV-10 identifier integrity
    for e in ents:
        if e.get('minted') and not e.get('minted_reason'):
            f.append(('error', 'INV-10', f'{e["id"]}: minted without a minted_reason'))
        if not e.get('minted') and e['id'].startswith('HOX:'):
            f.append(('error', 'INV-10', f'{e["id"]}: local id not flagged as minted'))
        for x in e.get('xrefs', []):
            if x['authority'] not in authorities:
                f.append(('error', 'INV-10', f'{e["id"]}: unregistered authority {x["authority"]}'))
            if not x.get('pinned_version'):
                f.append(('error', 'INV-10', f'{e["id"]}: xref {x["authority"]} has no pinned version'))

    # INV-02 hierarchical consistency: single parent, acyclic
    parent = {}
    for e in ents:
        p = e.get('part_of')
        if p:
            if p not in by_id:
                f.append(('error', 'INV-02', f'{e["id"]}: part_of names undefined entity {p}'))
            parent[e['id']] = p
    pc = {}
    for r in rels:
        if r['type'] == 'part_of':
            pc.setdefault(r['source'], []).append(r['target'])
    for eid, parents in pc.items():
        declared_p = parent.get(eid)
        extra = [p for p in parents if p != declared_p]
        if declared_p and extra:
            f.append(('error', 'INV-02',
                      f'{eid}: multiple part_of parents ({declared_p} and {", ".join(extra)})'))
        elif len(set(parents)) > 1:
            f.append(('error', 'INV-02', f'{eid}: multiple part_of parents ({", ".join(sorted(set(parents)))})'))
    for eid in parent:
        seen, cur = [], eid
        while cur in parent:
            cur = parent[cur]
            if cur in seen:
                f.append(('error', 'INV-02', f'containment cycle: {" -> ".join(seen + [cur])}'))
                break
            seen.append(cur)

    # INV-05 scale consistency: declared depth, and level-skipping justification
    for e in ents:
        sub = e.get('subsystem')
        cap = declared.get(sub)
        if cap is None:
            f.append(('error', 'INV-05', f'{e["id"]}: subsystem "{sub}" has no declared depth'))
            continue
        for L in ([e['level']] if 'level' in e else e.get('spatial_scale', [])):
            if L > cap:
                f.append(('error', 'INV-05',
                          f'{e["id"]} at L{L} exceeds declared depth L{cap} for {sub}'))
    # The skip rule targets edges that could assert false causation across scales
    # (BRB-06). Structural relations are exempt: their legitimate level pairs are
    # already enumerated in ADMISSIBLE, so a system being part_of an organism
    # (L2 to L0, skipping regions) is admissible by construction, not a skip.
    STRUCTURAL = {'part_of', 'member_of', 'composed_of', 'located_in',
                  'adjacent_to', 'connected_to', 'participates_in'}
    for r in rels:
        a, b = lvl.get(r['source']), lvl.get(r['target'])
        if a is None or b is None or r['type'] in STRUCTURAL:
            continue
        if abs(a - b) > 1 and not r.get('skip_justification'):
            f.append(('error', 'INV-05',
                      f'{r["id"]}: unjustified level skip L{a} to L{b} ({r["type"]}) — '
                      f'name the skipped levels and why the claim holds without them'))

    # INV-13 representation honesty (advisory)
    for e in ents:
        mode, L = e.get('representation_mode'), e.get('level')
        if mode and L is not None and L in scl_by_level:
            if mode not in scl_by_level[L]['representation_mode']:
                f.append(('warn', 'INV-13',
                          f'{e["id"]}: claims mode "{mode}" unavailable at L{L} '
                          f'(offers {", ".join(scl_by_level[L]["representation_mode"])})'))

    # INV-01 biological consistency: relation admissibility
    for r in rels:
        if r['source'] not in by_id or r['target'] not in by_id:
            f.append(('error', 'INV-01', f'{r["id"]}: endpoint not defined'))
            continue
        rule = ADMISSIBLE.get(r['type'], 'UNKNOWN')
        if rule == 'UNKNOWN':
            f.append(('error', 'INV-01', f'{r["id"]}: unknown relation type "{r["type"]}"'))
            continue
        a, b = lvl.get(r['source']), lvl.get(r['target'])
        if rule is None or a is None or b is None:
            continue
        if rule == 'same-level':
            if a != b:
                f.append(('error', 'INV-01',
                          f'{r["id"]}: {r["type"]} requires same level, got L{a} and L{b}'))
        elif (a, b) not in rule:
            f.append(('error', 'INV-01',
                      f'inadmissible relation: {r["type"]} from {r["source"]}(L{a}) '
                      f'to {r["target"]}(L{b})'))
        if r['type'] == 'associated_with' and not r.get('prose_justification'):
            f.append(('error', 'INV-01', f'{r["id"]}: associated_with without prose_justification'))

    # relation provenance (FR-REL-008)
    for r in rels:
        pcl = r.get('provenance_claim')
        if not pcl:
            f.append(('error', 'INV-07', f'{r["id"]}: edge carries no provenance claim'))
        elif pcl not in claim_ids:
            f.append(('error', 'INV-07', f'{r["id"]}: provenance claim {pcl} undefined'))

    # INV-04 unit consistency + INV-07 evidence + INV-12 species, over claims
    for c in claims:
        if is_quantity(c.get('object')) and not c.get('unit'):
            f.append(('error', 'INV-04', f'{c["id"]}: quantity with no unit'))
        if c.get('unit') and not UCUM_OK.match(c['unit']):
            f.append(('error', 'INV-04', f'{c["id"]}: unit "{c["unit"]}" is not a UCUM code'))
        ec = c.get('evidence_class')
        if ec != 'EVC-8' and not c.get('sources'):
            f.append(('error', 'INV-07', f'{c["id"]}: {ec} with no sources'))
        if ec == 'EVC-8' and c.get('sources'):
            f.append(('warn', 'INV-07', f'{c["id"]}: EVC-8 (UNKNOWN) carrying sources'))
        for fld in ('species', 'population', 'limitations', 'assigned_by', 'date_asserted'):
            if not c.get(fld):
                f.append(('error', 'INV-07', f'{c["id"]}: incomplete claim record, missing {fld}'))
        if ec in STRONG:
            if not str(c.get('assigned_by', '')).startswith('human:'):
                f.append(('error', 'INV-07',
                          f'{c["id"]}: {ec} assigned by non-human reviewer '
                          f'"{c.get("assigned_by")}" — BR-002 forbids this'))
        allowed = class_source.get(ec)
        if allowed and c.get('source_type') and c['source_type'] not in allowed:
            f.append(('error', 'INV-07',
                      f'{c["id"]}: {ec} unsupported by source type '
                      f'"{c["source_type"]}" (admits: {", ".join(allowed)})'))
        # A class demanding independent agreement cannot rest on one source.
        need = min_sources.get(ec)
        if need and len(c.get('sources') or ()) < need:
            f.append(('error', 'INV-07',
                      f'{c["id"]}: {ec} requires {need} independent source(s), '
                      f'has {len(c.get("sources") or ())}'))
        sp = c.get('species')
        if sp and sp not in HUMAN and not c.get('transfer_justification'):
            f.append(('error', 'INV-12',
                      f'{c["id"]}: cross-species claim ({sp}) without transfer justification'))
        if is_quantity(c.get('object')) and not c.get('conditions'):
            f.append(('warn', 'INV-07', f'{c["id"]}: quantitative claim with no measurement conditions'))
        if c.get('subject') and c['subject'] not in by_id:
            f.append(('warn', 'INV-07', f'{c["id"]}: subject {c["subject"]} not a defined entity'))

    # INV-03 functional + INV-06 temporal consistency, over processes
    for p in procs:
        for ref in list(p.get('inputs', [])) + list(p.get('outputs', [])) + list(p.get('participants', [])):
            if ref not in by_id:
                f.append(('error', 'INV-03', f'{p["id"]}: references undefined entity {ref}'))
        if not p.get('timescale_domain'):
            f.append(('error', 'INV-06', f'{p["id"]}: no timescale domain declared'))
        if p.get('representation_status') in ('structured', 'parameterized', 'executable'):
            for fld in ('inputs', 'outputs', 'state_variables', 'mechanism',
                        'failure_states', 'limitations', 'characteristic_duration'):
                if not p.get(fld):
                    f.append(('error', 'INV-03',
                              f'{p["id"]}: status {p["representation_status"]} with empty {fld}'))
            for sv in p.get('state_variables', []):
                if not sv.get('unit'):
                    f.append(('error', 'INV-04', f'{p["id"]}: state variable "{sv.get("name")}" has no unit'))
                if not sv.get('evidence_class'):
                    f.append(('error', 'INV-07', f'{p["id"]}: state variable "{sv.get("name")}" has no evidence class'))
            for fb in p.get('feedback_loops', []):
                if not fb.get('damping'):
                    f.append(('error', 'INV-03', f'{p["id"]}: feedback loop with no damping named'))
        cap = declared.get(p.get('subsystem'))
        if cap is not None:
            for L in p.get('spatial_scale', []):
                if L > cap:
                    f.append(('error', 'INV-05',
                              f'{p["id"]} spans L{L}, exceeding declared depth L{cap} '
                              f'for {p["subsystem"]} — spanning is not a route around the contract'))
        if p.get('spatial_scale') and not p.get('level_contributions'):
            f.append(('error', 'INV-05', f'{p["id"]}: spanning process with no per-level contributions'))

    # INV-11 licence integrity (T1/T2 must not reach T0 layers)
    for s in spatials:
        for g in s.get('geometry', []):
            if not g.get('licence') or not g.get('licence_tier'):
                f.append(('error', 'INV-11', f'{s["id"]}: geometry {g.get("asset_id")} missing licence or tier'))
            if not g.get('representation_kind'):
                f.append(('error', 'INV-11', f'{s["id"]}: geometry {g.get("asset_id")} missing representation kind'))
    blob = json.dumps({'entities': ents, 'claims': claims, 'relationships': rels})
    for pat in (r'bodyparts3d', r'z-anatomy'):
        if re.search(pat, blob, re.I):
            f.append(('error', 'INV-11',
                      f'tier violation: T1 source "{pat}" referenced inside a T0 layer'))

    # INV-08 / INV-09 personalization (overlays are Phase 7; check any that exist)
    for ov in data.get('overlays', []):
        if not ov.get('pinned_release'):
            f.append(('error', 'INV-08', f'{ov.get("id")}: overlay with no pinned release'))
        for v in ov.get('values', []):
            if not str(v.get('target_path', '')).startswith('overlay.'):
                f.append(('error', 'INV-08',
                          f'overlay {ov.get("id")} attempts write to reference path '
                          f'"{v.get("target_path")}"'))
            for fld in ('value', 'unit', 'measured_at', 'method', 'source_rank', 'confidence'):
                if v.get(fld) in (None, ''):
                    f.append(('error', 'INV-09',
                              f'overlay value {v.get("id")}: missing {fld}'))

    # INV-15 compilation-status coherence: status is a capability constraint, not
    # a label. A mechanistic claim resting on a narrative endpoint is a mechanism
    # asserted over prose nobody has typed yet (CH-13).
    RANK = {'narrative': 0, 'structured': 1, 'mechanistic': 2, 'parameterized': 3}
    est = {e['id']: RANK.get(e.get('compilation_status', 'narrative'), 0) for e in ents}
    for r in rels:
        rs = RANK.get(r.get('compilation_status', 'narrative'), 0)
        if rs < 2:
            continue
        for end in ('source', 'target'):
            ref = r[end]
            if ref in est and est[ref] < 1:
                f.append(('error', 'INV-15',
                          f'{r["id"]} at status {r.get("compilation_status")} depends on '
                          f'narrative {ref}'))
    for p in procs:
        if p.get('representation_status') in ('parameterized', 'executable'):
            for ref in list(p.get('inputs', [])) + list(p.get('outputs', [])):
                if ref in est and est[ref] < 1:
                    f.append(('error', 'INV-15',
                              f'{p["id"]} at status {p["representation_status"]} depends on '
                              f'narrative {ref}'))

    # INV-17 review-state integrity. The failure this guards against has now
    # happened twice in this project's own history (D-013, D-017): content that
    # no human examined, attributed to a human who does not exist, at a class
    # only a human may certify. Each clause below is one of the ways that
    # showed up.
    for c in claims:
        state = c.get('review_state', 'provisional')
        assigner = c.get('assigned_by', '')
        if state not in ('reviewed', 'provisional'):
            f.append(('error', 'INV-17',
                      f'{c["id"]}: review_state {state!r} is neither reviewed '
                      f'nor provisional'))
        if state == 'provisional' and assigner.startswith('human:'):
            f.append(('error', 'INV-17',
                      f'{c["id"]}: provisional but assigned_by {assigner} — an '
                      f'unreviewed claim naming a human reviewer is a '
                      f'fabricated review (D-013, D-017)'))
        if state == 'reviewed' and not assigner.startswith('human:'):
            f.append(('error', 'INV-17',
                      f'{c["id"]}: marked reviewed but assigned_by {assigner!r} '
                      f'names no human; review is something a person did'))
        if state != 'reviewed' and c.get('evidence_class') in ('EVC-1', 'EVC-2'):
            f.append(('error', 'INV-17',
                      f'{c["id"]}: unreviewed at {c["evidence_class"]}. The '
                      f'canonical graph admits nothing unreviewed at EVC-1 or '
                      f'EVC-2 (BR-002, BIO_Evidence_and_Provenance §Pipeline). '
                      f'Record the assessment in proposed_class instead'))
        proposed = c.get('proposed_class')
        if proposed and proposed > c.get('evidence_class', 'EVC-8'):
            f.append(('error', 'INV-17',
                      f'{c["id"]}: proposed_class {proposed} is weaker than the '
                      f'asserted {c["evidence_class"]}. proposed_class records '
                      f'an assessment awaiting confirmation, never a downgrade'))
    for e in ents:
        state = e.get('review_state', 'provisional')
        if state not in ('reviewed', 'provisional'):
            f.append(('error', 'INV-17',
                      f'{e["id"]}: review_state {state!r} is neither reviewed '
                      f'nor provisional'))
        if state == 'reviewed' and not str(
                e.get('admitted_by', '')).startswith(('human:', 'APPR:')):
            f.append(('error', 'INV-17',
                      f'{e["id"]}: marked reviewed with admitted_by '
                      f'{e.get("admitted_by")!r} — a reviewed entity names the '
                      f'approval or the human behind it'))

    # INV-18 claim-kind integrity. A definition is not a finding, and the two
    # registers must not leak into one another: an EVC class on a definition
    # would let "the heart is a muscular organ" be offered as evidence for a
    # physiological assertion, which is the confusion D-021 separated.
    for c in claims:
        kind = c.get('kind', 'biological')
        grade = c.get('evidence_class', '')
        if kind not in ('biological', 'terminological'):
            f.append(('error', 'INV-18',
                      f'{c["id"]}: claim kind {kind!r} is neither biological '
                      f'nor terminological'))
            continue
        if kind == 'terminological':
            if not grade.startswith('TRM-'):
                f.append(('error', 'INV-18',
                          f'{c["id"]}: a terminological claim is graded on the '
                          f'TRM register; {grade} is an evidence class, and a '
                          f'definition is not evidence'))
            if not c.get('authority'):
                f.append(('error', 'INV-18',
                          f'{c["id"]}: a terminological claim names the '
                          f'authority whose definition it records'))
            if grade == 'TRM-1' and not c.get('definition_source'):
                f.append(('error', 'INV-18',
                          f'{c["id"]}: TRM-1 asserts the authority\'s source '
                          f'resolves, so the source must be named'))
        else:
            if not grade.startswith('EVC-'):
                f.append(('error', 'INV-18',
                          f'{c["id"]}: a biological claim is graded on the EVC '
                          f'ladder; {grade} is a terminological grade'))
            if c.get('authority') or c.get('definition_source'):
                f.append(('error', 'INV-18',
                          f'{c["id"]}: authority/definition_source belong to '
                          f'terminological claims; a biological claim carries '
                          f'sources'))

    # SCL completeness
    for s in scls:
        for fld in ('representation_mode', 'evidence_model', 'resolution_limit'):
            if not s.get(fld):
                f.append(('error', 'INV-05',
                          f'{s["id"]}: empty {fld} — an undeclared level is how a model overclaims'))
    return f


def coverage(data):
    declared = (data.get('declared_depth') or [{}])[0]
    ents = data.get('entities', [])
    rows = {}
    for e in ents:
        sub = e.get('subsystem')
        for L in ([e['level']] if 'level' in e else e.get('spatial_scale', [])):
            rows.setdefault(sub, {}).setdefault(L, 0)
            rows[sub][L] += 1
    print('COVERAGE — populated against declared depth (FR-SCAL-010)')
    for sub in sorted(declared):
        cap = declared[sub]
        got = rows.get(sub, {})
        cells = ' '.join(f'L{L}:{got.get(L, 0)}' for L in range(cap + 1))
        unmet = [L for L in range(cap + 1) if got.get(L, 0) == 0]
        mark = f'  UNPOPULATED: {", ".join("L%d" % L for L in unmet)}' if unmet else ''
        print(f'  {sub:<18} declared L{cap}  {cells}{mark}')
    print('\nCounts are populated/declared per level. A declared level with zero entities')
    print('is an unmet declaration, and is shown rather than implied.')


def _find(seq, key, val):
    """Locate a record by id. Index-based mutations break as the substrate grows."""
    for x in seq:
        if x.get(key) == val:
            return x
    raise KeyError(f'{val} not present in substrate')


SELFTESTS = [
    ('INV-01', 'a produces edge between inadmissible levels',
     lambda d: d['relationships'].append({'id': 'REL:bad', 'source': 'GO:0030017',
                                          'target': 'UBERON:0004535', 'type': 'produces',
                                          'provenance_claim': 'CLM:heart-function-pump'})),
    ('INV-02', 'an entity given two part_of parents',
     lambda d: d['relationships'].append({'id': 'REL:bad2', 'source': 'UBERON:0000948',
                                          'target': 'UBERON:0000468', 'type': 'part_of',
                                          'provenance_claim': 'CLM:heart-function-pump'})),
    ('INV-03', 'a process output naming an undefined molecule',
     lambda d: _find(d['processes'], 'id', 'BPR-01')['outputs'].append('CHEBI:99999999')),
    ('INV-04', 'a state variable with its unit removed',
     lambda d: _find(d['processes'], 'id', 'BPR-01')['state_variables'][0].pop('unit')),
    ('INV-05', 'an L7 entity in an L3-declared subsystem',
     lambda d: d['entities'].append({'id': 'HOX:celltype:islet-beta-cell', 'minted': True,
                                     'minted_reason': 'test', 'entity_class': 'CellType',
                                     'level': 7, 'subsystem': 'immune',
                                     'preferred_term': 'Beta cell',
                                     'compilation_status': 'structured'})),
    ('INV-06', 'a process with its timescale domain removed',
     lambda d: _find(d['processes'], 'id', 'BPR-01').pop('timescale_domain')),
    ('INV-07', 'an UNKNOWN claim promoted to VERIFIED with no source added',
     lambda d: _find(d['claims'], 'id', 'CLM:myocardium-fibre-architecture')
                    .update({'evidence_class': 'EVC-1'})),
    ('INV-08', 'an overlay operation targeting a reference entity field',
     lambda d: d.setdefault('overlays', []).append(
         {'id': 'OV:test', 'individual_id': 'IND:test', 'pinned_release': 'rel-1',
          'values': [{'id': 'OVV:1', 'target_path': 'UBERON:0000948.function',
                      'value': 1, 'unit': 's', 'measured_at': '2026-07-26T00:00:00Z',
                      'method': 'test', 'source_rank': 'clinical_measurement',
                      'confidence': 'high'}]})),
    ('INV-09', 'an overlay value with its measurement method removed',
     lambda d: d.setdefault('overlays', []).append(
         {'id': 'OV:t2', 'individual_id': 'IND:t2', 'pinned_release': 'rel-1',
          'values': [{'id': 'OVV:2', 'target_path': 'overlay.heart_rate',
                      'value': 60, 'unit': '/min', 'measured_at': '2026-07-26T00:00:00Z',
                      'source_rank': 'self_reported', 'confidence': 'low'}]})),
    ('INV-10', 'an xref to an unregistered authority',
     lambda d: _find(d['entities'], 'id', 'UBERON:0000948').setdefault('xrefs', []).append(
         {'authority': 'NOTREAL', 'id': 'X:1', 'pinned_version': '1'})),
    ('INV-11', 'a T1 source embedded in a T0 entity record',
     lambda d: _find(d['entities'], 'id', 'UBERON:0000948')
                    .update({'preferred_term': 'Heart (mesh from BodyParts3D)'})),
    ('INV-12', 'a rodent-derived claim with its transfer justification removed',
     lambda d: _find(d['claims'], 'id', 'CLM:cytosolic-ca-diastolic').pop('transfer_justification')),
    ('INV-13', 'an entity claiming enumerated at a typed level',
     lambda d: _find(d['entities'], 'id', 'CL:0000746')
                    .update({'representation_mode': 'enumerated'})),
    # No EVC-2 claim survives in the substrate after D-017, so this one is
    # constructed: a reviewed claim (which alone may sit at EVC-2) resting on a
    # single source, which the ladder forbids at that class.
    ('INV-07', 'an EVC-2 claim reduced to a single source',
     lambda d: _find(d['claims'], 'id', 'CLM:sarcomere-resting-length')
                    .update({'evidence_class': 'EVC-2', 'review_state': 'reviewed',
                             'assigned_by': 'human:reviewer-cardio-01',
                             'proposed_class': None,
                             'sources': [{'citation': 'one', 'identifier': 'DOI:1'}]})),
    ('INV-15', 'a mechanistic relationship pointing at a narrative endpoint',
     lambda d: d['relationships'].append(
         {'id': 'REL:bad15', 'source': 'CL:0000746',
          'target': 'HOX:function:cardiaccycle', 'type': 'responds_to',
          'compilation_status': 'mechanistic',
          'skip_justification': 'test fixture',
          'provenance_claim': 'CLM:heart-function-pump'})),
    ('INV-17', 'an unreviewed claim attributed to a human reviewer',
     lambda d: _find(d['claims'], 'id', 'CLM:heart-function-pump')
                    .update({'assigned_by': 'human:reviewer-cardio-01'})),
    ('INV-17', 'unreviewed content sitting at EVC-2',
     lambda d: _find(d['claims'], 'id', 'CLM:region-thorax-boundary')
                    .update({'evidence_class': 'EVC-2'})),
    ('INV-17', 'an entity marked reviewed with no approval behind it',
     lambda d: _find(d['entities'], 'id', 'UBERON:0000948')
                    .update({'review_state': 'reviewed'})),
    ('INV-17', 'a proposed_class weaker than the class asserted',
     lambda d: _find(d['claims'], 'id', 'CLM:cytosolic-ca-diastolic')
                    .update({'proposed_class': 'EVC-6'})),
    ('INV-18', 'a definition graded as biological evidence',
     lambda d: _find(d['claims'], 'id', 'CLM:region-thorax-boundary')
                    .update({'evidence_class': 'EVC-2'})),
    # Mutating only `kind` fires the terminological branch (no TRM grade), so
    # it never exercised the biological one. Grading a finding TRM does.
    ('INV-18', 'a finding graded on the terminological register',
     lambda d: _find(d['claims'], 'id', 'CLM:sarcomere-resting-length')
                    .update({'evidence_class': 'TRM-1'})),
    ('INV-18', 'a terminological claim with no authority behind it',
     lambda d: _find(d['claims'], 'id', 'CLM:region-thorax-boundary')
                    .update({'authority': None})),
    ('INV-18', 'a biological claim carrying a definition source',
     lambda d: _find(d['claims'], 'id', 'CLM:cross-bridge-cycle-duration')
                    .update({'definition_source': 'ISBN:1'})),
]


def selftest(root):
    """Every invariant is deliberately violated. A validator that cannot fail is not one."""
    base = load(root)
    doc_sources, doc_minimums = load_ladder()
    clean = ladder_divergence(doc_sources, doc_minimums)
    clean += eco_divergence(load_eco_mapping())
    clean += relation_divergence(load_relations())
    clean += check(base, doc_sources, doc_minimums)
    hard = [x for x in clean if x[0] == 'error']
    print(f'baseline: {len(hard)} errors, {len(clean) - len(hard)} warnings')
    if hard:
        for lv, inv, m in clean:
            print(f'  {lv.upper()}: [{inv}] {m}')
        print('SELFTEST ABORTED — baseline substrate is not clean')
        return 1
    failed = 0
    for inv, desc, mutate in SELFTESTS:
        d = json.loads(json.dumps(base))
        try:
            mutate(d)
        except Exception as e:  # a mutation that cannot apply is itself a test failure
            print(f'  {inv}  MUTATION FAILED ({e})')
            failed += 1
            continue
        got = [x for x in check(d, doc_sources, doc_minimums) if x[1] == inv]
        ok = bool(got)
        print(f'  {inv}  {"detected" if ok else "NOT DETECTED"}  — {desc}')
        if not ok:
            failed += 1
    # INV-16 is checked against the document rather than the substrate, so its
    # violation is injected into the parsed ladder rather than into the data.
    divergent = dict(doc_sources or CLASS_SOURCE)
    divergent['EVC-1'] = tuple(sorted(set(divergent.get('EVC-1', ())) |
                                      {'reference textbook'}))
    got16 = ladder_divergence(divergent, doc_minimums)
    detected16 = any(x[1] == 'INV-16' for x in got16)
    print(f'  INV-16  {"detected" if detected16 else "NOT DETECTED"}  — '
          f'the checker table diverging from the ladder document')
    if not detected16:
        failed += 1
    eco_bad = dict(load_eco_mapping() or ECO_TO_EVC)
    eco_bad['ECO:0000006'] = 'EVC-1'
    detected_eco = any(x[1] == 'INV-16' for x in eco_divergence(eco_bad))
    print(f'  INV-16  {"detected" if detected_eco else "NOT DETECTED"}  — '
          f'the ECO mapping diverging from the ladder document')
    if not detected_eco:
        failed += 1

    # INV-19 is checked against the document too, so its violations are injected
    # into the parsed vocabulary rather than into the substrate. Three shapes:
    # a relation the code has and the document does not (today's defect), one
    # the document has and the code does not, and an inverse that disagrees.
    # Each case must isolate ONE branch. The first version did not: removing
    # `is_a` from the document fired both the code-only branch and the
    # ADMISSIBLE-orphan loop, so a mutation disabling either survived because
    # the other covered it. Overlapping negative tests are how a selftest comes
    # to certify checks that no longer run.
    doc_rel = load_relations() or {}
    no_part_of = {k: v for k, v in doc_rel.items() if k != 'part_of'}
    for desc, doc_side, code_side in (
            ('a relation in the code and not in the document',
             doc_rel, {**doc_rel, 'HOX:invented': 'HOX:invented_inverse'}),
            ('a relation in the document and not in the code',
             {**doc_rel, 'documented_only': 'documented_only_inverse'}, doc_rel),
            ('an inverse that disagrees between code and document',
             doc_rel, {**doc_rel, 'part_of': 'contains'}),
            ('an admissibility rule with no row in the document',
             no_part_of, no_part_of)):
        got = relation_divergence(doc_side, code_side)
        ok19 = any(x[1] == 'INV-19' and x[0] == 'error' for x in got)
        print(f'  INV-19  {"detected" if ok19 else "NOT DETECTED"}  — {desc}')
        if not ok19:
            failed += 1
    # INV-14 is enforced at runtime in the retrieval pipeline, not over the substrate
    print('  INV-14  n/a here — enforced at runtime by the groundedness guard (EV-RETR-001)')
    print(f'\nselftest: {len(SELFTESTS) + 6} invariants exercised, '
          f'{failed} not detected')
    return 1 if failed else 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    if '--selftest' in argv:
        root = next((a for a in argv[1:] if not a.startswith('--')), 'ontology')
        return selftest(root)
    def arg_after(flag, default=None):
        i = argv.index(flag)
        return argv[i + 1] if i + 1 < len(argv) else default

    root = argv[1]
    if not os.path.isdir(root):
        print(f'not a directory: {root}')
        return 2
    data = load(root)
    if '--coverage' in argv:
        coverage(data)
        return 0
    # Both documents are overridable, so the divergence checks can be driven
    # through the real command-line path with a diverging file. Without that,
    # deleting either call site below is invisible: `--selftest` calls the
    # functions directly and would keep certifying a check that no longer runs.
    ladder_path = (arg_after('--ladder', LADDER_DOC) if '--ladder' in argv
                   else LADDER_DOC)
    relations_path = (arg_after('--relations', ONTOLOGY_DOC)
                      if '--relations' in argv else ONTOLOGY_DOC)
    doc_sources, doc_minimums = load_ladder(ladder_path)
    findings = ladder_divergence(doc_sources, doc_minimums)
    findings += eco_divergence(load_eco_mapping(ladder_path), ladder_path)
    findings += relation_divergence(load_relations(relations_path),
                                    path=relations_path)
    findings += check(data, doc_sources, doc_minimums)
    errs = [(i, m) for lv, i, m in findings if lv == 'error']
    warns = [(i, m) for lv, i, m in findings if lv == 'warn']
    for i, m in errs:
        print(f'ERROR: [{i}] {m}')
    for i, m in warns:
        print(f'WARN:  [{i}] {m}')
    if '--json' in argv:
        out = argv[argv.index('--json') + 1]
        json.dump({'findings': [{'level': lv, 'invariant': i, 'message': m}
                                for lv, i, m in findings]}, open(out, 'w'), indent=1)
    n = sum(len(v) for k, v in data.items() if not k.startswith('_'))
    strict = '--strict' in argv
    print(f'biocheck: {n} records, {len(errs)} errors, {len(warns)} warnings'
          + (' (strict)' if strict else ''))
    print('Consistency is not correctness — see BIO_Validation_Framework '
          '"What Validation Does Not Establish".')
    return 1 if errs or (strict and warns) else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except BrokenPipeError:
        sys.exit(0)
