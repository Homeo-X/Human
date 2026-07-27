"""Search: name, function, clinical, spatial, negative-space, and structured.

Every result carries the compilation status of what matched and the evidence
class of the claim that matched it. A results list is where evidence grading is
most easily lost and most needed (FR-SRCH-002).

The negative-space mode is what distinguishes this from a search box: a user can
ask what is *not* known and get an enumerated answer rather than inferring it
from an empty result (FR-SRCH-004).

Realizes: FR-SRCH-001, FR-SRCH-002, FR-SRCH-003, FR-SRCH-004, FR-SRCH-005,
FR-SRCH-006, FR-SRCH-007, FR-SRCH-008.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .evidence import EvidenceService
from .graph import Graph
from .scale import ScaleService

MODES = ('name', 'function', 'clinical', 'spatial', 'negative', 'structured')
DEFAULT_LIMIT = 50
MAX_TRAVERSAL = 6

# Lay and clinical vocabulary mapped to structures. Deliberately small and
# explicit: this maps terms to anatomy, and never to a diagnosis (FR-SRCH-008).
CLINICAL_TERMS = {
    'heart attack': ('UBERON:0000948', 'UBERON:0002349'),
    'myocardial infarction': ('UBERON:0000948', 'UBERON:0002349'),
    'heart muscle': ('UBERON:0002349',),
    'pump chamber': ('UBERON:0002084',),
}


@dataclass
class Result:
    entity_id: str
    label: str
    level: int | None
    subsystem: str
    compilation_status: str
    matched_on: str
    matched_term: str | None = None
    matched_claim: str | None = None
    evidence_class: str | None = None
    note: str | None = None

    def as_dict(self) -> dict:
        return {
            'entity': self.entity_id, 'label': self.label, 'level': self.level,
            'subsystem': self.subsystem,
            'compilation_status': self.compilation_status,
            'matched_on': self.matched_on, 'matched_term': self.matched_term,
            'matched_claim': self.matched_claim,
            'evidence_class': self.evidence_class, 'note': self.note,
        }


@dataclass
class ResultSet:
    mode: str
    query: str
    results: list[Result] = field(default_factory=list)
    excluded_by_filter: int = 0
    ranking_basis: str = 'relevance'
    statement: str | None = None

    def as_dict(self) -> dict:
        return {
            'mode': self.mode, 'query': self.query,
            'count': len(self.results),
            'excluded_by_filter': self.excluded_by_filter,
            'ranking_basis': self.ranking_basis,
            'statement': self.statement,
            'results': [r.as_dict() for r in self.results],
        }


class QuerySyntaxError(ValueError):
    """A structured query that could not be parsed. Never a partial execution."""


class SearchService:
    def __init__(self, graph: Graph, evidence: EvidenceService,
                 scale: ScaleService):
        self.graph = graph
        self.evidence = evidence
        self.scale = scale

    # ---- dispatch ------------------------------------------------------

    def search(self, query: str, mode: str = 'name', *,
               min_class: str | None = None,
               limit: int = DEFAULT_LIMIT) -> ResultSet:
        if mode not in MODES:
            raise QuerySyntaxError(
                f'unknown mode {mode!r}; expected one of {", ".join(MODES)}')
        fn = getattr(self, f'_search_{mode}')
        rs = fn(query, limit)
        if min_class:
            rs = self._filter_by_class(rs, min_class)
        return rs

    def _filter_by_class(self, rs: ResultSet, min_class: str) -> ResultSet:
        """Filter by evidence class, reporting how many were hidden.

        The count matters: an empty filtered view must not read as "nothing is
        known" (FR-SRCH-006, FR-NAV-007).
        """
        try:
            threshold = int(min_class.split('-')[1])
        except (IndexError, ValueError) as exc:
            raise QuerySyntaxError(f'bad evidence class {min_class!r}') from exc
        kept, dropped = [], 0
        for r in rs.results:
            if r.evidence_class is None:
                kept.append(r)
                continue
            rank = int(r.evidence_class.split('-')[1])
            if rank <= threshold:
                kept.append(r)
            else:
                dropped += 1
        rs.results = kept
        rs.excluded_by_filter += dropped
        rs.ranking_basis = f'relevance; filtered to {min_class} or stronger'
        return rs

    # ---- modes ---------------------------------------------------------

    def _search_name(self, query: str, limit: int) -> ResultSet:
        """Match preferred terms, synonyms, eponyms and abbreviations.

        The matched form is reported, not just the answer: showing which term
        matched teaches the vocabulary (FR-SRCH-001).
        """
        q = query.strip().lower()
        rs = ResultSet(mode='name', query=query)
        # Rank exactness before position: an exact synonym must outrank a
        # substring of some unrelated preferred term ("cor" inside "Cortex").
        scored: list[tuple[int, Result]] = []
        for e in self.graph.entities():
            if e.is_retired:
                continue
            hit = None
            if q == e.preferred_term.lower():
                hit = (0, 'preferred term', e.preferred_term)
            else:
                for s in e.synonyms:
                    term = str(s.get('term', ''))
                    if q == term.lower():
                        hit = (1, f'synonym ({s.get("register", "unspecified")})',
                               term)
                        break
            if hit is None and q in e.preferred_term.lower():
                hit = (2, 'preferred term (partial)', e.preferred_term)
            if hit is None:
                for s in e.synonyms:
                    term = str(s.get('term', ''))
                    if q in term.lower():
                        hit = (3,
                               f'synonym, partial '
                               f'({s.get("register", "unspecified")})', term)
                        break
            if hit:
                scored.append((hit[0],
                               self._result(e, hit[1], matched_term=hit[2])))
        scored.sort(key=lambda pair: (pair[0], pair[1].label))
        rs.results = [r for _, r in scored[:limit]]
        rs.ranking_basis = 'exactness of term match, then label'
        if not rs.results:
            near = self._near_matches(q, limit=5)
            rs.statement = (
                'No match. ' + (f'Nearest terms: {", ".join(near)}.' if near
                                else 'No similar terms in this release.'))
        return rs

    def _search_function(self, query: str, limit: int) -> ResultSet:
        """Match function and process claims, not only labels (FR-SRCH-003)."""
        q = query.strip().lower()
        rs = ResultSet(mode='function', query=query)
        for c in self.evidence.all_claims():
            text = f'{c.predicate} {c.object}'.lower()
            if q not in text:
                continue
            e = self.graph.get(c.subject)
            if e is None or e.is_retired:
                continue
            note = None
            if e.compilation_status == 'narrative':
                note = ('Narrative content: this describes the function, it does '
                        'not model it.')
            rs.results.append(self._result(
                e, 'function claim', matched_claim=c.id,
                evidence_class=c.evidence_class, note=note))
            if len(rs.results) >= limit:
                break
        return rs

    def _search_clinical(self, query: str, limit: int) -> ResultSet:
        """Map clinical vocabulary to structures — never to a diagnosis."""
        q = query.strip().lower()
        rs = ResultSet(mode='clinical', query=query)
        targets = CLINICAL_TERMS.get(q)
        if targets is None:
            for term, ids in CLINICAL_TERMS.items():
                if q in term:
                    targets = ids
                    break
        if not targets:
            rs.statement = (
                'No clinical mapping for this term in this release. The model '
                'maps clinical vocabulary to anatomical structures only; it '
                'does not interpret, diagnose, or advise.')
            return rs
        for eid in targets[:limit]:
            e = self.graph.get(eid)
            if e:
                rs.results.append(self._result(
                    e, 'clinical term mapping',
                    note=('Mapped to the structures involved. This is a '
                          'vocabulary mapping, not a diagnosis.')))
        rs.statement = ('Structures associated with this clinical term. The '
                        'model does not diagnose, treat, or advise.')
        return rs

    def _search_spatial(self, query: str, limit: int) -> ResultSet:
        """Containment, adjacency and laterality over spatial identities.

        Operates on spatial identities rather than mesh proximity, so it works
        for entities with no geometry at all (FR-SPAT-008).
        """
        rs = ResultSet(mode='spatial', query=query)
        parts = query.strip().split(':', 1)
        if len(parts) != 2:
            raise QuerySyntaxError(
                'spatial query form: "<predicate>:<entity>" where predicate is '
                'adjacent_to, contains, or contained_in')
        predicate, ref = parts[0].strip(), parts[1].strip()
        # Validate the predicate before resolving the reference: a bad predicate
        # is a syntax error whether or not the entity happens to exist, and
        # checking resolution first would mask it behind "no such entity".
        if predicate not in ('adjacent_to', 'contained_in', 'contains'):
            raise QuerySyntaxError(
                f'unknown spatial predicate {predicate!r}; expected '
                'adjacent_to, contained_in, or contains')
        try:
            entity = self.graph.resolve(ref)
        except KeyError:
            rs.statement = f'No entity resolves to {ref!r}.'
            return rs
        si = self.graph.spatial_identity(entity.id)
        if si is None:
            rs.statement = (
                f'{entity.preferred_term} has no spatial identity in this '
                'release, so spatial predicates cannot be evaluated for it.')
            return rs
        if predicate == 'adjacent_to':
            ids = si.adjacent_to
        elif predicate == 'contained_in':
            ids = (si.contained_in,) if si.contained_in else ()
        else:
            ids = tuple(s.entity for s in self.graph.substrate.spatial_identities
                        if s.contained_in == entity.id)
        for eid in ids[:limit]:
            e = self.graph.get(eid)
            if e:
                rs.results.append(self._result(e, f'spatial: {predicate}'))
            else:
                rs.results.append(Result(
                    entity_id=eid, label=eid, level=None, subsystem='unknown',
                    compilation_status='narrative',
                    matched_on=f'spatial: {predicate}',
                    note='Referenced by a spatial identity but not defined as an '
                         'entity in this release.'))
        return rs

    def _search_negative(self, query: str, limit: int) -> ResultSet:
        """What is unknown, unrepresented, or unmodelled about a subject."""
        rs = ResultSet(mode='negative', query=query)
        try:
            entity = self.graph.resolve(query.strip())
        except KeyError:
            rs.statement = f'No entity resolves to {query!r}.'
            return rs
        ns = self.evidence.negative_space(entity.id)
        rs.statement = ns.statement
        for uc in ns.unknown_claims[:limit]:
            rs.results.append(Result(
                entity_id=entity.id, label=entity.preferred_term,
                level=entity.shallowest_level, subsystem=entity.subsystem,
                compilation_status=entity.compilation_status,
                matched_on='recorded gap', matched_claim=uc['claim'],
                evidence_class=uc['evidence_class'],
                note=str(uc['object'])))
        if ns.unpopulated_levels:
            rs.statement += (
                ' Declared but unpopulated levels in this subsystem: '
                + ', '.join(f'L{lvl}' for lvl in ns.unpopulated_levels) + '.')
        return rs

    def _search_structured(self, query: str, limit: int) -> ResultSet:
        """Filter expression: `key=value` pairs separated by whitespace.

        Keys: class (entity class), level, subsystem, status (compilation),
        relation (has an edge of this type), evidence (best claim class).
        """
        rs = ResultSet(mode='structured', query=query)
        filters: dict[str, str] = {}
        for token in query.split():
            if '=' not in token:
                raise QuerySyntaxError(
                    f'expected key=value, got {token!r} at position '
                    f'{query.index(token)}')
            k, v = token.split('=', 1)
            if k not in ('class', 'level', 'subsystem', 'status', 'relation',
                         'evidence'):
                raise QuerySyntaxError(f'unknown filter key {k!r}')
            filters[k] = v
        for e in self.graph.entities():
            if e.is_retired:
                continue
            if 'class' in filters and e.entity_class != filters['class']:
                continue
            if 'subsystem' in filters and e.subsystem != filters['subsystem']:
                continue
            if 'status' in filters and e.compilation_status != filters['status']:
                continue
            if 'level' in filters:
                try:
                    want = int(filters['level'])
                except ValueError as exc:
                    raise QuerySyntaxError('level must be an integer') from exc
                if want not in e.levels:
                    continue
            if 'relation' in filters:
                if not self.graph.edges(e.id, types={filters['relation']}):
                    continue
            best = None
            claims = self.evidence.claims_for(e.id)
            if claims:
                best = min(c.evidence_class for c in claims)
            if 'evidence' in filters:
                if best is None or best > filters['evidence']:
                    continue
            rs.results.append(self._result(
                e, 'structured filter', evidence_class=best))
            if len(rs.results) >= limit:
                break
        rs.ranking_basis = 'substrate order; structured queries are unranked'
        return rs

    # ---- helpers -------------------------------------------------------

    def _result(self, entity, matched_on: str, **kw) -> Result:
        return Result(
            entity_id=entity.id, label=entity.preferred_term,
            level=entity.shallowest_level, subsystem=entity.subsystem,
            compilation_status=entity.compilation_status,
            matched_on=matched_on, **kw)

    def _near_matches(self, q: str, limit: int) -> list[str]:
        scored = []
        for e in self.graph.entities():
            term = e.preferred_term.lower()
            shared = len(set(q) & set(term))
            if shared >= max(2, len(q) // 2):
                scored.append((shared, e.preferred_term))
        scored.sort(reverse=True)
        return [t for _, t in scored[:limit]]
