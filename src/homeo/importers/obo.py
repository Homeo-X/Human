"""Import terms from OBO ontologies into the substrate's own record shapes.

What an ontology can and cannot give this project is the thing to be clear
about, because assuming the wrong half is how an import quietly produces a
terminology wearing a knowledge model's clothes.

**It gives**: identifiers, preferred terms, definitions with their sources,
typed synonyms, cross-references to other authorities, and a subsumption
hierarchy. All of it openly licensed (UBERON CC-BY, CL CC-BY, ECO CC0), which
is why it is usable where Gray's and Terminologia Anatomica are not.

**It does not give**: this project's containment ladder, its levels, or its
system memberships. UBERON has the heart `part_of` *"heart plus pericardium"*,
not `part_of` thorax — of 204 `organ_slim` terms only 17 have a `part_of` edge
pointing at another organ. Placement is curation work, and this module refuses
rather than guesses at it.

Three rules do the work, and each one refuses rather than assuming:

- **the human warrant** — a UBERON class is vertebrate-general, so a term is
  admitted as human only on evidence (an `FMA:` xref, FMA being human-only, or
  membership of the `human_reference_atlas` subset). Otherwise the claim names
  the vertebrate class and carries an INV-12 transfer justification;
- **the grouping filter** — terms tagged `grouping_class`, `non_informative` or
  `upper_level` are structural scaffolding in the source ontology, not anatomy
  anyone navigates to;
- **the level rule** — `entity_class` and level come from a stated rule table,
  and a term no rule covers is refused and reported, never placed on a guess.

Definitions become **terminological** claims on the TRM register (D-021), and
every edge mints its own claim rather than borrowing an endpoint's — edges do
not inherit their endpoints' evidence (FR-REL-008).
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

# Identifier prefixes that resolve to something a reader can retrieve. The
# distinction is the whole of the TRM-1/TRM-2 boundary: UBERON's heart cites
# `Wikipedia:Heart` and an ORCID, and CL's cell cites `CARO:mah` — a curator's
# initials. None of those is a retrievable source, and grading them as one would
# make TRM-1 mean nothing.
RESOLVABLE = ('PMID:', 'PMCID:', 'DOI:', 'ISBN:', 'FMA:', 'GO:', 'CHEBI:',
              'http://dx.doi.org', 'https://doi.org')

# Subsets marking terms that exist to organize the ontology rather than to name
# a structure. Skipped: "heart plus pericardium" is a grouping device, and a
# user navigating the body should never arrive at one.
SCAFFOLDING = ('grouping_class', 'non_informative', 'upper_level')

# FMA is a human-only anatomy; an FMA cross-reference is therefore positive
# evidence that a vertebrate-general class applies to humans.
HUMAN_WARRANTS = ('FMA:',)
HUMAN_SUBSETS = ('human_reference_atlas',)

VERTEBRATE = 'Vertebrata'
TRANSFER_NOTE = (
    'Imported from a vertebrate-general ontology class with no human-specific '
    'warrant (no FMA cross-reference, not in the human reference atlas). The '
    'term is recorded at its own taxonomic scope; applying it to Homo sapiens '
    'is a curation judgement nobody has made yet (INV-12).')

OBO_PART_OF = 'BFO_0000050'
OBO_IS_A = 'is_a'

# The authorities whose cross-references may be recorded (INV-10). Read from the
# same file `tools/biocheck.py` checks against rather than restated here: a
# registry written down twice is precisely the divergence INV-16 and INV-19 were
# built to catch, and a third copy would earn a third guard.
AUTHORITY_REGISTRY = os.path.join('ontology', 'vocabularies', 'authorities.json')


def registered_authorities(path: str = AUTHORITY_REGISTRY) -> frozenset[str]:
    """Authority prefixes admissible on an xref, or empty when unreadable.

    Empty means *record no cross-references* — the conservative direction. An
    unreadable registry must not become a licence to admit anything.
    """
    try:
        with open(path, encoding='utf-8') as fh:
            return frozenset(json.load(fh))
    except (OSError, ValueError):
        return frozenset()


REGISTERED_AUTHORITIES = registered_authorities()


@dataclass(frozen=True)
class ImportRule:
    """How a term becomes an entity. Stated, not inferred.

    The rule table is the reviewable artifact: one reviewer can judge "terms in
    UBERON's `organ_slim` are organs at L3" once, rather than judging two
    hundred organs one at a time. That is the shape the review bottleneck
    (RSK-02) has to be attacked in.
    """
    authority: str
    subset: str | None
    entity_class: str
    level: int
    representation_mode: str
    rationale: str


RULES = (
    ImportRule('UBERON', 'organ_slim', 'Organ', 3, 'enumerated',
               "UBERON's own organ subset; organs are L3 and enumerated "
               'because they are countable, named, located structures.'),
    ImportRule('CL', None, 'CellType', 7, 'typed',
               'Every Cell Ontology term names a cell type. L7 is typed rather '
               'than enumerated: a cell type is a kind, not a located object.'),
)


@dataclass
class Term:
    """One ontology term, normalized across OBO-JSON and OBO stanza format."""
    id: str
    label: str = ''
    definition: str = ''
    definition_sources: tuple[str, ...] = ()
    synonyms: tuple[tuple[str, str], ...] = ()      # (scope, term)
    xrefs: tuple[str, ...] = ()
    subsets: frozenset[str] = frozenset()
    parents: tuple[tuple[str, str], ...] = ()       # (predicate, target id)
    obsolete: bool = False

    @property
    def authority(self) -> str:
        return self.id.split(':', 1)[0]

    @property
    def is_scaffolding(self) -> bool:
        return any(s in self.subsets for s in SCAFFOLDING)

    @property
    def human_warrant(self) -> str | None:
        """Why this vertebrate-general term may be recorded as human — or None."""
        for xref in self.xrefs:
            if xref.startswith(HUMAN_WARRANTS):
                return f'cross-referenced to {xref} (FMA is human-only)'
        for subset in HUMAN_SUBSETS:
            if subset in self.subsets:
                return f'member of the {subset} subset'
        return None

    def grade(self) -> str:
        """The TRM grade this term's definition earns.

        Only called when a definition exists. A term the ontology names but does
        not define produces no definitional claim at all — writing
        "X (no definition given)" would be fabricating the very content the
        claim is supposed to record.
        """
        if any(s.startswith(RESOLVABLE) for s in self.definition_sources):
            return 'TRM-1'
        if self.definition_sources:
            return 'TRM-2'
        return 'TRM-3'


@dataclass
class Refusal:
    term: str
    label: str
    reason: str

    def as_dict(self) -> dict:
        return {'term': self.term, 'label': self.label, 'reason': self.reason}


@dataclass
class ImportResult:
    """What an import produced, and — equally — what it would not produce."""
    entities: list[dict] = field(default_factory=list)
    claims: list[dict] = field(default_factory=list)
    relationships: list[dict] = field(default_factory=list)
    refusals: list[Refusal] = field(default_factory=list)
    # Terms the ontology names but does not define. Imported as entities,
    # carrying no definitional claim, and counted rather than papered over.
    undefined: list[str] = field(default_factory=list)

    def summary(self) -> dict:
        by_reason: dict = {}
        for r in self.refusals:
            key = r.reason.split(':')[0]
            by_reason[key] = by_reason.get(key, 0) + 1
        return {
            'entities': len(self.entities), 'claims': len(self.claims),
            'relationships': len(self.relationships),
            'refused': len(self.refusals), 'refused_by_reason': by_reason,
            'imported_without_a_definition': len(self.undefined),
            'note': ('Refusals are the honest half of an import. A term placed '
                     'on a guessed level is worse than a term left out, because '
                     'the guess is invisible once it is in the graph.'),
        }


# ---- parsing ---------------------------------------------------------------

def parse_obo_json(path: str) -> dict[str, Term]:
    """Parse OBO-JSON (UBERON's `basic.json`)."""
    with open(path, encoding='utf-8') as fh:
        graph = json.load(fh)['graphs'][0]
    terms: dict[str, Term] = {}
    for node in graph.get('nodes', []):
        if node.get('type') != 'CLASS':
            continue
        curie = _curie(node['id'])
        if curie is None:
            continue
        meta = node.get('meta', {})
        definition = meta.get('definition', {})
        terms[curie] = Term(
            id=curie,
            label=node.get('lbl') or '',
            definition=definition.get('val') or '',
            definition_sources=tuple(definition.get('xrefs') or ()),
            synonyms=tuple((s.get('pred', ''), s.get('val', ''))
                           for s in meta.get('synonyms', [])),
            xrefs=tuple(x.get('val', '') for x in meta.get('xrefs', [])),
            subsets=frozenset(s.rsplit('#', 1)[-1]
                              for s in meta.get('subsets', [])),
            obsolete=bool(meta.get('deprecated')))
    for edge in graph.get('edges', []):
        sub, obj = _curie(edge['sub']), _curie(edge['obj'])
        pred = edge['pred'].rsplit('/', 1)[-1]
        if sub in terms and obj and pred in (OBO_IS_A, OBO_PART_OF):
            terms[sub].parents += ((pred, obj),)
    return terms


def parse_obo(path: str) -> dict[str, Term]:
    """Parse OBO stanza format (CL, ECO)."""
    terms: dict[str, Term] = {}
    current: dict | None = None

    def flush():
        if current and current.get('id'):
            terms[current['id']] = Term(
                id=current['id'], label=current.get('name', ''),
                definition=current.get('def', ''),
                definition_sources=tuple(current.get('def_sources', ())),
                synonyms=tuple(current.get('synonyms', ())),
                xrefs=tuple(current.get('xrefs', ())),
                subsets=frozenset(current.get('subsets', ())),
                parents=tuple(current.get('parents', ())),
                obsolete=current.get('obsolete', False))

    with open(path, encoding='utf-8') as fh:
        for raw in fh:
            line = raw.rstrip('\n')
            if line.startswith('['):
                flush()
                current = {'synonyms': [], 'xrefs': [], 'subsets': [],
                           'parents': [], 'def_sources': []} \
                    if line.startswith('[Term]') else None
                continue
            if current is None or ':' not in line:
                continue
            key, _, value = line.partition(':')
            value = value.strip()
            if key == 'id':
                current['id'] = value
            elif key == 'name':
                current['name'] = value
            elif key == 'def':
                text, sources = _obo_quoted(value)
                current['def'] = text
                current['def_sources'] = sources
            elif key == 'synonym':
                text, _ = _obo_quoted(value)
                scope = 'hasExactSynonym' if ' EXACT ' in value else (
                    'hasNarrowSynonym' if ' NARROW ' in value
                    else 'hasRelatedSynonym')
                current['synonyms'].append((scope, text))
            elif key == 'xref':
                current['xrefs'].append(value.split(' ', 1)[0])
            elif key == 'subset':
                current['subsets'].append(value.rsplit(':', 1)[-1])
            elif key == 'is_a':
                current['parents'].append((OBO_IS_A, value.split(' ')[0]))
            elif key == 'relationship' and value.startswith('part_of '):
                current['parents'].append(
                    (OBO_PART_OF, value.split(' ')[1]))
            elif key == 'is_obsolete':
                current['obsolete'] = value == 'true'
    flush()
    return terms


_QUOTED = re.compile(r'"(.*?)"(?:\s*\[(.*?)\])?')


def _obo_quoted(value: str) -> tuple[str, tuple[str, ...]]:
    """`"text" [SRC:1, SRC:2]` → (text, sources)."""
    m = _QUOTED.match(value)
    if not m:
        return value, ()
    sources = tuple(s.strip() for s in (m.group(2) or '').split(',') if s.strip())
    return m.group(1), sources


def _curie(iri: str) -> str | None:
    tail = iri.rsplit('/', 1)[-1]
    return tail.replace('_', ':', 1) if '_' in tail else None


# ---- importing -------------------------------------------------------------

class OboImporter:
    """Turns parsed terms into proposal payloads. Admits nothing."""

    def __init__(self, terms: dict[str, Term], *, pinned_version: str,
                 placement=None, existing=frozenset(),
                 agent: str = 'agent:anatomy', rules=RULES):
        """`placement(term) -> subsystem | None` decides where a term belongs.

        There is no default that places anything. UBERON knows what the heart
        *is*; it does not know that this project files it under
        `cardiovascular`, and inventing a subsystem here would be the importer
        asserting curation it has not done. A caller supplies the rule table and
        anything it cannot place is refused and reported.
        """
        self.terms = terms
        self.pinned_version = pinned_version
        self.placement = placement or (lambda term: None)
        # Ids already in the substrate. An importer that does not know what is
        # already there will overwrite it: the first run of this importer
        # re-imported UBERON:0000948 and silently replaced a curated heart —
        # "Heart", part_of thorax, in the cardiovascular slice — with the raw
        # ontology term, which has no containment and a lowercase label. The
        # substrate's loader takes the last record read, so the curation simply
        # disappeared.
        self.existing = frozenset(existing)
        self.agent = agent
        self.rules = rules

    def rule_for(self, term: Term) -> ImportRule | None:
        for rule in self.rules:
            if rule.authority != term.authority:
                continue
            if rule.subset is None or rule.subset in term.subsets:
                return rule
        return None

    def select(self, subset: str | None = None) -> list[Term]:
        chosen = [t for t in self.terms.values()
                  if subset is None or subset in t.subsets]
        return sorted(chosen, key=lambda t: t.id)

    def build(self, terms: list[Term]) -> ImportResult:
        result = ImportResult()
        admitted: set[str] = set()

        for term in terms:
            refusal = self._refuse(term)
            if refusal:
                result.refusals.append(refusal)
                continue
            entity, claim = self._entity(term, self.rule_for(term))
            result.entities.append(entity)
            if claim is not None:
                result.claims.append(claim)
            else:
                result.undefined.append(term.id)
            admitted.add(term.id)

        # Edges last, so both endpoints are known to be admitted. An edge to a
        # term we refused would assert structure into a hole.
        for term in terms:
            if term.id not in admitted:
                continue
            for pred, target in term.parents:
                if target not in admitted:
                    continue
                if pred == OBO_PART_OF and self._is_scaffolding(target):
                    continue
                rel, rel_claim = self._relationship(term, pred, target)
                result.relationships.append(rel)
                result.claims.append(rel_claim)
        return result

    # ---- refusals ------------------------------------------------------

    def _refuse(self, term: Term) -> Refusal | None:
        if term.id in self.existing:
            return Refusal(
                term.id, term.label,
                'already present: this term is in the substrate, and importing '
                'it again would replace whatever curation it has accumulated '
                'with the raw ontology record')
        if term.obsolete:
            return Refusal(term.id, term.label,
                           'obsolete: the source ontology has retired this term')
        if term.is_scaffolding:
            return Refusal(
                term.id, term.label,
                'scaffolding: tagged as a grouping or upper-level class, which '
                'organizes the ontology rather than naming a structure')
        if not term.label:
            return Refusal(term.id, term.label,
                           'unnamed: no preferred term to display')
        if self.rule_for(term) is None:
            return Refusal(
                term.id, term.label,
                f'unclassed: no rule assigns {term.authority} terms outside '
                f'the covered subsets a class and level, and a guessed level is '
                f'invisible once it is in the graph')
        if self.placement(term) is None:
            # The placement rule knows *why* it declined — no human warrant, a
            # system with no anchor, no mapped system at all. Reporting all
            # three as "unplaced" made the summary say the importer could not
            # file the term when in fact it had refused it for a different and
            # more interesting reason, and 67 non-human refusals disappeared
            # into that one bucket (D-027).
            stated = getattr(self.placement, 'refusals', {}).get(term.id)
            return Refusal(
                term.id, term.label,
                stated or
                'unplaced: no subsystem rule covers this term. An ontology '
                'knows what a structure is, not which system this project '
                'files it under; placing it on a guess would assert curation '
                'nobody did')
        return None

    def _is_scaffolding(self, term_id: str) -> bool:
        term = self.terms.get(term_id)
        return term is None or term.is_scaffolding

    # ---- records -------------------------------------------------------

    def _entity(self, term: Term, rule: ImportRule) -> tuple[dict, dict | None]:
        warrant = term.human_warrant
        entity = {
            'id': term.id, 'minted': False,
            'entity_class': rule.entity_class, 'level': rule.level,
            'subsystem': self.placement(term),
            'preferred_term': term.label,
            'compilation_status': 'structured',
            'representation_mode': rule.representation_mode,
            'review_state': 'provisional', 'admitted_by': self.agent,
            'provenance_source': f'{term.authority} {self.pinned_version}',
            # The self-reference, plus every cross-reference to a *registered*
            # authority (INV-10). The FMA one matters most: it is the human
            # warrant this import runs on — 67 terms were refused for lacking
            # it — and the first version recorded that warrant only as prose
            # inside the claim's `limitations`, discarding the identifier. One
            # of 107 organs ended up carrying an FMA xref, so nothing could be
            # joined to it by id, and the rule that admitted each organ was
            # unauditable except by reading sentences (D-032).
            #
            # `pinned_version` is deliberately the UBERON snapshot's, not
            # FMA's: what is pinned is *UBERON asserting this cross-reference*.
            # We never read an FMA release, and claiming one would be citing a
            # source we have not opened.
            'xrefs': ([{'authority': term.authority, 'id': term.id,
                        'pinned_version': self.pinned_version}]
                      + [{'authority': x.split(':', 1)[0], 'id': x,
                          'pinned_version': self.pinned_version,
                          'asserted_by': f'{term.authority} '
                                         f'{self.pinned_version}'}
                         for x in term.xrefs
                         if x.split(':', 1)[0] in REGISTERED_AUTHORITIES]),
            'synonyms': [{'term': text, 'source': term.authority,
                          'register': _register(scope)}
                         for scope, text in term.synonyms if text],
        }
        if not term.definition:
            # Named but undefined. The entity is real and navigable; asserting a
            # definition it does not have would be inventing one.
            return entity, None
        claim = {
            'id': f'CLM:{term.id.replace(":", "-").lower()}-definition',
            'subject': term.id, 'predicate': 'has_definition',
            'object': term.definition,
            'kind': 'terminological',
            'evidence_class': term.grade(),
            'authority': term.authority,
            'definition_source': (', '.join(term.definition_sources) or None),
            'source_type': 'curated database',
            'species': 'Homo sapiens' if warrant else VERTEBRATE,
            'population': 'not applicable',
            'date_asserted': '2026-07-27',
            'review_state': 'provisional', 'assigned_by': self.agent,
            'limitations': self._limitations(term, warrant),
        }
        if not warrant:
            claim['transfer_justification'] = TRANSFER_NOTE
        return entity, claim

    @staticmethod
    def _limitations(term: Term, warrant: str | None) -> str:
        base = ('A definition recorded from an ontology, not a finding about a '
                'body. No human reviewer has examined this record.')
        if warrant:
            return f'{base} Human applicability warranted: {warrant}.'
        return (f'{base} The source class is vertebrate-general and carries no '
                f'human-specific warrant, so it is recorded at that scope.')

    def _relationship(self, term: Term, pred: str,
                      target: str) -> tuple[dict, dict]:
        rel_type = 'is_a' if pred == OBO_IS_A else 'part_of'
        rid = f'REL:{term.id.replace(":", "-").lower()}-{rel_type}-' \
              f'{target.replace(":", "-").lower()}'
        claim_id = f'CLM:{rid[4:]}-assertion'
        rel = {
            'id': rid, 'source': term.id, 'target': target, 'type': rel_type,
            'compilation_status': 'structured',
            'review_state': 'provisional',
            # Its own claim, never an endpoint's: an edge does not inherit the
            # evidence of the things it connects (FR-REL-008).
            'provenance_claim': claim_id,
            'prose_justification': (
                f'{term.authority} asserts {term.id} {rel_type} {target}.'),
        }
        claim = {
            'id': claim_id, 'subject': term.id,
            'predicate': f'asserted_{rel_type}', 'object': target,
            'kind': 'terminological',
            # The ontology asserts the edge in its own release; that release is
            # a resolvable, pinned artifact, which is what TRM-1 requires.
            'evidence_class': 'TRM-1',
            'authority': term.authority,
            'definition_source': f'{term.authority} {self.pinned_version}',
            'source_type': 'curated database',
            'species': 'Homo sapiens' if term.human_warrant else VERTEBRATE,
            'population': 'not applicable', 'date_asserted': '2026-07-27',
            'review_state': 'provisional', 'assigned_by': self.agent,
            'limitations': (
                f'Records that {term.authority} asserts this relation, not that '
                f'it has been checked against a body. No human reviewer has '
                f'examined it.'),
        }
        if not term.human_warrant:
            claim['transfer_justification'] = TRANSFER_NOTE
        return rel, claim


def _register(scope: str) -> str:
    return {'hasExactSynonym': 'exact', 'hasNarrowSynonym': 'narrow',
            'hasRelatedSynonym': 'related'}.get(scope, 'related')


def load_snapshot(name: str, manifest_path: str = None) -> tuple[dict, str]:
    """Load a pinned snapshot, refusing to proceed if its hash has moved."""
    import hashlib
    manifest_path = manifest_path or os.path.join(
        'ontology', 'vocabularies', 'SNAPSHOTS.json')
    with open(manifest_path, encoding='utf-8') as fh:
        manifest = json.load(fh)
    record = manifest['snapshots'][name]
    path = os.path.join(manifest.get('cache', 'vendor/ontologies'),
                        record['file'])
    digest = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            digest.update(block)
    if digest.hexdigest() != record['sha256']:
        raise ValueError(
            f'{name}: the cached snapshot does not match the pinned hash. An '
            f'import against a moving source is not reproducible (G-07); '
            f're-run tools/fetch_authorities.py')
    parser = parse_obo_json if record['format'] == 'obo-json' else parse_obo
    return parser(path), (record.get('data_version') or record['fetched'])
