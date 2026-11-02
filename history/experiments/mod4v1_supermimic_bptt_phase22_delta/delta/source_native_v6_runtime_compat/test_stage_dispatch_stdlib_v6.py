"""SYNTHETIC files/AST/mock-Popen only; never source-stage native inputs or launch an owner."""
import argparse
import ast
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stage_a1_native_v6 as stage
import dispatch_a1_native_v6_once as dispatch

PROJECT = HERE.parent
ORIGINAL_PLAN = PROJECT / 'payload_supermimic_eight_v1' / 'SOURCE_PLAN.json'
OWNER = PROJECT / 'source_app_close_semantics_v5' / stage.OWNER_NAME
CONTRACTS = PROJECT / 'source_resume_runtime_v2' / 'resume_runtime_contracts_v3.py'
FIXTURES = None


def actual_fourteen_sources():
    helper = PROJECT.parent / 'mod4v1_experts_fulldr_rm70_20261101' / 'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102' / 'parent_source' / 'original_budget_and_asset_refs'
    mapping = {name: helper / name for name in ('three_slot_common_v1.py', 'single_writer72_authority_V85M_source.py')}
    mapping['shared_gpu_admission_v1.py'] = PROJECT / 'source_runtime/shared_gpu_admission_v1.py'
    mapping[stage.OWNER_NAME] = OWNER
    for name in (stage.WORKER_NAME, 'app_close_semantics_v5.py', 'resume_runtime_app_close_v5.py'):
        mapping['worker_sources/' + name] = OWNER.parent / name
    mapping['worker_sources/native_supermimic_bridge.py'] = PROJECT / 'source_runtime/native_supermimic_bridge.py'
    for name in ('ctx_reward_full_resume_candidate_v2.py', 'resume_runtime_contracts_v3.py', 'resume_runtime_install_hook_v4.py'):
        mapping['worker_sources/' + name] = PROJECT / 'source_resume_runtime_v2' / name
    mapping['worker_sources/command_tracking_torch_candidate_v1.py'] = PROJECT / 'source_command_review_v1/command_tracking_torch_candidate_v1.py'
    mapping['worker_sources/original_role_command_binding_candidate_v2.py'] = PROJECT / 'source_runtime/original_role_command_binding_candidate_v2.py'
    mapping['worker_sources/pose_cache_runtime_adapter_v3.py'] = HERE / 'pose_cache_runtime_adapter_v4.py'
    mapping['worker_sources/app_close_semantics_v5.py'] = PROJECT / 'source_app_close_runtime_compat_v6/app_close_semantics_v6.py'
    return mapping


def write_file(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return path


def new_folder():
    return Path(tempfile.mkdtemp(prefix='case_', dir=FIXTURES))


def synthetic_template():
    # Metadata only; teacher paths are NEVER queried. No old runtime is cloned in tests.
    return json.loads(ORIGINAL_PLAN.read_bytes())


def fake_complete_stage():
    folder = new_folder();run = 'MOD4V1_A1_RAW35_V6_SYNTHETIC_ONLY'
    root = folder / run
    contracts = stage.import_pure_gates(CONTRACTS)
    plan = stage.make_plan(synthetic_template(), root, run, contracts)
    static = write_file(folder / 'fake_static.py', b'SYNTHETIC_FAKE_STATIC = True\n')
    bank = write_file(folder / 'bank.npz', b'SYNTHETIC_NOT_NUMPY_ARCHIVE')
    def material(path): return path, stage.identity(path)
    jobs = {role: {'runtime/fake_static.py': material(static), 'runtime/bank.npz': material(bank)} for role in stage.ROLE_ORDER}
    prepared = dict(plan=plan, sources={stage.OWNER_NAME: material(OWNER)}, jobs=jobs,
        source_index={'kind': 'SYNTHETIC_FAKE_TEST_NO_NATIVE_SOURCE_BUNDLE'}, observed_static_trees={},
        template_SHA='1' * 64, source_index_SHA='2' * 64)
    receipt = stage.stage(prepared, root)
    digest = stage.sha_bytes((root / 'STAGE_COMPLETE_V6.json').read_bytes())
    parent = folder / 'SYNTHETIC_PARENT.json'
    stage.put_once(parent, dict(kind=dispatch.PARENT_KIND, run_id=run, root=str(root.resolve()),
        stage_complete_SHA=digest, owner_relative=stage.OWNER_NAME, dispatch_token='SYNTHETIC_PARENT_TOKEN_123456',
        actual_native_launch_requested=True, original_authority_gates_required=True, no_foreign_owner_signal_or_C_steal=True))
    return root, run, receipt, digest, parent


class SourceAndPlan(unittest.TestCase):
    def test_local_modules_no_torch_sdk_authority_imports(self):
        self.assertNotIn('torch', sys.modules)
        for name in ('three_slot_common_v1', 'single_writer72_authority_V85M_source', 'isaaclab', 'omni'):
            self.assertNotIn(name, sys.modules)

    def test_two_clis_default_nonexecuting(self):
        for path in (HERE / 'stage_a1_native_v6.py', HERE / 'dispatch_a1_native_v6_once.py'):
            source = path.read_text();ast.parse(source);compile(source, str(path), 'exec')
            self.assertIn("action='store_true'", source)
        self.assertNotIn('subprocess', (HERE / 'stage_a1_native_v6.py').read_text())

    def test_sealed_owner_protected_and_main_AST(self):
        stage.verify_owner_AST(OWNER)

    def test_sealed_v5_runtime_pins(self):
        mapping = actual_fourteen_sources()
        for rel in (stage.OWNER_NAME, 'worker_sources/' + stage.WORKER_NAME, 'worker_sources/app_close_semantics_v5.py', 'worker_sources/resume_runtime_app_close_v5.py'):
            self.assertEqual(stage.identity(mapping[rel])['SHA'], stage.FIXED_PINS[rel])

    def test_v5_code_seal_identity(self):
        self.assertEqual(stage.identity(OWNER.parent / 'CODE_DELIVERABLES_SHA256_V5.json')['SHA'], stage.V5_ABI_CODE_SEAL_SHA)

    def test_ALL_FIXED_PIN_LEN64(self):
        for name, pin in stage.FIXED_PINS.items():
            with self.subTest(name=name): self.assertTrue(stage.is_sha(pin), 'every golden source pin must be 64 lowercase hex')

    def test_all_fourteen_actual_sources_match_golden_pins(self):
        mapping = actual_fourteen_sources()
        self.assertEqual(len(mapping), 14);self.assertEqual(set(mapping), set(stage.FIXED_PINS))
        for name, path in mapping.items():
            # EXACT source list only. Old helper source-folder name contains budget;
            # it is not a ledger and is copied flat by the parent, never opened as C.
            with self.subTest(name=name):
                raw = path.read_bytes();self.assertEqual(stage.sha_bytes(raw), stage.FIXED_PINS[name]);self.assertGreater(len(raw), 0)

    def test_plan_original_seed_teacher_family_and_base_unchanged(self):
        original = synthetic_template();lookup = {e['role']: e for e in original['entries']}
        root = new_folder() / 'MOD4V1_A1_RAW35_V6_PLAN_TEST'
        with patch.object(Path, 'stat', side_effect=AssertionError('no model stat during metadata plan')):
            # resolve(strict=False) may stat NEW directory ancestors: isolate it to a lexical owned path.
            with patch.object(Path, 'resolve', lambda self, strict=False: self.absolute()):
                result = stage.make_plan(original, root, root.name, stage.import_pure_gates(CONTRACTS))
        self.assertEqual([e['role'] for e in result['entries']], list(stage.ROLE_ORDER))
        for e in result['entries']:
            old = lookup[e['role']]
            for field in ('seed', 'teacher', 'family', 'base_root', 'role_key'): self.assertEqual(e[field], old[field])
            self.assertEqual(e['algorithm_variant'], 'A1_RAW35_FRESH');self.assertEqual(e['algorithm_family'], stage.ALGORITHM_FAMILY)
            self.assertNotIn('resume_bptt', e);self.assertEqual(set(e['expected_fresh_producer_counts'].values()), {0})
            self.assertEqual(e['num_envs'], 1024);self.assertGreaterEqual(e['target_bptt_steps'], 3000)
        self.assertFalse(result['old_A0_counts_spliced']);self.assertFalse(result['command_tracking_fixed'])

    def test_old_consumed_run_id_rejected(self):
        template = synthetic_template()
        with self.assertRaises(ValueError): stage.make_plan(template, new_folder() / template['run_id'], template['run_id'], stage.import_pure_gates(CONTRACTS))

    def test_reduced_target_rejected(self):
        with self.assertRaises(ValueError): stage.make_plan(synthetic_template(), new_folder() / 'MOD4V1_A1_RAW35_V6_SMALL', 'MOD4V1_A1_RAW35_V6_SMALL', stage.import_pure_gates(CONTRACTS), target=2999)

    def test_wrong_role_or_H1_rejected(self):
        value = synthetic_template();value['entries'][0]['role'] = 'H1'
        with self.assertRaises(ValueError): stage.make_plan(value, new_folder() / 'MOD4V1_A1_RAW35_V6_H1', 'MOD4V1_A1_RAW35_V6_H1', stage.import_pure_gates(CONTRACTS))

    def test_fresh_descriptor_rejects_resume(self):
        value = synthetic_template();value['entries'][0]['resume_bptt'] = {'path': 'DO_NOT_OPEN.pt'}
        with self.assertRaises(ValueError): stage.make_plan(value, new_folder() / 'MOD4V1_A1_RAW35_V6_RESUME', 'MOD4V1_A1_RAW35_V6_RESUME', stage.import_pure_gates(CONTRACTS))

    def test_skip_names_before_any_entry_stat(self):
        folder = new_folder()
        class Entry:
            def __init__(self, name): self.name=name;self.path=str(folder/name)
            def is_symlink(self): raise AssertionError('denied name classified')
            def is_dir(self, **kwargs): raise AssertionError('denied name stat')
            def is_file(self, **kwargs): raise AssertionError('denied name stat')
        class Entries:
            def __enter__(self): return [Entry(n) for n in ('model.pt', 'production', 'kit', 'private', 'cache', 'ROOT_BUDGET.json', 'raw.jsonl', 'file.pyc')]
            def __exit__(self, *args): return False
        with patch.object(stage.os, 'scandir', lambda path: Entries()): self.assertEqual(stage.collect_tree(folder), [])

    def test_npz_npy_retained(self):
        folder = new_folder();write_file(folder/'world.npz', b'x');write_file(folder/'terrain.npy', b'y')
        self.assertEqual({rel for rel, _ in stage.collect_tree(folder)}, {'world.npz', 'terrain.npy'})

    def test_pure_path_guards(self):
        for path in ('../bad.py', '/absolute.py', 'a\\b.py', 'model.pt', 'production/a.py', 'ROOT_BUDGET.json', 'a/cache/b.py'):
            with self.subTest(path=path), self.assertRaises(ValueError): stage.safe_relative(path)

    def test_unsealed_index_missing_before_file_access(self):
        with self.assertRaises(ValueError): stage.source_index_files(Path('DO_NOT_OPEN'), {'sealed': False})

    def test_missing_v5_seal_rejected_before_source_stat(self):
        with self.assertRaises(ValueError): stage.source_index_files(Path('DO_NOT_OPEN'), {'kind': stage.SOURCE_INDEX_KIND, 'sealed': True, 'files': []})

    def test_missing_required_source_rejected(self):
        with self.assertRaises(ValueError): stage.source_index_files(new_folder(), {'kind': stage.SOURCE_INDEX_KIND, 'sealed': True, 'v5_abi_code_seal_SHA': stage.V5_ABI_CODE_SEAL_SHA, 'files': []})

    def test_source_pin_mismatch_rejected(self):
        folder=new_folder();write_file(folder/'fake.py', b'x=1\n')
        index=dict(kind=stage.SOURCE_INDEX_KIND,sealed=True,v5_abi_code_seal_SHA=stage.V5_ABI_CODE_SEAL_SHA,files=[dict(source_relative='fake.py',install_relative=stage.OWNER_NAME,SHA='1'*64,bytes=4)])
        with self.assertRaises(ValueError): stage.source_index_files(folder,index)


class SyntheticStageDispatch(unittest.TestCase):
    def test_fake_stage_then_all_metadata_verification_no_launch(self):
        root, run, receipt, digest, parent = fake_complete_stage()
        dispatch.verify_stage(root, run, digest);dispatch.verify_parent_marker(parent, root, run, digest)
        self.assertEqual(receipt['owner_launches'], 0);self.assertEqual(receipt['selected_PT_stat_read_copy'], 0)
        self.assertFalse((root/dispatch.CONSUMED_NAME).exists())
        self.assertTrue((root/'SCHEDULE_PUBLIC.json').exists())
        self.assertEqual(receipt['source_only_owner_preflight']['real_C_stat_read_write'],0)

    def test_stage_unused_root_exclusive(self):
        root, _, _, _, _ = fake_complete_stage()
        with self.assertRaises(ValueError): stage.stage({'plan': {'run_id': root.name}}, root)

    def test_complete_SHA_mismatch(self):
        root, run, _, _, _ = fake_complete_stage()
        with self.assertRaises(ValueError): dispatch.verify_stage(root, run, '0'*64)

    def test_installed_source_change_detected(self):
        root, run, _, digest, _ = fake_complete_stage()
        with (root/stage.OWNER_NAME).open('ab') as f: f.write(b'\n# SYNTHETIC_TAMPER\n')
        with self.assertRaises(ValueError): dispatch.verify_stage(root, run, digest)

    def test_owner_or_GO_or_production_consumed(self):
        for name in ('OWNER_STARTED.json', 'roles/E3/GO_PRODUCTION.json', 'roles/E3/TASK.json', 'roles/E3/production'):
            root,run,_,digest,_=fake_complete_stage();write_file(root/name,b'{}')
            with self.subTest(name=name),self.assertRaises(ValueError): dispatch.verify_stage(root,run,digest)

    def test_stage_error_blocks(self):
        root,run,_,digest,_=fake_complete_stage();write_file(root/'STAGE_ERROR_V6.json',b'{}')
        with self.assertRaises(ValueError):dispatch.verify_stage(root,run,digest)

    def test_parent_run_root_SHA_flags_binding(self):
        root,run,_,digest,parent=fake_complete_stage();value=json.loads(parent.read_bytes())
        for field,bad in [('run_id','WRONG'),('root','WRONG'),('stage_complete_SHA','0'*64),('actual_native_launch_requested',False),('original_authority_gates_required',False),('dispatch_token','short')]:
            changed=dict(value);changed[field]=bad;temp=new_folder()/'parent.json';stage.put_once(temp,changed)
            with self.subTest(field=field),self.assertRaises(ValueError):dispatch.verify_parent_marker(temp,root,run,digest)

    def test_mock_only_one_Popen_and_consumed_marker(self):
        root,run,_,digest,parent=fake_complete_stage()
        class FakeProcess: pid=123456789
        with patch.object(dispatch.sys,'platform','linux'), patch.object(dispatch.subprocess,'Popen',return_value=FakeProcess()) as popen, patch.object(dispatch,'child_identity_metadata',return_value={'pid':123456789,'SYNTHETIC':True}):
            result=dispatch.dispatch_once(root,run,digest,parent,Path(sys.executable))
            self.assertEqual(popen.call_count,1);self.assertEqual(result['actual_Popen_calls'],1)
            self.assertEqual(popen.call_args.args[0][-1],str(root/stage.OWNER_NAME))
            with self.assertRaises(ValueError):dispatch.dispatch_once(root,run,digest,parent,Path(sys.executable))
            self.assertEqual(popen.call_count,1)
        self.assertTrue((root/dispatch.CONSUMED_NAME).exists())

    def test_mock_Popen_failure_preserves_purpose_no_retry(self):
        root,run,_,digest,parent=fake_complete_stage()
        with patch.object(dispatch.sys,'platform','linux'),patch.object(dispatch.subprocess,'Popen',side_effect=OSError('SYNTHETIC_POPEN_FAILURE')):
            with self.assertRaises(OSError):dispatch.dispatch_once(root,run,digest,parent,Path(sys.executable))
        self.assertTrue((root/dispatch.CONSUMED_NAME).exists());self.assertTrue((root/'OWNER_DISPATCH_ERROR_V6.json').exists())
        with self.assertRaises(ValueError):dispatch.verify_stage(root,run,digest)

    def test_copy_source_mutation_detected(self):
        folder=new_folder();source=write_file(folder/'a.py',b'x=1\n');info=stage.identity(source);source.write_bytes(b'x=2\n')
        with self.assertRaises(ValueError):stage.copy_materials(folder/'dest',{'a.py':(source,info)})



class V6SourceCompatibility(unittest.TestCase):
    def test_only_two_actual_source_pins_changed(self):
        prior = PROJECT / 'source_stage_a1_native_v5' / 'stage_a1_native_v5.py'
        namespace = {}
        tree = ast.parse(prior.read_text())
        selected = [n for n in tree.body if isinstance(n, ast.Assign)]
        exec(compile(ast.Module(body=selected, type_ignores=[]), str(prior) + ':CONSTANTS_ONLY', 'exec'), namespace)
        changed = {key for key in stage.FIXED_PINS if stage.FIXED_PINS[key] != namespace['FIXED_PINS'][key]}
        self.assertEqual(changed, {'worker_sources/pose_cache_runtime_adapter_v3.py', 'worker_sources/app_close_semantics_v5.py'})
        self.assertEqual(len(stage.FIXED_PINS), 14)

    def test_logical_old_ABI_has_explicit_new_source_bytes(self):
        mapping = actual_fourteen_sources()
        self.assertEqual(mapping['worker_sources/pose_cache_runtime_adapter_v3.py'].name, 'pose_cache_runtime_adapter_v4.py')
        self.assertIn('v6', mapping['worker_sources/app_close_semantics_v5.py'].parent.name.lower())
        self.assertEqual(stage.POSE_BYTES, 18161)
        self.assertNotEqual(stage.POSE_SHA, '73145a1caa7819e0938e66e53a1bb0be73e48d0d06c3cf9cd5dc76e9f0862209')

    def test_old_V5_run_prefix_is_not_a_new_V6_purpose(self):
        run = 'MOD4V1_A1_RAW35_V5_NOT_REPLAYED'
        with self.assertRaises(ValueError):
            stage.make_plan(synthetic_template(), new_folder() / run, run, stage.import_pure_gates(CONTRACTS))

    def test_old_V5_parent_kind_is_not_a_new_V6_dispatch(self):
        root, run, _, sha, parent = fake_complete_stage()
        value = json.loads(parent.read_bytes());value['kind'] = 'PARENT_APPROVED_NEW_A1_NATIVE_V5_DISPATCH_ONCE'
        path = new_folder() / 'OLD_KIND_ONLY.json';stage.put_once(path, value)
        with self.assertRaises(ValueError): dispatch.verify_parent_marker(path, root, run, sha)

    def test_old_V5_index_kind_fails_before_source_access(self):
        value = {'kind': 'SEALED_A1_NATIVE_V5_SOURCE_INDEX_V1', 'sealed': True, 'v5_abi_code_seal_SHA': stage.V5_ABI_CODE_SEAL_SHA, 'files': []}
        with self.assertRaises(ValueError): stage.source_index_files(Path('DO_NOT_OPEN'), value)

    def test_V6_names_and_original_owner_are_separate(self):
        self.assertEqual(stage.OWNER_NAME, 'supermimic_original_owner_shared_app_close_candidate_v5.py')
        self.assertEqual(stage.WORKER_NAME, 'worker_supermimic_bptt_app_close_candidate_v5.py')
        self.assertIn('V6', stage.ROOT_MANIFEST_NAME)
        self.assertEqual(dispatch.CONSUMED_NAME, 'PARENT_DISPATCH_CONSUMED_V6.json')
        self.assertEqual(stage.SOURCE_INDEX_KIND, 'SEALED_A1_NATIVE_V6_SOURCE_INDEX_V1')

    def test_static_and_original_resource_gate_helpers_AST_unchanged(self):
        old = ast.parse((PROJECT / 'source_stage_a1_native_v5/stage_a1_native_v5.py').read_text())
        new = ast.parse((HERE / 'stage_a1_native_v6.py').read_text())
        def functions(tree): return {n.name: ast.dump(n, include_attributes=False) for n in tree.body if isinstance(n, ast.FunctionDef)}
        a, b = functions(old), functions(new)
        for name in ('require', 'sha_bytes', 'is_sha', 'denied_name', 'safe_relative', 'identity', 'read_metadata', 'put_once', 'write_bytes_once', 'collect_tree', 'verify_owner_AST', 'import_pure_gates', 'copy_materials', 'source_only_owner_verify'):
            self.assertEqual(a[name], b[name], name)

    def test_new_plan_still_exact_A1_legacy_no_skill_offset_or_reward_change(self):
        run = 'MOD4V1_A1_RAW35_V6_PLAN_SNAPSHOT'
        plan = stage.make_plan(synthetic_template(), new_folder() / run, run, stage.import_pure_gates(CONTRACTS))
        self.assertEqual(plan['bound_anchor_reward_changes'], 0)
        self.assertFalse(plan['command_tracking_fixed']);self.assertFalse(plan['sensor_projection_exact'])
        self.assertFalse(plan['old_A0_counts_spliced']);self.assertEqual(plan['native_counter_start'], 0)
        self.assertEqual(plan['original_authority_limits_unchanged'], dict(parent_seconds=3900, save_seconds=3600, exit_headroom_seconds=300, resource_wait_seconds=1800))
        for entry in plan['entries']:
            self.assertEqual(entry['pose_cache_runtime_adapter']['SHA'], stage.POSE_SHA)
            self.assertEqual(entry['pose_cache_runtime_adapter']['bytes'], 18161)
            self.assertNotIn('resume_bptt', entry)


def main():
    global FIXTURES
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    FIXTURES=Path(tempfile.mkdtemp(prefix='SYNTHETIC_STAGE_DISPATCH_CASES_',dir=HERE))
    started=time.perf_counter();suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]);result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt=dict(kind='STDLIB_AST_SYNTHETIC_FILES_AND_MOCK_POPEN_NOT_REAL_STAGE_OR_NATIVE',passed=result.wasSuccessful(),tests_run=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),seconds=time.perf_counter()-started,synthetic_fixture_root=str(FIXTURES),
        real_stage_calls=0,real_owner_Popen=0,real_C_lock_model_SDK_GPU_Git_SSH_operations=0,Torch_imported='torch'in sys.modules,
        files=[dict(relative=p.name,**stage.identity(p))for p in(HERE/'stage_a1_native_v6.py',HERE/'dispatch_a1_native_v6_once.py')],
        notes='stage() runs ONLY artificial non-native fixture trees; Popen always mocked; no authority/owner import; original plan read as metadata only')
    stage.put_once(args.output,receipt)
    if not result.wasSuccessful():raise SystemExit(1)


if __name__=='__main__':main()
