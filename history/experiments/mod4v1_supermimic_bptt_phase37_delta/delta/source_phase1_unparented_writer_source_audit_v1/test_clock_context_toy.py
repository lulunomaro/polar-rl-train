"""Small stdlib order toy, NOT an implementation/test of the real C2 tap.
No original task module is imported. Models only the proposed metadata split.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import time
import unittest


class OrderToy:
    def __init__(self):
        self.counter = 0
        self.next_seq = 0
        self.active = []
        self.events = []
        self.original_calls = []

    def observe(self, kind, original, *, group=None, tick=None, joints=None):
        seq = self.next_seq
        self.next_seq += 1  # Reserve on entry, not when the callback completes.
        current = self.active[-1] if self.active else None
        e = dict(seq=seq, kind=kind, observed_sim_counter=self.counter)
        if kind in ('queue_submit', 'queue_apply'):
            e.update(group=group, queue_argument_tick=tick)
        elif kind == 'term_apply':
            e.update(group=group, physical_apply_tick=self.counter - 1)
        elif kind == 'target_write':
            e.update(observed_joint_ids=joints,
                     parent_term_apply_seq=None if current is None else current['seq'],
                     group='UNKNOWN' if current is None else current['group'],
                     physical_apply_tick=None if current is None else current['physical_apply_tick'],
                     domain='other_writer' if current is None else 'term_child_writer',
                     historical_C1_tick=self.counter - 1)
        if kind == 'term_apply':
            self.active.append(e)
        try:
            self.original_calls.append(kind)
            result = original()
        except BaseException as exc:
            e.update(outcome='RAISED', exception_identity=id(exc))
            self.events.append(e)
            raise
        else:
            e['outcome'] = 'RETURNED'
            self.events.append(e)
            return result
        finally:
            if kind == 'term_apply':
                self.active.pop()


def require_queue_tick(x):
    if type(x) is not int or x < 0:
        raise ValueError('typed integer/range')
    return x


class ClockContextToyTests(unittest.TestCase):
    def test_seq_zero_nonterm_write_retains_counter_zero(self):
        t = OrderToy()
        result = object()
        self.assertIs(t.observe('target_write', lambda: result, joints=(91, 92)), result)
        e = t.events[0]
        self.assertEqual((e['seq'], e['observed_sim_counter'], e['historical_C1_tick']), (0, 0, -1))
        self.assertEqual((e['group'], e['domain']), ('UNKNOWN', 'other_writer'))
        self.assertIsNone(e['parent_term_apply_seq'])
        self.assertIsNone(e['physical_apply_tick'])
        self.assertEqual(t.original_calls, ['target_write'])

    def test_eight_real_apply_arguments_stay_zero_through_seven(self):
        t = OrderToy()
        t.observe('target_write', lambda: None, joints=(91, 92))
        t.observe('queue_submit', lambda: None, group='legs', tick=t.counter)
        for _ in range(8):
            t.counter += 1  # Models the inspected unbatched SDK source order.
            def apply():
                t.observe('queue_apply', lambda: None, group='legs', tick=t.counter - 1)
                t.observe('target_write', lambda: None, joints=(1, 2, 3, 4))
            t.observe('term_apply', apply, group='legs')
        q = [e for e in t.events if e['kind'] == 'queue_apply']
        w = [e for e in t.events if e.get('domain') == 'term_child_writer']
        self.assertEqual([require_queue_tick(e['queue_argument_tick']) for e in q], list(range(8)))
        self.assertEqual([e['physical_apply_tick'] for e in w], list(range(8)))
        by_seq = {e['seq']: e for e in t.events}
        for a, child in zip(q, w):
            parent = by_seq[child['parent_term_apply_seq']]
            self.assertLess(parent['seq'], a['seq'])
            self.assertLess(a['seq'], child['seq'])
            self.assertEqual(parent['group'], a['group'])

    def test_later_unparented_write_is_not_previous_physics_tick(self):
        t = OrderToy()
        t.counter = 8
        t.observe('target_write', lambda: None)
        self.assertEqual(t.events[0]['observed_sim_counter'], 8)
        self.assertEqual(t.events[0]['historical_C1_tick'], 7)
        self.assertIsNone(t.events[0]['physical_apply_tick'])
        self.assertEqual(t.events[0]['domain'], 'other_writer')

    def test_same_position_setter_alone_does_not_identify_legs(self):
        t = OrderToy()
        for ids in ((91, 92), (1, 2, 3, 4), (17,)):
            t.observe('target_write', lambda: None, joints=ids)
        self.assertTrue(all(e['group'] == 'UNKNOWN' for e in t.events))
        self.assertEqual(len({e['observed_joint_ids'] for e in t.events}), 3)
        self.assertEqual(t.original_calls, ['target_write'] * 3)

    def test_entry_sequence_differs_from_completion_order(self):
        t = OrderToy()
        t.counter = 1
        t.observe('term_apply', lambda: t.observe('target_write', lambda: None), group='wheels')
        self.assertEqual([e['seq'] for e in t.events], [1, 0])
        self.assertEqual([e['seq'] for e in sorted(t.events, key=lambda e: e['seq'])], [0, 1])
        self.assertEqual(t.events[0]['parent_term_apply_seq'], 0)

    def test_once_identity_exception_and_context_cleanup(self):
        t = OrderToy()
        t.counter = 1
        marker = object()
        self.assertIs(t.observe('term_apply', lambda: marker, group='legs'), marker)
        error = RuntimeError('toy original')
        def fail():
            raise error
        with self.assertRaises(RuntimeError) as caught:
            t.observe('term_apply', fail, group='legs')
        self.assertIs(caught.exception, error)
        self.assertEqual(t.original_calls, ['term_apply', 'term_apply'])
        self.assertEqual(t.active, [])
        t.observe('target_write', lambda: None)
        self.assertIsNone(t.events[-1]['parent_term_apply_seq'])

    def test_actual_negative_queue_tick_stays_invalid(self):
        for x in (-1, True, 0.0, None):
            with self.subTest(x=x):
                with self.assertRaisesRegex(ValueError, 'typed integer/range'):
                    require_queue_tick(x)
        self.assertEqual(require_queue_tick(0), 0)
        self.assertEqual(require_queue_tick(7), 7)


def main():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ClockContextToyTests)
    started = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    record = dict(kind='OWN_STDLIB_CLOCK_CONTEXT_TOY_TEST_RECEIPT_V1',
                  source_only=True, native_enabled=False, exact=False,
                  tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                  passed=result.wasSuccessful(), elapsed_seconds=time.perf_counter() - started,
                  python=sys.version, original_task_code_imported_or_executed=False,
                  real_C1_C2_tap_tested=False,
                  meaning='Own order toy only. No SDK dispatch, actor, queue numerics or native evidence.',
                  source=dict(path=str(Path(__file__).resolve()),
                              sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    with (Path(__file__).parent/'STDLIB_TOY_TEST_RECEIPT.json').open('x', encoding='utf-8') as out:
        json.dump(record, out, indent=2)
        out.write('\n')
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == '__main__':
    main()
