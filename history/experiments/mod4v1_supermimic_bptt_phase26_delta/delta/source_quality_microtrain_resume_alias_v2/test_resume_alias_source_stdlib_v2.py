"""Eight NEW stdlib/source/metadata tests only; NEVER run Torch or core loader.
The stale-fixture statement block is exercised on Python dicts through the REAL
unchanged q/base metadata functions. Only the new one-statement ingress is used
for ordinary deepcopy semantics; no cropped native/core runtime is executed.
"""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import sys
import time
import unittest
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT/'source_resume_runtime_v2'))
sys.path.insert(0, str(ROOT/'source_quality_microtrain_executor_v1'))
import resume_runtime_contracts_v3 as base
import quality_microtrain_contracts_v1 as q


def text(name):
    return (HERE/name).read_text(encoding='utf-8')


def dump(node):
    return ast.dump(node, include_attributes=False)


def loader(tree):
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ContextRewardLearner')
    return next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'load_full_checkpoint')


def counts(n):
    return dict(q.zero_counts(), policy_attempts=n, pi_optimizer_steps=n, pi_bptt_optimizer_steps=n,
                wm_steps=20, aux_reward_done_steps=20, critic_steps=3)


def metadata_fixture():
    directory = HERE/'NEVER_CREATED_METADATA_SOURCE'
    cp = directory/'production/checkpoints/at3_complete.pt'
    c = counts(3)
    final = dict(kind=base.FINAL_KIND, role='E3', role_key='SOURCE_E3', run_id='SOURCE_RUN',
                 passed_execution=True, teacher_unchanged=True, actor_view=base.RAW35_ACTOR_VIEW,
                 algorithm_family='a1_raw35_legacy_v1', algorithm_variant='A1_RAW35_FRESH',
                 actual_BPTT_policy_steps=3, counts=c, checkpoint=dict(path=str(cp), SHA='b'*64,
                 bytes=1000, counts=c, full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True))
    raw = (json.dumps(final, sort_keys=True)+'\n').encode()
    entry = dict(role='E3', role_key='NEW_E3', run_id='NEW_RUN', num_envs=512,
                 algorithm_variant='A1_RAW35_RESUME', actor_view=base.RAW35_ACTOR_VIEW,
                 algorithm_family='a1_raw35_legacy_v1', resume_bptt=dict(kind='OWN_NEW_BPTT_FULL_CHECKPOINT_V2',
                 path=str(cp), SHA='b'*64, bytes=1000, actor_view=base.RAW35_ACTOR_VIEW,
                 algorithm_family='a1_raw35_legacy_v1', allow_environment_reset=True,
                 allow_partial_update=False, producer_run_id='SOURCE_RUN', producer_role_key='SOURCE_E3'),
                 microtrain=dict(schema=q.SCHEMA, target_verified_increment=2, source_final=dict(
                 path=str(directory/'production/FINAL.json'), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())))
    return final, entry


def ingress(payload):
    node = copy.deepcopy(loader(ast.parse(text('ctx_reward_full_resume_candidate_v3.py'))).body[0])
    body = ast.Module(body=[node], type_ignores=[])
    scope = dict(payload=payload, copy=copy)
    exec(compile(ast.fix_missing_locations(body), '<NEW_SINGLE_STATEMENT_STDLIB_ONLY>', 'exec'), scope)
    return scope['payload']


class SourceAliasTests(unittest.TestCase):
    def test01_two_line_core_patch_and_complete_body_AST(self):
        old = ast.parse((ROOT/'source_resume_runtime_v2/ctx_reward_full_resume_candidate_v2.py').read_bytes())
        new = ast.parse(text('ctx_reward_full_resume_candidate_v3.py'))
        first = loader(new).body.pop(0)
        self.assertEqual(dump(first), dump(ast.parse('payload = copy.deepcopy(payload)').body[0]))
        new.body = [n for n in new.body if not (isinstance(n, ast.Import) and n.names[0].name == 'copy')]
        self.assertEqual(dump(new), dump(old))
        self.assertEqual(dump(loader(new)), dump(loader(old)))

    def test02_CPU_V3_only_core_PIN_and_report_routing(self):
        a = text('test_quality_microtrain_torch_cpu_v2.py')
        b = text('test_quality_microtrain_torch_cpu_v3.py')
        sha = hashlib.sha256((HERE/'ctx_reward_full_resume_candidate_v3.py').read_bytes()).hexdigest()
        b = b.replace(sha, '8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac')
        b = b.replace('SYNTHETIC_CPU_A1_LEGACY_MICROTRAIN_WHOLE_INGRESS_COPY_CORE_V3', 'SYNTHETIC_CPU_A1_LEGACY_MICROTRAIN_CORRECTED_FIXTURE_ORIGINAL_811_V2')
        b = b.replace('SAME_CORRECTED_FIXTURE_WITH_CORE_V3_WHOLE_INGRESS_DEEPCOPY_V3', 'LEGAL_ORDERING_METADATA4_VS_PAYLOAD3_THEN_ORIGINAL_811_ALIAS_GUARD_V2')
        b = b.replace('QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V3.json', 'QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V2.json')
        self.assertEqual(b, a)
        for filename in ('test_quality_microtrain_torch_cpu_v2.py', 'test_quality_microtrain_torch_cpu_v3.py'):
            spec = importlib.util.spec_from_file_location('_LOCAL_STDLIB_ONLY_'+filename[:-3], HERE/filename)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertNotIn('torch', sys.modules)

    def test03_old_broken_stale_fixture_hits_ordering_not_payload(self):
        c = counts(3)
        c['pi_bptt_optimizer_steps'] += 1
        with self.assertRaisesRegex(ValueError, 'producer BPTT/optimizer/attempt counter ordering differs'):
            base.validate_count_snapshot(c)

    def test04_exact_new_stale_statement_block_reaches_actual_payload_gate(self):
        final, entry = metadata_fixture()
        run = next(n for n in ast.parse(text('test_quality_microtrain_torch_cpu_v2.py')).body if isinstance(n, ast.FunctionDef) and n.name == 'run')
        rebound = next(n for n in run.body if isinstance(n, ast.FunctionDef) and n.name == 'rebound')
        start = next(i for i,n in enumerate(run.body) if isinstance(n, ast.Assign) and any(isinstance(t,ast.Name) and t.id=='stale' for t in n.targets))
        end = next(i for i,n in enumerate(run.body) if isinstance(n, ast.Assign) and any(isinstance(t,ast.Name) and t.id=='stale_bound' for t in n.targets))
        block = ast.Module(body=[copy.deepcopy(rebound)]+copy.deepcopy(run.body[start:end+1]), type_ignores=[])
        scope = dict(final=final, entry=entry, q=q, base=base, copy=copy, json=json, hashlib=hashlib)
        exec(compile(ast.fix_missing_locations(block), '<NEW_STALE_FIXTURE_METADATA_ONLY>', 'exec'), scope)
        stale, bound = scope['stale'], scope['stale_bound']
        self.assertEqual([stale['counts'][k] for k in ('policy_attempts','pi_optimizer_steps','pi_bptt_optimizer_steps')], [4,4,4])
        self.assertEqual(stale['checkpoint']['counts'], stale['counts'])
        self.assertEqual(bound['target_bptt_steps'], 6)
        self.assertTrue(q.validate_worker_microtrain_task(bound))
        payload = dict(run_id='SOURCE_RUN', role='E3', role_key='SOURCE_E3', actor_view=base.RAW35_ACTOR_VIEW,
                       algorithm_family='a1_raw35_legacy_v1', context_reward_extension=dict(counts=counts(3)))
        with self.assertRaisesRegex(ValueError, '^actual full payload counters differ from source FINAL$'):
            q.validate_microtrain_payload(payload, bound)
        payload['context_reward_extension']['counts'] = copy.deepcopy(stale['counts'])
        self.assertTrue(q.validate_microtrain_payload(payload, bound))
        self.assertFalse((HERE/'NEVER_CREATED_METADATA_SOURCE').exists())

    def test05_whole_copy_keeps_unknown_roots_and_memo_aliases_without_source_mutation(self):
        shared = [dict(step=3)]
        payload = dict(opt_wm=dict(state=shared), unknown_future_root=dict(nested=shared), pending_iteration=dict(fraction=.375))
        payload['recursive_unknown_root'] = payload
        copied = ingress(payload)
        self.assertIsNot(copied, payload)
        self.assertIs(copied['recursive_unknown_root'], copied)
        self.assertIs(copied['opt_wm']['state'], copied['unknown_future_root']['nested'])
        self.assertIsNot(copied['opt_wm']['state'], payload['opt_wm']['state'])
        copied['opt_wm']['state'][0]['step'] += 2
        copied['pending_iteration']['fraction'] = 0
        self.assertEqual(payload['opt_wm']['state'][0]['step'], 3)
        self.assertEqual(payload['pending_iteration']['fraction'], .375)

    def test06_deepcopy_failure_precedes_any_old_body_statement(self):
        class CopyFailure(Exception): pass
        class UnknownUncopyable:
            def __deepcopy__(self, memo):
                raise CopyFailure('new ingress failed before original model/optimizer/pending mutation')
        with self.assertRaises(CopyFailure):
            ingress(dict(unknown_root=UnknownUncopyable()))
        fn = loader(ast.parse(text('ctx_reward_full_resume_candidate_v3.py')))
        self.assertIsInstance(fn.body[0], ast.Assign)
        self.assertEqual(ast.unparse(fn.body[0]), 'payload = copy.deepcopy(payload)')
        self.assertIn("ext = payload.get('context_reward_extension', {})", ast.unparse(fn.body[1]))

    def test07_actual_V1_evidence_remains_failed_and_negatives_incomplete(self):
        report = json.loads((ROOT/'reports/QUALITY_MICROTRAIN_TORCH_CPU_V1.json').read_bytes())
        self.assertEqual(report['returncode'], 1)
        receipt = report['receipt']
        self.assertFalse(receipt['passed'])
        self.assertIn('producer BPTT/optimizer/attempt counter ordering differs', receipt['unhandled_error'])
        self.assertIsNone(receipt.get('negative_case_count'))
        self.assertIsNone(receipt.get('counter_3_to_5_actual_path_passed'))
        guard = receipt['positive']['whole_retained_CPU_source_guard']
        self.assertFalse(guard['values_unchanged'])
        self.assertFalse(guard['tensor_identity_versions_unchanged'])
        self.assertTrue(guard['raw_bytes_unchanged'])
        self.assertTrue(any('opt_wm' in p or 'opt_pi' in p for p in guard['changed_value_paths']))
        self.assertTrue(guard['original_loader_received_retained_root_not_working_copy'])

    def test08_old_thirteen_and_CPU_V1_seals_still_match(self):
        for directory, inventory in (('source_quality_microtrain_executor_v1','SHA256_QUALITY_MICROTRAIN_V1.txt'),
                                     ('source_quality_microtrain_torch_validation_v1','SHA256_QUALITY_MICROTRAIN_TORCH_V1.txt')):
            rows = (ROOT/directory/inventory).read_text(encoding='utf-8').splitlines()
            self.assertEqual(len(rows), 13 if directory.endswith('executor_v1') else 4)
            for row in rows:
                sha, size, name = row.split(None, 2)
                p = Path(name)
                self.assertEqual(p.parent, ROOT/directory)
                self.assertIn(p.suffix, ('.py','.json','.md','.patch'))
                raw = p.read_bytes()
                self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (int(size), sha))
        self.assertNotIn('torch', sys.modules)


if __name__ == '__main__':
    started = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceAliasTests))
    receipt = dict(kind='NEW_STDLIB_SOURCE_ALIAS_FIXTURE_ONLY_V2', tests=result.testsRun,
                   failures=len(result.failures), errors=len(result.errors), passed=result.wasSuccessful(),
                   elapsed_seconds=time.perf_counter()-started, Torch_imported='torch' in sys.modules,
                   actual_Torch_tests_executed=0, actual_native_operations=0,
                   real_q_base_metadata_functions_used=True, actual_core_load_body_executed=False,
                   old_twenty_microtrain_or_other_suites_rerun=False, actual_CPU_V2=None, actual_CPU_V3=None)
    with (HERE/'TEST_RESULTS_RESUME_ALIAS_STDLIB_V2.json').open('x', encoding='utf-8', newline='\n') as f:
        json.dump(receipt, f, indent=2); f.write('\n')
    if not result.wasSuccessful():
        raise SystemExit(1)
