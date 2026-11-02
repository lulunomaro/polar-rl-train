"""Own metadata/AST fixtures only; no parent, worker, model or resource execution."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import time
import unittest

B = Path(__file__).resolve().parent
S = B.parent / 'source_a1_frozen_eval_integration_v2'
sys.path.insert(0, str(S))
sys.path.insert(0, str(B))
import frozen_eval_microbatch_runtime_v1 as m
import build_microbatch_candidates_v1 as build


def producer(role):
    job = B / 'CPU_ONLY_METADATA_NOT_PT' / role
    counts = {key: 0 for key in m._base.COUNT_FIELDS}
    counts.update(policy_attempts=3, pi_optimizer_steps=2, pi_bptt_optimizer_steps=2)
    checkpoint = dict(path=str(job / 'production/checkpoints/synthetic_complete.pt'), bytes=123,
        SHA='3' * 64, counts=copy.deepcopy(counts), teacher_unchanged=True,
        full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True)
    final = dict(kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3', passed_execution=True,
        teacher_unchanged=True, role=role, role_key='own_' + role, run_id='SYNTHETIC_RUN',
        actor_view='raw35_legacy_held_aux_v1', algorithm_family='a1_raw35_legacy_v1',
        algorithm_variant='A1_RAW35_FRESH', checkpoint=checkpoint,
        counts=counts, actual_BPTT_policy_steps=2)
    return dict(own_job_root=str(job), FINAL_path=str(job / 'production/FINAL.json'),
        FINAL_bytes=321, FINAL_SHA='4' * 64, FINAL=final, role_key='own_' + role, run_id='SYNTHETIC_RUN')


def plan_fixture():
    expected = dict(pose_source_SHA=m._base.POSE_PIN[1], pose_source_bytes=m._base.POSE_PIN[0],
        pose_source_version=m._base.POSE_VERSION, install_timing=m._base.POSE_TIMING,
        seed=20260928, num_envs=80, explicit_original_reset_count=1, physics_dt=.0025,
        control_dt=.02, feedback_hz=100, actor_observation='original_noisy_delayed_policy35')
    rows = []
    for role in m.ROLES:
        row = dict(m.ORIGINAL_SCOPES[role], role=role,
            runtime_root='/own/approved/runtime/' + role,
            worker='worker_sources/parent/worker_five_original_n80.py')
        if role in m.REQUESTED_ROLES:
            row['a1_producer'] = producer(role)
        rows.append(row)
    return dict(kind=m.PLAN_KIND, batch_purpose=m.BATCH_PURPOSE,
        requested_roles=list(m.REQUESTED_ROLES), deferred_roles=list(m.DEFERRED_ROLES),
        overall_eight_pass_rate=None, comparison=None, roles=rows,
        worker_files=[dict(relative=name, bytes=1, SHA='5' * 64) for name in m.STAGE_REQUIRED_ALIASES],
        group_id='OWN_SYNTHETIC_GROUP', GPU_UUID='GPU-SYNTHETIC-NO-DEVICE',
        asset_SHA=m.USD, contract_SHA=m.CONTRACT,
        paired_reset_protocol=dict(kind='PAIRED_FROZEN_RESET_POSE_PROTOCOL_V2',
            reference_planned_protocol=copy.deepcopy(expected), candidate_planned_protocol=expected,
            historical_bug_baseline_reused=False, reference_actual_receipt=None))


def task_fixture(role='E3'):
    plan = plan_fixture()
    row = next(row for row in plan['roles'] if row['role'] == role)
    return m.make_task(row, plan, time.time() + 30, [7, 8])


def validate_task(task):
    root = B / 'CPU_ONLY_METADATA_NOT_ADMISSION'
    fds = []
    result = m.validate_group_task(task, task['role'], root, root / 'cases' / task['role'],
        environment={'CUDA_VISIBLE_DEVICES': task['GPU_UUID']}, fd_check=fds.append, now=lambda: 0)
    return result, fds


def recovery_rows():
    return [dict(recipe=i, initial_envs=7 if i < 2 else 6, original_request=i != 12,
        first_episode_original_stable_credit=1 if i == 0 else (6 if i == 12 else 0),
        first_episode_physical_terminated=1 if i == 0 else 0) for i in range(13)]


def terminal_fixture():
    rows = []
    for role in m.REQUESTED_ROLES:
        skill = (dict(original_recovery_recipe_rows=recovery_rows()) if role == 'E3' else
            dict(original_RM70_interval_route_facts=dict(events=dict(natural_complete_intervals=87,
                complete_kinematic_bounds_met=44, complete_kinematic_false=43, partial_intervals=20))))
        rows.append(dict(role=role, actual_waited=True, returncode=0, passed_execution=True,
            semantic=dict(passed_execution=True, original_error=False, actual_waited_returncode=0),
            data=dict(skill=skill)))
    return rows


class SchemaTests(unittest.TestCase):
    def test_fixed_subset_and_full_eight_catalog_retained(self):
        plan = plan_fixture(); before = copy.deepcopy(plan)
        self.assertEqual([r['role'] for r in m.select_requested_roles(plan)], ['E3', 'W35'])
        self.assertEqual(plan, before)
        self.assertEqual(len(m.ROLES), 8); self.assertEqual(len(m.DEFERRED_ROLES), 6)
        self.assertEqual(m.ROLES, m._base.ROLES); self.assertEqual(m.CONTROLS, m._base.CONTROLS)

    def test_membership_and_false_coverage_counterexamples(self):
        for key, value in [('requested_roles', ['E3']), ('requested_roles', ['W35', 'E3']),
            ('requested_roles', list(m.ROLES)), ('requested_roles', ['E3', 'E3']),
            ('requested_roles', ['E3', 'H1']), ('deferred_roles', []),
            ('overall_eight_pass_rate', .9), ('comparison', {'improved': True}), ('kind', m.KIND)]:
            with self.subTest(key=key, value=value):
                plan = plan_fixture(); plan[key] = value
                with self.assertRaises(ValueError): m.select_requested_roles(plan)

    def test_required_source_map_metadata_is_not_an_admission_bypass(self):
        for mode in ('missing', 'duplicate', 'traversal', 'bytes_bool', 'bad_sha'):
            plan = plan_fixture()
            if mode == 'missing': plan['worker_files'].pop()
            elif mode == 'duplicate': plan['worker_files'].append(copy.deepcopy(plan['worker_files'][0]))
            elif mode == 'traversal': plan['worker_files'][0]['relative'] = '../foreign.py'
            elif mode == 'bytes_bool': plan['worker_files'][0]['bytes'] = True
            else: plan['worker_files'][0]['SHA'] = 'not-a-SHA'
            with self.subTest(mode=mode), self.assertRaises(ValueError): m.select_requested_roles(plan)

    def test_missing_or_duplicate_original_catalog_is_not_subset_coverage(self):
        for mutation in ('missing', 'duplicate', 'H1'):
            plan = plan_fixture()
            if mutation == 'missing': plan['roles'].pop()
            elif mutation == 'duplicate': plan['roles'][-1] = copy.deepcopy(plan['roles'][0])
            else: plan['roles'][-1]['role'] = 'H1'
            with self.assertRaises(ValueError): m.select_requested_roles(plan)

    def test_all_original_scope_controls_even_deferred_are_exact(self):
        for role in m.ROLES:
            for field, value in [('controls', 1), ('num_envs', 79), ('seed', 123),
                                 ('physics_dt', .005), ('TGS', [16, 2])]:
                plan = plan_fixture(); row = next(r for r in plan['roles'] if r['role'] == role)
                row[field] = value
                with self.subTest(role=role, field=field), self.assertRaises(ValueError): m.select_requested_roles(plan)

    def test_reference_metadata_does_not_create_actual_reference(self):
        plan = plan_fixture()
        expected = plan['paired_reset_protocol']['candidate_planned_protocol']
        plan['paired_reset_protocol']['reference_actual_receipt'] = dict(
            protocol=expected, passed_execution=True, eval_id='UNVERIFIED-EXAMPLE')
        with self.assertRaises(ValueError): m.select_requested_roles(plan)

    def test_producer_not_training_target_3000_gate(self):
        rows = m.select_requested_roles(plan_fixture())
        self.assertEqual(rows[0]['a1_producer']['FINAL']['actual_BPTT_policy_steps'], 2)
        for change in ('full', 'counts', 'identity', 'variant'):
            plan = plan_fixture(); final = plan['roles'][0]['a1_producer']['FINAL']
            if change == 'full': final['checkpoint']['full_new_model_critic_aux_optimizers_replay_RNG_hist_saved'] = False
            elif change == 'counts': final['actual_BPTT_policy_steps'] = 3000
            elif change == 'identity': final['role'] = 'W35'
            else: final['algorithm_variant'] = 'A0'
            with self.assertRaises(ValueError): m.select_requested_roles(plan)

    def test_make_task_changes_membership_not_original_scope(self):
        task = task_fixture()
        self.assertEqual(task['eval_members'], ['E3', 'W35'])
        self.assertEqual(task['role_catalog'], list(m.ROLES))
        self.assertEqual(task['controls'], 160); self.assertEqual(task['physics_callbacks'], 1280)
        self.assertEqual(task['feedback_samples'], 320); self.assertEqual(task['optimizer_updates'], 0)
        self.assertEqual(validate_task(task), (True, [7, 8]))
        self.assertEqual(task['integration'], m._base.INTEGRATION)

    def test_original_eight_validator_is_still_strict(self):
        task = task_fixture(); root = B / 'CPU_ONLY_METADATA_NOT_ADMISSION'
        with self.assertRaisesRegex(ValueError, 'all eight members'):
            m._base.validate_group_task(task, 'E3', root, root / 'E3',
                environment={'CUDA_VISIBLE_DEVICES': task['GPU_UUID']}, fd_check=lambda fd: None, now=lambda: 0)

    def test_new_task_resource_scope_and_producer_checks_fail_closed(self):
        for key, value in [('num_envs', 79), ('seed', 0), ('gas_N', 200), ('physics_dt', .005),
            ('source_SHA', 'f' * 64), ('asset_SHA', 'a' * 64), ('controls', 10),
            ('eval_members', list(m.ROLES)), ('batch_purpose', m.KIND), ('overall_eight_pass_rate', 1.)]:
            task = task_fixture(); task[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): validate_task(task)
        for key in ('source_SDK_admitted', 'private_GPU_EX_held', 'global_finite_EX_held'):
            task = task_fixture(); task['actual_group_admission'][key] = False
            with self.assertRaises(ValueError): validate_task(task)
        for fds in ([7], [7, 7], [7, True]):
            task = task_fixture(); task['actual_group_admission']['inherited_lock_fds'] = fds
            with self.assertRaises(ValueError): validate_task(task)


class BarrierAndResultTests(unittest.TestCase):
    def test_two_member_start_with_six_deferred(self):
        plan = plan_fixture(); value = m.batch_start(plan, ['W35', 'E3'], 1.)
        self.assertTrue(m.validate_start(task_fixture(), value))
        self.assertIsNone(value['overall_eight_pass_rate'])
        for members in (['E3'], ['E3', 'E3'], list(m.ROLES), list(m.ROLES) + ['H1']):
            value['members'] = members
            with self.assertRaises(ValueError): m.validate_start(task_fixture(), value)

    def test_wrong_group_GPU_purpose_and_unready_are_not_start(self):
        for key, value in [('group_id', 'foreign'), ('GPU_UUID', 'foreign'), ('batch_purpose', m.KIND),
                           ('all_members_ready', False), ('all_members_ready', 1)]:
            start = m.batch_start(plan_fixture(), ['E3', 'W35'], 1.); start[key] = value
            with self.assertRaises(ValueError): m.validate_start(task_fixture(), start)

    def test_actual_wait_start_fixture_no_SDK_getters_or_control(self):
        group = Path(tempfile.mkdtemp(prefix='CPU_ONLY_BARRIER_', dir=B)); out = group / 'cases/E3'
        out.mkdir(parents=True); task = task_fixture()
        m._base.put_json(group / 'GROUP_EVAL_START.json', m.batch_start(plan_fixture(), ['E3', 'W35'], 1.))
        result = m.wait_start(task, out, group, dict(num_envs=80, controls=160))
        self.assertEqual(set(result['members']), {'E3', 'W35'})
        ready = json.loads((out / 'WORKER_SCENE_READY.json').read_text())
        self.assertIs(ready['zero_controls_before_group_barrier'], True)
        self.assertTrue((out / 'WORKER_EVAL_STARTED.json').exists())

    def test_group_abort_is_error_before_start(self):
        group = Path(tempfile.mkdtemp(prefix='CPU_ONLY_ABORT_', dir=B)); out = group / 'E3'; out.mkdir()
        (group / 'GROUP_ABORT.json').write_text('{}')
        with self.assertRaises(RuntimeError): m.wait_start(task_fixture(), out, group, dict(num_envs=80))

    def test_original_E3_74_denominator_normal_excluded_credit_prefix_kept(self):
        result = m.batch_result(plan_fixture(), terminal_fixture(), 1., epoch=2.)
        skill = result['absolute_original_scope_results']['E3']
        self.assertEqual((skill['passed'], skill['denominator']), (1, 74))
        self.assertEqual(skill['absolute_original_scope_rate'], 1 / 74)
        self.assertFalse(skill['normal_scored_as_rescue'])
        self.assertEqual(skill['normal_group']['first_episode_original_stable_credit'], 6)
        self.assertIsNone(skill['global_expert_graduation'])

    def test_unknown_E3_cohort_or_counter_is_null_not_false_or_proxy(self):
        for mutation in ('missing', 'bool', 'wrong74'):
            data = terminal_fixture()[0]['data']
            if mutation == 'missing': data['skill']['original_recovery_recipe_rows'].pop()
            elif mutation == 'bool': data['skill']['original_recovery_recipe_rows'][0]['initial_envs'] = True
            else: data['skill']['original_recovery_recipe_rows'][0]['initial_envs'] += 1
            self.assertIsNone(m._absolute_skill('E3', data)['absolute_original_scope_rate'])

    def test_W35_combined_counter_is_never_moving_rate(self):
        skill = m.batch_result(plan_fixture(), terminal_fixture(), 1., epoch=2.)['absolute_original_scope_results']['W35']
        self.assertEqual(skill['original_combined_events']['complete_kinematic_bounds_met'], 44)
        self.assertIsNone(skill['moving_rate']); self.assertIsNone(skill['standing_rate'])
        self.assertIsNone(skill['absolute_original_scope_rate'])

    def test_deferred_not_failure_and_no_eight_or_relative_rate(self):
        result = m.batch_result(plan_fixture(), terminal_fixture(), 1., epoch=2.)
        self.assertTrue(result['all_requested_actual_execution_complete'])
        self.assertEqual(sum(v == 'deferred' for v in result['coverage'].values()), 6)
        for key in ('overall_eight_pass_rate', 'all_eight_actual_execution_complete',
                    'comparison', 'relative_improvement', 'paired_actual_reference', 'UID_alignment',
                    'reference_cache_match', 'E0_original_binary_predicate', 'SLOPE_INDEPENDENT50_original_binary_predicate'):
            self.assertIsNone(result[key])

    def test_RC_error_missing_wait_or_semantic_failure_cannot_count_success(self):
        for field, value in [('returncode', 1), ('returncode', False), ('actual_waited', False),
                             ('passed_execution', False), ('semantic', None)]:
            rows = terminal_fixture(); rows[0][field] = value
            result = m.batch_result(plan_fixture(), rows, 1., epoch=2.)
            self.assertFalse(result['all_requested_actual_execution_complete'])
            self.assertIsNone(result['absolute_original_scope_results']['E3']['absolute_original_scope_rate'])
        rows = terminal_fixture(); rows[0]['semantic']['original_error'] = True
        self.assertFalse(m.batch_result(plan_fixture(), rows, 1., epoch=2.)['all_requested_actual_execution_complete'])


class SourceIdentityTests(unittest.TestCase):
    def test_original_components_are_identical_not_reimplemented(self):
        for name in ('A1CheckpointAdapter', 'install_paired_pose_before_original_reset', 'record_primary_error',
                     'close_original_eval_resources', 'evaluate_waited_eval_case', 'build_a1_original_vec'):
            self.assertIs(getattr(m, name), getattr(m._base, name))

    def test_full_parent_and_worker_AST_whitelist_undo(self):
        cases = [('single_gpu_eight_a1_frozen_parent_candidate_v2.py', build.PARENT_PIN,
                   build.PARENT, build.replacements),
                 ('worker_formal_a1_frozen_candidate_v2.py', build.WORKER_PIN,
                   build.WORKER, build.worker_replacements)]
        for original, pin, candidate, transform in cases:
            old = build.read_pinned(original, pin); expected, pairs = transform(old)
            new = (B / candidate).read_text(encoding='utf-8')
            self.assertEqual(new, expected); build.undo_equal(old, new, pairs)
        build.verify_validator()

    def test_original_admission_and_finally_are_LF_identical(self):
        old = build.read_pinned('single_gpu_eight_a1_frozen_parent_candidate_v2.py', build.PARENT_PIN)
        new = (B / build.PARENT).read_text(encoding='utf-8')
        self.assertEqual(old.split('class BusyResource', 1)[1].split('deadline=time.time()+2400', 1)[0],
                         new.split('class BusyResource', 1)[1].split('deadline=time.time()+2400', 1)[0])
        self.assertEqual(old.split('finally:', 1)[1], new.split('finally:', 1)[1])
        self.assertIn('rc=p.wait();semantic=evaluate_waited_eval_case', new)
        for text in ('+1800', '<23500', '>96*1024**3', '>25*1024**3', '+2400', '+900',
                     "'state/finite_environment_validation.lock'", 'canonical.read_bytes()'):
            self.assertIn(text, new)

    def test_sealed_index_all_twelve_source_mappings_are_unchanged(self):
        index = json.loads(build.read_pinned('FROZEN_EVAL_SEALED_SOURCE_INDEX_V2.json', build.INDEX_PIN))
        self.assertEqual(len(index['entries']), 12)
        for entry in index['entries']:
            path = Path(entry['path']); self.assertEqual(path.suffix, '.py')
            raw = path.read_bytes()
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (entry['bytes'], entry['SHA256']))

    def test_no_model_or_SDK_imported_and_no_PT_fixture_created(self):
        self.assertNotIn('torch', sys.modules)
        self.assertFalse(any(name == 'isaaclab' or name.startswith('isaaclab.') for name in sys.modules))
        self.assertFalse((B / 'CPU_ONLY_METADATA_NOT_PT').exists())


if __name__ == '__main__':
    if (B / 'DELIVERABLES_SHA256_V1.json').exists():
        raise SystemExit('sealed outputs are immutable; run in a new scratch/version')
    started = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    receipt = dict(kind='STDLIB_SOURCE_FAKE_MICROBATCH_NOT_NATIVE_ADMISSION_OR_EVAL',
        tests=result.testsRun, failures=len(result.failures), errors=len(result.errors), passed=result.wasSuccessful(),
        seconds=time.perf_counter() - started, requested_roles=['E3', 'W35'], full_role_catalog=8,
        actual_SDK_Torch_GPU_PT_C_account_lock_Git_or_dispatch_operations=0,
        comparison=None, overall_eight_pass_rate=None)
    (B / 'CPU_TEST_RESULTS_V1.json').write_text(json.dumps(receipt, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps(receipt, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
