#!/usr/bin/env python3
"""specgraph.py — derive and validate the spec graph from a generated docs/ set.

Files are the canonical serialization (AGENTS.md §10); this tool extracts the
model latent in their ID grammar and validates it semantically. Nothing is
ever edited here — drift between graph and files is a finding, not a merge.

Usage:
  python3 tools/specgraph.py <docs-dir> [--strict] [--json OUT] [--trace SRC ...]
  Memory renderers (read-only, exit 0):
    --why <ID>        decisions and references that shaped an ID
    --impact <D-NNN>  what a decision binds (its affects, forward)
    --excluded <term> search the negative space (non-goals, exclusions, rejections)
    --context <ID|Module>  working-set brief for an ID or module
    --digest [--write]     one-line active-decision digest (optionally to docs/)
    --stale [days]    decisions and grounding due for re-examination (default 90)
    --history <ID>    change history via git -S, else CHANGE_LEDGER.md
  Integrity: default validation mode maintains docs/INTEGRITY.json hashes of
  Decision Log entries and warns on mutation (append-only check).

Errors (always fail): duplicate ID definitions; references to undefined IDs;
Must requirements with an empty acceptance-criteria cell; (bio profile) an SCL
level missing its representation mode, evidence model, or resolution limit; a
quantitative row carrying a value with no unit.
Strict-only (fail with --strict, else warn): Success Metrics not tracing to a
defined KPI id (G-NN); Data Touched entities absent from the Data Overview;
Must AI behavior without an EV row; decision `Affects:` naming missing files;
HYP/DC/BPR/INV defined but referenced nowhere; (bio profile) a declared
evidence-class cell left empty.
--trace: report Must FRs with zero references under the given source dirs.
Exit: 0 clean, 1 errors (or warnings under --strict), 2 usage.
Stdlib only.
"""
import json, os, re, sys

# Registers declared in SPEC_MODEL.md that carry no AREA segment. AGT/TOOL/CH/CM
# were declared and mapped by kind() upstream but never matched here, leaving
# agent, tool, challenge and causal-mechanism ids unvalidated; SCL/BPR/EVC/INV/BRB
# are the bio profile's additions (templates/bio/README.md).
FLAT = 'PIL|MECH|ARCH|HYP|EXP|DC|CM|AGT|TOOL|CH|SCL|BPR|EVC|INV|BRB'
ID_DEF = re.compile(r'^(FR|BR|NFR|RSK|UC|NTF|EV)-[A-Z0-9]{0,5}-?\d+$|^(?:' + FLAT + r')-\d+$')
ID_REF = re.compile(r'\b((?:FR|BR|NFR|RSK|UC|NTF|EV)-[A-Z0-9]{0,5}-?\d+|(?:' + FLAT + r')-\d+|D-\d{3}|G-\d{2})\b')
D_DEF = re.compile(r'^###\s+(D-\d{3})\b')
KPI_DEF = re.compile(r'^(G-\d{2})$')

def cells(line):
    if not line.strip().startswith('|'):
        return None
    c = [x.strip() for x in line.strip().strip('|').split('|')]
    return None if all(re.fullmatch(r':?-{2,}:?', x) for x in c if x) else c

def parse(docs):
    files = sorted(f for f in os.listdir(docs) if f.endswith('.md'))
    defs, refs, findings = {}, [], []
    entities, touched, metrics, musts, affects, kpis = set(), [], [], [], [], set()
    ai_must_files, ev_files = set(), set()
    bio_rows = []   # (fn, ln, hdr, cells) for every table row in a BIO_ doc
    for fn in files:
        path = os.path.join(docs, fn)
        section, hdr = '', []
        for ln, raw in enumerate(open(path, encoding='utf-8'), 1):
            line = raw.rstrip('\n')
            m = D_DEF.match(line)
            if m:
                did = m.group(1)
                if did in defs:
                    findings.append(('error', f'{fn}:{ln} duplicate id {did} (also {defs[did]})'))
                defs[did] = f'{fn}:{ln}'
            if line.startswith('## '):
                section, hdr = line[3:].lower(), []
            m = re.match(r'^-\s+\*\*Affects:\*\*\s*(.+)$', line)
            if m:
                affects.append((fn, ln, m.group(1)))
            c = cells(line)
            if c is None:
                # A line that is not part of a table at all ends the current
                # table (a separator row is part of one, and must not reset).
                # Without this, a second table in the same section inherits the
                # first one's header and column-driven checks read wrong columns.
                if not line.strip().startswith('|'):
                    hdr = []
                for rid in ID_REF.findall(line):
                    refs.append((rid, fn, ln))
                continue
            if not hdr:
                hdr = [h.lower() for h in c]
                continue
            first = c[0]
            if fn.startswith('BIO_'):
                bio_rows.append((fn, ln, hdr, c))
            for rid in ID_REF.findall(line):
                refs.append((rid, fn, ln))
            if ID_DEF.match(first):
                if first in defs:
                    findings.append(('error', f'{fn}:{ln} duplicate id {first} (also {defs[first]})'))
                defs[first] = f'{fn}:{ln}'
                if first.startswith('EV-'):
                    ev_files.add(fn)
                if first.startswith('FR-') and 'requirements' in section:
                    pri = c[1] if len(c) > 1 else ''
                    ac_i = next((i for i, h in enumerate(hdr) if 'acceptance' in h), None)
                    ac = c[ac_i] if ac_i is not None and ac_i < len(c) else ''
                    if pri.lower() == 'must':
                        musts.append((first, fn, ln))
                        if not ac:
                            findings.append(('error', f'{fn}:{ln} {first} is Must with empty acceptance-criteria cell'))
            elif KPI_DEF.match(first):
                kpis.add(first); defs[first] = f'{fn}:{ln}'
            elif 'core entities' in section and fn.startswith('PRD_Data_Overview'):
                entities.add(first)
            elif 'data touched' in section and fn.startswith('PRD_FR_'):
                if 'not a Data Overview entity' not in first:
                    base = re.sub(r'\s*\(.*\)$', '', first)
                    for ent in re.split(r'[,/]\s*', base):
                        if ent:
                            touched.append((ent.strip(), fn, ln))
            elif 'success metrics' in section and fn.startswith('PRD_FR_'):
                tr_i = next((i for i, h in enumerate(hdr) if 'traces' in h), None)
                if tr_i is not None and tr_i < len(c):
                    metrics.append((c[0], c[tr_i], fn, ln))
    return (files, defs, refs, findings, entities, touched, metrics, musts,
            affects, kpis, ai_must_files, ev_files, bio_rows)


# --- bio profile checks (templates/bio/README.md) ---------------------------
SCL_REQUIRED = ('representation mode', 'evidence model', 'resolution limit')


def bio_checks(bio_rows):
    """Findings specific to the bio profile's honesty rules.

    A level whose limits were never stated, a claim column left blank, or a
    quantity without a unit are the three ways this profile's documents
    overclaim without saying anything false.
    """
    out = []

    def col(hdr, cells, *names):
        for i, h in enumerate(hdr):
            if any(n in h for n in names):
                return cells[i].strip() if i < len(cells) else ''
        return None

    for fn, ln, hdr, c in bio_rows:
        first = c[0].strip()
        if first.startswith('SCL-'):
            for req in SCL_REQUIRED:
                v = col(hdr, c, req)
                if v is not None and not v:
                    out.append(('error', f'{fn}:{ln} {first} has empty "{req}" — '
                                         'an undeclared level is how a model overclaims'))
        ev = col(hdr, c, 'evidence class')
        if ev is not None and not ev and first and not first.startswith('<'):
            out.append(('warn', f'{fn}:{ln} row "{first[:40]}" declares an evidence-class '
                                'column but leaves it empty'))
        unit = col(hdr, c, 'unit')
        val = col(hdr, c, 'value', 'quantity')
        if unit is not None and val:
            if not unit and val.lower() not in ('none', 'n/a', 'unknown', '—'):
                out.append(('error', f'{fn}:{ln} row "{first[:40]}" carries a value with no unit'))
    return out

DEC_HEAD = re.compile(r'^###\s+(D-\d{3})\s+—\s+(.*?)\s*(?:\((.*?)\))?\s*$')

def parse_decisions(docs):
    """All D-entries across docs (Decision Log + archives). Tolerant of old schemas."""
    entries = {}
    for fn in sorted(os.listdir(docs)):
        if not fn.endswith('.md'):
            continue
        cur = None
        for ln, raw in enumerate(open(os.path.join(docs, fn), encoding='utf-8'), 1):
            line = raw.rstrip('\n')
            m = DEC_HEAD.match(line)
            if m:
                cur = m.group(1)
                meta = (m.group(3) or '')
                entries[cur] = {'id': cur, 'title': m.group(2), 'meta': meta,
                                'file': fn, 'line': ln, 'body': [], 'fields': {}}
                continue
            if line.startswith(('### ', '## ')) and cur:
                cur = None
            if cur:
                entries[cur]['body'].append(line)
                fm = re.match(r'^-\s+\*\*(.+?):\*\*\s*(.*)$', line)
                if fm:
                    entries[cur]['fields'][fm.group(1).lower()] = fm.group(2)
    for e in entries.values():
        sup = e['fields'].get('supersedes', '')
        e['supersedes'] = re.findall(r'D-\d{3}', sup)
        e['superseded_by'] = []
    for e in entries.values():
        for t in e['supersedes']:
            if t in entries:
                entries[t]['superseded_by'].append(e['id'])
    for e in entries.values():
        st = e['fields'].get('status', '')
        e['active'] = not e['superseded_by'] and 'superseded' not in st.lower()
    return entries

def entry_hash(e):
    import hashlib
    norm = '\n'.join(l.strip() for l in [e['title']] + e['body'] if l.strip())
    return hashlib.sha256(norm.encode()).hexdigest()[:12]

def entry_date(e):
    m = re.search(r'(\d{4}-\d{2}-\d{2})', e['meta'] + ' ' + ' '.join(e['body'][:3]))
    return m.group(1) if m else None

def brief_lines(docs, mod):
    path = os.path.join(docs, f'PRD_FR_{mod}.md')
    if not os.path.isfile(path):
        return None
    keep, sec = [], ''
    for line in open(path, encoding='utf-8'):
        if line.startswith('## '):
            sec = line[3:].strip().lower()
        if any(k in sec for k in ('purpose', 'requirements', 'data touched', 'dependencies', 'states', 'open questions')):
            keep.append(line.rstrip())
    return keep

def decisions_touching(entries, needle_ids, needle_files):
    hits = []
    for e in entries.values():
        blob = ' '.join(e['body'])
        aff = e['fields'].get('affects', '')
        if any(i in blob or i in aff for i in needle_ids) or \
           any(f.replace('.md', '') in aff or f.replace('.md', '') in blob for f in needle_files):
            hits.append(e)
    return hits

def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    docs = argv[1]; strict = '--strict' in argv
    out = argv[argv.index('--json') + 1] if '--json' in argv else None
    trace = argv[argv.index('--trace') + 1:] if '--trace' in argv else []
    if not os.path.isdir(docs):
        print(f'not a directory: {docs}'); return 2
    (files, defs, refs, findings, entities, touched, metrics, musts,
     affects, kpis, ai_must, ev_files, bio_rows) = parse(docs)
    findings += bio_checks(bio_rows)

    def arg_after(flag, default=None):
        return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) else default

    if '--why' in argv:
        i = arg_after('--why');  entries = parse_decisions(docs)
        print(f'WHY {i}')
        print(f'  defined: {defs.get(i, "NOT DEFINED")}')
        for e in decisions_touching(entries, [i], [defs.get(i, "::").split(":")[0]]):
            tag = 'active' if e['active'] else 'superseded by ' + ','.join(e['superseded_by'])
            print(f'  decision {e["id"]} [{tag}] — {e["title"]} ({e["file"]}:{e["line"]})')
        rr = [(f, l) for r, f, l in refs if r == i and defs.get(i) != f + ':' + str(l)]
        for f, l in rr[:12]:
            print(f'  referenced: {f}:{l}')
        return 0
    if '--impact' in argv:
        d = arg_after('--impact'); entries = parse_decisions(docs)
        e = entries.get(d)
        if not e:
            print(f'no such decision {d}'); return 2
        print(f'IMPACT {d} — {e["title"]} [{ "active" if e["active"] else "superseded" }]')
        aff = e['fields'].get('affects', '(no affects field)')
        print(f'  affects: {aff}')
        for tok in re.split(r'[,;]\s*', aff):
            tok = tok.strip().rstrip('.')
            base = tok if tok.endswith('.md') else tok + '.md'
            if base in files:
                n = sum(1 for i2, loc in defs.items() if loc.startswith(base + ':'))
                print(f'    {base}: exists, {n} defined ids')
            elif ID_REF.fullmatch(tok or ''):
                print(f'    {tok}: {"defined at " + defs[tok] if tok in defs else "NOT DEFINED"}')
        if e['supersedes']: print(f'  supersedes: {", ".join(e["supersedes"])}')
        if e['superseded_by']: print(f'  superseded by: {", ".join(e["superseded_by"])}')
        return 0
    if '--excluded' in argv:
        term = arg_after('--excluded').lower()
        print(f'EXCLUDED-SPACE matches for "{term}"')
        neg = ('non-goal', 'out of scope', 'excluded', 'fold record', 'rejected')
        for fn in files:
            sec = ''
            for ln, raw in enumerate(open(os.path.join(docs, fn), encoding='utf-8'), 1):
                line = raw.rstrip('\n')
                if line.startswith('## '): sec = line.lower()
                inneg = any(k in sec for k in neg) or 'rejected_because' in line or '— rejected' in line
                if inneg and term in line.lower():
                    print(f'  {fn}:{ln}  {line.strip()[:110]}')
        return 0
    if '--context' in argv:
        x = arg_after('--context'); entries = parse_decisions(docs)
        if re.match(r'^[A-Z]+-', x):
            print(f'CONTEXT for {x}\n  defined: {defs.get(x, "NOT DEFINED")}')
            loc = defs.get(x)
            if loc:
                f2, l2 = loc.rsplit(':', 1)
                row = open(os.path.join(docs, f2), encoding='utf-8').read().split('\n')[int(l2) - 1]
                print(f'  row: {row.strip()[:140]}')
            for e in decisions_touching(entries, [x], []):
                print(f'  decision {e["id"]} — {e["title"]}')
            for r, f2, l2 in refs:
                if r == x and defs.get(x) != f2 + ':' + str(l2):
                    print(f'  ref: {f2}:{l2}')
        else:
            kl = brief_lines(docs, x)
            if kl is None:
                print(f'--context: no PRD_FR_{x}.md in {docs}'); return 2
            print(f'# Working set — {x} (rendered; do not edit)')
            print('\n'.join(kl))
            ds = decisions_touching(entries, [], [f'PRD_FR_{x}.md']) 
            if ds:
                print('\n## Decisions binding this module')
                for e in ds: print(f'- {e["id"]} — {e["title"]} [{ "active" if e["active"] else "superseded" }]')
        return 0
    if '--digest' in argv:
        entries = parse_decisions(docs)
        lines = ['# Decisions Digest (generated — do not edit)', '']
        for e in sorted(entries.values(), key=lambda e: e['id']):
            if e['active']:
                lines.append(f'- **{e["id"]}** {e["title"]} ({entry_date(e) or "?"}; affects: {e["fields"].get("affects", "—")[:80]})')
        sup = [e for e in sorted(entries.values(), key=lambda e: e['id']) if not e['active']]
        if sup:
            lines.append('\n**Superseded:** ' + ' · '.join(f'{e["id"]}→{",".join(e["superseded_by"]) or "closed"}' for e in sup))
        outtxt = '\n'.join(lines)
        if '--write' in argv:
            open(os.path.join(docs, 'DECISIONS_DIGEST.md'), 'w').write(
                '---\ndoc: DECISIONS_DIGEST\nversion: generated\nstatus: generated\nowner: tool\nlast_updated: generated\n---\n\n' + outtxt + '\n')
            print(f'wrote {docs}/DECISIONS_DIGEST.md ({sum(1 for e in entries.values() if e["active"])} active)')
        else:
            print(outtxt)
        return 0
    if '--stale' in argv:
        import datetime as dt
        days = int(arg_after('--stale', '90') if (arg_after('--stale') or '').isdigit() else 90)
        today = dt.date.today(); entries = parse_decisions(docs); n = 0
        for e in sorted(entries.values(), key=lambda e: e['id']):
            if not e['active']: continue
            vw = e['fields'].get('valid while')
            d0 = entry_date(e)
            age = (today - dt.date.fromisoformat(d0)).days if d0 else None
            rev = e['fields'].get('reversibility', '').lower()
            if vw and 'unconditional' not in vw.lower():
                print(f'REVIEW {e["id"]} — valid while: {vw}'); n += 1
            elif age is not None and age > days and ('low' in rev or 'medium' in rev):
                print(f'AGED   {e["id"]} — {age}d old, reversibility {rev or "?"} — {e["title"]}'); n += 1
        for fn in files:
            for ln, raw in enumerate(open(os.path.join(docs, fn), encoding='utf-8'), 1):
                for m in re.finditer(r'\[grounded:\s*([^,\]]+),\s*(\d{4}-\d{2}-\d{2})\]', raw):
                    age = (today - dt.date.fromisoformat(m.group(2))).days
                    if age > days:
                        print(f'GROUND {fn}:{ln} — {m.group(1).strip()} grounding {age}d old'); n += 1
        print(f'stale-check: {n} item(s) due for re-examination (threshold {days}d)')
        return 0
    if '--history' in argv:
        import subprocess
        i = arg_after('--history')
        root = os.path.abspath(docs)
        while root != '/' and not os.path.isdir(os.path.join(root, '.git')):
            root = os.path.dirname(root)
        if os.path.isdir(os.path.join(root, '.git')):
            r = subprocess.run(['git', '-C', root, 'log', '-S', i, '--oneline', '--', os.path.abspath(docs)],
                               capture_output=True, text=True)
            print(r.stdout.strip() or f'(git: no commits touching {i})')
        else:
            led = os.path.join(docs, 'CHANGE_LEDGER.md')
            if os.path.isfile(led):
                hits = [l.rstrip() for l in open(led, encoding='utf-8') if i in l]
                print('\n'.join(hits) or f'(ledger: no entries for {i})')
            else:
                print('no git repo and no CHANGE_LEDGER.md — history unavailable (see MEMORY.md gap 2)')
        return 0
    for rid, fn, ln in refs:
        if rid not in defs:
            findings.append(('error', f'{fn}:{ln} references undefined id {rid}'))
    for name, fn, ln in touched:
        if entities and name not in entities and name.lower() not in ('none', ''):
            findings.append(('warn', f'{fn}:{ln} Data Touched "{name}" not in PRD_Data_Overview core entities'))
    for metric, tr, fn, ln in metrics:
        if not any(k in tr for k in kpis):
            findings.append(('warn', f'{fn}:{ln} metric "{metric}" traces to no defined KPI id (G-NN)'))
    for fn, ln, val in affects:
        for tok in re.split(r'[,;]\s*', val):
            tok = tok.strip().rstrip('.')
            if tok.endswith('.md') or tok.startswith(('PRD_', 'TECH_')):
                base = tok if tok.endswith('.md') else tok + '.md'
                if base not in files:
                    findings.append(('warn', f'{fn}:{ln} decision affects missing file {base}'))
    if any(fn.startswith('PRD_Decision_Log') for fn in files):
        entries = parse_decisions(docs)
        ipath = os.path.join(docs, 'INTEGRITY.json')
        prev = {}
        if os.path.isfile(ipath):
            try: prev = json.load(open(ipath))
            except Exception: findings.append(('warn', 'INTEGRITY.json unreadable — regenerating'))
        cur = {e['id']: entry_hash(e) for e in entries.values()}
        for did, h in prev.items():
            if did not in cur:
                findings.append(('warn', f'decision {did} present at last check, now MISSING (append-only violation?)'))
            elif cur[did] != h:
                findings.append(('warn', f'decision {did} content CHANGED since last check (append-only violation? supersede instead)'))
        try: json.dump(cur, open(ipath, 'w'), indent=0, sort_keys=True)
        except OSError: pass

    ref_ids = {r for r, f, l in refs if defs.get(r) != f + ':' + str(l)}
    for i, loc in sorted(defs.items()):
        if i.startswith(('HYP-', 'DC-')) and i not in ref_ids:
            findings.append(('warn', f'{loc} {i} defined but referenced nowhere — broken research trace chain'))
        if i.startswith(('BPR-', 'INV-')) and i not in ref_ids:
            findings.append(('warn', f'{loc} {i} defined but referenced nowhere — broken bio trace chain'))
    if trace:
        pat = re.compile(r'\bFR-[A-Z0-9]{2,5}-\d+\b')
        test_pat = re.compile(r'(^|/)(tests?|specs?)(/|$)|_test\.|\.test\.|_spec\.|\.spec\.')
        test_hits, any_hits = set(), set()
        for root in trace:
            for dp, _, fns in os.walk(root):
                if any(seg in dp for seg in ('.git', 'node_modules', 'docs')):
                    continue
                for f in fns:
                    fp = os.path.join(dp, f)
                    try:
                        found = set(pat.findall(open(fp, encoding='utf-8', errors='ignore').read()))
                    except OSError:
                        continue
                    any_hits |= found
                    if test_pat.search(fp):
                        test_hits |= found
        for rid, fn, ln in musts:
            if rid not in any_hits:
                findings.append(('warn', f'{fn}:{ln} Must {rid} has no implementation trace under {" ".join(trace)}'))
            elif rid not in test_hits:
                findings.append(('warn', f'{fn}:{ln} Must {rid} claimed (code refs only) — no test reference verifies it'))
    if out:
        def kind(i):
            for pre, k in (('FR-','requirement'),('BR-','business-rule'),('NFR-','nfr'),
                           ('RSK-','risk'),('UC-','use-case'),('NTF-','notification'),
                           ('EV-','evaluation'),('D-','decision'),('G-','kpi'),
                           ('PIL-','pillar'),('MECH-','mechanic'),('ARCH-','archetype'),
                           ('HYP-','hypothesis'),('EXP-','experiment'),('DC-','decision-criterion'),
                           ('CM-','causal-mechanism'),('AGT-','agent'),('TOOL-','tool'),
                           ('CH-','challenge'),('SCL-','scale-level'),('BPR-','biological-process'),
                           ('EVC-','evidence-class'),('INV-','invariant'),('BRB-','rubric-item')):
                if i.startswith(pre): return k
            return 'unknown'
        nodes = [{'id': i, 'kind': kind(i), 'at': loc} for i, loc in sorted(defs.items())]
        edges = [{'ref': r, 'file': f, 'line': l} for r, f, l in refs if r in defs]
        json.dump({'model': 'SPEC_MODEL.md', 'nodes': nodes,
                   'entities': sorted(entities), 'edges': edges,
                   'findings': [{'level': lv, 'msg': m} for lv, m in findings]},
                  open(out, 'w'), indent=1)
    if '--brief' in sys.argv:
        mod = sys.argv[sys.argv.index('--brief') + 1]
        fn = f'PRD_FR_{mod}.md'
        path = os.path.join(docs, fn)
        if not os.path.isfile(path):
            print(f'--brief: no {fn} in {docs}'); return 2
        keep, sec = [], ''
        for line in open(path, encoding='utf-8'):
            if line.startswith('## '): sec = line[3:].strip().lower()
            if any(k in sec for k in ('purpose','requirements','data touched','dependencies','states')):
                keep.append(line.rstrip())
        print(f'# Implementation brief — {mod} (rendered from spec IR; do not edit)')
        print('\n'.join(keep))
    errs = [m for lv, m in findings if lv == 'error']
    warns = [m for lv, m in findings if lv == 'warn']
    for m in errs: print('ERROR:', m)
    for m in warns: print('WARN: ', m)
    print(f'specgraph: {len(defs)} ids, {len([r for r in refs if r[0] in defs])} resolved refs, '
          f'{len(errs)} errors, {len(warns)} warnings' + (' (strict)' if strict else ''))
    return 1 if errs or (strict and warns) else 0

if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except BrokenPipeError:
        sys.exit(0)
