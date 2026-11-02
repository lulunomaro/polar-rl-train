"""Only NEW source/metadata/fake-owner tests. No real C, locks, model or SDK."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,tempfile,time,types,unittest
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
SEALED=HERE.parent/'source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source'
sys.path.insert(0,str(SEALED));sys.path.insert(0,str(HERE))
import quality_microtrain_contracts_v1 as q
import resume_runtime_contracts_v3 as base

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def fresh(role='E3',increment=17):return dict(role=role,role_key='OWN_'+role,family='parent',num_envs=1024,seed=123,
    actor_view=base.RAW35_ACTOR_VIEW,algorithm_variant='A1_RAW35_FRESH',microtrain=dict(schema=q.SCHEMA,target_verified_increment=increment,source_final=None),teacher=dict(path='MOTHER_NEVER_OPENED.pt',SHA='a'*64,bytes=20000000))
def plan(entries):return dict(kind=q.PLAN_KIND,run_id='OWN_NEW_SEGMENT',H1_excluded=True,requested_roles=[e['role']for e in entries],deferred_roles=[r for r in q.ROLES if r not in{e['role']for e in entries}],entries=entries)
def task(entry):
    e=q.validate_microtrain_entry(entry);return q.bind_microtrain_task(dict(e,run_id='OWN_NEW_SEGMENT',teacher_path=e['teacher']['path'],teacher_SHA='a'*64,teacher_bytes=20000000),e)
def counts(n):return dict(q.zero_counts(),policy_attempts=n,pi_optimizer_steps=n,pi_bptt_optimizer_steps=n)
def resumed(directory):
    e=fresh();e['algorithm_variant']='A1_RAW35_RESUME';cp=directory/'production/checkpoints/model_BPTT002182_I002282_S0005_complete.pt'
    e['resume_bptt']=dict(kind='OWN_NEW_BPTT_FULL_CHECKPOINT_V2',path=str(cp),SHA='b'*64,bytes=235000000,actor_view=base.RAW35_ACTOR_VIEW,algorithm_family='a1_raw35_legacy_v1',allow_environment_reset=True,allow_partial_update=False,producer_run_id='ACTUAL_SOURCE_RUN',producer_role_key='SOURCE_E3')
    c=counts(2182);f=dict(kind=base.FINAL_KIND,role='E3',role_key='SOURCE_E3',run_id='ACTUAL_SOURCE_RUN',passed_execution=True,teacher_unchanged=True,actor_view=base.RAW35_ACTOR_VIEW,algorithm_family='a1_raw35_legacy_v1',algorithm_variant='A1_RAW35_FRESH',actual_BPTT_policy_steps=2182,counts=c,checkpoint=dict(path=str(cp),SHA='b'*64,bytes=235000000,counts=c,full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True))
    raw=(json.dumps(f)+'\n').encode();e['microtrain']['source_final']=dict(path=str(directory/'production/FINAL.json'),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),metadata=f)
    return e,raw

def resumed_receipt(c):return dict(restored_counts=c,byte_cache=dict(physical_byte_opens=1,SHA_calculations=1,decodes=1,whole_full_checkpoint_retained=True),reset_resume_stream_cut_required=True,no_actor_only_fallback=True,no_counter_offset_or_fresh_count_splicing=True)
def semantic(e,stopped=False,n=None):
    t=task(e);c=t['microtrain']['declared_source_counts'];receipt=resumed_receipt(c)if t.get('resume_bptt')else None
    start=q.start_microtrain_segment(t,c,resume_receipt=receipt);n=t['target_bptt_steps']if n is None else n;end=counts(n);s=q.finish_microtrain_segment(start,end,stopped=stopped)
    f=dict(run_id=t['run_id'],role=t['role'],role_key=t['role_key'],counts=end,parent_finite_saved_stop=stopped,target_reached=s['target_reached'],microtrain_segment=s,checkpoint=dict(microtrain_segment=s))
    return dict(kind='ORIGINAL_APP_V6_SEMANTIC_FIXTURE_NOT_NATIVE',passed_execution=True,original_error=False,reasons=[],final=f)

class Normalize(ast.NodeTransformer):
    def visit_Assign(self,n):
        if any(isinstance(t,ast.Name)and t.id=='segment'for t in n.targets):return None
        if isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id in('bind_microtrain_task','bind_microtrain_go'):return None
        return self.generic_visit(n)
    def visit_Expr(self,n):
        if isinstance(n.value,ast.Call):
            call=n.value
            if isinstance(call.func,ast.Name)and call.func.id=='validate_microtrain_payload':return None
            if isinstance(call.func,ast.Name)and call.func.id=='put'and call.args and 'MICROTRAIN_SEGMENT_BASELINE_V1.json'in ast.unparse(call.args[0]):return None
        return self.generic_visit(n)
    def visit_Call(self,n):
        self.generic_visit(n)
        if isinstance(n.func,ast.Name)and n.func.id=='validate_microtrain_plan':return n.args[0]
        if isinstance(n.func,ast.Name)and n.func.id=='validate_worker_microtrain_task':return ast.parse("task['target_bptt_steps']>=3000",mode='eval').body
        for k in n.keywords:
            if k.arg=='target_per_expert'and isinstance(k.value,ast.Constant)and k.value.value is None:k.value=ast.Constant(3000)
            if k.arg=='target_bptt_steps'and ast.unparse(k.value)=="segment['target_cumulative_verified_counter']":k.value=ast.parse("task['target_bptt_steps']",mode='eval').body
        n.keywords=[k for k in n.keywords if not(k.arg or'').startswith('microtrain_')]
        return n

def source(name):return (SEALED/name).read_text(encoding='utf-8')
def function(text,name):return next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name==name)
def dump(node):return ast.dump(node,include_attributes=False)

class MicrotrainTests(unittest.TestCase):
    def test01_fresh_zero_plus_small_increment(self):
        t=task(fresh());s=q.start_microtrain_segment(t,q.zero_counts());self.assertEqual(s['target_cumulative_verified_counter'],17);self.assertEqual(s['source_lineage'],'OWN_FRESH_ZERO')
    def test02_only_one_or_two_explicit_pending(self):
        for n in(1,2):
            p=q.validate_microtrain_plan(plan([fresh(r)for r in('E3','W35')[:n]]));self.assertEqual(len(p['entries']),n);self.assertEqual(len(p['deferred_roles']),8-n)
    def test03_bad_subsets_H1_and_deferred(self):
        for p in(plan([]),plan([fresh(r)for r in('E3','W35','E0')]),plan([fresh('H1')]),plan([fresh(),fresh()])):
            with self.assertRaises((ValueError,KeyError)):q.validate_microtrain_plan(p)
        p=plan([fresh()]);p['deferred_roles']=[]
        with self.assertRaises(ValueError):q.validate_microtrain_plan(p)
    def test04_increment_and_family_negative(self):
        for value in(0,301,-1,True,1.5):
            with self.assertRaises(ValueError):q.validate_microtrain_entry(fresh(increment=value))
        for field,value in(('actor_view','baseline_fullctx_v1'),('algorithm_variant','BOUND_V1'),('algorithm_family','new_family')):
            e=fresh();e[field]=value
            with self.assertRaises(ValueError):q.validate_microtrain_entry(e)
    def test05_actual_source_FINAL_once_no_checkpoint(self):
        e,raw=resumed(HERE/'NEVER_CREATED_SOURCE');calls=[]
        p=q.validate_microtrain_plan(plan([e]),reader=lambda path:(calls.append(path),raw)[1]);self.assertEqual(calls,[e['microtrain']['source_final']['path']]);self.assertEqual(p['entries'][0]['target_bptt_steps'],2199)
    def test06_source_FINAL_pin_and_lineage_negative(self):
        e,raw=resumed(HERE/'NEVER_CREATED_SOURCE')
        with self.assertRaises(ValueError):q.validate_microtrain_plan(plan([e]),reader=lambda path:raw+b' ')
        for field in('producer_run_id','producer_role_key'):
            bad=copy.deepcopy(e);bad['resume_bptt'][field]='WRONG'
            with self.assertRaises(ValueError):q.validate_microtrain_entry(bad)
    def test07_loaded_counter_target_not_offset(self):
        e,_=resumed(HERE/'NEVER_CREATED_SOURCE');t=task(e);c=counts(2182);s=q.start_microtrain_segment(t,c,resume_receipt=resumed_receipt(c));self.assertEqual(s['target_cumulative_verified_counter'],2199)
        with self.assertRaises(ValueError):q.start_microtrain_segment(t,counts(0),resume_receipt=resumed_receipt(counts(0)))
    def test08_payload_run_key_counts_before_original_load(self):
        e,_=resumed(HERE/'NEVER_CREATED_SOURCE');t=task(e);payload=dict(run_id='ACTUAL_SOURCE_RUN',role='E3',role_key='SOURCE_E3',actor_view=base.RAW35_ACTOR_VIEW,algorithm_family='a1_raw35_legacy_v1',context_reward_extension=dict(counts=counts(2182)))
        self.assertTrue(q.validate_microtrain_payload(payload,t))
        for key,value in(('run_id','OTHER'),('role_key','FRESH_SPLICE'),('role','W35')):
            bad=dict(payload,**{key:value})
            with self.assertRaises(ValueError):q.validate_microtrain_payload(bad,t)
        payload['context_reward_extension']['counts']=counts(2181)
        with self.assertRaises(ValueError):q.validate_microtrain_payload(payload,t)
    def test09_one_whole_bytes_hash_decode_old_API(self):
        raw=b'OWN_FAKE_PAYLOAD_NOT_PT';e,_=resumed(HERE/'NEVER_CREATED_SOURCE');d=dict(e['resume_bptt'],SHA=hashlib.sha256(raw).hexdigest(),bytes=len(raw));reads=[];decodes=[]
        cache=base.PinnedOwnFullCheckpoint(d,lambda stream:(decodes.append(stream.read()),{'retained':'whole'})[1],read_bytes=lambda path:(reads.append(path),raw)[1]);self.assertEqual(len(reads),1);self.assertEqual(decodes,[raw]);self.assertTrue(cache.receipt()['whole_full_checkpoint_retained'])
    def test10_fresh_count_splice_and_resume_cache_negative(self):
        with self.assertRaises(ValueError):q.start_microtrain_segment(task(fresh()),counts(1))
        e,_=resumed(HERE/'NEVER_CREATED_SOURCE');t=task(e);r=resumed_receipt(counts(2182));r['byte_cache']['physical_byte_opens']=2
        with self.assertRaises(ValueError):q.start_microtrain_segment(t,counts(2182),resume_receipt=r)
    def test11_target_and_late_STOP_full_receipt(self):
        t=task(fresh());s=q.start_microtrain_segment(t,counts(0));end=q.finish_microtrain_segment(s,counts(17),stopped=False);self.assertEqual(end['actual_verified_increment'],17);self.assertTrue(end['target_reached']);partial=q.finish_microtrain_segment(s,counts(6),stopped=True);self.assertFalse(partial['target_reached']);self.assertEqual(partial['total_original_verified_counter'],6)
        with self.assertRaises(ValueError):q.finish_microtrain_segment(s,counts(18),stopped=False)
    def test12_original_error_never_cleared(self):
        original=dict(passed_execution=False,original_error=True,reasons=['real_original_close_error'],final=None);result=q.enforce_microtrain_waited_result(original,fresh());self.assertEqual(result['reasons'],original['reasons']);self.assertTrue(result['original_error'])
    def test13_parent_segment_good_and_tamper(self):
        e=fresh();old=semantic(e);self.assertTrue(q.enforce_microtrain_waited_result(old,e)['passed_execution']);bad=copy.deepcopy(old);bad['final']['microtrain_segment']['actual_verified_increment']=16;self.assertTrue(q.enforce_microtrain_waited_result(bad,e)['original_error'])
    def test14_resume_total_and_delta_distinct(self):
        e,_=resumed(HERE/'NEVER_CREATED_SOURCE');result=q.enforce_microtrain_waited_result(semantic(e),e);self.assertTrue(result['passed_execution']);segment=result['final']['microtrain_segment'];self.assertEqual((segment['starting_verified_counter'],segment['actual_verified_increment'],segment['total_original_verified_counter']),(2182,17,2199))
    def test15_parent_resource_account_AST_unchanged(self):
        old=source('supermimic_original_owner_shared_app_close_candidate_v5.py');new=(HERE/'owner_quality_microtrain_v1.py').read_text(encoding='utf-8')
        for name in('require','gpu','account','environment','admit','plan_protocol'):self.assertEqual(dump(function(old,name)),dump(function(new,name)),name)
        self.assertEqual(dump(Normalize().visit(function(new,'main'))),dump(function(old,'main')))
    def test16_worker_whole_main_after_only_metadata_and_target_normalization(self):
        old=source('worker_supermimic_bptt_app_close_candidate_v5.py');new=(HERE/'worker_quality_microtrain_v1.py').read_text(encoding='utf-8');self.assertEqual(dump(Normalize().visit(function(new,'main'))),dump(function(old,'main')))
        for name in('worker_entry_v2','H','put'):self.assertEqual(dump(function(old,name)),dump(function(new,name)))
    def test17_original_resume_and_temporal_body_pins(self):
        pins={'ctx_reward_full_resume_candidate_v2.py':'8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac','resume_runtime_contracts_v3.py':'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7','app_close_semantics_v6.py':'3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39'}
        for name,h in pins.items():self.assertEqual(hashlib.sha256((SEALED/name).read_bytes()).hexdigest(),h)
        text=source('ctx_reward_full_resume_candidate_v2.py');self.assertIn('self.buffer.seal_stream_boundary()',text);self.assertIn('self.obs_hist.zero_()',text);self.assertLess(text.index('self.buffer.import_state'),text.index("restore_rng(ext['rng'])"))
    def test18_new_actual_training_not_enabled_no_Torch(self):
        self.assertIs(q.SOURCE_ONLY_STATUS['enabled_for_actual_training'],False);self.assertIs(q.SOURCE_ONLY_STATUS['implemented_for_actual_training'],False);self.assertNotIn('torch',sys.modules)
    def fake_owner(self,n):
        events=[];data={};clock=[100.];fds=[10];processes=[]
        class FD:
            def __init__(self,path):self.path=str(path);fds[0]+=1;self.number=fds[0]
            def fileno(self):return self.number
            def close(self):events.append(('fd_close',self.number))
        b=types.ModuleType('three_slot_common_v1');b.C=Path('/OWN_FAKE_CANONICAL');b.LOCKS=(Path('/OWN_FAKE_LOCK_A'),Path('/OWN_FAKE_LOCK_B'))
        b.put=lambda path,value:(events.append(('put',str(path))),data.__setitem__(str(path),copy.deepcopy(value)))
        b.read=lambda path:data[str(path)];b.H=lambda path:'a'*64;b.ident=lambda pid:dict(pid=pid,creation='OWN_FAKE')
        b.terminal=lambda row:bool(row.get('terminal_all_own_children_waited')and row.get('returncode')is not None)
        def charge(c,a,go,rows,now):
            events.append(('charge',set(go),set(rows)))
            for key,g in go.items():
                x=a['experts'].setdefault(key,dict(accounted_through_epoch=g['learning_started_epoch'],charged_seconds=0.));end=rows[key]['owner_received_terminal_epoch']if key in rows else now;dt=end-x['accounted_through_epoch'];x['accounted_through_epoch']=end;x['charged_seconds']+=dt;c['charged_training_seconds']+=dt;c['remaining_training_seconds']-=dt;a['charged_expert_seconds']+=dt
            return c,a
        b.charge_values=charge
        shim=types.ModuleType('resume_runtime_app_close_v5');shim.bind_future_task_extensions=lambda t,e:dict(t,**base.validate_worker_variant(e))
        shim.evaluate_waited_worker=lambda J,rc,e,run:semantic(e)
        auth=types.ModuleType('single_writer72_authority_V85M_source');auth.authority_tracking_schema_admitted=lambda c:True;auth.authority_original_extension_count=lambda c:9;auth.authority_budget_GO_allowed=lambda c:True
        fcntl=types.ModuleType('fcntl');fcntl.LOCK_EX=2;fcntl.LOCK_NB=4;fcntl.LOCK_SH=1;fcntl.LOCK_UN=8;fcntl.flock=lambda fd,mode:events.append(('flock',fd,mode))
        with patch.dict(sys.modules,{'three_slot_common_v1':b,'resume_runtime_app_close_v5':shim,'single_writer72_authority_V85M_source':auth,'fcntl':fcntl}):owner=load(HERE/'owner_quality_microtrain_v1.py','NEW_FAKE_OWNER_ONLY')
        owner.B=HERE/'NEVER_CREATED_OWNER';p=plan([fresh(r)for r in('E3','W35')[:n]])
        for e in p['entries']:e['job_root']=str(owner.B/'roles'/e['role'])
        data[str(owner.B/'OWNER_PLAN.json')]=p;data[str(owner.C)]=dict(active_segment=None,authority_generation=1,budget_mode='finite_original_limits_restored_after_single4090_return',remaining_training_seconds=2268000.,charged_training_seconds=0.,completed_segments=[])
        owner.verify_sources=lambda plan:events.append(('fake_source_manifest_only',len(plan['entries'])))
        owner.gpu=lambda uuid:dict(actual_GPU_fixture=True)
        class Process:
            def __init__(self,*args,**kwargs):self.pid=1000+len(processes);self.args=args;self.kwargs=kwargs;processes.append(self);events.append(('Popen',args,kwargs))
            def poll(self):return 0
            def wait(self):events.append(('actual_fake_wait',self.pid));return 0
        fake_time=types.SimpleNamespace(time=lambda:clock[0],monotonic=lambda:clock[0],sleep=lambda seconds:clock.__setitem__(0,clock[0]+seconds))
        with patch.object(owner,'time',fake_time),patch.object(owner.subprocess,'Popen',Process),patch.object(Path,'open',lambda path,*a,**k:FD(path)),patch.object(Path,'mkdir',lambda *a,**k:None),patch.object(Path,'exists',lambda path:str(path)in data):owner.main()
        final=data[str(owner.B/'COHORT_FINAL.json')];exit=data[str(owner.B/'OWNER_EXIT_ACTUAL.json')]
        self.assertEqual(len(processes),n);self.assertEqual(len(final['go']),n);self.assertEqual(final['pending_unstarted_roles'],[]);self.assertEqual(final['microtrain_requested_roles'],p['requested_roles']);self.assertEqual(len(final['microtrain_deferred_roles']),8-n)
        self.assertTrue(exit['all_own_children_waited']and exit['original_cost_settled']and exit['original_leases_released']);self.assertEqual(exit['errors'],[])
        waits=[i for i,e in enumerate(events)if e[0]=='actual_fake_wait'];unlocks=[i for i,e in enumerate(events)if e[0]=='flock'and e[2]==8];self.assertLess(max(waits),min(unlocks));self.assertIsNone(data[str(owner.C)]['active_segment']);self.assertTrue(all(len(x.kwargs['pass_fds'])==4 for x in processes));return events
    def test19_one_requested_only_one_fake_Popen_no_deferred(self):self.fake_owner(1)
    def test20_two_requested_only_two_fake_Popen_no_deferred(self):self.fake_owner(2)

if __name__=='__main__':
    begin=time.monotonic();result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MicrotrainTests));value=dict(kind='QUALITY_MICROTRAIN_SOURCE_STDLIB_FAKE_NOT_NATIVE_V1',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),seconds=time.monotonic()-begin,Torch_imported='torch'in sys.modules,old_suites_rerun=False,actual_SSH_PT_raw_GPU_SDK_C_locks_Git_training_operations=0,actual_whole_payload_tensor_software_validation=None)
    (HERE/'TEST_RESULTS_QUALITY_MICROTRAIN_STDLIB_V1.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');raise SystemExit(0 if result.wasSuccessful()else 1)
