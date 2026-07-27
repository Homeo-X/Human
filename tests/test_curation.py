"""The curation plane — the gate everything canonical passes through.

These tests are adversarial on purpose. The plane's value is entirely in what
it refuses, so most of what follows attempts a bypass and asserts that it fails.
A test suite that only exercised the happy path would pass against a service
with the gate deleted.
"""
import contextlib
import io
import os
import shutil
import tempfile
import unittest

from homeo import cli
from homeo.curation import (Approval, Competence, CurationError,
                            CurationService, Proposal, digest)
from homeo.graph import Graph
from homeo.promotion import PromotionRequest, PromotionService
from homeo.evidence import EvidenceService
from homeo.scale import ScaleService
from homeo.substrate import load

CARDIO = 'human:reviewer-cardio-01'
NEURO = 'human:reviewer-neuro-01'
JUNIOR = 'human:reviewer-junior-01'
BOT = 'agent:ontology'


def _service(ceiling=25):
    return CurationService([
        Competence(CARDIO, frozenset({'cardiovascular'}), max_level=8,
                   note='cardiac physiology'),
        Competence(NEURO, frozenset({'nervous'}), max_level=8),
        Competence(JUNIOR, frozenset({'cardiovascular'}), max_level=3,
                   note='gross anatomy only'),
        Competence(BOT, frozenset({'cardiovascular'}), max_level=10),
    ], queue_ceiling=ceiling)


def _proposal(pid='PROP:1', kind='claim', subsystem='cardiovascular', level=4,
              payload=None, sources=('PMID:1234567',), steps=('read', 'draft')):
    return Proposal(
        id=pid, kind=kind, subsystem=subsystem, level=level,
        payload=payload if payload is not None else {'id': 'CLM:x'},
        proposed_by='AGT-2',
        derivation={'sources': list(sources), 'steps': list(steps),
                    'rationale': 'test fixture'})


class TestApprovalIsMandatory(unittest.TestCase):
    """[FR-CUR-001] — no path reaches canonical content without an Approval."""

    def setUp(self):
        self.svc = _service()

    def test_accepted_payloads_all_carry_an_approval(self):
        queued = self.svc.submit(_proposal())
        self.assertEqual([], self.svc.accepted_payloads())
        self.svc.accept(queued.id, CARDIO, 'sources check out')
        admitted = self.svc.accepted_payloads()
        self.assertEqual(1, len(admitted))
        self.assertTrue(admitted[0]['approval']['id'].startswith('APPR:'))

    def test_no_public_method_admits_without_review(self):
        """The guarantee is an absence: there is no override to call.

        Asserted structurally rather than by wording, so adding a bypass named
        anything plausible fails this test.
        """
        self.svc.submit(_proposal())
        surface = [n for n in dir(self.svc) if not n.startswith('_')]
        for name in surface:
            self.assertNotIn(
                name, ('force_accept', 'admit', 'override', 'bypass',
                       'admin_accept', 'accept_unreviewed'),
                f'{name} would be a path around the review gate')
        # ... and the only producer of admitted content filters on approval.
        for task in self.svc.tasks.values():
            task.state = 'accepted'          # state forged, approval absent
        self.assertEqual([], self.svc.accepted_payloads())

    def test_approval_digests_what_was_approved(self):
        task = self.svc.submit(_proposal(payload={'id': 'CLM:y', 'v': 1}))
        appr = self.svc.accept(task.id, CARDIO, 'fine')
        self.assertEqual(digest({'id': 'CLM:y', 'v': 1}), appr.payload_digest)
        self.assertNotEqual(appr.payload_digest,
                            digest({'id': 'CLM:y', 'v': 2}))

    def test_a_decision_is_recorded_once(self):
        task = self.svc.submit(_proposal())
        self.svc.accept(task.id, CARDIO, 'fine')
        with self.assertRaises(CurationError) as ctx:
            self.svc.accept(task.id, CARDIO, 'fine again')
        self.assertIn('already accepted', str(ctx.exception))

    def test_acceptance_requires_a_reason(self):
        task = self.svc.submit(_proposal())
        with self.assertRaises(CurationError):
            self.svc.accept(task.id, CARDIO, '   ')


class TestProposalMustBeReviewable(unittest.TestCase):
    """[FR-CUR-002] — a proposal carries the derivation needed to judge it."""

    def setUp(self):
        self.svc = _service()

    def test_claim_without_sources_is_refused(self):
        with self.assertRaises(CurationError) as ctx:
            self.svc.submit(_proposal(sources=()))
        self.assertIn('cannot judge a claim', str(ctx.exception))

    def test_proposal_without_derivation_steps_is_refused(self):
        with self.assertRaises(CurationError) as ctx:
            self.svc.submit(_proposal(steps=()))
        self.assertIn('derivation steps', str(ctx.exception))

    def test_unknown_change_kind_is_refused(self):
        with self.assertRaises(CurationError):
            self.svc.submit(_proposal(kind='whatever'))

    def test_queued_task_exposes_its_derivation(self):
        task = self.svc.submit(_proposal())
        self.assertEqual(['PMID:1234567'],
                         task.as_dict()['derivation']['sources'])
        self.assertEqual('AGT-2', task.as_dict()['proposed_by'])


class TestRejectionPersists(unittest.TestCase):
    """[FR-CUR-003] — a rejection attaches to the proposal, not the task."""

    def setUp(self):
        self.svc = _service()

    def test_rejection_requires_a_reason(self):
        task = self.svc.submit(_proposal())
        with self.assertRaises(CurationError) as ctx:
            self.svc.reject(task.id, CARDIO, '')
        self.assertIn('returns unchanged', str(ctx.exception))

    def test_resubmitting_rejected_content_is_blocked_with_the_reason(self):
        payload = {'id': 'CLM:contested', 'value': 42}
        first = self.svc.submit(_proposal(payload=payload))
        self.svc.reject(first.id, CARDIO, 'source is a preprint, not peer review')
        second = self.svc.submit(_proposal(pid='PROP:2', payload=payload))
        self.assertEqual('blocked', second.state)
        self.assertIn('preprint', second.blocked_reason)

    def test_a_blocked_task_cannot_be_accepted(self):
        payload = {'id': 'CLM:contested'}
        first = self.svc.submit(_proposal(payload=payload))
        self.svc.reject(first.id, CARDIO, 'no')
        second = self.svc.submit(_proposal(pid='PROP:2', payload=payload))
        with self.assertRaises(CurationError) as ctx:
            self.svc.accept(second.id, CARDIO, 'looks fine to me')
        self.assertIn('blocked', str(ctx.exception))

    def test_a_materially_different_proposal_is_not_blocked(self):
        first = self.svc.submit(_proposal(payload={'id': 'CLM:a', 'v': 1}))
        self.svc.reject(first.id, CARDIO, 'wrong value')
        second = self.svc.submit(
            _proposal(pid='PROP:2', payload={'id': 'CLM:a', 'v': 2}))
        self.assertEqual('queued', second.state)


class TestCompetenceScope(unittest.TestCase):
    """[FR-CUR-004] — competence is scoped by subsystem and level."""

    def setUp(self):
        self.svc = _service()

    def test_out_of_subsystem_acceptance_is_refused(self):
        task = self.svc.submit(_proposal(subsystem='cardiovascular'))
        with self.assertRaises(CurationError) as ctx:
            self.svc.accept(task.id, NEURO, 'seems right')
        self.assertIn('no declared competence in cardiovascular',
                      str(ctx.exception))

    def test_above_level_acceptance_is_refused(self):
        task = self.svc.submit(_proposal(level=7))
        with self.assertRaises(CurationError) as ctx:
            self.svc.accept(task.id, JUNIOR, 'looks plausible')
        self.assertIn('competent to L3', str(ctx.exception))

    def test_within_level_acceptance_succeeds(self):
        task = self.svc.submit(_proposal(level=3))
        self.assertIsInstance(self.svc.accept(task.id, JUNIOR, 'gross anatomy'),
                              Approval)

    def test_undeclared_reviewer_reviews_nothing(self):
        """Deny-by-default: an unknown reviewer is not an unlimited one."""
        task = self.svc.submit(_proposal())
        ok, why = self.svc.can_review('human:stranger', task.id)
        self.assertFalse(ok)
        self.assertIn('deny-by-default', why)

    def test_a_reviewer_with_no_declared_subsystems_reviews_nothing(self):
        svc = CurationService([Competence('human:empty', max_level=10)])
        task = svc.submit(_proposal())
        ok, _ = svc.can_review('human:empty', task.id)
        self.assertFalse(ok)

    def test_a_non_human_cannot_be_a_reviewer_however_declared(self):
        """BOT is declared with wide scope and still cannot accept."""
        task = self.svc.submit(_proposal())
        ok, why = self.svc.can_review(BOT, task.id)
        self.assertFalse(ok)
        self.assertIn('not a human reviewer', why)
        with self.assertRaises(CurationError):
            self.svc.accept(task.id, BOT, 'self-approved')

    def test_claim_lock_stops_a_second_reviewer(self):
        task = self.svc.submit(_proposal())
        self.svc.claim_task(task.id, CARDIO)
        with self.assertRaises(CurationError):
            self.svc.claim_task(task.id, NEURO)


class TestAdjudication(unittest.TestCase):
    """[FR-CUR-005] — conflicts need two reviewers and lose no position."""

    def setUp(self):
        self.svc = _service()
        self.svc.competences[NEURO] = Competence(
            NEURO, frozenset({'nervous', 'cardiovascular'}), max_level=8)

    def test_one_reviewer_cannot_adjudicate(self):
        task = self.svc.submit(_proposal())
        with self.assertRaises(CurationError) as ctx:
            self.svc.adjudicate(task.id, [CARDIO, CARDIO], 'I decide')
        self.assertIn('two distinct reviewers', str(ctx.exception))

    def test_two_reviewers_adjudicate_and_both_are_named(self):
        task = self.svc.submit(_proposal())
        appr = self.svc.adjudicate(
            task.id, [CARDIO, NEURO],
            'both measurements stand; the disagreement is population, not method')
        self.assertIn(CARDIO, appr.reviewer)
        self.assertIn(NEURO, appr.reviewer)
        self.assertEqual('adjudication', appr.kind)

    def test_original_positions_survive_adjudication(self):
        task = self.svc.submit(_proposal())
        self.svc.escalate(task.id, CARDIO, 'conflicts with the Sarnoff value')
        self.svc.adjudicate(task.id, [CARDIO, NEURO], 'population difference')
        decisions = [r.decision for r in self.svc.tasks[task.id].reviews]
        self.assertIn('escalated', decisions,
                      'the escalation that prompted adjudication was erased')

    def test_adjudication_requires_a_recorded_resolution(self):
        task = self.svc.submit(_proposal())
        with self.assertRaises(CurationError):
            self.svc.adjudicate(task.id, [CARDIO, NEURO], '  ')

    def test_an_out_of_scope_adjudicator_is_refused(self):
        task = self.svc.submit(_proposal())
        self.svc.competences[NEURO] = Competence(NEURO, frozenset({'nervous'}),
                                                 max_level=8)
        with self.assertRaises(CurationError):
            self.svc.adjudicate(task.id, [CARDIO, NEURO], 'agreed')


class TestPromotionIsReviewed(unittest.TestCase):
    """[FR-CUR-006] — status promotion is a reviewed change, reviewer recorded."""

    def setUp(self):
        graph = Graph(load('ontology'))
        self.promotion = PromotionService(
            graph, EvidenceService(graph, ScaleService(graph)))

    def test_promotion_records_the_reviewer_that_authorized_it(self):
        decision = self.promotion.evaluate(PromotionRequest(
            'HOX:function:cardiaccycle', 'structured', CARDIO,
            'typed 6 relations, assigned levels, reviewed sources'))
        self.assertEqual(CARDIO, decision.reviewer)

    def test_an_unreviewed_promotion_is_refused(self):
        decision = self.promotion.evaluate(PromotionRequest(
            'HOX:function:cardiaccycle', 'structured', '', 'work done'))
        self.assertFalse(decision.allowed)

    def test_promotion_travels_the_curation_plane_like_any_other_change(self):
        svc = _service()
        task = svc.submit(Proposal(
            id='PROP:promo', kind='promotion', subsystem='cardiovascular',
            level=4, payload={'entity': 'HOX:function:cardiaccycle',
                              'to': 'structured'},
            proposed_by='AGT-1',
            derivation={'steps': ['evaluated'], 'sources': []}))
        self.assertEqual('promotion', task.proposal.kind)
        appr = svc.accept(task.id, CARDIO, 'the typing work is real')
        self.assertEqual('promotion', appr.kind)
        self.assertEqual(CARDIO, appr.reviewer)


class TestThrottle(unittest.TestCase):
    """[FR-CUR-009] — generation is bounded by review capacity, not by ambition."""

    def test_queue_beyond_ceiling_pauses_generation(self):
        svc = _service(ceiling=3)
        for i in range(3):
            svc.submit(_proposal(pid=f'PROP:{i}', payload={'id': f'CLM:{i}'}))
        self.assertTrue(svc.is_throttled('cardiovascular'))
        with self.assertRaises(CurationError) as ctx:
            svc.submit(_proposal(pid='PROP:x', payload={'id': 'CLM:x'}))
        self.assertIn('Review capacity is the planning unit',
                      str(ctx.exception))

    def test_throttle_is_per_subsystem(self):
        svc = _service(ceiling=2)
        svc.competences[NEURO] = Competence(NEURO, frozenset({'nervous'}), 8)
        for i in range(2):
            svc.submit(_proposal(pid=f'PROP:{i}', payload={'id': f'CLM:{i}'}))
        self.assertTrue(svc.is_throttled('cardiovascular'))
        self.assertFalse(svc.is_throttled('nervous'))
        svc.submit(_proposal(pid='PROP:n', subsystem='nervous',
                             payload={'id': 'CLM:n'}))

    def test_capacity_is_restored_by_deciding_not_by_waiting(self):
        svc = _service(ceiling=2)
        tasks = [svc.submit(_proposal(pid=f'PROP:{i}',
                                      payload={'id': f'CLM:{i}'}))
                 for i in range(2)]
        self.assertTrue(svc.is_throttled('cardiovascular'))
        svc.accept(tasks[0].id, CARDIO, 'reviewed')
        self.assertFalse(svc.is_throttled('cardiovascular'))


class TestBatchReview(unittest.TestCase):
    """[FR-CUR-010] — batching a decision, not collapsing the record."""

    def test_each_item_keeps_its_own_approval(self):
        svc = _service()
        tasks = [svc.submit(_proposal(pid=f'PROP:{i}',
                                      payload={'id': f'CLM:{i}'}))
                 for i in range(5)]
        approvals = svc.accept_batch([t.id for t in tasks], CARDIO,
                                     'all five follow the same upstream split')
        self.assertEqual(5, len(approvals))
        self.assertEqual(5, len({a.id for a in approvals}))
        self.assertEqual(5, len({a.payload_digest for a in approvals}))

    def test_batch_records_that_it_was_a_batch(self):
        svc = _service()
        task = svc.submit(_proposal())
        svc.accept_batch([task.id], CARDIO, 'same split')
        self.assertIn('[batch of 1]', svc.tasks[task.id].reviews[0].reason)

    def test_batch_stops_at_the_first_out_of_scope_item(self):
        """A batch is not a way to smuggle one item past competence scope."""
        svc = _service()
        good = svc.submit(_proposal(pid='PROP:1', payload={'id': 'CLM:1'}))
        bad = svc.submit(_proposal(pid='PROP:2', level=7,
                                   payload={'id': 'CLM:2'}))
        with self.assertRaises(CurationError):
            svc.accept_batch([good.id, bad.id], JUNIOR, 'same split')
        self.assertIsNone(svc.tasks[bad.id].approval)


class TestOperatorView(unittest.TestCase):
    """[FR-CUR-008] — the bottleneck is published, not inferred."""

    def setUp(self):
        self.svc = _service(ceiling=2)
        self.a = self.svc.submit(_proposal(pid='P1', payload={'id': 'C1'}))
        self.b = self.svc.submit(_proposal(pid='P2', payload={'id': 'C2'}))
        self.svc.reject(self.a.id, CARDIO, 'preprint only')

    def test_view_reports_depth_ceiling_and_throttled_subsystems(self):
        view = self.svc.operator_view()
        self.assertEqual(2, view['queue_ceiling'])
        self.assertEqual(1, view['queue_depth'])
        self.assertEqual(1, view['decided'])
        self.assertEqual([], view['throttled_subsystems'])

    def test_view_reports_blocked_items_with_reasons(self):
        blocked = self.svc.submit(_proposal(pid='P3', payload={'id': 'C1'}))
        view = self.svc.operator_view()
        rows = [r for r in view['blocked'] if r['task'] == blocked.id]
        self.assertEqual(1, len(rows))
        self.assertIn('preprint', rows[0]['reason'])

    def test_view_publishes_reviewer_capacity(self):
        cap = self.svc.operator_view()['reviewer_capacity']
        self.assertEqual(3, cap[JUNIOR]['max_level'])
        self.assertEqual(['cardiovascular'], cap[JUNIOR]['subsystems'])


class TestQueuePersistence(unittest.TestCase):
    """[FR-CUR-003] [FR-CUR-008] — the queue outlives the process.

    Reviewers are people with other work; a queue held only in an agent's
    memory is a queue nobody reviews. These tests care most about what must
    survive a restart: the approvals, and the rejections.
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, 'queue.json')

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _saved(self):
        svc = _service()
        accepted = svc.submit(_proposal(pid='P1', payload={'id': 'CLM:1'}))
        rejected = svc.submit(_proposal(pid='P2', payload={'id': 'CLM:2'}))
        pending = svc.submit(_proposal(pid='P3', payload={'id': 'CLM:3'}))
        svc.accept(accepted.id, CARDIO, 'sources check out')
        svc.reject(rejected.id, CARDIO, 'preprint, not peer reviewed')
        svc.save(self.path)
        return svc, accepted, rejected, pending

    def test_approvals_survive_a_restart_with_their_digests(self):
        svc, accepted, _, _ = self._saved()
        back = CurationService.load(self.path)
        self.assertEqual(svc.tasks[accepted.id].approval.payload_digest,
                         back.tasks[accepted.id].approval.payload_digest)
        self.assertEqual(1, len(back.approvals()))
        self.assertEqual(1, len(back.accepted_payloads()))

    def test_rejections_survive_and_still_block_resubmission(self):
        self._saved()
        back = CurationService.load(self.path)
        again = back.submit(_proposal(pid='P9', payload={'id': 'CLM:2'}))
        self.assertEqual('blocked', again.state)
        self.assertIn('preprint', again.blocked_reason)

    def test_competence_scoping_survives(self):
        _, _, _, pending = self._saved()
        back = CurationService.load(self.path)
        self.assertFalse(back.can_review(NEURO, pending.id)[0])
        self.assertTrue(back.can_review(CARDIO, pending.id)[0])

    def test_reloaded_ids_do_not_collide_with_existing_ones(self):
        self._saved()
        back = CurationService.load(self.path)
        fresh = back.submit(_proposal(pid='P4', payload={'id': 'CLM:4'}))
        self.assertNotIn(fresh.id, {'TASK:00001', 'TASK:00002', 'TASK:00003'})
        self.assertEqual(4, len(back.tasks))

    def test_pending_excludes_decided_tasks(self):
        _, accepted, rejected, pending = self._saved()
        ids = {t.id for t in CurationService.load(self.path).pending()}
        self.assertEqual({pending.id}, ids)


class TestReviewCommands(unittest.TestCase):
    """[FR-CUR-007] — write access is a separate plane, reached deliberately."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, 'queue.json')
        svc = _service()
        self.task = svc.submit(_proposal(pid='P1', payload={'id': 'CLM:1'}))
        svc.save(self.path)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _run(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_reading_the_model_needs_no_reviewer_identity(self):
        code, out, _ = self._run(['entity', 'heart'])
        self.assertEqual(0, code)
        self.assertIn('preferred_term', out)

    def test_an_out_of_scope_review_is_refused_at_the_command_line(self):
        code, _, err = self._run(
            ['review', self.task.id, 'accept', '--queue', self.path,
             '--reviewer', NEURO, '--reason', 'looks fine'])
        self.assertEqual(1, code)
        self.assertIn('out of competence scope', err)

    def test_an_in_scope_review_writes_an_approval_that_persists(self):
        code, out, _ = self._run(
            ['review', self.task.id, 'accept', '--queue', self.path,
             '--reviewer', CARDIO, '--reason', 'sources check out'])
        self.assertEqual(0, code)
        self.assertIn('payload_digest', out)
        self.assertIsNotNone(
            CurationService.load(self.path).tasks[self.task.id].approval)

    def test_a_refused_review_leaves_the_queue_unchanged(self):
        before = self._queue_bytes()
        self._run(['review', self.task.id, 'accept', '--queue', self.path,
                   '--reviewer', NEURO, '--reason', 'looks fine'])
        self.assertEqual(before, self._queue_bytes())

    def _queue_bytes(self) -> str:
        with open(self.path, encoding='utf-8') as fh:
            return fh.read()

    def test_the_queue_command_marks_what_is_outside_a_reviewers_scope(self):
        code, out, _ = self._run(['queue', '--queue', self.path,
                                  '--reviewer', NEURO])
        self.assertEqual(0, code)
        self.assertIn('out_of_scope', out)
        self.assertNotIn('derivation', out,
                         'a reviewer outside scope was shown the full task')

    def test_a_missing_queue_is_reported_not_invented(self):
        code, _, err = self._run(
            ['operator', '--queue', os.path.join(self.dir, 'absent.json')])
        self.assertEqual(1, code)
        self.assertIn('nothing to review', err)


if __name__ == '__main__':
    unittest.main()
