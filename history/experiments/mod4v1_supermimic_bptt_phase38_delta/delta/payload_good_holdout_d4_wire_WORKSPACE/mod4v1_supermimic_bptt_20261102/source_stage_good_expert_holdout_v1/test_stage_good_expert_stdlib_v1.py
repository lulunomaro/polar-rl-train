"""SOURCE/fake/whole-module/AST tests only: stage() and CLI --stage are NEVER called.
Real sealed twenty Python/JSON pins and producer source pins are retained. Synthetic
owner/FINAL/asset descriptors are not actual wait/admission/asset-integrity proof.
Only deliberately created marker NPZ/NPY below this test's owned temp are read.
"""
from pathlib import Path
import ast
import builtins
import copy
import hashlib
import importlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
R=HERE.parent
SEALED=R/'source_good_expert_holdout_subset_v1'
OLD=R/'source_frozen_embedded_teacher_native_v1/stage_embedded_teacher_native_v1.py'
INDEX_PATH=SEALED/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json'
INDEX=json.loads(INDEX_PATH.read_bytes())
ROOT=None
AUDIT=dict(model_stat_lstat_open=0,native_imports=0,process_network_lock=0,fake_static_marker_opens=0)
MODEL={'.pt','.pth','.ckpt','.safetensors','.onnx','.pt2','.pkl','.pickle','.lock'}


def forbidden_path(path):
    if isinstance(path,int):return False
    p=Path(os.fsdecode(path))
    return p.suffix.lower() in MODEL or 'budget' in p.name.lower()


def audit(event,args):
    if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
        path=Path(os.fsdecode(args[0]))
        if forbidden_path(path):
            AUDIT['model_stat_lstat_open']+=1;raise AssertionError('SOURCE model/budget/lock open')
        if path.suffix.lower() in ('.npz','.npy','.raw'):
            if ROOT is None or not path.is_relative_to(ROOT) or 'FAKE_STATIC_MARKER' not in path.name:
                AUDIT['model_stat_lstat_open']+=1;raise AssertionError('real raw/static bank is outside this SOURCE test')
            AUDIT['fake_static_marker_opens']+=1
    if event=='import' and args and str(args[0]).split('.')[0] in ('torch','numpy','isaacsim','isaaclab','omni','warp','pxr','rsl_rl','tensordict'):
        AUDIT['native_imports']+=1;raise AssertionError('native import in SOURCE test')
    if event in ('subprocess.Popen','os.system','socket.connect','fcntl.flock'):
        AUDIT['process_network_lock']+=1;raise AssertionError('SOURCE process/network/lock operation')

sys.addaudithook(audit)
REAL_STAT,REAL_LSTAT=os.stat,os.lstat

def stat_guard(function):
    def guarded(path,*args,**kwargs):
        if forbidden_path(path):
            AUDIT['model_stat_lstat_open']+=1;raise AssertionError('SOURCE model/budget/lock stat/lstat')
        return function(path,*args,**kwargs)
    return guarded

os.stat,os.lstat=stat_guard(REAL_STAT),stat_guard(REAL_LSTAT)


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():path.read_bytes()
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def SHA(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def functions(path):
    return {n.name:n for n in ast.parse(path.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}


def AST(node):return ast.dump(node,include_attributes=False)


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global ROOT
        cls.temp=tempfile.TemporaryDirectory(prefix='FAKE_MATERIALIZER_SOURCE_NOT_STAGE_',dir=HERE)
        cls.root=Path(cls.temp.name).resolve();ROOT=cls.root
        assert cls.root.is_relative_to(HERE) and cls.root.name.startswith('FAKE_MATERIALIZER_SOURCE_NOT_STAGE_')
        cls.s=load(HERE/'stage_good_expert_holdout_v1.py','_new_holdout_source_cli_test')
        cls.flat=cls.root/'flat20';cls.flat.mkdir()
        cls.view=cls.root/'complete_real_metadata_imports';cls.view.mkdir()
        for row in INDEX['overlay_entries']:
            source=Path(row['path']);raw=source.read_bytes()
            assert (len(raw),hashlib.sha256(raw).hexdigest())==(row['bytes'],row['SHA256'])
            (cls.flat/source.name).write_bytes(raw)
            target=cls.view/row['relative'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        cls.original_paths={row['path']:(row['bytes'],row['SHA256']) for row in INDEX['overlay_entries']+INDEX['inherited_original_worker_source_entries']+INDEX['provenance']}
        cls.old_path=sys.path[:];sys.path[:0]=[str(cls.view),str(cls.view/'worker_sources/e1')]
        cls.runtime=importlib.import_module('good_expert_holdout_runtime_v1')
        cls.identities=copy.deepcopy(cls.runtime.BASELINE_IDENTITIES)
        cls.worker=R/'source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py'
        cls.bridge=cls.flat/'native_supermimic_bridge.py'
        assert (cls.worker.stat().st_size,SHA(cls.worker))==cls.runtime._guard.WORKER_PIN
        assert (cls.bridge.stat().st_size,SHA(cls.bridge))==cls.runtime._guard.BRIDGE_PIN
        cls.modules_before={name:sys.modules.get(name) for name in ('good_expert_holdout_runtime_v1','a1_frozen_eval_runtime_v2')}
    @classmethod
    def tearDownClass(cls):
        sys.path[:]=cls.old_path
        assert cls.root.resolve()==Path(cls.temp.name).resolve() and cls.root.is_relative_to(HERE)
        cls.temp.cleanup()
    def setUp(self):
        self.case=self.root/self._testMethodName;self.case.mkdir()
        self.native=self.case/self.s.NATIVE_RUN_ID
        self.fake_paths={}
    def producer(self,role):
        s=self.s;job=self.native/'roles'/role;key=role.lower();base=self.identities[role]
        cp=job/'production/checkpoints/FAKE_NEVER_CREATED_complete.pt';self.fake_paths[role]=str(cp)
        teacher=dict(source_path=base['mother_source_path'],source_SHA=base['mother_source_SHA'],source_bytes=base['mother_source_bytes'],teacher_frozen=True)
        counts=dict.fromkeys(s.COUNTS,0)
        checkpoint=dict(path=str(cp),bytes=base['source_bytes'],SHA=base['source_SHA'],iteration=0,counts=counts,
            full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True,teacher_unchanged=True,teacher_source=teacher)
        final=dict(kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3',passed_execution=True,teacher_unchanged=True,
            role=role,role_key=key,run_id=s.NATIVE_RUN_ID,actor_view='raw35_legacy_held_aux_v1',algorithm_family='a1_raw35_legacy_v1',
            algorithm_variant='A1_RAW35_FRESH',actual_BPTT_policy_steps=0,counts=counts,checkpoint=checkpoint,teacher=teacher)
        fp=job/'production/FINAL.json';put(fp,final)
        files=[]
        for rel,source in ((self.runtime._guard.WORKER_REL,self.worker),(self.runtime._guard.BRIDGE_REL,self.bridge)):
            target=job/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
            files.append(dict(relative=rel,bytes=target.stat().st_size,SHA=SHA(target)))
        put(job/'INSTALL_MANIFEST.json',dict(files=files))
        put(job/'TASK.json',dict(role=role,role_key=key,run_id=s.NATIVE_RUN_ID,teacher_path=teacher['source_path'],teacher_SHA=teacher['source_SHA'],teacher_bytes=teacher['source_bytes'],manifest_SHA=SHA(job/'INSTALL_MANIFEST.json')))
        semantic=dict(kind='ACTUAL_WAIT_APP_CLOSE_SEMANTIC_RESULT_V5',passed_execution=True,original_error=False,actual_wait_returned=True,
            returncode=0,reasons=[],error_sidefiles=[],final=final)
        row=dict(key=key,role=role,phase='terminal',terminal_all_own_children_waited=True,returncode=0,original_error=False,semantic_result=semantic,final=final)
        put(job/'PARENT_WAITED_ACTUAL.json',row)
        return dict(role=role,role_key=key,job_root=str(job)),row
    def boundary(self):
        entries=[];rows={};go={}
        for role in self.s.ROLES:
            if role in self.s.REQUESTED:
                entry,row=self.producer(role);rows[entry['role_key']]=row
                go[entry['role_key']]=dict(role=role,role_key=entry['role_key'],run_id=self.s.NATIVE_RUN_ID)
            else:entry=dict(role=role,role_key=role.lower(),job_root=str(self.native/'roles'/role))
            entries.append(entry)
        put(self.native/'OWNER_PLAN.json',dict(run_id=self.s.NATIVE_RUN_ID,entries=entries))
        put(self.native/'OWNER_EXIT_ACTUAL.json',dict(run_id=self.s.NATIVE_RUN_ID,all_own_children_waited=True,original_cost_settled=True,original_leases_released=True,errors=[],H1_excluded=True))
        put(self.native/'COHORT_FINAL.json',dict(run_id=self.s.NATIVE_RUN_ID,all_own_children_waited=True,original_cost_settled=True,errors=[],H1_excluded=True,rows=rows,go=go,pending_unstarted_roles=[]))
        return self.s.native_boundary(self.native)
    def prepared(self,seed):
        s=self.s;producers,boundary=self.boundary()
        sources,index_receipt,_=s.source_mappings(self.flat,INDEX_PATH)
        rows=[]
        for role in s.ROLES:
            row=dict(role=role,controls=s.CONTROLS[role],status='deferred_not_constructed')
            if role in s.REQUESTED:
                producer=producers[role];teacher=producer['FINAL']['teacher'];cp=producer['FINAL']['checkpoint']
                row.update(worker=self.runtime.WORKER_ALIASES[role],a1_producer=producer,seed=seed,num_envs=80,
                    policy_variant=self.runtime.POLICY_VARIANT,actor_semantics='EMBEDDED_ORIGINAL_TEACHER_MEAN',
                    actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE',original_bootstrap_teacher=teacher,
                    source_path=cp['path'],source_SHA=cp['SHA'],source_bytes=cp['bytes'])
                row['producer_teacher_freeze_evidence']=self.runtime._guard.derive_producer_guard(producer)
            rows.append(row)
        plan=dict(kind=self.runtime.PLAN_KIND,seed=seed,batch_purpose=self.runtime.purpose_for(seed),policy_variant=self.runtime.POLICY_VARIANT,
            enabled=False,staged=False,source_native_enabled=False,dispatched=False,group_id='FAKE_NOT_STAGE_SEED'+str(seed),GPU_UUID='GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
            asset_SHA=s.USD,contract_SHA=s.CONTRACT,holdout_protocol=self.runtime.holdout_protocol(seed),paired_reset_protocol=s.paired_plan(seed),
            requested_roles=list(s.REQUESTED),deferred_roles=[r for r in s.ROLES if r not in s.REQUESTED],roles=rows,
            overall_eight_pass_rate=None,comparison=None,worker_files=[dict(relative=rel,**info) for rel,(_,info) in sources.items()])
        return dict(plan=plan,materials=sources,new_root=self.case/plan['group_id'],source_index=index_receipt,boundary=boundary,
            native_vendor=dict(fixture='NOT_ASSET_OR_VENDOR7_INTEGRITY_PROOF'),selected_runtime_trees={},original_plan_SHA='f'*64)
    def checked_import(self,name,*args,**kwargs):
        module=self.real_import(name,*args,**kwargs)
        if name=='good_expert_holdout_runtime_v1':
            # Only fixture own-job containment paths are substituted IN MEMORY.
            # File bytes/SHA, actual mother identity, full cache source and guard stay exact.
            for role,cp in self.fake_paths.items():module.BASELINE_IDENTITIES[role]['source_path']=cp
        return module
    def validate(self,prepared):
        self.real_import=importlib.import_module
        with patch.object(importlib,'import_module',side_effect=self.checked_import):return self.s.metadata_validate(prepared)
    def test_01_exact_real_twenty_flat_PINs_and_aliases(self):
        sources,receipt,_=self.s.source_mappings(self.flat,INDEX_PATH)
        self.assertEqual(len(sources),20);self.assertTrue(receipt['provenance_paths_not_dereferenced'])
        self.assertEqual(sources['a1_frozen_eval_runtime_v2.py'][1]['SHA'],'7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e')
        self.assertIn('resume_runtime_contracts_v3.py',sources)
    def test_02_pin_corruption_rejected_before_any_module_execution(self):
        path=self.flat/'good_expert_holdout_runtime_v1.py';original=path.read_bytes()
        try:
            path.write_bytes(original+b'\n# FAKE_CORRUPTION_TEST\n')
            with self.assertRaisesRegex(ValueError,'pinned source differs'):self.s.source_mappings(self.flat,INDEX_PATH)
        finally:path.write_bytes(original)
    def test_03_synthetic_closed_native_boundary_and_actual_guard_sources(self):
        producers,boundary=self.boundary();self.assertEqual(set(producers),set(self.s.REQUESTED))
        self.assertFalse(boundary['actual_canonical_ledger_read_or_written'])
        for producer in producers.values():
            guard=self.runtime._guard.derive_producer_guard(producer);self.assertTrue(guard['parent_verified_actual_staged_source'])
    def test_04_native_boundary_requires_exact_original_actual_wait(self):
        self.boundary();path=self.native/'OWNER_EXIT_ACTUAL.json';value=json.loads(path.read_bytes());value['all_own_children_waited']=False;put(path,value)
        with self.assertRaisesRegex(ValueError,'boundary not closed'):self.s.native_boundary(self.native)
    def test_05_final_mismatch_rejected_without_checkpoint_stat(self):
        self.boundary();path=self.native/'roles/CURB_PROTECTED878/production/FINAL.json';value=json.loads(path.read_bytes());value['counts']['wm_optimizer_steps']=1;put(path,value)
        with self.assertRaises(ValueError):self.s.native_boundary(self.native)
    def test_06_whole_real_safe_import_closure_and_tasks_seed20260929(self):
        prepared=self.prepared(20260929);receipt=self.validate(prepared)
        self.assertTrue(receipt['passed']);self.assertEqual(receipt['seed'],20260929)
        self.assertTrue(receipt['full_modules_not_AST_cropped_or_stubbed']);self.assertEqual(len(receipt['task_checks']),2)
        self.assertTrue(receipt['dependency_completeness']['helper_base_is_actual_imported_contracts'])
        self.assertFalse(prepared['new_root'].exists());self.assertEqual(receipt['parent_launches'],0)
    def test_07_second_seed_is_distinct_purpose_no_old_seed_alias(self):
        prepared=self.prepared(20260930);receipt=self.validate(prepared)
        self.assertEqual(receipt['purpose'],'GOOD_EXPERT_HOLDOUT_C878_S135_SEED20260930_V1')
        self.assertTrue(receipt['historical_seed_rejected']);self.assertTrue(all(r['cross_seed_pose_rejected'] for r in receipt['task_checks']))
    def test_08_missing_critical_Base_is_real_import_failure_not_stubbed(self):
        prepared=self.prepared(20260929);prepared['materials']=dict(prepared['materials']);prepared['materials'].pop('resume_runtime_contracts_v3.py')
        with self.assertRaises((ValueError,FileNotFoundError,ImportError)):self.validate(prepared)
    def test_09_bad_producer_source_guard_fails_real_full_import_validator(self):
        prepared=self.prepared(20260929);entry=next(r for r in prepared['plan']['roles'] if r['role']=='CURB_PROTECTED878')
        entry['producer_teacher_freeze_evidence']={'verified':True}
        with self.assertRaises(ValueError):self.validate(prepared)
    def test_10_original_helper_AST_allowlist_and_separate_native_layer(self):
        before,after=functions(OLD),functions(HERE/'stage_good_expert_holdout_v1.py')
        changed={name for name in before if name in after and AST(before[name])!=AST(after[name])}
        self.assertEqual(changed,{'source_mappings','paired_plan','prepare','metadata_validate','preflight_summary','stage','main'})
        self.assertEqual(set(before),set(after))
        for name in set(before)-changed:self.assertEqual(AST(before[name]),AST(after[name]),name)
        text=(HERE/'stage_good_expert_holdout_v1.py').read_text(encoding='utf-8')
        self.assertNotIn('subprocess',text);self.assertNotIn('Popen',text)
    def test_11_complete_tree_preserves_fake_NPZ_NPY_and_nonpython_deps(self):
        bank=self.case/'original_static_tree';bank.mkdir()
        for name in ('FAKE_STATIC_MARKER_bank.npz','FAKE_STATIC_MARKER_points.npy','asset.usd','native_extension.so','descriptor.txt'):
            (bank/name).write_bytes(('FAKE_STATIC_MARKER_NOT_REAL_RAW:'+name).encode())
        result=self.s.tree(bank)
        self.assertEqual(set(result),{'FAKE_STATIC_MARKER_bank.npz','FAKE_STATIC_MARKER_points.npy','asset.usd','native_extension.so','descriptor.txt'})
        self.assertEqual(result['FAKE_STATIC_MARKER_bank.npz'][1]['bytes'],(bank/'FAKE_STATIC_MARKER_bank.npz').stat().st_size)
    def test_12_denied_model_name_is_skipped_before_DirEntry_stat(self):
        directory=self.case/'model_skip';directory.mkdir()
        class Poison:
            name='NEVER_STAT_OR_OPEN.pt'
            def __getattr__(self,key):raise AssertionError('denied DirEntry classified: '+key)
        class Entries:
            def __enter__(self):return iter([Poison()])
            def __exit__(self,*args):pass
        with patch.object(self.s.os,'scandir',return_value=Entries()):self.assertEqual(self.s.tree(directory),{})
    def test_13_static_symlink_and_escape_guards(self):
        for rel in ('../escape','a/../b','/absolute','C:/bad','a\\b'):
            with self.assertRaises(ValueError):self.s.safe_relative(rel)
        for name in ('checkpoints','production','x.pt','x.lock','GO_PRODUCTION.json','RAW_actual.npz'):self.assertTrue(self.s.denied(name))
        self.assertFalse(self.s.denied('FAKE_STATIC_MARKER_original.npz'))
    def test_14_prepare_binds_only_two_runtime_trees_complete_sources_and_vendor7_AST(self):
        function=functions(HERE/'stage_good_expert_holdout_v1.py')['prepare'];text=ast.unparse(function)
        self.assertIn('if role in REQUESTED:',text);self.assertIn('files = tree(old_runtime)',text)
        self.assertIn("materials['runtimes/' + role + '/' + rel] = value",text)
        self.assertIn('observed[\'files\']',text);self.assertIn('VENDOR_PIN',text)
        self.assertIn("plan['worker_files']",text);self.assertIn('inherited_original_worker_source_entries',text)
        self.assertIn('holdout_protocol=dict(',text);self.assertIn('seed=seed',text)
    def test_15_newroot_and_seed_rejection_happens_before_real_inputs(self):
        root=self.case/'EXISTS_SEED20260929';root.mkdir()
        with self.assertRaisesRegex(ValueError,'absent one-use'):
            self.s.prepare('NOT_READ','NOT_READ','NOT_READ','NOT_READ',root,root.name,'GPU-aaaaaaaa',20260929)
        with self.assertRaisesRegex(ValueError,'holdout seed'):
            self.s.prepare('NOT_READ','NOT_READ','NOT_READ','NOT_READ',self.case/'absent','absent','GPU-aaaaaaaa',20260928)
    def test_16_preflight_summary_creates_no_input_or_newroot(self):
        prepared=self.prepared(20260929);prepared['metadata_validation']=self.validate(prepared)
        before={str(path):SHA(path) for path in self.case.rglob('*.json')}
        receipt=self.s.preflight_summary(prepared)
        self.assertFalse(receipt['staged']);self.assertFalse(receipt['source_native_enabled']);self.assertFalse(receipt['new_root_created'])
        self.assertFalse(prepared['new_root'].exists())
        self.assertEqual(before,{str(path):SHA(path) for path in self.case.rglob('*.json')})
    def test_17_stage_not_executed_streaming_full_materials_receipt_and_false_gates_AST(self):
        node=functions(HERE/'stage_good_expert_holdout_v1.py')['stage'];text=ast.unparse(node)
        self.assertIn("sorted(prepared['materials'].items())",text)
        self.assertIn("source.open('rb')",text);self.assertIn('1024 * 1024',text)
        self.assertIn('source_native_enabled=False, staged=False, dispatched=False',text)
        self.assertIn('COMPLETE_NAME',text);self.assertIn('root_consumed_no_same_root_retry=True',text)
        self.assertEqual(self.s.COMPLETE_NAME,'STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json')
    def test_18_all_indexed_originals_and_sealed_V1_bytes_unchanged(self):
        for source,(size,sha) in self.original_paths.items():
            raw=Path(source).read_bytes();self.assertEqual((len(raw),hashlib.sha256(raw).hexdigest()),(size,sha),source)
        seal=json.loads((SEALED/'GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json').read_bytes())
        self.assertEqual(seal['root_SHA256'],'032c431b844aedc02bffad76549b9516f92e5cfd06cce6194e47d5f4451c7534')


def main():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceTests))
    report=dict(kind='SOURCE_FAKE_REAL_PIN_AST_MATERIALIZER_TESTS_NOT_STAGE_V1',passed=result.wasSuccessful(),tests_run=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),audit=AUDIT,
        source_native_enabled=False,staged=False,dispatched=False,stage_function_calls=0,CLI_stage_calls=0,
        actual_inputs_preflighted=False,real_asset_vendor7_integrity_not_tested=True,
        fake_metadata_not_actual_wait_admission_or_quality_proof=True)
    put(HERE/'TEST_REPORT_STAGE_GOOD_EXPERT_V1.json',report)
    print(json.dumps(report,sort_keys=True));raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__=='__main__':main()
