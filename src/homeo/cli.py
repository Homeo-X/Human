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
from .release import ReleaseBuilder, diff, load_manifest, verify_rebuild


def _print(payload) -> None:
    print(json.dumps(payload, indent=1, ensure_ascii=False))


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

    if args.command == 'serve':
        serve(args.substrate, args.host, args.port, args.release)
        return 0

    svc = Service(args.substrate, release=args.release)
    if args.command == 'coverage' and args.table:
        rows = svc.scale.coverage(args.subsystem)
        print('COVERAGE — populated against declared depth')
        for row in rows:
            cells = ' '.join(f'L{c.level}:{c.populated}' for c in row.cells)
            unmet = (('  UNPOPULATED: '
                      + ', '.join(f'L{n}' for n in row.unmet_levels))
                     if row.unmet_levels else '')
            print(f'  {row.subsystem:<18} declared L{row.declared_depth}  '
                  f'{cells}{unmet}')
        print('\nA declared level with zero entities is an unmet declaration,')
        print('and is shown rather than implied.')
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
