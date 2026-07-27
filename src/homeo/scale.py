"""Scale contracts, declared depth, and the honest terminal answer.

This module is where the model refuses to overclaim. Descending past a
subsystem's declared depth returns a composed answer about the *model*, never an
empty result and never an error — a user who reaches the edge has been served
correctly (FR-SCAL-003, FR-NAV-003).

Realizes: FR-SCAL-001, FR-SCAL-002, FR-SCAL-003, FR-SCAL-005, FR-SCAL-006,
FR-SCAL-009, FR-SCAL-010, FR-NAV-002, FR-NAV-003.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .graph import Graph
from .substrate import CONTAINMENT, ScaleContract

# BIO_Scale_Contract §Level Vocabulary Reconciliation. The common eight-level
# teaching scheme omits regions and cell populations; mapping it explicitly is
# what stops content being silently renumbered on ingest (FR-SCAL-008).
COMMON_SCHEME_TO_LEVEL = {1: 0, 2: 2, 3: 3, 4: 4, 5: 5, 6: 7, 7: 8, 8: 9}

# Levels that participate in the *containment* ladder.
#
# L2 is absent deliberately. An organ is physically contained in a region and is
# a MEMBER of a system; a system is a functional grouping, not a spatial
# container (D-006, BIO_Anatomical_Ontology §Hierarchy Rules). A containment
# path from organism to organ therefore runs L0 → L1 → L3 and is contiguous
# despite the numeric jump.
#
# L9 and L10 are absent for the same kind of reason: molecules and mechanisms
# attach to structures by participation, not containment — a molecule is not
# *part of* a sarcomere in the mereological sense.
CONTAINMENT_LEVELS = (0, 1, 3, 4, 5, 6, 7, 8)


@dataclass(frozen=True)
class TerminalAnswer:
    """What the model says when asked for something below its declared depth.

    A designed response with its own shape, deliberately not an error type: the
    HTTP layer returns it with 200, because a system that 404s "we do not model
    that" teaches users its honesty is a malfunction (TECH_API_Specification).
    """
    subsystem: str
    declared_level: int
    requested_level: int
    representation_mode: tuple[str, ...]
    resolution_limit: str
    statement: str
    external_resources: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {
            'not_represented': True,
            'subsystem': self.subsystem,
            'declared_level': self.declared_level,
            'requested_level': self.requested_level,
            'representation_mode': list(self.representation_mode),
            'resolution_limit': self.resolution_limit,
            'statement': self.statement,
            'external_resources': list(self.external_resources),
        }


@dataclass(frozen=True)
class LevelTransition:
    """Announced on every level crossing (FR-NAV-002).

    Carries the resolution limit because a user arriving by deep link never saw
    the transition that would otherwise have told them.
    """
    from_level: int | None
    to_level: int
    represents: str
    representation_mode: tuple[str, ...]
    resolution_limit: str
    located_in_body: bool

    def as_dict(self) -> dict:
        return {
            'from_level': self.from_level,
            'to_level': self.to_level,
            'represents': self.represents,
            'representation_mode': list(self.representation_mode),
            'resolution_limit': self.resolution_limit,
            'located_in_body': self.located_in_body,
            'note': (None if self.located_in_body else
                     'What is shown at this level is a representative type, not '
                     'a located object in this body.'),
        }


@dataclass
class CoverageCell:
    level: int
    populated: int
    declared: bool

    @property
    def unmet(self) -> bool:
        """A declared level with nothing in it is a promise not kept."""
        return self.declared and self.populated == 0


@dataclass
class SubsystemCoverage:
    subsystem: str
    declared_depth: int
    cells: list[CoverageCell] = field(default_factory=list)

    @property
    def unmet_levels(self) -> list[int]:
        return [c.level for c in self.cells if c.unmet]

    @property
    def populated_total(self) -> int:
        return sum(c.populated for c in self.cells)

    def as_dict(self) -> dict:
        return {
            'subsystem': self.subsystem,
            'declared_depth': self.declared_depth,
            'levels': [{'level': c.level, 'populated': c.populated,
                        'declared': c.declared, 'unmet': c.unmet}
                       for c in self.cells],
            'unmet_levels': self.unmet_levels,
            'populated_total': self.populated_total,
        }


# Modes at which the thing shown is a type or an exemplar rather than a located
# object in this particular body.
NON_LOCATED_MODES = frozenset({'typed', 'statistical', 'exemplar', 'referenced'})


class ScaleService:
    """Level contracts and the rules governing movement between them."""

    def __init__(self, graph: Graph):
        self.graph = graph
        sub = graph.substrate
        self.contracts: dict[int, ScaleContract] = {
            c.level: c for c in sub.scale_contracts}
        self.declared_depth: dict[str, int] = dict(sub.declared_depth)

    # ---- contracts -----------------------------------------------------

    def contract(self, level: int) -> ScaleContract | None:
        return self.contracts.get(level)

    def declared(self, subsystem: str) -> int | None:
        return self.declared_depth.get(subsystem)

    def map_common_scheme(self, common_level: int) -> int:
        """Translate an eight-level teaching scheme level into ours."""
        if common_level not in COMMON_SCHEME_TO_LEVEL:
            raise KeyError(f'no mapping for common-scheme level {common_level}')
        return COMMON_SCHEME_TO_LEVEL[common_level]

    def within_declared_depth(self, subsystem: str, level: int) -> bool:
        cap = self.declared(subsystem)
        return cap is not None and level <= cap

    # ---- transitions and the terminal answer ---------------------------

    def transition(self, to_level: int,
                   from_level: int | None = None) -> LevelTransition:
        c = self.contracts.get(to_level)
        if c is None:
            raise KeyError(f'no scale contract for L{to_level}')
        located = not (set(c.representation_mode) & NON_LOCATED_MODES)
        return LevelTransition(
            from_level=from_level, to_level=to_level, represents=c.represents,
            representation_mode=c.representation_mode,
            resolution_limit=c.resolution_limit, located_in_body=located)

    def terminal_answer(self, subsystem: str, requested_level: int,
                        external_resources: tuple[str, ...] = ()) -> TerminalAnswer:
        """Compose the answer for a request below declared depth.

        The wording is deliberate: it is a statement about the model, not about
        the biology, and it says so.
        """
        cap = self.declared(subsystem)
        if cap is None:
            raise KeyError(f'subsystem {subsystem!r} has no declared depth')
        c = self.contracts.get(cap)
        modes = c.representation_mode if c else ()
        limit = c.resolution_limit if c else 'not stated'
        statement = (
            f'Not represented at this level. The {subsystem} subsystem is '
            f'modelled to L{cap} ({", ".join(modes) or "unspecified"}). Below '
            f'that, this model holds nothing — that is a statement about the '
            f'model, not about the biology.')
        return TerminalAnswer(
            subsystem=subsystem, declared_level=cap,
            requested_level=requested_level, representation_mode=modes,
            resolution_limit=limit, statement=statement,
            external_resources=external_resources)

    def descend(self, entity_id: str) -> list[str] | TerminalAnswer:
        """One level down from an entity, or the terminal answer (FR-SCAL-003)."""
        entity = self.graph.resolve(entity_id)
        children = self.graph.children(entity.id)
        if children:
            return children
        current = entity.shallowest_level
        requested = (current + 1) if current is not None else 0
        return self.terminal_answer(entity.subsystem, requested)

    # ---- cross-scale paths ---------------------------------------------

    def cross_scale_path(self, start: str, end: str,
                         max_depth: int = 12) -> dict:
        """Find a containment path between two entities across levels.

        A broken chain is the interesting result and is reported as such: a path
        query that silently returns nothing teaches nothing (FR-SCAL-009).
        """
        a = self.graph.resolve(start)
        b = self.graph.resolve(end)
        up = self.graph.lineage(a.id)
        if b.id in up:
            path = up[:up.index(b.id) + 1]
            return self._path_result(path, complete=True)
        down = self.graph.lineage(b.id)
        if a.id in down:
            path = list(reversed(down[:down.index(a.id) + 1]))
            return self._path_result(path, complete=True)
        shared = set(up) & set(down)
        if shared:
            join = min(shared, key=lambda x: up.index(x))
            path = up[:up.index(join) + 1] + list(
                reversed(down[:down.index(join)]))
            return self._path_result(path, complete=True)
        missing = self._missing_levels(a, b)
        return {
            'complete': False,
            'from': a.id, 'to': b.id,
            'missing_levels': missing,
            'statement': (
                'No containment path exists between these entities in this '
                'release. ' + (
                    f'Levels {", ".join("L%d" % m for m in missing)} are '
                    'unpopulated between them.' if missing else
                    'They are not related by containment.')),
        }

    def _path_result(self, path: list[str], complete: bool) -> dict:
        """Report a containment path, and whether it is level-contiguous.

        A path that reaches its destination while skipping a level is *found*,
        not *complete*. For a model whose whole thesis is that skipped levels
        must be declared, reporting such a path as complete would be the
        characteristic failure committed by the tool meant to detect it — which
        is precisely what happened before D-013.
        """
        steps = []
        for eid in path:
            e = self.graph.get(eid)
            steps.append({
                'entity': eid,
                'label': e.preferred_term if e else eid,
                'level': e.shallowest_level if e else None,
                'compilation_status': e.compilation_status if e else None,
            })
        levels = [s['level'] for s in steps if s['level'] is not None]
        # Contiguity is assessed against the containment ladder, not against
        # every integer: a path from organism to organ legitimately runs
        # L0 → L1 → L3, because L2 attaches by membership rather than
        # containment. Measuring against all levels would report correct
        # structure as a gap.
        ladder = CONTAINMENT_LEVELS
        skipped: list[int] = []
        for a, b in zip(levels, levels[1:]):
            if a not in ladder or b not in ladder:
                continue
            lo, hi = sorted((ladder.index(a), ladder.index(b)))
            skipped.extend(ladder[i] for i in range(lo + 1, hi))
        contiguous = not skipped
        result = {
            'complete': complete and contiguous,
            'path_found': complete,
            'level_contiguous': contiguous,
            'from': path[0] if path else None,
            'to': path[-1] if path else None,
            'steps': steps,
            'missing_levels': sorted(set(skipped)),
        }
        if skipped:
            gaps = ', '.join(f'L{n}' for n in sorted(set(skipped)))
            result['statement'] = (
                f'A containment path exists, but it skips {gaps}: no entity at '
                f'{"those levels" if len(set(skipped)) > 1 else "that level"} '
                f'lies on it. The path is found, not complete — the model holds '
                f'nothing there.')
        return result

    def _missing_levels(self, a, b) -> list[int]:
        la, lb = a.shallowest_level, b.shallowest_level
        if la is None or lb is None:
            return []
        lo, hi = sorted((la, lb))
        populated = {lvl for e in self.graph.entities()
                     if e.subsystem in (a.subsystem, b.subsystem)
                     for lvl in e.levels}
        return [lvl for lvl in range(lo + 1, hi) if lvl not in populated]

    # ---- coverage ------------------------------------------------------

    def coverage(self, subsystem: str | None = None) -> list[SubsystemCoverage]:
        """Populated against declared, per subsystem per level.

        Reported as counts against the declared denominator rather than as a
        bare percentage, because a percentage is improved by shrinking its
        denominator (BR-021, FR-SCAL-010).
        """
        counts: dict[str, dict[int, int]] = {}
        for e in self.graph.entities():
            if e.is_retired:
                continue
            for lvl in e.levels:
                counts.setdefault(e.subsystem, {}).setdefault(lvl, 0)
                counts[e.subsystem][lvl] += 1
        out: list[SubsystemCoverage] = []
        names = ([subsystem] if subsystem else sorted(self.declared_depth))
        for name in names:
            cap = self.declared_depth.get(name)
            if cap is None:
                continue
            got = counts.get(name, {})
            cells = [CoverageCell(level=lvl, populated=got.get(lvl, 0),
                                  declared=True) for lvl in range(cap + 1)]
            out.append(SubsystemCoverage(subsystem=name, declared_depth=cap,
                                         cells=cells))
        return out

    def coverage_summary(self) -> dict:
        rows = self.coverage()
        return {
            'subsystems': [r.as_dict() for r in rows],
            'declared_levels': sum(len(r.cells) for r in rows),
            'unmet_declarations': sum(len(r.unmet_levels) for r in rows),
            'note': ('Counts are populated against declared depth. A declared '
                     'level with zero entities is an unmet declaration and is '
                     'shown rather than implied.'),
        }
