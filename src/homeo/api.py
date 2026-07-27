"""The read API — stateless, release-pinned, unauthenticated.

The status-code posture is the product's honesty made machine-readable
(TECH_API_Specification §Error Handling): **the model's limits are 200s, and
only genuine caller errors are 4xx.** A system that returns 404 for "we do not
model that" teaches its users that its honesty is a malfunction.

No authentication, deliberately: the reference model is a public good and has no
privileged data (FR-CUR-007). Adding auth would be theatre.

Realizes: TECH_API_Specification; serves FR-ONTO-*, FR-REL-*, FR-EVID-*,
FR-SCAL-*, FR-SRCH-*, FR-PHYS-*, FR-VER-*, FR-RETR-*.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from .evidence import EvidenceService
from .graph import EntityRetired, Graph
from .groundedness import Assertion, GroundednessGuard
from .scale import ScaleService, TerminalAnswer
from .search import QuerySyntaxError, SearchService
from .substrate import load

API_VERSION = 'v1'


@dataclass
class Reply:
    status: int
    body: dict
    headers: dict | None = None


def error(code: str, http: int, message: str, **detail) -> Reply:
    return Reply(http, {'error': {
        'code': code, 'message': message, 'detail': detail or {}}})


class Service:
    """The API's logic, independent of transport so it is directly testable."""

    def __init__(self, substrate_root: str, release: str = 'unpinned'):
        self.graph = Graph(load(substrate_root))
        self.scale = ScaleService(self.graph)
        self.evidence = EvidenceService(self.graph, self.scale)
        self.search = SearchService(self.graph, self.evidence, self.scale)
        self.guard = GroundednessGuard(self.graph, self.evidence, self.scale,
                                       release=release)
        self.release = release

    # ---- envelope ------------------------------------------------------

    def _envelope(self, payload: dict) -> dict:
        """Every response states which release answered it, and the boundary.

        A caller must never have to guess what answered them
        (TECH_API_Specification §Conventions).
        """
        payload.setdefault('release', self.release)
        payload.setdefault('api_version', API_VERSION)
        payload.setdefault(
            'boundary',
            'Educational and research reference. Not a medical device; does not '
            'diagnose, treat, or advise.')
        return payload

    def _entity_payload(self, e) -> dict:
        si = self.graph.spatial_identity(e.id)
        claims = self.evidence.claims_for(e.id)
        return {
            'id': e.id, 'preferred_term': e.preferred_term,
            'entity_class': e.entity_class, 'subsystem': e.subsystem,
            'level': e.level, 'spatial_scale': list(e.spatial_scale),
            'level_contributions': e.level_contributions,
            # Never optional: status and grade are part of what a thing is here,
            # not metadata about it (FR-ONTO-006, FR-EVID-002).
            'compilation_status': e.compilation_status,
            'representation_mode': e.representation_mode,
            'minted': e.minted, 'minted_reason': e.minted_reason,
            'synonyms': list(e.synonyms), 'xrefs': list(e.xrefs),
            'lineage': self.graph.lineage(e.id),
            'memberships': self.graph.memberships(e.id),
            'claim_summary': {
                'count': len(claims),
                'classes': sorted({c.evidence_class for c in claims}),
                'unknown': sum(1 for c in claims if c.is_unknown)},
            'spatial_identity': (None if si is None else {
                'id': si.id, 'coordinate_frame': si.coordinate_frame,
                'anatomical_position': si.anatomical_position,
                'laterality': si.laterality,
                'has_geometry': si.has_geometry,
                'note': (None if si.has_geometry else
                         'Described, not depicted: this entity has a spatial '
                         'identity but no geometry in this release. That is a '
                         'statement about available assets, not about the '
                         'anatomy.')}),
            'provenance_source': e.provenance_source,
        }

    # ---- entities ------------------------------------------------------

    def entity(self, ref: str) -> Reply:
        try:
            e = self.graph.resolve(ref)
        except EntityRetired as exc:
            # 301, not 404: the caller's reference was valid and deserves an
            # answer (FR-ONTO-004, FR-VER-007).
            return Reply(301, self._envelope({
                'error': {'code': 'ENTITY_RETIRED',
                          'message': f'{exc.entity_id} was retired',
                          'detail': {'retired_at': exc.retired_at,
                                     'successor': exc.successor}},
                'successor': exc.successor}),
                headers=({'Location': f'/{API_VERSION}/entities/{exc.successor}'}
                         if exc.successor else None))
        except KeyError:
            return error('NOT_FOUND', 404, f'no entity resolves to {ref!r}')
        return Reply(200, self._envelope(self._entity_payload(e)))

    def relations(self, ref: str, *, types: set[str] | None = None,
                  direction: str = 'both') -> Reply:
        try:
            e = self.graph.resolve(ref)
        except (KeyError, EntityRetired):
            return error('NOT_FOUND', 404, f'no entity resolves to {ref!r}')
        rows = []
        for edge in self.graph.edges(e.id, types=types, direction=direction):
            other = self.graph.get(edge.other)
            rows.append({
                'relation': edge.relation.id, 'type': edge.type,
                'outbound': edge.outbound, 'other': edge.other,
                'other_label': other.preferred_term if other else edge.other,
                'compilation_status': edge.relation.compilation_status,
                # An untyped association must be labelled at every surface that
                # shows it, and never rendered as a mechanism (FR-REL-006).
                'untyped_association': edge.is_untyped_association,
                'prose_justification': edge.relation.prose_justification,
                'skip_justification': edge.relation.skip_justification,
                'provenance_claim': edge.relation.provenance_claim,
            })
        return Reply(200, self._envelope({
            'entity': e.id, 'count': len(rows), 'relations': rows}))

    def claims(self, ref: str, evidence_class: str | None = None) -> Reply:
        try:
            e = self.graph.resolve(ref)
        except (KeyError, EntityRetired):
            return error('NOT_FOUND', 404, f'no entity resolves to {ref!r}')
        rows = [self.evidence.provenance(c.id).as_dict()
                for c in self.evidence.claims_for(
                    e.id, evidence_class=evidence_class)]
        return Reply(200, self._envelope({
            'entity': e.id, 'count': len(rows), 'claims': rows}))

    def unknowns(self, ref: str) -> Reply:
        try:
            ns = self.evidence.negative_space(ref)
        except (KeyError, EntityRetired):
            return error('NOT_FOUND', 404, f'no entity resolves to {ref!r}')
        return Reply(200, self._envelope(ns.as_dict()))

    def geometry(self, ref: str) -> Reply:
        try:
            e = self.graph.resolve(ref)
        except (KeyError, EntityRetired):
            return error('NOT_FOUND', 404, f'no entity resolves to {ref!r}')
        si = self.graph.spatial_identity(e.id)
        if si is None:
            return Reply(200, self._envelope({
                'entity': e.id, 'spatial_identity': None, 'geometry': [],
                'statement': ('This entity has no spatial identity in this '
                              'release, so no geometry can bind to it.')}))
        return Reply(200, self._envelope({
            'entity': e.id, 'spatial_identity': si.id,
            'coordinate_frame': si.coordinate_frame,
            'geometry': [dict(g) for g in si.geometry],
            'statement': (None if si.has_geometry else
                          'Described, not depicted: position and relations are '
                          'available; no geometry has been bound.')}))

    # ---- claims --------------------------------------------------------

    def claim(self, claim_id: str) -> Reply:
        if not self.evidence.has(claim_id):
            return error('NOT_FOUND', 404, f'no claim {claim_id!r}')
        return Reply(200, self._envelope(
            {'claim': self.evidence.provenance(claim_id).as_dict()}))

    def provenance(self, claim_id: str) -> Reply:
        if not self.evidence.has(claim_id):
            return error('NOT_FOUND', 404, f'no claim {claim_id!r}')
        return Reply(200, self._envelope(
            self.evidence.provenance(claim_id).as_dict()))

    def conflicts(self, claim_id: str) -> Reply:
        if not self.evidence.has(claim_id):
            return error('NOT_FOUND', 404, f'no claim {claim_id!r}')
        rows = [p.as_dict() for p in self.evidence.conflicts(claim_id)]
        return Reply(200, self._envelope({
            'claim': claim_id, 'count': len(rows), 'conflicts': rows,
            'statement': ('Both positions are retained. The system does not '
                          'select between credible sources.')}))

    # ---- scale ---------------------------------------------------------

    def levels(self) -> Reply:
        rows = [{
            'id': c.id, 'level': c.level, 'represents': c.represents,
            'representation_mode': list(c.representation_mode),
            'evidence_model': c.evidence_model,
            'uncertainty_model': c.uncertainty_model,
            'computational_cost': c.computational_cost,
            'resolution_limit': c.resolution_limit,
        } for c in sorted(self.scale.contracts.values(), key=lambda x: x.level)]
        return Reply(200, self._envelope({'count': len(rows), 'levels': rows}))

    def level(self, n: int) -> Reply:
        c = self.scale.contract(n)
        if c is None:
            return error('NOT_FOUND', 404, f'no scale contract for L{n}')
        return Reply(200, self._envelope({
            'id': c.id, 'level': c.level, 'represents': c.represents,
            'representation_mode': list(c.representation_mode),
            'data_model': c.data_model, 'spatial_model': c.spatial_model,
            'functional_model': c.functional_model,
            'evidence_model': c.evidence_model,
            'uncertainty_model': c.uncertainty_model,
            'computational_cost': c.computational_cost,
            'resolution_limit': c.resolution_limit}))

    def descend(self, ref: str) -> Reply:
        """One level down, or the terminal answer — both HTTP 200.

        NOT_REPRESENTED is an answer, and an error status would misrepresent a
        designed response as a fault (FR-SCAL-003).
        """
        try:
            result = self.scale.descend(ref)
        except (KeyError, EntityRetired):
            return error('NOT_FOUND', 404, f'no entity resolves to {ref!r}')
        if isinstance(result, TerminalAnswer):
            payload = result.as_dict()
            payload['code'] = 'NOT_REPRESENTED'
            return Reply(200, self._envelope(payload))
        rows = []
        for cid in result:
            child = self.graph.get(cid)
            if child is None:
                continue
            transition = None
            lvl = child.shallowest_level
            if lvl is not None and self.scale.contract(lvl):
                transition = self.scale.transition(lvl).as_dict()
            rows.append({'entity': cid, 'label': child.preferred_term,
                         'level': lvl,
                         'compilation_status': child.compilation_status,
                         'transition': transition})
        return Reply(200, self._envelope({
            'entity': ref, 'count': len(rows), 'children': rows}))

    def coverage(self, subsystem: str | None = None) -> Reply:
        if subsystem:
            rows = self.scale.coverage(subsystem)
            if not rows:
                return error('NOT_FOUND', 404,
                             f'no declared depth for subsystem {subsystem!r}')
            return Reply(200, self._envelope(rows[0].as_dict()))
        return Reply(200, self._envelope(self.scale.coverage_summary()))

    def path(self, start: str, end: str) -> Reply:
        try:
            return Reply(200, self._envelope(
                self.scale.cross_scale_path(start, end)))
        except (KeyError, EntityRetired) as exc:
            return error('NOT_FOUND', 404, str(exc))

    # ---- processes -----------------------------------------------------

    def processes(self) -> Reply:
        rows = [{
            'id': p.id, 'label': p.label, 'subsystem': p.subsystem,
            'spatial_scale': list(p.spatial_scale),
            'timescale_domain': p.timescale_domain,
            # A named process rendered like a modelled one is BRB-17; the status
            # is mandatory in every payload that carries a process.
            'representation_status': p.representation_status,
            'evidence_class': p.evidence_class,
        } for p in self.graph.substrate.processes]
        return Reply(200, self._envelope({
            'count': len(rows), 'processes': rows,
            'note': ('Representation status is not decoration: only a process '
                     'at "structured" or above carries inputs, outputs, state '
                     'variables and a mechanism.')}))

    def process(self, pid: str) -> Reply:
        for p in self.graph.substrate.processes:
            if p.id == pid:
                return Reply(200, self._envelope({
                    'id': p.id, 'label': p.label, 'subsystem': p.subsystem,
                    'spatial_scale': list(p.spatial_scale),
                    'level_contributions': p.level_contributions,
                    'timescale_domain': p.timescale_domain,
                    'characteristic_duration': p.characteristic_duration,
                    'representation_status': p.representation_status,
                    'evidence_class': p.evidence_class,
                    'inputs': list(p.inputs), 'outputs': list(p.outputs),
                    'participants': list(p.participants),
                    'state_variables': [dict(s) for s in p.state_variables],
                    'mechanism': list(p.mechanism),
                    'depends_on': list(p.depends_on),
                    'feedback_loops': [dict(f) for f in p.feedback_loops],
                    'failure_states': [dict(f) for f in p.failure_states],
                    'limitations': p.limitations,
                    'executable': p.is_executable}))
        return error('NOT_FOUND', 404, f'no process {pid!r}')

    def run_process(self, pid: str) -> Reply:
        """Refuse to run a non-executable process (FR-SIM-001)."""
        for p in self.graph.substrate.processes:
            if p.id == pid:
                if not p.is_executable:
                    return error(
                        'PROCESS_NOT_EXECUTABLE', 409,
                        f'{pid} is at status {p.representation_status!r} and '
                        f'cannot be executed',
                        unmet=['every parameter sourced',
                               'every coupling declared',
                               'capability limits written'],
                        status=p.representation_status)
                return error('NOT_IMPLEMENTED', 501,
                             'the simulation runtime is Phase 6')
        return error('NOT_FOUND', 404, f'no process {pid!r}')

    # ---- search and retrieval ------------------------------------------

    def do_search(self, q: str, mode: str, min_class: str | None,
                  limit: int) -> Reply:
        try:
            rs = self.search.search(q, mode, min_class=min_class, limit=limit)
        except QuerySyntaxError as exc:
            return error('QUERY_SYNTAX', 422, str(exc), mode=mode, query=q)
        return Reply(200, self._envelope(rs.as_dict()))

    def ask(self, question: str, assertions: list[dict]) -> Reply:
        """Guarded natural-language response.

        Refusals and gaps return 200 with their reason: a refusal is a valid
        answer, and 4xx would imply the caller erred (FR-RETR-001).
        """
        parsed = [Assertion(text=a.get('text', ''),
                            claim_ids=list(a.get('claims', [])))
                  for a in assertions]
        return Reply(200, self._envelope(
            self.guard.guard(question, parsed).as_dict()))

    # ---- release -------------------------------------------------------

    def release_info(self) -> Reply:
        return Reply(200, self._envelope({
            'release': self.release,
            'records': self.graph.substrate.record_count(),
            'entities': len(self.graph),
            'completeness': self.evidence.completeness(),
            'coverage': self.scale.coverage_summary()}))


ROUTES = [
    (re.compile(rf'^/{API_VERSION}/entities/([^/]+)/relations$'), 'relations'),
    (re.compile(rf'^/{API_VERSION}/entities/([^/]+)/claims$'), 'claims'),
    (re.compile(rf'^/{API_VERSION}/entities/([^/]+)/unknowns$'), 'unknowns'),
    (re.compile(rf'^/{API_VERSION}/entities/([^/]+)/geometry$'), 'geometry'),
    (re.compile(rf'^/{API_VERSION}/entities/([^/]+)/descend$'), 'descend'),
    (re.compile(rf'^/{API_VERSION}/entities/([^/]+)$'), 'entity'),
    (re.compile(rf'^/{API_VERSION}/claims/([^/]+)/provenance$'), 'provenance'),
    (re.compile(rf'^/{API_VERSION}/claims/([^/]+)/conflicts$'), 'conflicts'),
    (re.compile(rf'^/{API_VERSION}/claims/([^/]+)$'), 'claim'),
    (re.compile(rf'^/{API_VERSION}/levels/(\d+)$'), 'level'),
    (re.compile(rf'^/{API_VERSION}/levels$'), 'levels'),
    (re.compile(rf'^/{API_VERSION}/coverage$'), 'coverage'),
    (re.compile(rf'^/{API_VERSION}/path$'), 'path'),
    (re.compile(rf'^/{API_VERSION}/processes/([^/]+)/runs$'), 'run_process'),
    (re.compile(rf'^/{API_VERSION}/processes/([^/]+)$'), 'process'),
    (re.compile(rf'^/{API_VERSION}/processes$'), 'processes'),
    (re.compile(rf'^/{API_VERSION}/search$'), 'search'),
    (re.compile(rf'^/{API_VERSION}/ask$'), 'ask'),
    (re.compile(rf'^/{API_VERSION}/release$'), 'release'),
]


def dispatch(service: Service, path: str, query: dict,
             body: dict | None = None) -> Reply:
    """Route a request. Kept transport-free so tests exercise it directly."""
    for pattern, name in ROUTES:
        m = pattern.match(path)
        if not m:
            continue
        args = [unquote(g) for g in m.groups()]
        if name == 'relations':
            types = query.get('type')
            return service.relations(
                args[0], types=set(types[0].split(',')) if types else None,
                direction=query.get('direction', ['both'])[0])
        if name == 'claims':
            cls = query.get('class', [None])[0]
            return service.claims(args[0], evidence_class=cls)
        if name in ('unknowns', 'geometry', 'descend', 'entity'):
            return getattr(service, name)(args[0])
        if name in ('claim', 'provenance', 'conflicts'):
            return getattr(service, name)(args[0])
        if name == 'level':
            return service.level(int(args[0]))
        if name == 'levels':
            return service.levels()
        if name == 'coverage':
            return service.coverage(query.get('subsystem', [None])[0])
        if name == 'path':
            start = query.get('from', [None])[0]
            end = query.get('to', [None])[0]
            if not start or not end:
                return error('QUERY_SYNTAX', 422,
                             'path requires from= and to= parameters')
            return service.path(start, end)
        if name in ('processes', 'process', 'run_process'):
            return (service.processes() if name == 'processes'
                    else getattr(service, name)(args[0]))
        if name == 'search':
            q = query.get('q', [''])[0]
            return service.do_search(
                q, query.get('mode', ['name'])[0],
                query.get('class', [None])[0],
                int(query.get('limit', ['50'])[0]))
        if name == 'ask':
            payload = body or {}
            return service.ask(payload.get('question', ''),
                               payload.get('assertions', []))
        if name == 'release':
            return service.release_info()
    return error('NOT_FOUND', 404, f'no route for {path}')


class Handler(BaseHTTPRequestHandler):
    service: Service

    def _reply(self, reply: Reply) -> None:
        blob = json.dumps(reply.body, indent=1, ensure_ascii=False).encode()
        self.send_response(reply.status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(blob)))
        for k, v in (reply.headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(blob)

    def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
        u = urlparse(self.path)
        self._reply(dispatch(self.service, u.path, parse_qs(u.query)))

    def do_POST(self) -> None:  # noqa: N802
        u = urlparse(self.path)
        length = int(self.headers.get('Content-Length') or 0)
        try:
            body = json.loads(self.rfile.read(length) or b'{}')
        except ValueError:
            self._reply(error('BAD_JSON', 400, 'request body is not valid JSON'))
            return
        self._reply(dispatch(self.service, u.path, parse_qs(u.query), body))

    def log_message(self, *args) -> None:
        pass


def serve(substrate_root: str, host: str = '127.0.0.1', port: int = 8080,
          release: str = 'unpinned') -> None:
    Handler.service = Service(substrate_root, release=release)
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f'homeo read API on http://{host}:{port}/{API_VERSION}/  '
          f'release={release}  entities={len(Handler.service.graph)}')
    httpd.serve_forever()
