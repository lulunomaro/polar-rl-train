"""Stdlib source/fixture counterexamples for explicit A0/A1 separation. No Torch."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import resume_runtime_contracts_v3 as v3
import test_source_resume_runtime_stdlib_v2 as v2_tests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = Path(tempfile.mkdtemp(prefix='VARIANT_STDLIB_SYNTHETIC_CASES_', dir=HERE))


def a1_case():
    task, contract, layout, payload = v2_tests.full_case()
    task.update(actor_view=v3.RAW35_ACTOR_VIEW, algorithm_variant='A1_RAW35_RESUME')
    task['resume_bptt'].update(actor_view=v3.RAW35_ACTOR_VIEW, algorithm_family='a1_raw35_legacy_v1')
    contract['obs_dim'] = 35
    payload['context_reward_extension']['contract'] = copy.deepcopy(contract)
    payload.update(actor_view=v3.RAW35_ACTOR_VIEW, algorithm_family='a1_raw35_legacy_v1',
                   algorithm_variant='A1_RAW35_FRESH', run_id='old-own-run')
    return task, contract, layout, payload


class Array:
    def __init__(self, rows):
        self.rows = rows
        self.shape = (len(rows), len(rows[0]))
        self.ndim = 2
    def __getitem__(self, key):
        assert key[0] == Ellipsis
        return Array([row[key[-1]] for row in self.rows])
    def repeat(self, batch_repeats, times):
        assert batch_repeats == 1
        return Array([row * times for row in self.rows])


def extracted_raw35():
    path = ROOT / 'source_command_review_v1/command_tracking_torch_candidate_v1.py'
    node = next(n for n in ast.parse(path.read_text(encoding='utf-8')).body
                if isinstance(n, ast.ClassDef) and n.name == 'Raw35ActorMDP')
    ns = {'UnknownCommandEvolution': ValueError}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(node)], type_ignores=[])), str(path), 'exec'), ns)
    return ns['Raw35ActorMDP']


class VariantTests(unittest.TestCase):
    def test_default_a0_fresh_preserves_old_view(self):
        out = v3.validate_worker_variant({})
        self.assertEqual(out['algorithm_variant'], 'A0_FULLCTX_FRESH')
        self.assertEqual(out['actor_view'], v3.BASELINE_ACTOR_VIEW)

    def test_a0_resume_accepts_legacy_complete_metadata(self):
        task, contract, layout, payload = v2_tests.full_case()
        out = v3.validate_full_resume_payload(payload, task, contract, layout)
        self.assertEqual(out['restored_counts']['pi_bptt_optimizer_steps'], 2520)

    def test_a1_fresh_explicit_no_resume(self):
        entry = dict(actor_view=v3.RAW35_ACTOR_VIEW, algorithm_variant='A1_RAW35_FRESH')
        out = v3.bind_future_task_extensions({'seed': 7}, entry)
        self.assertNotIn('resume_bptt', out)
        self.assertEqual(out['actor_observation_dim'], 35)
        self.assertFalse(out['command_tracking_fixed'])
        self.assertFalse(out['sensor_projection_exact'])
        self.assertEqual(out['bound_anchor_reward_changes'], 0)

    def test_a1_fresh_cannot_take_a0_resume(self):
        entry = dict(actor_view=v3.RAW35_ACTOR_VIEW, algorithm_variant='A1_RAW35_FRESH', resume_bptt=v2_tests.descriptor())
        with self.assertRaises(ValueError): v3.bind_future_task_extensions({}, entry)

    def test_a1_resume_must_be_explicitly_complete_and_same_view(self):
        task, contract, layout, payload = a1_case()
        out = v3.validate_full_resume_payload(payload, task, contract, layout)
        self.assertEqual(out['restored_counts'], v2_tests.counts())

    def test_a1_resume_no_a0_payload_even_with_forged_outer_label(self):
        task, contract, layout, payload = a1_case()
        payload['context_reward_extension']['contract']['obs_dim'] = 119
        with self.assertRaises(ValueError): v3.validate_full_resume_payload(payload, task, contract, layout)

    def test_a1_requires_embedded_view(self):
        task, contract, layout, payload = a1_case()
        del payload['actor_view']
        with self.assertRaises(ValueError): v3.validate_full_resume_payload(payload, task, contract, layout)

    def test_a1_requires_embedded_family(self):
        task, contract, layout, payload = a1_case()
        payload['algorithm_family'] = 'a0_fullctx_legacy_v1'
        with self.assertRaises(ValueError): v3.validate_full_resume_payload(payload, task, contract, layout)

    def test_a1_descriptor_cannot_claim_original_fullctx(self):
        task, contract, layout, payload = a1_case()
        task['resume_bptt']['actor_view'] = v3.BASELINE_ACTOR_VIEW
        with self.assertRaises(ValueError): v3.validate_full_resume_payload(payload, task, contract, layout)

    def test_a0_cannot_load_a1_same_width_trick(self):
        task, contract, layout, payload = v2_tests.full_case()
        payload['actor_view'] = v3.RAW35_ACTOR_VIEW
        with self.assertRaises(ValueError): v3.validate_full_resume_payload(payload, task, contract, layout)

    def test_a1_actor_only_and_each_optimizer_missing(self):
        for key in ('wm', 'critic', 'opt_wm', 'opt_pi', 'opt_v'):
            task, contract, layout, payload = a1_case()
            del payload[key]
            with self.assertRaises(ValueError): v3.validate_full_resume_payload(payload, task, contract, layout)

    def test_a1_pin_is_still_one_read_one_decode(self):
        raw = b'A1_PURE_SYNTHETIC_NOT_MODEL_BYTES'
        task, contract, layout, payload = a1_case()
        descriptor = task['resume_bptt']
        descriptor.update(bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())
        events = []
        pinned = v3.PinnedOwnFullCheckpoint(descriptor,
            lambda stream: (events.append(('decode', stream.read())) or payload),
            read_bytes=lambda path: (events.append(('read', path)) or raw))
        learner, trace = v2_tests.fake_loader(contract)
        receipt = v3.load_decoded_full_checkpoint_once(learner, pinned, task, layout)
        self.assertEqual([event[0] for event in events], ['read', 'decode'])
        self.assertEqual(receipt['byte_cache']['decodes'], 1)
        self.assertEqual(vars(learner.counts), v2_tests.counts())
        self.assertEqual(trace[-1][0], 'restore_rng')

    def test_raw35_real_obs_identity_and_known_command_goal(self):
        cls = extracted_raw35()
        raw = Array([[float(i) for i in range(40)], [float(i) + .123 for i in range(40)]])
        base = type('Base', (), {'to': lambda self, device: self})()
        mdp = cls(base, transition_projector=None)
        obs = mdp.obs(None, None, raw, None)
        self.assertEqual(obs.rows, [row[:35] for row in raw.rows])
        self.assertEqual(mdp.goal_with_context(None, 1, raw).rows, [row[:3] for row in raw.rows])
        self.assertIs(mdp.add_noise(obs), obs)
        self.assertEqual(mdp.actor_context_offset, 0)

    def test_original_projection_delegates_without_oracle(self):
        cls = extracted_raw35()
        events = []
        class Base:
            def project_predicted_context(self, context, s1, action, frames):
                events.append((context, s1, action, frames))
                return context
        mdp = cls(Base(), transition_projector=None)
        context = object()
        # These are exactly the three original-core lookup/call statements.
        project = getattr(mdp, 'project_predicted_context', None)
        if callable(project): result = project(context, 'state1', 'action', 'next_frames')
        self.assertIs(result, context)
        self.assertEqual(len(events), 1)
        self.assertEqual(mdp.last_projection_status, 'not_used')

    def test_core_has_no_strict_projection_or_reward_anchor_hooks(self):
        path = HERE / 'ctx_reward_full_resume_candidate_v2.py'
        source = path.read_text(encoding='utf-8')
        method = v2_tests.ast_method(path, 'ContextRewardLearner', 'policy_update')
        constants = {n.value for n in ast.walk(method) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        self.assertIn('project_predicted_context', constants)
        self.assertNotIn('project_transition_context', constants)
        self.assertNotIn('project_imagined_reward', constants)
        self.assertNotIn('policy_regularizer', constants)
        self.assertNotIn('command_candidate.v1', source)

    def test_v3_worker_uses_only_original_scaled_policy(self):
        path = HERE / 'worker_supermimic_bptt_actor_variant_candidate_v3.py'
        source = path.read_text(encoding='utf-8')
        self.assertIn('TeacherResidualPolicy(super()._make_policy(),actor,bridge.mdp.actor_context_offset,scale=.05)', source)
        self.assertIn('Raw35ActorMDP(bridge.mdp,transition_projector=None)', source)
        self.assertNotIn('BoundedTeacherResidualPolicy(', source)
        self.assertNotIn('load_state_dict(', source)
        self.assertNotIn('learner.load(', source)
        self.assertIn('all(value==0 for value in vars(learner.counts).values())', source)

    def test_v3_worker_exactly_one_original_reset_and_teacher_buffer_check(self):
        source = (HERE / 'worker_supermimic_bptt_actor_variant_candidate_v3.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        self.assertEqual(sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'env' and n.func.attr == 'reset' for n in ast.walk(tree)), 1)
        self.assertIn('value.detach().clone() for key,value in actor.state_dict().items()', source)
        self.assertIn('torch.equal(current[key],value)', source)
        self.assertLess(source.index('bind_original_command_after_fresh_reset(env,role,obs)'), source.index('bridge=BridgeClass('))

    def test_new_owner_protected_functions_and_globals_unchanged(self):
        for new, old in [('supermimic_original_owner_actor_variant_candidate_v3.py', 'supermimic_original_owner.py'),
                         ('supermimic_original_owner_shared_actor_variant_candidate_v3.py', 'supermimic_original_owner_shared_v2.py')]:
            a = ast.parse((HERE / new).read_text(encoding='utf-8'))
            b = ast.parse((ROOT / 'source_runtime' / old).read_text(encoding='utf-8'))
            protected = lambda tree: [ast.dump(n, include_attributes=False) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.Assign)) and getattr(n, 'name', None) != 'main']
            self.assertEqual(protected(a), protected(b))

    def test_frozen_raw35_and_payload_core_sha(self):
        self.assertEqual(hashlib.sha256((ROOT / 'source_command_review_v1/command_tracking_torch_candidate_v1.py').read_bytes()).hexdigest(), 'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223')
        self.assertEqual(hashlib.sha256((HERE / 'ctx_reward_full_resume_candidate_v2.py').read_bytes()).hexdigest(), '8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac')

    def test_variant_final_bad_family_blocks_after_actual_wait(self):
        job = Path(tempfile.mkdtemp(prefix='job_', dir=CASES))
        output = job / 'production'; output.mkdir()
        entry = dict(role='E0', role_key='E0', actor_view=v3.RAW35_ACTOR_VIEW, algorithm_variant='A1_RAW35_FRESH')
        count = v2_tests.counts(3)
        checkpoint = dict(path=str(output / 'checkpoints/own_synthetic.pt'), SHA='a' * 64, bytes=32,
                          full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True, counts=count)
        final = dict(kind=v3.FINAL_KIND, passed_execution=True, run_id='new-run', role='E0', role_key='E0',
                     counts=count, actual_BPTT_policy_steps=3, checkpoint=checkpoint, teacher_unchanged=True,
                     actor_view=v3.RAW35_ACTOR_VIEW, algorithm_family='a1_raw35_legacy_v1')
        life = dict(kind=v3.LIFECYCLE_KIND, passed_execution=True, role='E0', run_id='new-run', all_original_close_calls_returned=True)
        (output / 'FINAL.json').write_text(json.dumps(final), encoding='utf-8')
        (output / 'WORKER_LIFECYCLE_COMPLETE_V3.json').write_text(json.dumps(life), encoding='utf-8')
        self.assertFalse(v3.evaluate_waited_worker(job, 0, entry, 'new-run')['original_error'])
        final['algorithm_family'] = 'a0_fullctx_legacy_v1'
        (output / 'FINAL.json').write_text(json.dumps(final), encoding='utf-8')
        self.assertTrue(v3.evaluate_waited_worker(job, 0, entry, 'new-run')['original_error'])

    def test_no_torch_or_sdk_imported(self):
        self.assertNotIn('torch', sys.modules)
        self.assertFalse(any(name.startswith(('isaaclab', 'isaacsim', 'omni.')) for name in sys.modules))


if __name__ == '__main__':
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(v2_tests),
                                unittest.defaultTestLoader.loadTestsFromTestCase(VariantTests)])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = dict(kind='STDLIB_V2_REGRESSION_AND_V3_ACTOR_VARIANT_NOT_TORCH_OR_NATIVE', tests_run=result.testsRun,
                   passed=result.wasSuccessful(), failures=len(result.failures), errors=len(result.errors),
                   new_variant_tests=unittest.defaultTestLoader.loadTestsFromTestCase(VariantTests).countTestCases(),
                   fixture_root=str(CASES), Torch_imported='torch' in sys.modules,
                   real_checkpoint_bytes_opened=0, SDK_imports=0, GPU_operations=0, native_runs=0,
                   training_updates=0, original_account_C_lock_operations=0,
                   interpretation='AST/extracted actual loader and Raw35 class with fake objects; actual A1 Torch/full-resume validation remains pending')
    with (HERE / 'TEST_RESULTS_ACTOR_VARIANTS_STDLIB_V3.json').open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, indent=2)
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
