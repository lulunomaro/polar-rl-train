"""Entirely invented decoded fixtures; never loads a worker, SDK or artifact."""
import ast
import copy
from pathlib import Path
import random
import unittest
import capture_evidence_verifier_v1 as v


def cache(width, value, tick):
    return dict(last=[tick]*8,cur=copy.deepcopy(value),out=copy.deepcopy(value),sample_tick=[tick]*8,ready=[False]*8)

def clock(tick, depth=0, phase='scene_update'):
    return dict(physics_tick=tick,feedback_tick=tick//4,sim_time_us=tick*2500,common_control_counter=tick//8,
        phase=phase,control_slot='mid' if tick%8==4 else 'end',reset_depth=depth,
        is_original_100hz_slot=phase=='scene_update' and depth==0 and tick%4==0)

def feedback(key,tick,old=None):
    width=v.CHANNELS[key]; fb=tick//4
    clean=[[.25+fb/16]*width for _ in range(8)]
    noise=[[.001953125]*width for _ in range(8)]; bias=[[.00390625]*width for _ in range(8)]
    noisy=[[v.f32(v.f32(x+y)+(z if key=='leg_pos' else 0.)) for x,y,z in zip(a,b,c)] for a,b,c in zip(clean,noise,bias)]
    after=cache(width,noisy,fb)
    if old is not None:
        after['ready']=[True]*8
        for i in range(8):
            if i%2: after['out'][i]=old['cur'][i][:]; after['sample_tick'][i]=fb-1
    pre=dict(enabled=True,delay_steps=[i%2 for i in range(8)],episode=[1]*8,cache=copy.deepcopy(old) if old is not None else 'UNKNOWN')
    post=dict(enabled=True,delay_steps=pre['delay_steps'][:],episode=[1]*8,cache=after)
    return dict(call_id=fb*10+list(v.CHANNELS).index(key),key=key,clock=clock(tick),clean_origin='actual feedback raw argument, before noise and lag',
        clean=clean,full_clean35='UNKNOWN',sensor_stage=dict(profile='noise_bias_mild_v1',before=dict(episode=[1]*8,noise_cache_last=[fb-1]*8,draw_counts={key:0}),
        fresh_due_local='UNKNOWN',noise_used=noise,noise_cache_last=[fb]*8,leg_bias_used=bias if key=='leg_pos' else 'UNKNOWN',episode=[1]*8,
        draw_counts={key:80},actual_noisy_return=noisy,dtype='torch.float32'),delay_actual_input=copy.deepcopy(noisy),
        delay_stage=dict(before=pre,after=post,actual_return=copy.deepcopy(after['out']),local_delayed_mask='UNKNOWN'),
        exception=None,**{'return':copy.deepcopy(after['out'])})

def initial_queue(width,group,start=0):
    lag=[(i+(group=='wheels'))%3 for i in range(80)]
    q={k:[] for k in v.QUEUE}
    for i in range(80):
        for k in v.QUEUE:
            if k=='lag_steps': x=lag[i]
            elif k=='episode': x=1
            elif k in ('pending','applied'): x=[(.125 if group=='legs' else .25) if start else 0.]*width
            elif k=='pending_valid': x=False
            elif k=='applied_valid': x=bool(start)
            elif k=='last_apply_tick': x=start-1
            elif k in ('issued_tick','applied_issue_tick','last_submit_tick'): x=start-8 if start else -1
            elif k in ('due_tick','first_apply_tick'): x=start-8+lag[i] if start else -1
            q[k].append(x)
    return q

def window(index,initial=None):
    start=index*8; events=[]; ends={}; seq=index*100
    def event(kind,g,tick,pre,post,args,**kw):
        nonlocal seq
        e=dict(seq=seq,kind=kind,group=g,tick=tick,pre=copy.deepcopy(pre),post=copy.deepcopy(post),args=copy.deepcopy(args),kwargs={},outcome='RETURNED',**kw)
        seq+=1; events.append(e); return e
    for group,width in v.GROUPS.items():
        q=copy.deepcopy(initial[group]) if initial else initial_queue(width,group,start)
        before=copy.deepcopy(q); target=[[.125 if group=='legs' else .25]*width for _ in range(80)]
        for i in range(80):
            q['pending'][i]=target[i][:]; q['pending_valid'][i]=True; q['issued_tick'][i]=start
            q['due_tick'][i]=start+q['lag_steps'][i]; q['last_submit_tick'][i]=start
        issue=event('issue',group,start,before,q,[[[0.]*width for _ in range(80)]])
        event('queue_submit',group,start,before,q,[group,target,start])
        for tick in range(start,start+8):
            before=copy.deepcopy(q)
            for i in range(80):
                if q['pending_valid'][i] and q['due_tick'][i]==tick:
                    q['applied'][i]=q['pending'][i][:]; q['applied_valid'][i]=True; q['applied_issue_tick'][i]=q['issued_tick'][i]
                    q['first_apply_tick'][i]=tick; q['pending_valid'][i]=False
                q['last_apply_tick'][i]=tick
            term=event('term_apply',group,tick,before,q,[])
            event('queue_apply',group,tick,before,q,[group,tick],selected_target=copy.deepcopy(q['applied']))
            event('target_write',group,tick,q,q,[q['applied']],parent_term_apply_seq=term['seq'],physical_readback={'status':'UNKNOWN'})
        ends[group]=copy.deepcopy(q)
    return dict(control_index=index,events=events),ends

def fixture():
    task=dict(kind=v.TASK_KIND,purpose=v.PURPOSE,batch_purpose=v.PURPOSE,integration=v.INTEGRATION,policy_variant=v.POLICY,
        role='E3',requested_roles=['E3'],role_catalog=v.ROLES[:],num_envs=80,seed=20260928,model_PT_reads=0,synthetic_action=[0.]*6,
        train=False,quality_evaluation=False,full_clean35='UNKNOWN',controls=64,physics=copy.deepcopy(v.PHYSICS),
        asset_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',
        overall_eight_pass_rate=None,comparison=None,group_id='SYNTHETIC_NEVER_EXECUTED',GPU_UUID='FAKE_NOT_A_DEVICE',absolute_worker_deadline_epoch=1000.)
    actor=dict(kind='actor35_original_buffer',payload=dict(control_index=0,original_return_identity=True,untapped_bitwise='UNKNOWN',actor35=[[0.]*35 for _ in range(8)]))
    terminal=dict(kind='terminal_pre_reset',payload=dict(clock=clock(8,phase='outside_scene_update'),bridge_pre=dict(s1=[[0.]*73 for _ in range(8)],term=[False]*8,trunc=[False]*8),episode=[1]*8))
    events=[]; memories={}
    for tick in (4,8):
        for key in v.CHANNELS:
            p=feedback(key,tick,memories.get(key)); memories[key]=copy.deepcopy(p['delay_stage']['after']['cache'])
            events.append(dict(sequence=len(events)+1,kind='feedback',payload=p))
    events += [dict(sequence=11,**actor),dict(sequence=12,**terminal)]
    w0,e0=window(0); w1,_=window(1,e0); w62,e62=window(62); w63,_=window(63,e62)
    static=dict(evidence='STORED_SOURCE_CONFIGURATION_OR_MODEL_MEMORY_NOT_PHYSICAL_READBACK',physical_readback={'status':'UNKNOWN'},
        motors={g:{k:[[1.]*width for _ in range(80)] for k in ('episode_scale','step_scale')} for g,width in v.GROUPS.items()})
    final=dict(kind=v.FINAL_KIND,purpose=v.PURPOSE,integration=v.INTEGRATION,role='E3',group_id=task['group_id'],GPU_UUID=task['GPU_UUID'],num_envs=80,
        controls=64,requested_controls=64,physics_callbacks=512,feedback_samples=128,delay_calls=dict(legs=512,wheels=512),passed_execution=True,
        execution_scope='BOUNDED_SYNTHETIC_INTERFACE_NOT_SKILL',policy_variant=v.POLICY,model_PT_reads=0,training_updates=0,optimizer_updates=0,
        learner_created=False,replay_created=False,teacher_created=False,actor35_source='ORIGINAL_RETURNED_POLICY_BUFFER',clean16_only=True,full_clean35='UNKNOWN',
        sensor=dict(bounded=dict(kind='BOUNDED_PASSIVE_CAPTURE_V1',retained_first=events,retained_last=copy.deepcopy(events),capture_errors=0,capture_exhausted=False)),
        actuation=dict(status=dict(dropped_events=0,observer_errors=0,missing_hooks=[],restore_conflicts=[]),static_before=copy.deepcopy(static),static_after=copy.deepcopy(static)),
        boundary=dict(actions=64,original_step_transitions=64,pending_original_step=False),coverage=dict(deficits=['SYNTHETIC_ONLY']),
        rng_counts={k:dict(sensor_draw_counts={c:(0 if k=='before' else 100) for c in v.CHANNELS},observer_rng_draws=0) for k in ('before','after')},
        bounded_trace=dict(sensor_special=dict(reset_boundary=[],terminal_pre_reset=[terminal],actor35_original_buffer=[actor]),
            actuation=dict(control_windows_seen=64,retained_window_bound=4,first=[w0,w1],last=[w62,w63])),
        restore=dict(ok=True,order=['actuation','sensor','bridge'],errors=[]),
        original_setup=dict(started_epoch=10.,GO_epoch=12.,first_control_epoch=14.,last_control_epoch=20.),inconclusive_reasons=['LIVE_VERIFIER_PENDING'],
        interface_coverage_status='INCONCLUSIVE_PENDING_LIVE_VERIFIER',gate1='UNKNOWN',exact=False,capture_interface_passed=False,paper_ready=False,stage2_GO=False,
        skill_success_rate=None,overall_eight_pass_rate=None,reference_comparison=None)
    semantic=dict(kind='PHASE1_CAPTURE_WAITED_EXECUTION_SEMANTICS_V1',purpose=v.PURPOSE,passed_execution=True,errors=[],actual_wait_call_attested_by_caller=True,waited_return_observed_epoch=21.)
    group=dict(kind='PHASE1_PASSIVE_CAPTURE_GROUP_FINAL_V1',purpose=v.PURPOSE,integration=v.INTEGRATION,group_id=task['group_id'],requested_roles=['E3'],deferred_roles=v.ROLES[1:],
        terminal=[dict(role='E3',GPU_UUID=task['GPU_UUID'],pid=222,returncode=0,actual_waited=True,ready=True,started=True,pre_close=True,passed_execution=True,error=None,semantic=semantic,data=final)],
        passed_execution=True,GO_epoch=12.,terminal_epoch=22.,gate1='UNKNOWN',exact=False,stage2_GO=False,capture_interface_passed=False)
    scope=dict(all_own_children_waited=True,original_single_GPU_private_EX_released=True,original_global_finite_EX_released=True,canonical_writes=0,errors=[],no_foreign_scope_touched=True,
        child_waits=[dict(role='E3',pid=222,returncode=0,actual_waited=True)],epoch=23.)
    grade=dict(kind='PHASE1_CAPTURE_CLOSED_SOURCE_GRADE_V1',purpose=v.PURPOSE,passed_closed_capture_execution=True,errors=[],gate1='UNKNOWN',exact=False,stage2_GO=False,capture_interface_passed=False)
    controller=dict(pid=100,linux_start_ticks='111'); parent=dict(pid=200,linux_start_ticks='222')
    sha=v.SOURCE_PINS['source_phase1_capture_worker_v2/single_gpu_passive_capture_parent_v1.py'][1]
    life=dict(group_final=group,parent_exit_scope=scope,source_grade=grade,common_go=dict(kind='PHASE1_PASSIVE_CAPTURE_COMMON_START_V1',purpose=v.PURPOSE,group_id=task['group_id'],members=['E3'],epoch=12.,stage2_GO=False),
        worker_ready=dict(kind=v.INTEGRATION,role='E3',epoch=11.),worker_started=dict(kind=v.INTEGRATION,role='E3',epoch=13.,GO_epoch=12.),
        env_close=dict(closed=True),app_close_binding=dict(fast_shutdown=True),app_fast_intent=dict(kind='PINNED_PHASE1_CAPTURE_FAST_CLOSE_INTENT_V1',binding=dict(fast_shutdown=True),original_env_close_returned=True,final_SHA='a'*64,final_bytes=123456),
        parent_dispatch=dict(kind='ONE_ORIGINAL_PHASE1_CAPTURE_PARENT_POPEN_NOT_RESOURCE_ADMISSION',group_id=task['group_id'],controller=controller,parent=parent,parent_source_SHA=sha,actual_native_parent_Popen_calls=1,epoch=9.),
        controller_started=dict(kind='OWN_PHASE1_CAPTURE_PARENT_ACTUAL_WAIT_CONTROLLER_V1',controller=controller,parent_source_SHA=sha,epoch=8.,controller_resource_SDK_model_C_lock_or_signal_operations=0),
        outer_parent_wait=dict(kind='ACTUAL_EXTERNAL_PARENT_POPEN_WAIT_PHASE1_CAPTURE_V1',group_id=task['group_id'],controller=controller,parent=parent,parent_source_SHA=sha,actual_native_parent_Popen_calls=1,
            actual_parent_p_wait_returned=True,returncode=0,controller_errors=[],epoch=24.,wall_seconds=16.,original_parent_resource_close_wait_not_replaced=True,controller_resource_SDK_model_C_lock_or_signal_operations=0),
        parent_started=dict(pid=200,epoch=10.))
    return final,task,life

def provenance(f,t,l):
    docs={'worker_final':f,'task':t,**l}
    return dict(schema_reference_id=v.SOURCE_ID,schema_source_pins={k:dict(bytes=n,SHA256=s) for k,(n,s) in v.SOURCE_PINS.items()},
        whole_documents={k:dict(original_bytes=123456,original_SHA256='a'*64,decoded_canonical_SHA256=v.digest(value)) for k,value in docs.items() if value is not None})

def row(result,name):
    return next(x for group in ('schema','lifecycle','components') for x in result[group] if x['check']==name)

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.template=fixture()
    def setUp(self): self.f,self.t,self.l=copy.deepcopy(self.template)
    def run_case(self): return v.verify_capture(self.f,self.t,self.l,provenance(self.f,self.t,self.l))
    def component(self,name): return row(self.run_case(),name)
    def test_01_positive_components_not_admission(self):
        r=self.run_case(); self.assertTrue(r['execution']['value']); self.assertEqual(r['status'],'INCONCLUSIVE')
        self.assertTrue(all(x['status']=='CONSISTENT' for x in r['components'])); self.assertEqual(r['gate1'],'UNKNOWN'); self.assertFalse(r['stage2_GO'])
    def test_02_missing_FINAL_null_not_RC0_pass(self):
        r=v.verify_capture(None,self.t,self.l,provenance(None,self.t,self.l)); self.assertEqual(r['status'],'NOT_EVALUABLE'); self.assertIsNone(r['execution']['value']); self.assertIsNone(r['counts'])
    def test_03_projection_not_original_FINAL(self):
        self.f={'controls':64,'passed_execution':True}; self.assertEqual(self.run_case()['status'],'CONTRADICTED')
    def test_04_wrong_producer_or_source_id(self):
        self.f['kind']='QUALITY_FINAL'; self.assertEqual(self.run_case()['status'],'CONTRADICTED')
        p=provenance(*self.template); p['schema_reference_id']='0'*64
        self.assertEqual(v.verify_capture(*self.template,p)['status'],'CONTRADICTED')
        # Consistent new dispatch SHA is a schema fact, not automatic future-producer source qualification.
        f,t,l=copy.deepcopy(self.template)
        for name in ('parent_dispatch','outer_parent_wait','controller_started'): l[name]['parent_source_SHA']='c'*64
        r=v.verify_capture(f,t,l,provenance(f,t,l)); self.assertTrue(r['execution']['value'])
        self.assertEqual(row(r,'published_outer_actual_parent_wait')['detail']['actual_parent_runtime_source_qualification'],'UNKNOWN_EXTERNAL_PRODUCER_BINDING')
    def test_05_task_bool_is_not_int(self):
        self.t['num_envs']=True; self.assertEqual(self.run_case()['status'],'CONTRADICTED')
        self.t=[]; self.assertEqual(self.run_case()['status'],'CONTRADICTED')
    def test_06_clock_counters_bool_or_wrong(self):
        self.f['physics_callbacks']=True; self.assertFalse(self.run_case()['execution']['value'])
        self.f['physics_callbacks']=511; self.assertFalse(self.run_case()['execution']['value'])
    def test_07_typed_finite_timestamp(self):
        self.l['common_go']['epoch']='12'; self.assertFalse(self.run_case()['execution']['value'])
        with self.assertRaises(ValueError): v.number(float('nan'))
    def test_08_child_RC0_without_wait_or_EX(self):
        self.l['parent_exit_scope']['original_global_finite_EX_released']=False; self.assertFalse(self.run_case()['execution']['value'])
    def test_09_outer_actual_wait_rc1_is_fact_not_success(self):
        self.l['outer_parent_wait']['returncode']=1
        r=self.run_case(); rr=row(r,'published_outer_actual_parent_wait'); self.assertEqual(rr['status'],'CONSISTENT'); self.assertTrue(rr['detail']['actual_parent_wait_returned']); self.assertFalse(r['execution']['value'])
    def test_10_outer_dispatch_identity_and_missing(self):
        self.l['outer_parent_wait']=copy.deepcopy(self.l['outer_parent_wait']); self.l['outer_parent_wait']['parent']['linux_start_ticks']='999'
        self.assertFalse(self.run_case()['execution']['value'])
        del self.l['outer_parent_wait']; self.assertIsNone(self.run_case()['execution']['value'])
    def test_11_original_bytes_not_reencoded_intent(self):
        self.l['app_fast_intent']['final_SHA']='b'*64; self.assertFalse(self.run_case()['execution']['value'])
    def test_12_mid_end_and_scene_update_inside_reset(self):
        p=self.f['sensor']['bounded']['retained_first'][0]['payload']; p['clock']=clock(4,depth=1)
        self.f['sensor']['bounded']['retained_last']=[]
        self.assertEqual(self.component('clean16_used_noise_bias_delay_and_episode_clock')['status'],'CONSISTENT')
        p['clock']['is_original_100hz_slot']=True
        self.assertEqual(self.component('clean16_used_noise_bias_delay_and_episode_clock')['status'],'CONTRADICTED')
    def test_13_noise_formula_and_shape(self):
        self.f['sensor']['bounded']['retained_last']=[]
        p=self.f['sensor']['bounded']['retained_first'][0]['payload']; p['sensor_stage']['actual_noisy_return'][0][0]+=1
        self.assertEqual(self.component('clean16_used_noise_bias_delay_and_episode_clock')['status'],'CONTRADICTED')
    def test_14_warmup_current_not_old_episode(self):
        self.f['sensor']['bounded']['retained_last']=[]
        self.f['sensor']['bounded']['retained_first'][0]['payload']['delay_stage']['after']['cache']['ready'][0]=True
        self.assertEqual(self.component('clean16_used_noise_bias_delay_and_episode_clock')['status'],'CONTRADICTED')
    def test_15_actual_delay_cur_out_sample_selection(self):
        self.f['sensor']['bounded']['retained_last']=[]
        self.f['sensor']['bounded']['retained_first'][5]['payload']['delay_stage']['after']['cache']['sample_tick'][1]=2
        self.assertEqual(self.component('clean16_used_noise_bias_delay_and_episode_clock')['status'],'CONTRADICTED')
    def test_16_sameTick_reuse_new_raw_does_not_force_fresh(self):
        p=copy.deepcopy(self.f['sensor']['bounded']['retained_first'][0]['payload']); old=copy.deepcopy(p['delay_stage']['after']['cache'])
        p['clean'][0][0]+=1; p['sensor_stage']['actual_noisy_return'][0][0]+=1; p['delay_actual_input'][0][0]+=1
        p['delay_stage']['before']['cache']=old
        v.feedback_record(p,{})
        p['delay_stage']['after']['cache']['out'][0][0]+=1
        with self.assertRaises(ValueError): v.feedback_record(p,{})
    def test_17_actor_sameobject_not_bitwise_counterfactual(self):
        r=self.component('original_actor_same_buffer_sanity'); self.assertEqual(r['detail']['untapped_counterfactual_bitwise'],'UNKNOWN')
        self.f['sensor']['bounded']['retained_last']=[]  # avoid a different-payload duplicate masking this assertion
        for e in self.f['bounded_trace']['sensor_special']['actor35_original_buffer']: e['payload']['untapped_bitwise']=True
        self.assertEqual(self.component('original_actor_same_buffer_sanity')['status'],'CONTRADICTED')
    def test_18_retention_not_whole64(self):
        r=self.component('retained_actuation_queue_issue_apply_write')['detail']; self.assertEqual(r['retained_control_indices'],[0,1,62,63]); self.assertTrue(r['not_all_controls_retained'])
    def test_19_due_first_latency_and_held_age(self):
        r=self.component('retained_actuation_queue_issue_apply_write')['detail']; self.assertEqual(r['first_transition_latency_us']['legs'],[0,2500,5000]); self.assertGreater(r['max_held_age_us']['legs'],5000)
        self.f['bounded_trace']['actuation']['first'][0]['events'][1]['post']['due_tick'][0]+=1
        self.assertEqual(self.component('retained_actuation_queue_issue_apply_write')['status'],'CONTRADICTED')
    def test_20_original_writer_linkage_and_4plus2_shape(self):
        es=self.f['bounded_trace']['actuation']['first'][0]['events']; e=next(e for e in es if e['kind']=='target_write'); e['args'][0][0][0]+=1
        self.assertEqual(self.component('retained_actuation_queue_issue_apply_write')['status'],'CONTRADICTED')
        self.f,self.t,self.l=copy.deepcopy(self.template)
        # A locally valid held-value transition must not teleport between consecutive callbacks.
        es=self.f['bounded_trace']['actuation']['first'][0]['events']
        for e in es:
            if e['group']=='legs' and e['tick']==1 and e['kind'] in ('term_apply','queue_apply','target_write'):
                for side in ('pre','post'): e[side]['applied'][0][0]+=1
                if e['kind']=='queue_apply': e['selected_target'][0][0]+=1
                if e['kind']=='target_write': e['args'][0][0][0]+=1
        self.assertEqual(self.component('retained_actuation_queue_issue_apply_write')['status'],'CONTRADICTED')
    def test_21_missing_apply_tick_not_full_trace_assumption(self):
        es=self.f['bounded_trace']['actuation']['first'][0]['events']; es[:]=[e for e in es if not(e['kind']=='queue_apply' and e['group']=='legs' and e['tick']==3)]
        self.assertEqual(self.component('retained_actuation_queue_issue_apply_write')['status'],'UNKNOWN')
    def test_22_actuation_partial_reset_no_unselected_pollution(self):
        first=self.f['bounded_trace']['actuation']['first']; end={g:copy.deepcopy(next(e for e in reversed(first[0]['events']) if e['kind']=='queue_apply' and e['group']==g)['post']) for g in v.GROUPS}
        for g,q in end.items():
            q['episode'][0]+=1; q['pending'][0]=[0.]*v.GROUPS[g]; q['applied'][0]=[0.]*v.GROUPS[g]
            q['pending_valid'][0]=q['applied_valid'][0]=False
            for k in ('issued_tick','due_tick','applied_issue_tick','first_apply_tick','last_submit_tick'): q[k][0]=-1
        first[1],_=window(1,end)
        self.assertEqual(self.component('retained_actuation_queue_issue_apply_write')['detail']['adjacent_reset_group_rows'],2)
        end['legs']['applied'][1][0]+=1; first[1],_=window(1,end)
        self.assertEqual(self.component('retained_actuation_queue_issue_apply_write')['status'],'CONTRADICTED')
    def test_23_terminal_pre_reset_and_sensor_partial_reset(self):
        term=self.f['bounded_trace']['sensor_special']['terminal_pre_reset'][0]['payload']; term['bridge_pre']['term'][0]=True
        for e in self.f['sensor']['bounded']['retained_first']+self.f['sensor']['bounded']['retained_last']:
            if e['kind']=='terminal_pre_reset': e['payload']['bridge_pre']['term'][0]=True
        before=dict(sensor_episode=[1]*8,delay_episode=[1]*8,queue={k:copy.deepcopy(self.f['sensor']['bounded']['retained_first'][5+i]['payload']['delay_stage']['after']['cache']) for i,k in enumerate(v.CHANNELS)})
        after=copy.deepcopy(before)
        for k in ('sensor_episode','delay_episode'): after[k][0]+=1
        for q in after['queue'].values(): q['last'][0]=-1; q['sample_tick'][0]=-1; q['ready'][0]=False
        reset=dict(kind='reset_boundary',payload=dict(clock=clock(8,phase='outside_scene_update'),ids=[0],before=before,after=after,exception=None))
        self.f['bounded_trace']['sensor_special']['reset_boundary']=[reset]
        self.assertEqual(self.component('pre_reset_bridge_and_partial_reset')['detail']['linked_reset_edges'],1)
        after['queue']['base_ang_vel']['cur'][1][0]+=1
        self.assertEqual(self.component('pre_reset_bridge_and_partial_reset')['status'],'CONTRADICTED')
    def test_24_missing_dtype_and_no_static_readback_claim(self):
        self.f['sensor']['bounded']['retained_first'][0]['payload']['sensor_stage']['dtype']='UNKNOWN'; self.f['sensor']['bounded']['retained_last']=[]
        self.assertEqual(self.component('clean16_used_noise_bias_delay_and_episode_clock')['status'],'UNKNOWN')
        self.f['actuation']['static_before']['physical_readback']={'status':'MEASURED'}
        self.assertEqual(self.component('stored_RNG_static_memory_and_source_claims')['status'],'CONTRADICTED')
    def test_25_input_RNG_purity_and_builtin_output(self):
        p=provenance(self.f,self.t,self.l); before=v.digest([self.f,self.t,self.l,p]); rng=random.getstate()
        r=v.verify_capture(self.f,self.t,self.l,p); self.assertEqual(before,v.digest([self.f,self.t,self.l,p])); self.assertEqual(rng,random.getstate()); v.digest(r)
    def test_26_duplicate_records_and_decoded_pin_tamper(self):
        self.f['sensor']['bounded']['retained_last'][0]['payload']['key']='leg_vel'
        self.assertEqual(self.component('sensor_retention_schema')['status'],'CONTRADICTED')
        p=provenance(self.f,self.t,self.l); p['whole_documents']['worker_final']['decoded_canonical_SHA256']='b'*64
        self.assertEqual(v.verify_capture(self.f,self.t,self.l,p)['status'],'CONTRADICTED')
    def test_27_processor_AST_stdlib_no_I_O_or_entrypoint(self):
        tree=ast.parse(Path(v.__file__).read_text(encoding='utf8'))
        self.assertEqual({a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names},{'copy','hashlib','json','math','struct'})
        self.assertFalse(any(isinstance(n,ast.ImportFrom) for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'open','eval','exec','compile','__import__','input'} for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in {'read_bytes','read_text','write_bytes','write_text','load','dump','system','Popen','run'} for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n,(ast.If,ast.For,ast.While,ast.With,ast.Try)) for n in tree.body))

if __name__=='__main__': unittest.main(verbosity=2)
