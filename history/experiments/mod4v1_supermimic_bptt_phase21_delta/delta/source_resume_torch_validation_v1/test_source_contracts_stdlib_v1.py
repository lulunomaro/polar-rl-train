"""Local stdlib/AST checks only; never imports Torch or executes CPU test run()."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPT = HERE / 'test_resume_legacy_torch_cpu_v1.py'
PIN = '08c89b3603eb7b32b4eb430a9cde112035ca187695272ee992742ceb147079d7'
SOURCE = SCRIPT.read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)
SPEC = importlib.util.spec_from_file_location('_stdlib_only_new_resume_test_source_v1', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def function(name): return next(n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef) and n.name == name)
def text(name): return ast.get_source_segment(SOURCE, function(name))
def calls(node, name):
    return [n for n in ast.walk(node) if isinstance(n, ast.Call) and
            (getattr(n.func, 'attr', None) == name or getattr(n.func, 'id', None) == name)]


class SourceContracts(unittest.TestCase):
    def test_01_frozen_script_identity_and_compile(self):
        self.assertEqual(hashlib.sha256(SCRIPT.read_bytes()).hexdigest(), PIN)
        compile(SOURCE, str(SCRIPT), 'exec')
    def test_02_import_is_stdlib_only(self):
        self.assertNotIn('torch', sys.modules)
        self.assertFalse(any(n == 'isaaclab' or n.startswith(('isaaclab.', 'omni.')) for n in sys.modules))
    def test_03_all_actual_source_pins_match(self):
        paths = dict(fixture=ROOT / 'source_runtime/synthetic_cpu_contract_check.py',
            bridge_source=ROOT / 'source_runtime/native_supermimic_bridge.py',
            payload_core=ROOT / 'source_resume_runtime_v2/ctx_reward_full_resume_candidate_v2.py',
            resume_contracts=ROOT / 'source_resume_runtime_v2/resume_runtime_contracts_v3.py',
            raw35_source=ROOT / 'source_command_review_v1/command_tracking_torch_candidate_v1.py')
        self.assertEqual(set(paths), set(MODULE.PINS))
        for key, path in paths.items(): self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), MODULE.PINS[key])
    def test_04_ast_exec_excludes_fixture_bottom(self):
        value = text('ast_classes')
        self.assertIn('isinstance(n, ast.ClassDef)', value)
        self.assertIn('n.name in names', value)
        self.assertIn('ast.Module(body=selected', value)
        run = text('run')
        self.assertIn("('FakeTeacher', 'Synthetic')", run)
        self.assertIn("('BridgeState', 'OriginalTaskMdp')", run)
        self.assertIn("('TeacherResidualPolicy',)", run)
        self.assertNotIn('PinnedTeacher(', run)
        self.assertNotIn('NativeTaskBridge(', run)
    def test_05_explicit_real_import_origins(self):
        self.assertIn('Path(module.__file__).resolve() == Path(path).resolve()', text('import_exact'))
        self.assertIn("actual_vendor == vendor_parent / 'supermimic_vendor_v2' / 'learner.py'", text('run'))
        for attr in ('payload_core', 'resume_contracts', 'raw35_source'):
            self.assertIn('import_exact(args.' + attr, text('run'))
    def test_06_legacy_core_does_not_call_new_strict_hooks(self):
        source = (ROOT / 'source_resume_runtime_v2/ctx_reward_full_resume_candidate_v2.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'policy_update')
        constants = [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        self.assertIn('project_predicted_context', constants)
        for hook in ('project_transition_context', 'project_imagined_reward', 'policy_regularizer'):
            self.assertNotIn(hook, constants)
    def test_07_no_oracle_or_bound_anchor_reward(self):
        self.assertIn('Raw35ActorMDP(base, transition_projector=None)', text('run'))
        self.assertIn('type(learner.pi) is TeacherResidualPolicy', text('make_learner'))
        self.assertIn('learner.pi.scale == .05', text('make_learner'))
        self.assertIn("last_projection_status == 'not_used'", text('one_variant'))
        self.assertFalse(calls(TREE, 'project_transition_context'))
        self.assertFalse(calls(TREE, 'lower_confidence_reward'))
    def test_08_both_independent_views_and_actual_zero_counters(self):
        self.assertIn("('A0_FULLCTX', contracts.BASELINE_ACTOR_VIEW)", text('run'))
        self.assertIn("('A1_RAW35', contracts.RAW35_ACTOR_VIEW)", text('run'))
        self.assertIn('dict.fromkeys(contracts.COUNT_FIELDS, 0)', text('make_learner'))
        self.assertIn('all(not optimizer.state', text('make_learner'))
        assignments = [n for n in ast.walk(TREE) if isinstance(n, ast.Assign) for t in n.targets
                       if isinstance(t, ast.Attribute) and t.attr == 'counts']
        self.assertFalse(assignments, 'test must not assign/splice producer count objects')
    def test_09_real_loop_plan_h16_hist10_collect8_wm20_pi3(self):
        self.assertIn('horizon=16', text('run'))
        self.assertIn('hist=10', text('run'))
        self.assertIn('learner.collect(8)', text('one_variant'))
        self.assertIn('for _ in range(20): learner.wm_update()', text('one_variant'))
        self.assertIn('for index in range(3):', text('one_variant'))
        self.assertIn('learner.policy_update()', text('one_variant'))
    def test_10_all_actual_gradient_receipts_required(self):
        value = text('gradient_receipt')
        for key in ('verified_bptt_optimizer_step', 'cross_time_finite', 'cross_time_grad_norm',
                    'wm_path_finite', 'wm_path_grad_norm', 'parameter_grad_norm', 'probe_parameter_delta_l2'):
            self.assertIn(key, value)
    def test_11_only_new_synthetic_PT_output_writes(self):
        value = text('write_own_synthetic')
        self.assertIn('is_relative_to(output.resolve())', value)
        self.assertIn("path.open('xb')", value)
        self.assertIn('torch.save(payload, stream)', value)
        self.assertIn('SYNTHETIC_TEACHER_IDENTITY_NO_FILE', text('run'))
        for forbidden in ('unlink', 'rmdir', 'rmtree', 'rename', 'remove', 'system', 'Popen', 'connect'):
            self.assertFalse(calls(TREE, forbidden), forbidden)
    def test_12_single_physical_read_and_single_BytesIO_decode(self):
        self.assertEqual(len(calls(function('reader'), 'read_bytes')), 1)
        self.assertEqual(len(calls(function('decoder'), 'load')), 1)
        self.assertIn('map_location=\'cpu\', weights_only=True', text('decoder'))
        self.assertIn('isinstance(stream, io.BytesIO)', text('decoder'))
        self.assertEqual(len(calls(function('pinned_read_and_load'), 'PinnedOwnFullCheckpoint')), 1)
        self.assertIn('physical_reads=1, decodes=1, decoded_loader_calls=1', text('pinned_read_and_load'))
    def test_13_real_contract_gate_then_real_decoded_loader(self):
        self.assertIn('contracts.load_decoded_full_checkpoint_once(learner, pinned, read_task, layout)', text('pinned_read_and_load'))
        self.assertIn('actual_api(payload, **kwargs)', text('counted_api'))
        self.assertIn('allow_environment_reset=True, allow_partial_update=False', text('counted_api'))
        path_loads = [n for n in calls(function('pinned_read_and_load'), 'load')
                      if isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                      and n.func.value.id == 'learner']
        self.assertFalse(path_loads)
    def test_14_metadata_fields_are_explicit_and_synthetic(self):
        for field in ('teacher_path', 'teacher_SHA', 'teacher_bytes', 'asset_SHA', 'contract_SHA', 'original_protocol',
                      'actor_view', 'algorithm_variant', 'num_envs', 'run_id', 'role'):
            self.assertIn(field, text('base_task'))
        self.assertIn('SYNTHETIC_ONLY', text('base_task'))
        self.assertIn('new_algorithm_not_PPO_resume=True', text('one_variant'))
        self.assertIn('bootstrap_teacher=teacher_identity', text('one_variant'))
    def test_15_four_models_four_optimizers_and_norm_values(self):
        for name in ('wm', 'pi', 'critic', 'aux', 'opt_wm', 'opt_pi', 'opt_v', 'opt_aux'):
            self.assertIn("'" + name + "'", text('full_states'))
        self.assertIn('four_models_four_optimizers', text('assert_all_restored'))
        self.assertIn("key.endswith(('.mean', '.var', '.count'))", text('one_variant'))
    def test_16_replay_streamcut_not_done_relabel_and_fresh_hist(self):
        value = text('assert_all_restored')
        for field in ('done', 'term', 'trunc', 'xi1_valid', 'stream_cut'):
            self.assertIn("'" + field + "'", value)
        self.assertIn('torch.count_nonzero(learner.obs_hist) == 0', value)
        self.assertIn("torch.count_nonzero(ext['obs_hist']) > 0", value)
        self.assertIn("windows['mask'][:, 1] == 0", text('one_variant'))
        self.assertIn('fresh_env.fresh_initializations == 1', text('one_variant'))
    def test_17_RNG_state_and_sequence_without_manual_global_restore(self):
        self.assertIn('core.capture_rng()', text('assert_all_restored'))
        self.assertIn('isolated_python.setstate', text('rng_sequence_probe'))
        self.assertIn('isolated_torch.set_state', text('rng_sequence_probe'))
        self.assertIn('isolated_np.set_state', text('rng_sequence_probe'))
        self.assertFalse(calls(TREE, 'restore_rng'))
    def test_18_cumulative_continue_three_to_four_not_fresh_offset(self):
        value = text('one_variant')
        self.assertIn('restored_counts = dict(vars(restored.counts))', value)
        self.assertIn('restored.collect(1)', value)
        self.assertIn('restored.wm_update()', value)
        self.assertIn('restored.policy_update()', value)
        self.assertIn('pi_bptt_optimizer_steps=4', value)
        self.assertIn('wm_optimizer_steps=21', value)
        self.assertIn('restored.iteration == 4 and restored.sim_steps == 72', value)
    def test_19_actual_teacher_weights_and_buffers_not_source_cache_only(self):
        self.assertIn('torch.equal(current[key], value)', text('assert_teacher'))
        self.assertIn('parameter.grad is None', text('assert_teacher'))
        for field in ('teacher.net.weight', 'teacher.synthetic_frozen_buffer'):
            self.assertIn(field, text('one_variant'))
        self.assertIn('pinned_read_and_load(bad_learner, bad_task)', text('one_variant'))
        self.assertIn('assert_teacher(bad_teacher, bad_snapshot)', text('one_variant'))
        self.assertIn('teacher_source_versions', text('one_variant'))
    def test_20_cross_view_real_metadata_and_isolated_torch_shape_gates(self):
        value = text('run')
        self.assertIn('contracts.validate_worker_variant(wrong)', value)
        self.assertIn('contracts.validate_full_resume_payload(payload, metadata_case', value)
        self.assertIn("target_learner.pi.load_state_dict(payload['pi'], strict=True)", value)
        self.assertIn('not an admitted resume and never continued', value)
    def test_21_error_receipt_and_new_output_directory(self):
        value = text('main')
        self.assertIn('exist_ok=False', value)
        self.assertEqual(len(calls(function('main'), 'open')), 2)
        self.assertIn('except BaseException:', value)
        self.assertIn('traceback.format_exc()', value)
        self.assertIn('SYNTHETIC_TORCH_RESUME_RECEIPT_V1.json', value)
    def test_22_no_native_claim_and_explicit_CPU_checks(self):
        for field in ('original_model_PT_reads=0', 'native_expert_BPTT_updates_counted=0',
                      'sensor_projection_exact=False', 'command_tracking_fixed=False', 'oracle_used=False'):
            self.assertIn(field, text('run'))
        self.assertIn("value.device.type == 'cpu'", text('make_learner'))
        self.assertIn('not torch.cuda.is_initialized()', text('run'))
        self.assertIn("'App.close semantics'", text('run'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceContracts))
    receipt = dict(kind='LOCAL_STDLIB_AST_SOURCE_CONTRACTS_ONLY_NOT_TORCH_EXECUTION_V1',
        passed=result.wasSuccessful(), tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        elapsed_seconds=time.monotonic() - started, script_SHA256=PIN,
        Torch_imported='torch' in sys.modules, actual_checkpoint_reads=0, own_synthetic_PT_created=0,
        SDK_GPU_native_training_C_GO_lock_operations=0,
        actual_CPU_Torch_result='PENDING_PARENT_EXECUTION',
        errors_detail=[dict(test=str(test), traceback=message) for test, message in result.failures + result.errors])
    with args.output.open('x', encoding='utf-8') as stream: json.dump(receipt, stream, indent=2)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__': main()
