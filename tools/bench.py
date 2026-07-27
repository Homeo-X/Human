#!/usr/bin/env python3
"""Measure the NFR register against synthetic substrates at volume.

Thirty-one NFR rows carry a number and a measurement method. Until this ran,
none carried a measurement. That is the ordinary way performance requirements
become decoration: they are written once, agreed to, and never executed, and the
first real measurement arrives when a user complains.

Only the rows measurable *here* are attempted. A benchmark that reports a number
for NFR-005 (30 fps on a mid-range GPU) from a headless container would be
fabricating a measurement, which is worse than the blank it replaces — the
unmeasurable rows are listed as such, with what they need.

    python3 tools/bench.py --sizes 1000,10000,100000
    python3 tools/bench.py --sizes 100000 --claims-per-entity 10   # NFR-008

Results go to `bench/RESULTS.json` with the date, the machine's own caveat, and
one row per (NFR, size). `--write-nfr` folds the measured column back into
docs/PRD_Non_Functional_Requirements.md.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import statistics
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from homeo.evidence import EvidenceService          # noqa: E402
from homeo.graph import Graph                       # noqa: E402
from homeo.scale import ScaleService                # noqa: E402
from homeo.substrate import load                    # noqa: E402

# Rows this harness cannot honestly measure, and what each would need. Listing
# them is the point: an unmeasured Must should be visible, not absent.
UNMEASURABLE = {
    'NFR-004': 'client instrumentation — needs the viewer (Phase 1)',
    'NFR-005': 'frame-time capture on real hardware — needs geometry and a GPU',
    'NFR-006': 'as NFR-005',
    'NFR-007': 'synthetic network test against a deployed build',
    'NFR-011': 'uptime monitoring over a month of real operation',
    'NFR-012': 'chaos test with a language model and index deployed',
    'NFR-013': 'offline test on the reference device, needs geometry',
    'NFR-015': 'WCAG audit of surfaces that do not exist yet',
    'NFR-016': 'manual audit with an assistive-technology user',
    'NFR-019': 'browser matrix', 'NFR-020': 'browser matrix',
    'NFR-024': 'needs a retrieval model in the loop',
}


def _pct(values: list[float], p: float) -> float:
    """Percentile in milliseconds, from seconds."""
    ordered = sorted(values)
    idx = min(int(len(ordered) * p), len(ordered) - 1)
    return ordered[idx] * 1000


def _time(fn, repeats: int) -> list[float]:
    out = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        out.append(time.perf_counter() - start)
    return out


def measure(root: str, repeats: int = 200) -> dict:
    """Every timing this harness can take against one substrate."""
    rss_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    start = time.perf_counter()
    substrate = load(root)
    load_s = time.perf_counter() - start

    start = time.perf_counter()
    graph = Graph(substrate)
    index_s = time.perf_counter() - start

    scale = ScaleService(graph)
    evidence = EvidenceService(graph, scale)
    rss_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    ids = [e.id for e in substrate.entities]
    step = max(1, len(ids) // repeats)
    sample = ids[::step][:repeats]

    # One pass over the sample, timed per entity rather than in bulk, so the
    # percentiles are per-request as NFR-001 states them.
    view_times = []
    for eid in sample:
        start = time.perf_counter()
        graph.get(eid)
        graph.edges(eid)
        evidence.claims_for(eid)
        view_times.append(time.perf_counter() - start)

    hop_times = []
    for eid in sample[:min(len(sample), 50)]:
        start = time.perf_counter()
        graph.traverse(eid, limit=3)
        hop_times.append(time.perf_counter() - start)

    # The navigation tree is the suspect: `Graph.children()` scans every entity
    # on every call, so a tree walk is O(n²). Measured separately from the
    # entity view because they diverge sharply if that is true.
    tree_times = []
    for eid in sample[:min(len(sample), 20)]:
        start = time.perf_counter()
        graph.descendants(eid)
        tree_times.append(time.perf_counter() - start)

    # One whole-tree walk from the root — FR-NAV-005's actual operation, and
    # the one that multiplies the per-call cost by the entity count. Timed once
    # rather than sampled: at the sizes where this matters, once is plenty.
    tree_root = substrate.entities[0].id
    start = time.perf_counter()
    graph.navigation_tree(tree_root)
    tree_walk_s = time.perf_counter() - start

    neg_times = []
    for eid in sample[:min(len(sample), 20)]:
        start = time.perf_counter()
        evidence.negative_space(eid)
        neg_times.append(time.perf_counter() - start)

    size = sum(os.path.getsize(os.path.join(dp, fn))
               for dp, _, fns in os.walk(root) for fn in fns)

    return {
        'entities': len(substrate.entities),
        'claims': len(substrate.claims),
        'relationships': len(substrate.relationships),
        'load_s': round(load_s, 3),
        'index_s': round(index_s, 3),
        'rss_mb': round((rss_after - rss_before) / 1024, 1),
        'disk_mb': round(size / 1e6, 1),
        'entity_view_p50_ms': round(_pct(view_times, 0.50), 2),
        'entity_view_p95_ms': round(_pct(view_times, 0.95), 2),
        'three_hop_p95_ms': round(_pct(hop_times, 0.95), 2),
        'negative_space_p95_ms': round(_pct(neg_times, 0.95), 2),
        'descendants_p95_ms': round(_pct(tree_times, 0.95), 2),
        'navigation_tree_ms': round(tree_walk_s * 1000, 1),
    }


def validation_time(root: str) -> dict:
    """NFR-009 — a full validation run at volume."""
    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), 'biocheck.py'),
         root],
        capture_output=True, text=True)
    return {'biocheck_s': round(time.perf_counter() - start, 2),
            'exit': proc.returncode}


def verdicts(row: dict) -> list[dict]:
    """Compare each measurement against the register's stated target."""
    return [
        {'nfr': 'NFR-001', 'target': 'p95 ≤ 300 ms, p50 ≤ 100 ms',
         'measured': f'p95 {row["entity_view_p95_ms"]} ms, '
                     f'p50 {row["entity_view_p50_ms"]} ms',
         'met': row['entity_view_p95_ms'] <= 300
                and row['entity_view_p50_ms'] <= 100},
        {'nfr': 'NFR-002', 'target': 'p95 ≤ 800 ms over ≤ 3 hops',
         'measured': f'p95 {row["three_hop_p95_ms"]} ms',
         'met': row['three_hop_p95_ms'] <= 800},
        {'nfr': 'NFR-002b', 'target': 'one step down the navigation tree, '
                                      'same p95 ≤ 800 ms budget',
         'measured': f'p95 {row["descendants_p95_ms"]} ms',
         'met': row['descendants_p95_ms'] <= 800},
        {'nfr': 'NFR-002c', 'target': 'whole navigation tree from the root, '
                                      'same p95 ≤ 800 ms budget',
         'measured': f'{row["navigation_tree_ms"]} ms',
         'met': row['navigation_tree_ms'] <= 800},
        {'nfr': 'NFR-003', 'target': 'p95 ≤ 1.5 s',
         'measured': f'p95 {row["negative_space_p95_ms"]} ms',
         'met': row['negative_space_p95_ms'] <= 1500},
        {'nfr': 'NFR-008', 'target': '10⁵ entities, 10⁶ claims, no '
                                     'architectural change',
         'measured': f'{row["entities"]} entities, {row["claims"]} claims, '
                     f'load {row["load_s"]} s, {row["rss_mb"]} MB resident',
         'met': None},
        {'nfr': 'NFR-026', 'target': '≤ 5 GB excluding geometry at Phase 5',
         'measured': f'{row["disk_mb"]} MB',
         'met': row['disk_mb'] <= 5000},
    ]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sizes', default='1000,10000,100000')
    ap.add_argument('--claims-per-entity', type=float, default=1.53)
    ap.add_argument('--work-dir', default='bench/substrates')
    ap.add_argument('--out', default='bench/RESULTS.json')
    ap.add_argument('--skip-validation', action='store_true')
    args = ap.parse_args(argv[1:])

    synth = os.path.join(os.path.dirname(__file__), 'synth.py')
    rows, all_verdicts = [], []
    for size in [int(s) for s in args.sizes.split(',')]:
        root = os.path.join(args.work_dir, str(size))
        if not os.path.isdir(root):
            subprocess.run([sys.executable, synth, root, '--entities',
                            str(size), '--claims-per-entity',
                            str(args.claims_per_entity)], check=True)
        row = measure(root)
        if not args.skip_validation:
            row.update(validation_time(root))
        rows.append(row)
        for v in verdicts(row):
            v['at_entities'] = row['entities']
            all_verdicts.append(v)
        print(f'{row["entities"]:>8} entities | load {row["load_s"]:>6.2f}s | '
              f'view p95 {row["entity_view_p95_ms"]:>7.2f}ms | '
              f'3-hop p95 {row["three_hop_p95_ms"]:>8.2f}ms | '
              f'desc p95 {row["descendants_p95_ms"]:>9.2f}ms | '
              f'neg p95 {row["negative_space_p95_ms"]:>8.2f}ms | '
              f'{row["rss_mb"]:>7.1f}MB')

    report = {
        'measured_on': time.strftime('%Y-%m-%d'),
        'caveat': ('Measured in a headless container against synthetic '
                   'substrates of the real one\'s shape. These are relative '
                   'and architectural numbers, not a claim about production '
                   'hardware; the rows requiring a browser, a GPU, geometry, '
                   'or a deployed service are listed as unmeasurable rather '
                   'than estimated.'),
        'unmeasurable': UNMEASURABLE,
        'rows': rows,
        'verdicts': all_verdicts,
    }
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=1)
    failed = [v for v in all_verdicts if v['met'] is False]
    print(f'\nwrote {args.out} — {len(all_verdicts)} verdicts, '
          f'{len(failed)} target(s) missed, '
          f'{len(UNMEASURABLE)} row(s) not measurable here')
    for v in failed:
        print(f'  MISSED {v["nfr"]} at {v["at_entities"]} entities: '
              f'{v["measured"]} against {v["target"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
