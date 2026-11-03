"""NEW SOURCE tests, not a replay of old18. No prepare/preflight/stage/main is called.
Actual fixed27 JSON +25 real text-source pins; fake asset/vendor/runtime markers are NOT real static-input proof.
Unmodified whole metadata_validate and overlay schema are exercised with synthetic producer descriptors only.
"""
from pathlib import Path
import ast
import builtins
import copy
import hashlib
import importlib
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent;R=HERE.parent;WORKSPACE=R.parent
tempfile.tempdir=str(HERE)  # Normal stdlib scratch routing, keep all SOURCE writes inside NEW.
sys.dont_write_bytecode=True
T=WORKSPACE/'mod4v1_experts_fulldr_rm70_20261101'
INDEX_PATH=R/'source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json'
PLAN_PATH=T/'reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json'
SEALED=[(R/'source_stage_good_expert_holdout_v1','SOURCE_STAGE_GOOD_EXPERT_SEAL_V1.json'),
        (R/'source_good_expert_holdout_subset_v1','GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json')]
INDEX=json.loads(INDEX_PATH.read_bytes());PLAN=json.loads(PLAN_PATH.read_bytes())
ROOT=None
AUDIT=dict(model_stat_lstat_open=0,real_raw_opens=0,native_imports=0,process_network_lock=0,escaped_writes=0)
MODEL={'.pt','.pth','.ckpt','.safetensors','.onnx','.pt2','.pkl','.pickle','.lock'}
NATIVE={'torch','numpy','isaacsim','isaaclab','omni','warp','pxr','rsl_rl','tensordict','psutil','fcntl'}


def forbidden(path):
    if isinstance(path,int):return False
    p=Path(os.fsdecode(path));return p.suffix.lower() in MODEL or 'budget' in p.name.lower()


def audit(event,args):
    if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
        p=Path(os.fsdecode(args[0]))
        if forbidden(p):AUDIT['model_stat_lstat_open']+=1;raise AssertionError('SOURCE model/C/lock open')
        if p.suffix.lower() in ('.npz','.npy','.raw'):
            AUDIT['real_raw_opens']+=1;raise AssertionError('raw/static data is outside this SOURCE test')
        mode=args[1] if len(args)>1 else None;flags=args[2] if len(args)>2 else 0
        writes=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT)))
        if writes and not p.is_relative_to(HERE):AUDIT['escaped_writes']+=1;raise AssertionError('SOURCE write escaped NEW folder')
    if event=='import' and args and str(args[0]).split('.')[0] in NATIVE:
        AUDIT['native_imports']+=1;raise AssertionError('native import in SOURCE test')
    if event in ('subprocess.Popen','os.system','socket.connect','fcntl.flock'):
        AUDIT['process_network_lock']+=1;raise AssertionError('SOURCE process/network/lock operation')

sys.addaudithook(audit)
REAL_STAT,REAL_LSTAT=os.stat,os.lstat

def guarded_stat(fn):
    def call(path,*aa,**kw):
        if forbidden(path):AUDIT['model_stat_lstat_open']+=1;raise AssertionError('SOURCE model/C/lock stat')
        return fn(path,*aa,**kw)
    return call
os.stat,os.lstat=guarded_stat(REAL_STAT),guarded_stat(REAL_LSTAT)


def H(raw):return hashlib.sha256(raw).hexdigest()
def source_path(value):
    text=str(value).replace('\\','/');prefix='F:/RMPOLAR-RL/'
    assert text.startswith(prefix),'unknown original SOURCE provenance root'
    parts=text[len(prefix):].split('/')
    assert all(p not in ('','.','..') for p in parts) and parts[0] in (R.name,T.name)
    return WORKSPACE.joinpath(*parts)
def identity(path):
    raw=path.read_bytes();return dict(bytes=len(raw),SHA=H(raw))
def write(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():path.read_bytes()
    path.write_bytes(raw)
def put(path,value):write(path,(json.dumps(value,indent=2,allow_nan=False)+'\n').encode())
def funcs(path):return {n.name:n for n in ast.parse(path.read_bytes()).body if isinstance(n,ast.FunctionDef)}
def AST(node):return ast.dump(node,include_attributes=False)
def sealed_snapshot():
    output={}
    for folder,name in SEALED:
        seal=json.loads((folder/name).read_bytes());output[str(folder/name)]=H((folder/name).read_bytes())
        for row in seal['files']:
            path=folder/row['name'];raw=path.read_bytes();assert (len(raw),H(raw))==(row['bytes'],row['SHA256'])
            output[str(path)]=H(raw)
    for row in INDEX['overlay_entries']+INDEX['inherited_original_worker_source_entries']+INDEX['provenance']:
        raw=source_path(row['path']).read_bytes();assert (len(raw),H(raw))==(row['bytes'],row['SHA256'])
        output[row['path']]=H(raw)
    return output


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global ROOT
        cls.before=sealed_snapshot()
        cls.temp=tempfile.TemporaryDirectory(prefix='SOURCE_ONLY_V2_NOT_STAGE_',dir=HERE)
        cls.root=Path(cls.temp.name).resolve();ROOT=cls.root
        spec=importlib.util.spec_from_file_location('_good_holdout_source_v2',HERE/'stage_good_expert_holdout_v2.py')
        cls.s=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.s)
        cls.flat=cls.root/'flat20';cls.view=cls.root/'safe_whole_modules'
        for row in INDEX['overlay_entries']:
            raw=source_path(row['path']).read_bytes();write(cls.flat/source_path(row['path']).name,raw);write(cls.view/row['relative'],raw)
        cls.path_before=sys.path[:];cls.modules_before=dict(sys.modules)
        sys.path[:0]=[str(cls.view),str(cls.view/'worker_sources/e1')]
        cls.runtime=importlib.import_module('good_expert_holdout_runtime_v1')
        cls.identities=copy.deepcopy(cls.runtime.BASELINE_IDENTITIES)
        cls.sources,_,_=cls.s.source_mappings(cls.flat,INDEX_PATH)
        cls.worker=R/'source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py'
        assert (cls.worker.stat().st_size,H(cls.worker.read_bytes()))==cls.runtime._guard.WORKER_PIN
    @classmethod
    def tearDownClass(cls):
        assert sealed_snapshot()==cls.before,'old seals/source changed'
        sys.path[:]=cls.path_before
        for name in list(sys.modules):
            if name not in cls.modules_before and (name.startswith('_') or name.startswith(('good_expert','a1_frozen','producer_teacher','embedded_teacher','frozen_a1','pose_cache','app_close','resume_runtime','e1_'))):sys.modules.pop(name,None)
        assert cls.root.is_relative_to(HERE) and cls.root.name.startswith('SOURCE_ONLY_V2_NOT_STAGE_')
        cls.temp.cleanup()
    def setUp(self):
        self.case=self.root/self._testMethodName;self.case.mkdir();self.fake_paths={}
    def fixture(self,*,supervisor_collision=False):
        s=self.s;originals={};required={}
        for row in INDEX['inherited_original_worker_source_entries']:
            path=source_path(row['path']);info=identity(path);originals[row['relative']]=(path,info);required[row['relative']]=(info['bytes'],info['SHA'])
        path=T/'NINE_N80_PARALLEL_SOURCE_V8/single_gpu_group_supervisor.py';info=identity(path)
        originals['single_gpu_group_supervisor.py']=(path,info);required['single_gpu_group_supervisor.py']=(info['bytes'],info['SHA'])
        markers={'pinned_assets/FAKE_ASSET.txt':b'FAKE SOURCE MARKER, NOT ORIGINAL ASSET\n'}
        for role in s.REQUESTED:markers['runtimes/'+role+'/FAKE_COMPLETE_BANK_REFERENCE.txt']=b'FAKE, NOT REAL ORIGINAL STATIC TREE\n'
        for name in ('__init__.py','learner.py','networks.py','geometry.py','replay.py','contract.py','FAKE_seventh.py'):
            alias='supermimic_vendor_v2/'+name
            if alias in self.sources:originals[alias]=self.sources[alias]
            else:markers[alias]=b'"""FAKE VENDOR MARKER, NOT ORIGINAL VENDOR7 PROOF."""\n'
        for rel,raw in markers.items():
            path=self.case/'fake_originals'/rel;write(path,raw);originals[rel]=(path,identity(path))
        sources=dict(self.sources)
        if supervisor_collision:
            path=self.case/'FAKE_ACTIVE_NEW_SUPERVISOR.py';write(path,b'"""FAKE active supervisor, never executed."""\n')
            sources['single_gpu_group_supervisor.py']=(path,identity(path))
        materials,proof=s.retain_originals(originals,sources,original_root='FAKE_ORIGINAL_ROOT_NOT_ADMISSION',
            original_plan_SHA=s.ORIGINAL_PLAN_PIN[1],native_root='FAKE_NATIVE_ROOT_NOT_ADMISSION',required=required)
        return originals,sources,materials,proof,required
    def producer(self,role):
        s=self.s;r=self.runtime;base=self.identities[role];job=self.case/s.NATIVE_RUN_ID/'roles'/role;key=role.lower()
        cp=job/'production/checkpoints/FAKE_NEVER_CREATED_complete.pt';self.fake_paths[role]=str(cp)
        teacher=dict(source_path=base['mother_source_path'],source_SHA=base['mother_source_SHA'],source_bytes=base['mother_source_bytes'],teacher_frozen=True)
        counts=dict.fromkeys(s.COUNTS,0)
        checkpoint=dict(path=str(cp),bytes=base['source_bytes'],SHA=base['source_SHA'],iteration=0,counts=counts,
            full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True,teacher_unchanged=True,teacher_source=teacher)
        final=dict(kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3',passed_execution=True,teacher_unchanged=True,role=role,role_key=key,
            run_id=s.NATIVE_RUN_ID,actor_view='raw35_legacy_held_aux_v1',algorithm_family='a1_raw35_legacy_v1',algorithm_variant='A1_RAW35_FRESH',
            actual_BPTT_policy_steps=0,counts=counts,checkpoint=checkpoint,teacher=teacher)
        raw=(json.dumps(final,indent=2)+'\n').encode();write(job/'production/FINAL.json',raw)
        producer=dict(own_job_root=str(job),FINAL_path=str(job/'production/FINAL.json'),FINAL_bytes=len(raw),FINAL_SHA=H(raw),FINAL=final,run_id=s.NATIVE_RUN_ID,role_key=key)
        files=[]
        for rel,path in ((r._guard.WORKER_REL,self.worker),(r._guard.BRIDGE_REL,self.sources['native_supermimic_bridge.py'][0])):
            target=job/rel;write(target,path.read_bytes());files.append(dict(relative=rel,**identity(target)))
        put(job/'INSTALL_MANIFEST.json',dict(files=files))
        put(job/'TASK.json',dict(role=role,role_key=key,run_id=s.NATIVE_RUN_ID,teacher_path=teacher['source_path'],teacher_SHA=teacher['source_SHA'],teacher_bytes=teacher['source_bytes'],manifest_SHA=H((job/'INSTALL_MANIFEST.json').read_bytes())))
        return producer
    def prepared(self,seed):
        s=self.s;r=self.runtime;originals,sources,materials,proof,required=self.fixture();rows=[]
        for role in s.ROLES:
            row=dict(role=role,controls=s.CONTROLS[role],status='deferred_not_constructed')
            if role in s.REQUESTED:
                p=self.producer(role);cp=p['FINAL']['checkpoint'];teacher=p['FINAL']['teacher']
                row.update(worker=r.WORKER_ALIASES[role],a1_producer=p,seed=seed,num_envs=80,policy_variant=r.POLICY_VARIANT,
                    actor_semantics='EMBEDDED_ORIGINAL_TEACHER_MEAN',actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE',
                    original_bootstrap_teacher=teacher,source_path=cp['path'],source_SHA=cp['SHA'],source_bytes=cp['bytes'],
                    producer_teacher_freeze_evidence=r._guard.derive_producer_guard(p))
            rows.append(row)
        aliases=set(sources)|set(required)|set(proof['baseline_provenance']['source_to_retained'].values())
        plan=dict(kind=r.PLAN_KIND,seed=seed,batch_purpose=r.purpose_for(seed),policy_variant=r.POLICY_VARIANT,
            enabled=False,staged=False,source_native_enabled=False,dispatched=False,group_id='FAKE_SOURCE_SEED'+str(seed),GPU_UUID='GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
            asset_SHA=s.USD,contract_SHA=s.CONTRACT,holdout_protocol=r.holdout_protocol(seed),paired_reset_protocol=s.paired_plan(seed),
            requested_roles=list(s.REQUESTED),deferred_roles=[k for k in s.ROLES if k not in s.REQUESTED],roles=rows,
            overall_eight_pass_rate=None,comparison=None,worker_files=[dict(relative=rel,**materials[rel][1]) for rel in sorted(aliases)])
        return dict(plan=plan,materials=materials,originals=originals,original_preservation=proof,original_dependency_files=required,
            new_root=self.case/plan['group_id'],source_index=dict(fake=True),boundary=dict(fake=True),native_vendor=dict(fake_not_vendor7=True),selected_runtime_trees={},original_plan_SHA=s.ORIGINAL_PLAN_PIN[1])
    def validate(self,prepared):
        original=importlib.import_module
        def imported(name,*aa,**kw):
            module=original(name,*aa,**kw)
            if name=='good_expert_holdout_runtime_v1':
                # Fixture containment path only, IN MEMORY. Exact file pins/mother identity/whole guard unchanged.
                for role,cp in self.fake_paths.items():module.BASELINE_IDENTITIES[role]['source_path']=cp
            return module
        with patch.object(importlib,'import_module',side_effect=imported):return self.s.metadata_validate(prepared)
    def test_01_actual_published27_exact_set_and_fixed_raw(self):
        expected=self.s.original_dependency_map(PLAN['worker_files'],INDEX)
        self.assertEqual(len(expected),27);raw=PLAN_PATH.read_bytes();self.assertEqual((len(raw),H(raw)),self.s.ORIGINAL_PLAN_PIN)
        self.assertEqual(expected['single_gpu_group_supervisor.py'],(9247,'7c826b983887cb9ec890c92737095c5e7e7d93538fafaa211021fea2e0d9fc27'))
        self.assertEqual(set(expected),{r['relative'] for r in PLAN['worker_files']})
    def test_02_missing_extra_not_permitted(self):
        rows=[r for r in PLAN['worker_files'] if r['relative']!='single_gpu_group_supervisor.py']
        with self.assertRaisesRegex(ValueError,'original27 worker_files'):self.s.original_dependency_map(rows,INDEX)
    def test_03_original_extra_tamper_and_unknown_extra_fail(self):
        rows=copy.deepcopy(PLAN['worker_files']);next(r for r in rows if r['relative']=='single_gpu_group_supervisor.py')['SHA']='0'*64
        with self.assertRaisesRegex(ValueError,'original27 dependency pin'):self.s.original_dependency_map(rows,INDEX)
        rows=copy.deepcopy(PLAN['worker_files']);rows.append(dict(relative='UNREQUESTED.py',bytes=1,SHA='f'*64))
        with self.assertRaises(ValueError):self.s.original_dependency_map(rows,INDEX)
    def test_04_index_provenance_and_duplicate_fail(self):
        index=copy.deepcopy(INDEX);index['inherited_original_worker_source_entries'][0]['bytes']+=1
        with self.assertRaisesRegex(ValueError,'provenance'):self.s.original_dependency_map(PLAN['worker_files'],index)
        rows=copy.deepcopy(PLAN['worker_files']);rows[-1]=copy.deepcopy(rows[0])
        with self.assertRaises(ValueError):self.s.original_dependency_map(rows,INDEX)
    def test_05_real25_text_inputs_and_three_actual_overlay_conflicts(self):
        originals,sources,materials,proof,required=self.fixture()
        self.assertEqual(len(required),25)  # Two original assets are metadata-only, never opened here.
        self.assertEqual(proof['baseline_provenance']['source_to_retained'],{k:self.s.RETAIN_PREFIX+k for k in (
            'worker_sources/e1/e1_fresh_runtime_bridge.py','worker_sources/e1/e1_parallel_worker_safe.py','worker_sources/e1/e1_route80_factories.py')})
        self.assertEqual(materials['single_gpu_group_supervisor.py'],originals['single_gpu_group_supervisor.py'])
        self.assertTrue(self.s.validate_preservation(proof,materials,originals=originals,required=required))
    def test_06_supervisor_collision_preserves_old_and_new_separately(self):
        originals,sources,materials,proof,required=self.fixture(supervisor_collision=True);rel='single_gpu_group_supervisor.py';alias=self.s.RETAIN_PREFIX+rel
        self.assertEqual(proof['baseline_provenance']['source_to_retained'][rel],alias)
        self.assertEqual(materials[rel],sources[rel]);self.assertEqual(materials[alias],originals[rel]);self.assertNotEqual(materials[rel][1],materials[alias][1])
    def test_07_lost_retained_original_rejected(self):
        originals,sources,materials,proof,required=self.fixture();materials.pop(next(iter(proof['baseline_provenance']['source_to_retained'].values())))
        with self.assertRaisesRegex(ValueError,'lost/changed'):self.s.validate_preservation(proof,materials,originals=originals,required=required)
    def test_08_forged_two_equal_arrays_do_not_self_prove(self):
        originals,sources,materials,proof,required=self.fixture();proof['baseline'].pop();proof['installed']=copy.deepcopy(proof['baseline']);proof['baseline_SHA']=self.s.preservation_digest(proof['baseline'])
        with self.assertRaisesRegex(ValueError,'baseline is incomplete'):self.s.validate_preservation(proof,materials,originals=originals,required=required)
    def test_09_incomplete_origin_and_input_path_spoof_fail(self):
        originals,sources,materials,proof,required=self.fixture();bad=copy.deepcopy(proof);bad['baseline_provenance']['original_logical_rows'].pop()
        with self.assertRaises(ValueError):self.s.validate_preservation(bad,materials,originals=originals,required=required)
        bad=copy.deepcopy(proof);bad['baseline_provenance']['original_logical_rows'][0]['input_path']='FAKE_OTHER_PATH'
        with self.assertRaisesRegex(ValueError,'path/read-byte'):self.s.validate_preservation(bad,materials,originals=originals,required=required)
    def test_10_real_stream_identity_observation_and_drop_tamper_negatives(self):
        originals,sources,materials,proof,required=self.fixture();observed={rel:identity(path) for rel,(path,_) in materials.items()}
        proof['installed']=[dict(relative=r['relative'],**observed[r['relative']]) for r in proof['baseline']]
        proof['installed_status']='TEST_SOURCE_READ_HASH_NOT_STAGE'
        self.assertTrue(self.s.validate_preservation(proof,materials,originals=originals,required=required,observed=observed))
        bad=dict(observed);bad.pop('single_gpu_group_supervisor.py')
        with self.assertRaisesRegex(ValueError,'stream dropped'):self.s.validate_preservation(proof,materials,originals=originals,required=required,observed=bad)
        bad=copy.deepcopy(observed);bad['single_gpu_group_supervisor.py']['SHA']='f'*64
        with self.assertRaisesRegex(ValueError,'actual installed retained bytes'):self.s.validate_preservation(proof,materials,originals=originals,required=required,observed=bad)
    def test_11_required_extra_drop_and_retained_namespace_collision_fail(self):
        originals,sources,materials,proof,required=self.fixture();bad=dict(originals);bad.pop('single_gpu_group_supervisor.py')
        with self.assertRaises(ValueError):self.s.retain_originals(bad,sources,original_root='FAKE',original_plan_SHA='0'*64,native_root='FAKE',required=required)
        old='worker_sources/e1/e1_parallel_worker_safe.py';bad=dict(originals);bad[self.s.RETAIN_PREFIX+old]=originals[old]
        with self.assertRaisesRegex(ValueError,'alias collides'):self.s.retain_originals(bad,sources,original_root='FAKE',original_plan_SHA='0'*64,native_root='FAKE',required=required)
    def test_12_unmodified_metadata_validate_accepts_extra_retained_seed29(self):
        prepared=self.prepared(20260929);receipt=self.validate(prepared)
        self.assertTrue(receipt['passed']);self.assertTrue(receipt['full_modules_not_AST_cropped_or_stubbed']);self.assertEqual(len(receipt['task_checks']),2)
        names={r['relative'] for r in prepared['plan']['worker_files']};self.assertIn('single_gpu_group_supervisor.py',names)
        self.assertTrue(any(k.startswith(self.s.RETAIN_PREFIX) for k in names));self.assertFalse(prepared['new_root'].exists())
    def test_13_unmodified_metadata_validate_seed30_and_missing_alias_negative(self):
        prepared=self.prepared(20260930);receipt=self.validate(prepared);self.assertEqual(receipt['seed'],20260930)
        prepared['plan']['worker_files']=[r for r in prepared['plan']['worker_files'] if r['relative']!='resume_runtime_contracts_v3.py']
        with self.assertRaisesRegex(ValueError,'all twenty'):self.validate(prepared)
    def test_14_original_overlay_schema_acceptance_and_counterexamples(self):
        prepared=self.prepared(20260929);plan=prepared['plan'];self.runtime._stage_file_metadata(plan)
        bad=copy.deepcopy(plan);bad['worker_files'].append(copy.deepcopy(bad['worker_files'][0]))
        with self.assertRaisesRegex(ValueError,'all twenty'):self.runtime._stage_file_metadata(bad)
        bad=copy.deepcopy(plan);bad['worker_files'].append(dict(relative='../escape.py',bytes=1,SHA='0'*64))
        with self.assertRaisesRegex(ValueError,'aliases must stay relative'):self.runtime._stage_file_metadata(bad)
        bad=copy.deepcopy(plan);bad['worker_files'][-1]['bytes']=0
        with self.assertRaisesRegex(ValueError,'bytes/SHA'):self.runtime._stage_file_metadata(bad)
    def test_15_exact_three_function_whitelist_rest_complete_AST(self):
        old=funcs(R/'source_stage_good_expert_holdout_v1/stage_good_expert_holdout_v1.py');new=funcs(HERE/'stage_good_expert_holdout_v2.py')
        changed={n for n in old if AST(old[n])!=AST(new[n])}
        self.assertEqual(changed,{'prepare','preflight_summary','stage'});self.assertEqual(len(old)-len(changed),22)
        self.assertEqual(AST(old['metadata_validate']),AST(new['metadata_validate']));self.assertEqual(AST(old['native_boundary']),AST(new['native_boundary']))
        text=ast.unparse(new['prepare']);self.assertIn('original_dependency_map(old_files, index)',text);self.assertIn('required=expected',text)
        self.assertIn('262144',text);self.assertNotIn('retained_static_inventory',text)
    def test_16_parent_hash_gate_and_overlay_pins_unchanged(self):
        parent=R/'source_good_expert_holdout_subset_v1/single_gpu_good_expert_holdout_parent_v1.py';text=parent.read_text(encoding='utf-8')
        self.assertEqual(H(parent.read_bytes()),'fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff')
        self.assertIn("for r in plan['worker_files']:",text);self.assertIn("hashlib.sha256(raw).hexdigest()==r['SHA']",text)
        self.assertEqual(H(INDEX_PATH.read_bytes()),'6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e')
        self.assertEqual(sealed_snapshot(),self.before)
    def test_17_stage_AST_binds_actual_stream_and_sidecar_separate_from_plan(self):
        stage=funcs(HERE/'stage_good_expert_holdout_v2.py')['stage'];text=ast.unparse(stage)
        self.assertIn('observed=written',text);self.assertIn('originals=prepared[',text)
        self.assertIn('root / ORIGINAL_PRESERVATION_NAME',text);self.assertIn("root / 'GROUP_PLAN.json'",text)
        self.assertLess(text.index('validate_preservation('),text.index("root / 'GROUP_PLAN.json'"))
        self.assertNotIn('Popen',text)
    def test_18_unicode_static_alias_and_wrong_retained_map_fail(self):
        originals,sources,materials,proof,required=self.fixture();path=self.case/'FAKE_unicode.txt';write(path,b'FAKE unicode alias bytes\n')
        originals['runtimes/SLOPE135/静态来源.txt']=(path,identity(path))
        materials,proof=self.s.retain_originals(originals,sources,original_root='FAKE',original_plan_SHA='0'*64,native_root='FAKE',required=required)
        self.assertTrue(self.s.validate_preservation(proof,materials,originals=originals,required=required))
        first=next(iter(proof['baseline_provenance']['source_to_retained']));proof['baseline_provenance']['source_to_retained'][first]='other_namespace.py'
        with self.assertRaisesRegex(ValueError,'exact retained-original'):self.s.validate_preservation(proof,materials,originals=originals,required=required)


def main():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceTests))
    report=dict(kind='GOOD_HOLDOUT_V2_NEW_SOURCE_REGRESSION_ONLY',passed=result.wasSuccessful(),tests_run=result.testsRun,
        errors=len(result.errors),failures=len(result.failures),audit=AUDIT,original_dependency_metadata_count=27,actual_original_text_sources_verified=25,
        old18_tests_replayed=False,actual_prepare_preflight_stage_dispatch_executed=False,actual_parent_worker_executed=False,
        pure_source_metadata_validate_exercised_with_synthetic_producers=True,fixture_model_paths_never_created_or_opened=True,
        original_assets_vendor7_fullstatic_integrity_actually_tested=False,actual_native_binding='UNKNOWN',source_native_enabled=False,staged=False,dispatched=False)
    put(HERE/'TEST_REPORT.json',report)
    os.stat,os.lstat=REAL_STAT,REAL_LSTAT
    if not result.wasSuccessful():raise SystemExit(1)
    if any(AUDIT.values()):raise SystemExit('SOURCE audit was nonzero')

if __name__=='__main__':main()
