"""NEW stdlib/fake-source checks: actual full imports, zero actual native/model access."""
from pathlib import Path
import ast, contextlib, copy, hashlib, importlib, importlib.util, json, sys, time, unittest
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
PROJECT=HERE.parent
NAME='bound_only_native_runtime_v1'
HELPER='bound_only_native_helper_v1'
ROUTE='bound_only_native_route_v1'
GUARD='producer_bound_probe_guard_v1'
VARIANT='A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1'
PURPOSE='FROZEN_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_N80_V1'
ACTOR='OWN_A1_TEACHER_PLUS_POINT05_TANH_RESIDUAL_ZERO_UPDATE'
WATCH=(NAME,HELPER,ROUTE,GUARD,'a1_frozen_eval_runtime_v2','frozen_a1_raw35_v1','app_close_semantics_v5','resume_runtime_contracts_v3')

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
s=module(HERE/'stage_bound_only_native_v1.py','_new_bound_stager_fixture')
fixture=module(PROJECT/'source_frozen_embedded_teacher_native_v1/test_embedded_teacher_native_stdlib_v1.py','_read_only_fixture_constructors')
# Constructor utilities only; NO old test suite or old actual input operation.
fixture.HERE=HERE;fixture.s=s
fixture.old_fixture.HERE=HERE;fixture.old_fixture.s=s
fixture.old_fixture.INDEX=HERE/'BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json'

def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2),encoding='utf-8')
@contextlib.contextmanager
def imported(root):
    before={n:sys.modules.get(n) for n in WATCH};old_path=list(sys.path)
    try:
        for n in WATCH:sys.modules.pop(n,None)
        sys.path.insert(0,str(root));yield importlib.import_module(NAME)
    finally:
        sys.path[:]=old_path
        for n,v in before.items():
            if v is None:sys.modules.pop(n,None)
            else:sys.modules[n]=v

def node(path,name):
    return next(n for n in ast.parse(path.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
def dump(value):return ast.dump(value,include_attributes=False)
def norm(value):
    class N(ast.NodeTransformer):
        def visit_Constant(self,n):
            n=copy.deepcopy(n)
            if n.value=='ONEGPU_ZERO_UPDATE_BOUND_ONLY_E3_W35_NATIVE_PROBE_V1':n.value='ONEGPU_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1'
            elif n.value==ACTOR:n.value='EMBEDDED_ORIGINAL_TEACHER_MEAN'
            return n
    return dump(N().visit(copy.deepcopy(value)))

class BoundNativeFixtures(unittest.TestCase):
    def setUp(self):
        fixture.TeacherNativeFixtures.setUp(self)
        cohort=json.loads((self.native/'COHORT_FINAL.json').read_bytes())
        qualified=dict(E3='a4c56390b4c549ba8bfb808a63206c0816ad50e8c9659dc053f98cc66b3c8127',W35='b2f2878ff9aa04ddcd283fe71f5b5924b1bff78b3f04118cfa689244b0665cff')
        for entry in self.entries:
            if entry['role'] not in s.REQUESTED:continue
            job=Path(entry['job_root']);final=json.loads((job/'production/FINAL.json').read_bytes())
            final['checkpoint']['SHA']=qualified[entry['role']]
            row=cohort['rows'][entry['role_key']];row['final']=final;row['semantic_result']['final']=final
            put(job/'production/FINAL.json',final);put(job/'PARENT_WAITED_ACTUAL.json',row)
        put(self.native/'COHORT_FINAL.json',cohort)
    def tearDown(self):fixture.TeacherNativeFixtures.tearDown(self)
    def prepare(self,stats=False):
        return s.prepare(self.old,self.old_plan,self.flat,self.index,self.native,self.new,self.new.name,
            'GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',vendor_pin=self.vendor_pin,collect_action_statistics=stats)
    def mutate(self,path,fn):
        v=json.loads(path.read_bytes());fn(v);put(path,v)
    def case_fixture(self):
        p=self.prepare();s.stage(p);row=dict(next(r for r in p['plan']['roles'] if r['role']=='E3'),paired_reset_protocol=p['plan']['paired_reset_protocol'])
        case=self.new/'cases/E3';case.mkdir(parents=True);return p,row,case
    def valid_final(self,r,entry,prepared):
        cp=entry['a1_producer']['FINAL']['checkpoint'];role=entry['role'];count=r.CONTROLS[role];p=r._probe
        source=dict(source_path=cp['path'],source_SHA=cp['SHA'],source_bytes=cp['bytes'],physical_byte_opens=1,SHA_calculations=1,CPU_decodes=1,
            mother_checkpoint_opens=0,whole_root_CPU_unchanged=True,replay_or_saved_history_sliced_or_restored=False,live_optimizer_WM_critic_replay_created=False,
            approved_reference_provenance=dict(r._base.APPROVED_REFERENCE_PROVENANCE),approved_RSL_model_source=dict(r._base.APPROVED_RSL_MODEL_SOURCE),
            actual_eval_RSL_source_binding=dict(r._base.APPROVED_RSL_MODEL_SOURCE),admitted_producer_run_id=entry['a1_producer']['run_id'],
            actual_BPTT_policy_steps=entry['a1_producer']['FINAL']['actual_BPTT_policy_steps'],policy_variant=VARIANT,
            policy_family='zero_update_tanh_postprocess_of_original_full_A1_not_training',native_enabled=True,actor_semantics=ACTOR,
            original_bootstrap_teacher=entry['original_bootstrap_teacher'],producer_teacher_freeze_evidence=entry['producer_teacher_freeze_evidence'],
            probe_training_updates=0,probe_BPTT_policy_steps=0,probe_optimizer_updates=dict(pi=0,wm=0,aux=0,critic=0))
        probe=dict(source,kind=p.KIND,purpose=p.PURPOSE,container_role=role,container_checkpoint_SHA=cp['SHA'],actor_calls=count,
            container_algorithm_family=p.h.FAMILY,container_algorithm_variant='A1_RAW35_FRESH',container_algorithm_actor_view=p.h.VIEW,
            residual_scale=.05,action_clip=6.,actor_frozen=True,inference_failed=False,qualified_native_execution=None,eligible_for_promotion=False,
            effective_wrapper=dict(qualname='make_bound_only_wrapper.<locals>.BoundTeacherResidualPolicy',source=p._source_binding()),
            actor_source_bindings={'rsl_rl.models.MLPModel':dict(p.APPROVED_RSL)},synthetic_only=False,
            original_episode_boundary_source=dict(bytes=p.BOUNDARY_PIN[0],SHA256=p.BOUNDARY_PIN[1]),
            original_episode_boundary=dict(actions=count,original_step_transitions=count,pending_original_step=False,synthetic_episode_mask=False),
            bound_probe_action_statistics=dict(enabled=False,forward_calls=count),
            paired_reset_protocol=dict(candidate_pose_installed=True,protocol=prepared['plan']['paired_reset_protocol']['reference_planned_protocol']))
        source['bound_only_probe']=probe
        return dict(passed_execution=True,integration=r.INTEGRATION,role=role,group_id=self.new.name,num_envs=80,controls=count,
            policy_variant=VARIANT,evaluation_purpose=PURPOSE,actor_semantics=ACTOR,source_cache=source)
    def write_close(self,case,r):fixture.TeacherNativeFixtures.write_close(self,case,r)
    def semantic(self,r,entry,case,final):
        put(case/'FINAL.json',final);return r.evaluate_waited_eval_case(case,0,entry,self.new.name)
    def test_01_real_full_imports_no_cycle_no_native_or_model(self):
        p=self.prepare();v=p['metadata_validation']
        self.assertTrue(v['zero_update_bound_probe']);self.assertFalse(v['actual_native_enabled']);self.assertFalse(v['actual_staged'])
        self.assertEqual(v['policy_variant'],VARIANT);self.assertTrue(v['dependency_completeness']['helper_base_is_actual_imported_contracts'])
        self.assertEqual(v['model_opens'],0);self.assertEqual(p['boundary']['checkpoint_stat_hash_open_decode'],0)
        self.assertFalse(self.new.exists());self.assertNotIn('torch',sys.modules)
        with imported(self.flat) as r:
            self.assertIs(r._route.base,r._base);self.assertIs(r._route.p,r._probe)
            self.assertIs(r.OriginalA1NoResetDecisionVec,r._base.OriginalA1NoResetDecisionVec)
            self.assertIs(r._probe.BoundOnlyFrozenMean.act,r._probe.h.FrozenA1MeanPolicy.act)
            self.assertIs(r.A1CheckpointAdapter.actor,r._route.BoundOnlyCheckpointAdapter.actor)
            for key in ('check','check_actor','assert_entire_root_unchanged'):
                self.assertIs(getattr(r.A1CheckpointAdapter,key),getattr(r._base.A1CheckpointAdapter,key))
            self.assertIs(r.A1CheckpointAdapter.caller_type,r.BoundProbeCaller)
    def test_02_exclusive_fake_stage_17_and_complete_filename(self):
        p=self.prepare();receipt=s.stage(p)
        self.assertEqual(len(s.ALIASES),17);self.assertEqual(receipt['parent_launches'],0);self.assertFalse(receipt['actual_native_enabled'])
        self.assertTrue((self.new/'STAGE_COMPLETE_BOUND_ONLY_NATIVE_V1.json').is_file())
        self.assertFalse((self.new/'STAGE_COMPLETE_EMBEDDED_TEACHER_REFERENCE_V1.json').exists())
        for rel in s.ALIASES:self.assertEqual(s.identity(self.new/rel),p['materials'][rel][1])
        for role in s.ROLES:
            self.assertTrue((self.new/'runtimes'/role/'static_contact.npz').exists())
            self.assertFalse((self.new/'runtimes'/role/'models').exists())
        with self.assertRaises(ValueError):s.stage(p)
    def test_03_original_eleven_dependencies_unchanged(self):
        old=json.loads((PROJECT/'payload_frozen_microbatch_v2/MICROBATCH_STAGE_INDEX_V2.json').read_bytes())
        new=json.loads(self.index.read_bytes());a={x['relative']:x for x in old['entries']};b={x['relative']:x for x in new['entries']}
        removed={'single_gpu_e3_w35_a1_frozen_parent_v1.py','frozen_eval_microbatch_runtime_v1.py','worker_sources/parent/worker_five_original_n80.py'}
        self.assertEqual(len(a.keys()-removed),11)
        for rel in a.keys()-removed:self.assertEqual(a[rel],b[rel])
        self.assertEqual(b['a1_frozen_eval_runtime_v2.py']['bytes'],37927)
        self.assertEqual(b['resume_runtime_contracts_v3.py']['bytes'],22337)
    def test_04_full_parent_main_and_worker_main_AST_preserved(self):
        old=PROJECT/'source_frozen_embedded_teacher_native_v1'
        for before,after in (('single_gpu_e3_w35_embedded_teacher_parent_v1.py','single_gpu_e3_w35_bound_only_parent_v1.py'),('worker_formal_embedded_teacher_v1.py','worker_formal_bound_only_v1.py')):
            self.assertEqual(norm(node(old/before,'main')),norm(node(HERE/after,'main')))
    def test_05_original_close_error_and_common_semantic_blocks_unchanged(self):
        core=PROJECT/'source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py';new=HERE/(NAME+'.py')
        for name in ('record_primary_error','close_original_eval_resources'):self.assertEqual(dump(node(core,name)),dump(node(new,name)))
        a=next(n for n in node(core,'evaluate_waited_eval_case').body if isinstance(n,ast.Try)).body
        b=next(n for n in node(new,'evaluate_waited_eval_case').body if isinstance(n,ast.Try)).body
        def i(nodes,token):return next(i for i,n in enumerate(nodes) if token in ast.unparse(n))
        self.assertEqual(dump(ast.Module(body=a[:i(a,"mean = source.get('frozen_mean')")],type_ignores=[])),dump(ast.Module(body=b[:i(b,"final.get('policy_variant')")],type_ignores=[])))
        self.assertEqual(dump(ast.Module(body=a[i(a,'PRE_CLOSE.json'):],type_ignores=[])),dump(ast.Module(body=b[i(b,'PRE_CLOSE.json'):],type_ignores=[])))
    def test_06_V1_actor_math_build_and_guard_AST_identical(self):
        old=PROJECT/'source_bound_only_frozen_probe_v1/bound_only_frozen_probe_v1.py';new=HERE/(HELPER+'.py')
        for name in ('make_bound_only_wrapper','build_bound_only_mean_policy','BoundOnlyFrozenMean','BoundOnlyPolicyCaller','ReadOnlyActionStatistics'):
            self.assertEqual(dump(node(old,name)),dump(node(new,name)))
        guard=PROJECT/'source_frozen_embedded_teacher_native_v1/producer_teacher_guard_v1.py'
        for name in ('derive_producer_guard','teacher_identity','source_guard_mechanism'):
            self.assertEqual(dump(node(guard,name)),dump(node(HERE/(GUARD+'.py'),name)))
    def test_07_explicit_task_selects_native_capability_not_old_false(self):
        p=self.prepare()
        with imported(self.flat) as r:
            row=next(x for x in p['plan']['roles'] if x['role']=='E3')
            self.assertTrue(r._route.validate_source_route_task(row)['native_enabled'])
            for key,value in (('native_enabled',False),('zero_update',False),('collect_action_statistics',0)):
                x=copy.deepcopy(row);x['bound_only_probe'][key]=value
                with self.assertRaises(ValueError):r._route.validate_source_route_task(x)
    def test_08_stats_default_off_and_explicit_true_only(self):
        p=self.prepare();self.assertTrue(all(x['bound_only_probe']['collect_action_statistics'] is False for x in p['plan']['roles'] if x['role'] in s.REQUESTED))
        q=self.prepare(True);self.assertTrue(all(x['bound_only_probe']['collect_action_statistics'] is True for x in q['plan']['roles'] if x['role'] in s.REQUESTED))
        with self.assertRaises(ValueError):self.prepare(1)
    def test_09_missing_producer_source_guard_and_manifest_tamper_stop(self):
        p=self.prepare();q=copy.deepcopy(p['plan']);next(x for x in q['roles'] if x['role']=='E3')['producer_teacher_freeze_evidence']['torch_equal_before_each_complete_save']=False
        with self.assertRaises(ValueError):s.metadata_validate(self.flat,plan_bytes=json.dumps(q).encode())
        self.mutate(self.native/'roles/E3/TASK.json',lambda x:x.update(manifest_SHA='0'*64))
        with self.assertRaises(ValueError):self.prepare()
        self.assertFalse(self.new.exists())
    def test_10_source_container_identity_not_mother_or_effective_actor(self):
        p=self.prepare()
        for x in p['plan']['roles']:
            if x['role'] not in s.REQUESTED:continue
            self.assertNotEqual(x['source_SHA'],x['original_bootstrap_teacher']['source_SHA'])
            self.assertEqual(x['source_SHA'],x['a1_producer']['FINAL']['checkpoint']['SHA']);self.assertEqual(x['actor_semantics'],ACTOR)
        for k in ('comparison','relative_improvement','UID_alignment','reference_cache_match','overall_eight_pass_rate'):self.assertIsNone(p['plan'][k])
    def test_11_semantic_component_success_never_manufactures_wait_qualification(self):
        p,e,c=self.case_fixture()
        with imported(self.new) as r:
            self.write_close(c,r);result=self.semantic(r,e,c,self.valid_final(r,e,p));self.assertTrue(result['passed_execution'],result)
            self.assertEqual(result['kind'],'ACTUAL_WAITED_ZERO_UPDATE_BOUND_ONLY_N80_SEMANTIC_V1');self.assertIsNone(result['UID_alignment'])
            self.assertIn('CALLER_ORIGINAL_P_WAIT_REQUIRED',result['actual_resource_admission_or_parent_wait_proof'])
    def test_12_old_V1_false_or_candidate_teacher_label_rejected(self):
        p,e,c=self.case_fixture()
        with imported(self.new) as r:
            self.write_close(c,r)
            for where,key,value in (('inner','native_enabled',False),('outer','policy_variant','A1_RAW35_FRESH'),('outer','actor_semantics','EMBEDDED_ORIGINAL_TEACHER_MEAN'),('inner','synthetic_only',True)):
                f=self.valid_final(r,e,p);target=f['source_cache']['bound_only_probe'] if where=='inner' else f;target[key]=value
                self.assertFalse(self.semantic(r,e,c,f)['passed_execution'],(where,key))
    def test_13_update_or_boundary_or_cache_counter_lie_rejected(self):
        p,e,c=self.case_fixture()
        with imported(self.new) as r:
            self.write_close(c,r)
            for key,value in (('probe_BPTT_policy_steps',1),('probe_training_updates',True),('physical_byte_opens',True),('actor_calls',True),('mother_checkpoint_opens',1)):
                f=self.valid_final(r,e,p);f['source_cache']['bound_only_probe'][key]=value;self.assertFalse(self.semantic(r,e,c,f)['passed_execution'],key)
            f=self.valid_final(r,e,p);f['source_cache']['bound_only_probe']['original_episode_boundary']['original_step_transitions']-=1
            self.assertFalse(self.semantic(r,e,c,f)['passed_execution'])
    def test_14_original_error_nonzero_and_missing_close_remain_errors(self):
        p,e,c=self.case_fixture()
        with imported(self.new) as r:
            f=self.valid_final(r,e,p);self.assertFalse(self.semantic(r,e,c,f)['passed_execution']);self.write_close(c,r)
            put(c/'WORKER_ERROR.json',dict(error='retained original fake error'));self.assertFalse(self.semantic(r,e,c,f)['passed_execution'])
            self.assertFalse(r.evaluate_waited_eval_case(c,1,e,self.new.name)['passed_execution']);self.assertTrue((c/'WORKER_ERROR.json').exists())
    def test_15_descriptor_no_checkpoint_stat_and_IO_modules_restore(self):
        old=(Path.resolve,s.os.stat,s.os.lstat,list(sys.path),{n:sys.modules.get(n) for n in WATCH});p=self.prepare()
        self.assertIs(Path.resolve,old[0]);self.assertIs(s.os.stat,old[1]);self.assertIs(s.os.lstat,old[2]);self.assertEqual(sys.path,old[3])
        self.assertEqual({n:sys.modules.get(n) for n in WATCH},old[4]);entry=next(x for x in p['plan']['roles'] if x['role']=='E3')
        with imported(self.flat) as r:
            attempted=[];a,b=s.os.stat,s.os.lstat
            def guarded(fn):
                def call(path,*args,**kwargs):
                    if isinstance(path,(str,bytes,Path)) and Path(path).suffix.lower()=='.pt':attempted.append(str(path));raise AssertionError('checkpoint stat')
                    return fn(path,*args,**kwargs)
                return call
            try:
                s.os.stat=guarded(a);s.os.lstat=guarded(b);r._producer_descriptor(entry['a1_producer'],'E3');self.assertEqual(attempted,[])
            finally:s.os.stat,s.os.lstat=a,b
    def test_16_task_and_ready_scope_are_two_only_not_matched(self):
        p=self.prepare()
        with imported(self.flat) as r:
            rows=r.select_requested_roles(p['plan']);t=r.make_task(rows[0],p['plan'],time.time()+100,[100,101]);start=r.batch_start(p['plan'],['E3','W35'],1.)
            self.assertEqual(t['eval_members'],['E3','W35']);self.assertIsNone(t['comparison']);self.assertTrue(r.validate_start(t,start))
            start['policy_variant']='A1_CANDIDATE'
            with self.assertRaises(ValueError):r.validate_start(t,start)
    def test_17_post_close_group_grade_preserves_wait_release_and_external_null(self):
        p=self.prepare();s.stage(p)
        with imported(self.new) as r:
            rows=[];waits=[]
            for i,x in enumerate(r.select_requested_roles(p['plan'])):
                e=dict(x,paired_reset_protocol=p['plan']['paired_reset_protocol']);c=self.new/'cases'/e['role'];c.mkdir(parents=True)
                f=self.valid_final(r,e,p);self.write_close(c,r);sem=self.semantic(r,e,c,f);self.assertTrue(sem['passed_execution'],sem)
                rows.append(dict(role=e['role'],pid=100+i,returncode=0,actual_waited=True,passed_execution=True,semantic=sem,data=f))
                waits.append(dict(role=e['role'],pid=100+i,returncode=0,actual_waited=True))
            put(self.new/'TERMINAL_ROWS.json',rows);put(self.new/'FINAL.json',r.batch_result(p['plan'],rows,1.,epoch=2.))
            put(self.new/'ACTUAL_GROUP_ADMISSION.json',dict(group_id=self.new.name,original_private_GPU_EX_held=True,original_global_finite_EX_held=True,canonical_writes=0,canonical_owner_at_read=None))
            close=dict(all_own_children_waited=True,child_waits=waits,original_single_GPU_private_EX_released=True,original_global_finite_EX_released=True,errors=[],canonical_writes=0)
            put(self.new/'PARENT_EXIT_SCOPE.json',close);grade=r.grade_closed_bound_probe_group(self.new)
            self.assertTrue(grade['passed_closed_bound_probe_source_grade'],grade);self.assertIsNone(grade['qualified_bound_probe_execution']);self.assertFalse(grade['external_parent_wait_proof_created_here'])
            close['original_global_finite_EX_released']=False;put(self.new/'PARENT_EXIT_SCOPE.json',close)
            self.assertFalse(r.grade_closed_bound_probe_group(self.new)['passed_closed_bound_probe_source_grade'])
            close['original_global_finite_EX_released']=True;put(self.new/'PARENT_EXIT_SCOPE.json',close);put(self.new/'cases/W35/WORKER_ERROR.json',dict(error='original fake error'))
            self.assertFalse(r.grade_closed_bound_probe_group(self.new)['passed_closed_bound_probe_source_grade'])
    def test_18_guard_pin_or_Base_missing_never_stubbed(self):
        self.prepare();x=self.flat/(GUARD+'.py');x.write_bytes(x.read_bytes()+b'\nraise RuntimeError("never execute changed source")\n')
        with self.assertRaises(ValueError):
            with imported(self.flat):pass
    def test_19_virtual_factory_no_second_build_or_wrapper(self):
        self.prepare()
        with imported(self.flat) as r:
            adapter=object.__new__(r.A1CheckpointAdapter);adapter.task={'role':'E3'};adapter.caller=None;adapter.cache=object();adapter.probe_config={'collect_action_statistics':False}
            mean=type('FakeMean',(),dict(t=object(),device='cpu'))();calls=[]
            class Caller:
                def __init__(self,m,*,boundary):self.mean=m;self.boundary=boundary
            adapter.caller_type=Caller
            with patch.object(r._route.base,'_validate_approved_reference'),patch.object(r._probe,'build_bound_only_mean_policy',side_effect=lambda *a,**k:(calls.append((a,k)) or mean)),patch.object(r._route.base,'OriginalEpisodeBoundary',return_value='real-constructor-substituted-only-in-own-unit-test'):
                result=adapter.actor('cpu');self.assertIs(result.mean,mean);self.assertEqual(len(calls),1)
                with self.assertRaises(ValueError):adapter.actor('cpu')
                self.assertEqual(len(calls),1)
    def test_20_new_helper_and_route_AST_import_aliases_no_core_overwrite(self):
        index=json.loads(self.index.read_bytes());by={x['relative']:x for x in index['entries']}
        self.assertEqual(by['a1_frozen_eval_runtime_v2.py']['SHA256'],'7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e')
        route=ast.parse((HERE/(ROUTE+'.py')).read_bytes());self.assertTrue(any(isinstance(x,ast.Import) and any(a.name=='a1_frozen_eval_runtime_v2' and a.asname=='base' for a in x.names) for x in route.body))
        adapter=node(HERE/(NAME+'.py'),'A1CheckpointAdapter');self.assertFalse(any(isinstance(x,ast.FunctionDef) and x.name=='actor' for x in adapter.body))
        wrapper=node(HERE/'single_gpu_e3_w35_bound_only_parent_v1.py','bound_probe_parent_entry');self.assertEqual(ast.unparse(wrapper.body[0]),'main()')
    def test_21_full_index_source_only_not_a_native_receipt(self):
        value=json.loads(self.index.read_bytes());self.assertFalse(value['actual_native_enabled']);self.assertFalse(value['actual_staged'])
        self.assertTrue(value['source_native_capable']);self.assertIsNone(value['actual_qualified_bound_probe_execution'])
    def test_22_failed_stage_consumes_newroot_no_automatic_retry(self):
        p=self.prepare()
        with patch.object(s,'metadata_validate',side_effect=ValueError('own fake failure')):
            with self.assertRaises(ValueError):s.stage(p)
        self.assertTrue((self.new/'STAGE_ERROR_BOUND_ONLY_NATIVE_V1.json').exists());self.assertFalse((self.new/'STAGE_COMPLETE_BOUND_ONLY_NATIVE_V1.json').exists())
        with self.assertRaises(ValueError):self.prepare()

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='TEST_RESULTS_BOUND_ONLY_NATIVE_STDLIB_V1.json');args=ap.parse_args()
    target=HERE/args.output;assert target.parent==HERE and not target.exists()
    start=time.perf_counter();result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(BoundNativeFixtures))
    value=dict(kind='SOURCE_ONLY_ZERO_UPDATE_BOUND_ONLY_NATIVE_STDLIB_FAKE_NOT_NATIVE_V1',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),seconds=time.perf_counter()-start,
        actual_full_stdlib_imports=True,old_test_suites_executed=False,Torch_imported='torch' in sys.modules,actual_PT_or_raw_or_SDK_GPU_C_lock_Git_native_operations=0,actual_native_qualification=None)
    with target.open('x',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
