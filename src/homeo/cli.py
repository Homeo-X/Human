"""Command-line entry point.

    python3 -m homeo.cli <command> [options]

Commands mirror the read API's surface so the same questions can be asked from a
shell, a script, or HTTP without a different mental model.
"""
from __future__ import annotations

import argparse
import json
import sys

from .api import Service, serve
from .curation import CurationError, CurationService
from .release import ReleaseBuilder, diff, load_manifest, verify_rebuild

DEFAULT_QUEUE = 'curation/queue.json'


def _csv(value: str | None) -> set[str] | None:
    return set(value.split(',')) if value else None


def _print(payload) -> None:
    print(json.dumps(payload, indent=1, ensure_ascii=False))


def _curation(args) -> int:
    """The review commands, which read and write a persisted queue.

    Separated from the read commands because they are a different plane, not a
    different verb: these need a reviewer identity, they refuse work outside
    that reviewer's competence, and they write. A deployment that serves reads
    never loads this file.
    """
    try:
        plane = CurationService.load(args.queue)
    except FileNotFoundError:
        print(f'no curation queue at {args.queue}. Agents write proposals '
              f'there; until one has run, there is nothing to review.',
              file=sys.stderr)
        return 1

    if args.command == 'operator':
        _print(plane.operator_view())
        return 0

    if args.command == 'queue':
        rows = []
        for task in plane.pending():
            ok, why = plane.can_review(args.reviewer, task.id)
            if ok:
                rows.append(task.as_dict())
            else:
                rows.append({'id': task.id, 'subsystem': task.proposal.subsystem,
                             'level': task.proposal.level,
                             'out_of_scope': why})
        _print({'reviewer': args.reviewer, 'depth': len(rows), 'tasks': rows})
        return 0

    try:
        if args.decision == 'accept':
            approval = plane.accept(args.task, args.reviewer, args.reason)
            plane.save(args.queue)
            _print(approval.as_dict())
        else:
            task = plane.reject(args.task, args.reviewer, args.reason)
            plane.save(args.queue)
            _print(task.as_dict())
    except CurationError as exc:
        print(f'refused: {exc}', file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog='homeo', description=__doc__)
    p.add_argument('--substrate', default='ontology',
                   help='substrate root (default: ontology)')
    p.add_argument('--release', default='unpinned',
                   help='release id to report as answering (default: unpinned)')
    sub = p.add_subparsers(dest='command', required=True)

    e = sub.add_parser('entity', help='resolve and describe an entity')
    e.add_argument('ref')

    r = sub.add_parser('relations', help='typed relations of an entity')
    r.add_argument('ref')
    r.add_argument('--type', default=None)

    c = sub.add_parser('claims', help='claims about an entity')
    c.add_argument('ref')
    c.add_argument('--class', dest='cls', default=None)

    u = sub.add_parser('unknowns', help='what the model does not know')
    u.add_argument('ref')

    d = sub.add_parser('descend', help='one level down, or the terminal answer')
    d.add_argument('ref')

    s = sub.add_parser('search', help='search the model')
    s.add_argument('query')
    s.add_argument('--mode', default='name')
    s.add_argument('--class', dest='cls', default=None)
    s.add_argument('--limit', type=int, default=20)

    vw = sub.add_parser('view', help='project a view: what is in view, and why')
    vw.add_argument('ref')
    vw.add_argument('--level', type=int, default=None)
    vw.add_argument('--magnification', type=float, default=1.0)
    vw.add_argument('--systems', default=None)
    vw.add_argument('--tissue-classes', dest='tissue_classes', default=None)
    vw.add_argument('--evidence', default=None,
                    help='show only entities carrying these evidence classes; '
                         'what is hidden is counted, never silently dropped')
    vw.add_argument('--isolate', default=None)

    zm = sub.add_parser('zoom', help='semantic or physical zoom — never both')
    zm.add_argument('ref')
    zm.add_argument('kind', choices=('semantic', 'physical'),
                    help='semantic changes ontological resolution; physical '
                         'changes magnification and changes no claim')
    zm.add_argument('amount', type=float,
                    help='a level for semantic, a factor for physical')

    rs = sub.add_parser('restore', help='restore a navigation address')
    rs.add_argument('address')

    pa = sub.add_parser('path', help='cross-scale path between two entities')
    pa.add_argument('start')
    pa.add_argument('end')

    cv = sub.add_parser('coverage', help='populated against declared depth')
    cv.add_argument('--subsystem', default=None)
    cv.add_argument('--table', action='store_true',
                    help='human-readable matrix instead of JSON')

    sub.add_parser('levels', help='the eleven scale contracts')
    sub.add_parser('processes', help='the process register')

    pr = sub.add_parser('process', help='one process specification')
    pr.add_argument('pid')

    bl = sub.add_parser('build', help='build a release manifest (no publish)')
    bl.add_argument('release_id')

    pb = sub.add_parser('publish', help='validate, hash and publish a release')
    pb.add_argument('release_id')
    pb.add_argument('--out', default='releases')

    vf = sub.add_parser('verify', help='rebuild and compare against a manifest')
    vf.add_argument('manifest')

    df = sub.add_parser('diff', help='diff two release manifests')
    df.add_argument('a')
    df.add_argument('b')

    sv = sub.add_parser('serve', help='run the read API')
    sv.add_argument('--host', default='127.0.0.1')
    sv.add_argument('--port', type=int, default=8080)
    sv.add_argument('--queue', default=None,
                    help='curation queue file; without it the served API has '
                         'no write surface at all')

    q = sub.add_parser('queue', help='proposals awaiting review')
    q.add_argument('--queue', default=DEFAULT_QUEUE)
    q.add_argument('--reviewer', required=True,
                   help='reviewer identity; the queue is scoped to competence')

    rv = sub.add_parser('review', help='accept or reject a proposal')
    rv.add_argument('task')
    rv.add_argument('decision', choices=('accept', 'reject'))
    rv.add_argument('--queue', default=DEFAULT_QUEUE)
    rv.add_argument('--reviewer', required=True)
    rv.add_argument('--reason', required=True,
                    help='mandatory: a decision without a reason teaches '
                         'nobody anything')

    op = sub.add_parser('operator', help='queue depth, throughput, blocked')
    op.add_argument('--queue', default=DEFAULT_QUEUE)

    args = p.parse_args(argv)

    if args.command in ('build', 'publish', 'verify', 'diff'):
        if args.command == 'verify':
            m = load_manifest(args.manifest)
            ok = verify_rebuild(args.substrate, m)
            print(f'{"MATCH" if ok else "MISMATCH"}  {m.release_id}  '
                  f'{m.content_hash}')
            return 0 if ok else 1
        if args.command == 'diff':
            _print(diff(load_manifest(args.a), load_manifest(args.b)))
            return 0
        builder = ReleaseBuilder(args.substrate)
        if args.command == 'build':
            _print(builder.build(args.release_id).as_dict())
            return 0
        m = builder.publish(args.release_id, args.out)
        print(f'published {m.release_id}  {m.content_hash}  '
              f'{len(m.artifacts)} artifacts')
        return 0

    if args.command in ('queue', 'review', 'operator'):
        return _curation(args)

    if args.command == 'serve':
        serve(args.substrate, args.host, args.port, args.release,
              queue=args.queue)
        return 0

    svc = Service(args.substrate, release=args.release)
    if args.command == 'coverage' and args.table:
        rows = svc.scale.coverage(args.subsystem)
        print('COVERAGE — populated (reviewed) against declared depth')
        for row in rows:
            cells = ' '.join(
                f'L{c.level}:--' if c.excluded
                else f'L{c.level}:{c.populated}({c.reviewed})'
                for c in row.cells)
            unmet = (('  UNPOPULATED: '
                      + ', '.join(f'L{n}' for n in row.unmet_levels))
                     if row.unmet_levels else '')
            print(f'  {row.subsystem:<18} declared L{row.declared_depth}  '
                  f'{cells}{unmet}')
        summary = svc.scale.coverage_summary()
        print(f'\n{summary["populated_entities"]} entities across '
              f'{summary["occupiable_levels"]} occupiable levels; '
              f'{summary["reviewed_entities"]} reviewed, '
              f'{summary["unreviewed_entities"]} not.')
        print('A declared level with zero entities is an unmet declaration and '
              'is shown rather than implied.')
        print('`--` marks a level the subsystem cannot occupy: an organ system '
              'has no L0 or L1 content,')
        print('because the organism and its regions are not cardiovascular or '
              'digestive. Those were never')
        print('promises, so counting them unmet reported worse than the truth '
              '(D-018).')
        return 0

    dispatch_map = {
        'entity': lambda: svc.entity(args.ref),
        'relations': lambda: svc.relations(
            args.ref, types={args.type} if args.type else None),
        'claims': lambda: svc.claims(args.ref, evidence_class=args.cls),
        'unknowns': lambda: svc.unknowns(args.ref),
        'descend': lambda: svc.descend(args.ref),
        'search': lambda: svc.do_search(args.query, args.mode, args.cls,
                                        args.limit),
        'path': lambda: svc.path(args.start, args.end),
        'view': lambda: svc.view(
            args.ref, args.level, args.magnification,
            _csv(args.systems), _csv(args.tissue_classes), _csv(args.evidence),
            args.isolate),
        'zoom': lambda: svc.zoom(args.ref, args.kind, args.amount),
        'restore': lambda: svc.restore(args.address),
        'coverage': lambda: svc.coverage(args.subsystem),
        'levels': svc.levels,
        'processes': svc.processes,
        'process': lambda: svc.process(args.pid),
    }
    reply = dispatch_map[args.command]()
    _print(reply.body)
    return 0 if reply.status < 400 else 1


if __name__ == '__main__':
    sys.exit(main())
