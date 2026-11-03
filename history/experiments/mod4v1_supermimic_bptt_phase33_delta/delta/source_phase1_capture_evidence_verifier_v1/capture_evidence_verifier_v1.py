"""Pure decoded ORIGINAL whole-FINAL processor; no I/O, target imports or admission.
Input/output schema and limitations: SCOPE_AND_API_V1.md. SOURCE/fake != live.
"""
import copy
import hashlib
import json
import math
import struct

PURPOSE = 'NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN'
TASK_KIND = 'PHASE1_PASSIVE_CAPTURE_E3_N80_TASK_V1'
FINAL_KIND = 'PHASE1_PASSIVE_CAPTURE_E3_N80_FINAL_V1'
INTEGRATION = 'PHASE1_CAPTURE_WORKER_SOURCE_V1'
POLICY = 'EXPLICIT_SYNTHETIC_ZERO6_NOT_POLICY_QUALITY'
SOURCE_ID = '83cb35d61298fdac4d2c720d1322ada0fbfa43b866709b4e5958b99ac82b62d2'
ROLES = ['E3','W35','CURB_INDEPENDENT113','CURB_PROTECTED878','SLOPE135','SLOPE_INDEPENDENT50','E0','E2']
PHYSICS = dict(physics_dt=.0025, control_dt=.02, decimation=8, feedback_hz=100, TGS=[32,4], closure=.01, mimic=.01)
CHANNELS = {'base_ang_vel':3,'projected_gravity':3,'leg_pos':4,'leg_vel':4,'wheel_vel':2}
GROUPS = {'legs':4,'wheels':2}
QUEUE = ('lag_steps','episode','pending','pending_valid','issued_tick','due_tick','applied','applied_valid','applied_issue_tick','first_apply_tick','last_submit_tick','last_apply_tick')
SOURCE_PINS = {
 'source_phase1_capture_worker_v2/phase1_capture_contract.py': (9518,'7910d7f3378923275b430b7960ed833f79b394feb3317c857d3a98c501729a0a'),
 'source_phase1_capture_worker_v2/phase1_capture_observer.py': (10438,'8a6faa66d55d4498fd1249aaabfeb9dfd7bb9e0b01013137adce3756b3c9004c'),
 'source_phase1_capture_worker_v2/worker_passive_interface_v1.py': (16323,'f2b7326efb546f0a274c978aa69c126506ed0d3c3a8a1792d80893fa9f163b0b'),
 'source_phase1_capture_worker_v2/phase1_capture_runtime.py': (19145,'490dcb8fd561b8db3af78db29db59d28b6dea33e7a8026609f3d1ddb62a93017'),
 'source_phase1_capture_worker_v2/single_gpu_passive_capture_parent_v1.py': (9336,'d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41'),
 'source_phase1_capture_worker_v2/SOURCE_SEAL.json': (2815,'caacf07e8bc46bd2cc5f4fa14138782430d86de4f6382bbb35adcdcde5d469d5'),
 'source_phase1_passive_sensor_capture_v1/passive_capture.py': (25610,'7df0694d6eb53d822395d7f5ccb066783a8b8fdefc80834096e5f32a5b677df8'),
 'source_phase1_passive_sensor_capture_v1/source_api.py': (11488,'324ac762b755f5e957d8c69e8f177a674ad3b5f3f23c491f720e1711348bd26c'),
 'source_phase1_actuation_capture_v1/actuation_tap.py': (18278,'b9b9e288124a1ba8c031a030c00a231f4d02d2ba7efee9981141ae90b8e28828'),
 'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/sensor_mild_math.py': (3733,'aa853a74a2c2d8840d003caab13a853bade0d761cf7966e4d13c200b929817b8'),
 'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/feedback_delay_mild.py': (3031,'90b339a6d3690294798befefb33e7f27cb7c3bfa0d8e38c98312e207685b5665'),
 'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/feedback_delay_runtime.py': (7380,'f16671c72f90aab85769e4010a91af5fadb286b0d1ac7d2561fe52e8c2ca97e8'),
 'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/action_delay_physics_queue.py': (8511,'a4238c581611ef7cdb710692291ddac48e076364b0587f631eb71fd6a7d15eb8'),
 'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/action_delay_sdk_adapter.py': (5209,'ecd1db05a0dfe215cdf089ccf346aea1a5c51d7974a2bcd6e486dff66b7f5494'),
 'source_runtime/native_supermimic_bridge.py': (13125,'8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29'),
 'source_phase1_capture_controller_v1/phase1_capture_parent_actual_wait_controller_v1.py': (3824,'95952059e6e8640a5ba37e858ca29c5f313340e041260093ecc8aaf671665831'),
 'source_phase1_capture_controller_v1/SOURCE_SEAL.json': (1057,'0f8f7ecb86bdd9d45433eec6dd7b1d120ed41479487b2cf155a9dcff79cd8f22'),
}

class Missing(ValueError):
    """Unretained/unpublished evidence is not a false measurement."""

def require(ok, text):
    if not ok: raise ValueError(text)

def field(obj, key):
    if type(obj) is not dict or key not in obj: raise Missing('missing field: '+key)
    value = obj[key]
    if value == 'UNKNOWN' or (type(value) is dict and value.get('status') == 'UNKNOWN'):
        raise Missing('explicit UNKNOWN: '+key)
    return value

def integer(x, low=None):
    require(type(x) is int and (low is None or x >= low), 'typed integer/range')
    return x

def number(x):
    require(type(x) in (int,float) and math.isfinite(x), 'finite number, not bool')
    return x

def vector(x, n, kind=int):
    require(type(x) is list and len(x)==n, 'decoded vector shape')
    for v in x:
        if kind is float: number(v)
        else: require(type(v) is kind, 'decoded scalar type')
    return x

def matrix(x, n, width):
    require(type(x) is list and len(x)==n, 'decoded matrix rows')
    for row in x: vector(row,width,float)
    return x

def typed_equal(a,b):
    if type(a) is not type(b): return False
    if type(a) is dict: return a.keys()==b.keys() and all(typed_equal(a[k],b[k]) for k in a)
    if type(a) is list: return len(a)==len(b) and all(typed_equal(x,y) for x,y in zip(a,b))
    return a==b

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def hexsha(x):
    return type(x) is str and len(x)==64 and all(c in '0123456789abcdef' for c in x)

def checked(out, group, name, fn):
    try:
        detail=fn()
        row=dict(check=name,status='CONSISTENT',detail=detail)
    except Missing as e: row=dict(check=name,status='UNKNOWN',detail=str(e))
    except (ValueError,TypeError,KeyError,IndexError,OverflowError,struct.error) as e:
        row=dict(check=name,status='CONTRADICTED',detail=str(e))
    out[group].append(row)
    return row

def task_contract(t):
    require(type(t) is dict,'task mapping required')
    expected=dict(kind=TASK_KIND,purpose=PURPOSE,batch_purpose=PURPOSE,integration=INTEGRATION,policy_variant=POLICY,
        role='E3',requested_roles=['E3'],role_catalog=ROLES,num_envs=80,seed=20260928,model_PT_reads=0,
        synthetic_action=[0.,0.,0.,0.,0.,0.],train=False,quality_evaluation=False,full_clean35='UNKNOWN',physics=PHYSICS,
        asset_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',
        contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755')
    for k,v in expected.items(): require(k in t and typed_equal(t[k],v),'task differs: '+k)
    require(type(t.get('controls')) is int and t['controls'] in (64,128),'controls64/128')
    require(all(t.get(k) is None for k in ('overall_eight_pass_rate','comparison')),'no skill/comparison')
    require(not any(k in t for k in ('teacher_path','source_path','checkpoint','a1_producer')),'no model fallback')
    require(type(t.get('group_id')) is str and t['group_id'] and type(t.get('GPU_UUID')) is str,'group/GPU identity')
    number(field(t,'absolute_worker_deadline_epoch'))
    return {'controls':t['controls'],'N':80,'seed':20260928}

def provenance_contract(p, docs):
    require(field(p,'schema_reference_id')==SOURCE_ID,'schema/method reference id differs')
    pins=field(p,'schema_source_pins')
    for name,(size,sha) in SOURCE_PINS.items():
        require(typed_equal(field(pins,name),{'bytes':size,'SHA256':sha}),'source pin differs: '+name)
    records=field(p,'whole_documents')
    for name,value in docs.items():
        if value is None: continue
        pin=field(records,name)
        integer(field(pin,'original_bytes'),1)
        require(hexsha(field(pin,'original_SHA256')),'original byte SHA syntax')
        require(field(pin,'decoded_canonical_SHA256')==digest(value),'decoded whole-document digest: '+name)
    return {'binding':'caller-supplied original-byte identities + decoded canonical digest; not authenticated I/O','documents':sorted(docs),
        'source_pin_scope':'17 frozen V2+B1+C+controller SCHEMA/METHOD references, not future whole-runtime provenance',
        'actual_producer_runtime_binding':'UNKNOWN_EXTERNAL_EXACT_INDEX_AND_SEAL_BINDING_NOT_PERFORMED'}

def final_contract(f,t):
    require(type(f) is dict,'ORIGINAL whole worker FINAL mapping')
    for k in ('sensor','actuation','boundary','coverage','rng_counts','bounded_trace','restore','original_setup','inconclusive_reasons'):
        require(k in f,'whole FINAL field absent (projection is not accepted): '+k)
    for k,v in dict(kind=FINAL_KIND,purpose=PURPOSE,integration=INTEGRATION,role='E3',num_envs=80,policy_variant=POLICY,
        actor35_source='ORIGINAL_RETURNED_POLICY_BUFFER',clean16_only=True,full_clean35='UNKNOWN',model_PT_reads=0,
        training_updates=0,optimizer_updates=0,learner_created=False,replay_created=False,teacher_created=False,
        gate1='UNKNOWN',exact=False,capture_interface_passed=False,paper_ready=False,stage2_GO=False).items():
        require(typed_equal(f.get(k),v),'FINAL producer/scope field: '+k)
    require(f.get('group_id')==t['group_id'] and f.get('GPU_UUID')==t['GPU_UUID'],'FINAL task identity')
    require(all(f.get(k) is None for k in ('skill_success_rate','overall_eight_pass_rate','reference_comparison')),'no skill promotion')
    require(type(f.get('passed_execution')) is bool,'typed producer execution claim')
    require(type(f['inconclusive_reasons']) is list,'deficits retained')
    return 'original V2 worker schema; producer claims remain separate from observation checks'

def execution(f,t):
    c=integer(field(f,'controls'),0); require(c==t['controls'],'incomplete controls')
    require(integer(field(f,'requested_controls'))==t['controls'],'requested control binding')
    require(integer(field(f,'physics_callbacks'))==8*c and integer(field(f,'feedback_samples'))==2*c,'50/400/100Hz counters')
    require(typed_equal(field(f,'delay_calls'),dict(legs=8*c,wheels=8*c)),'two original delay counters')
    b=field(f,'boundary')
    require(integer(field(b,'actions'))==c and integer(field(b,'original_step_transitions'))==c,'original step/action counts')
    require(field(b,'pending_original_step') is False,'pending step')
    restore=field(f,'restore')
    require(restore.get('ok') is True and restore.get('order')==['actuation','sensor','bridge'] and restore.get('errors')==[],'reverse restore receipt')
    require(f['passed_execution'] is True,'producer did not complete')
    return dict(controls=c,physics=8*c,feedback=2*c,scope='published worker counters, not all retained records or skill')

def outer_wait_contract(l,t):
    dispatch=field(l,'parent_dispatch'); waited=field(l,'outer_parent_wait'); started=field(l,'controller_started')
    require(dispatch.get('kind')=='ONE_ORIGINAL_PHASE1_CAPTURE_PARENT_POPEN_NOT_RESOURCE_ADMISSION','published dispatch kind')
    require(waited.get('kind')=='ACTUAL_EXTERNAL_PARENT_POPEN_WAIT_PHASE1_CAPTURE_V1','published outer wait kind')
    require(started.get('kind')=='OWN_PHASE1_CAPTURE_PARENT_ACTUAL_WAIT_CONTROLLER_V1','published controller start')
    for d in (dispatch,waited):
        require(d.get('group_id')==t['group_id'],'outer group identity')
        require(type(d.get('actual_native_parent_Popen_calls')) is int and d['actual_native_parent_Popen_calls']==1,'one original parent Popen')
        for name in ('controller','parent'):
            ident=field(d,name); integer(field(ident,'pid'),1)
            ticks=field(ident,'linux_start_ticks'); require(type(ticks) is str and ticks.isdecimal(),'published start ticks type')
            other=field(dispatch,name)
            require(ident['pid']==other['pid'] and ticks==other['linux_start_ticks'],'original dispatch envelope identity')
    parent_sha=field(dispatch,'parent_source_SHA'); require(hexsha(parent_sha),'published parent SHA syntax')
    for d in (dispatch,waited,started): require(d.get('parent_source_SHA')==parent_sha,'same original dispatch parent SHA')
    require(started.get('controller')==dispatch['controller'],'controller identity')
    require(waited.get('actual_parent_p_wait_returned') is True and waited.get('original_parent_resource_close_wait_not_replaced') is True,'actual parent wait/finally retained')
    for d in (started,waited): require(type(d.get('controller_resource_SDK_model_C_lock_or_signal_operations')) is int and d['controller_resource_SDK_model_C_lock_or_signal_operations']==0,'controller declared scope')
    rc=integer(field(waited,'returncode')); errors=field(waited,'controller_errors'); require(type(errors) is list,'controller errors list')
    require(number(field(started,'epoch'))<=number(field(dispatch,'epoch'))<=number(field(waited,'epoch')),'outer timestamp order')
    require(number(field(waited,'wall_seconds'))>=0,'outer wall duration')
    ps=field(l,'parent_started'); require(ps.get('pid')==dispatch['parent']['pid'],'original parent started pid')
    require(number(field(field(l,'parent_exit_scope'),'epoch'))<=waited['epoch'],'wait after parent exit/finally publication')
    return {'actual_parent_wait_returned':True,'returncode':rc,'successful_closed_execution':rc==0 and not errors,
            'parent_source_SHA_bound_to_dispatch':parent_sha,'actual_parent_runtime_source_qualification':'UNKNOWN_EXTERNAL_PRODUCER_BINDING',
            'scope':'decoded published wait/dispatch identity facts, no PID-gone, old-runtime-only or new costwriter gate'}

def lifecycle_contract(l,t,f,p):
    gf=field(l,'group_final'); scope=field(l,'parent_exit_scope'); grade=field(l,'source_grade')
    require(gf.get('kind')=='PHASE1_PASSIVE_CAPTURE_GROUP_FINAL_V1' and gf.get('purpose')==PURPOSE and gf.get('integration')==INTEGRATION,'group producer')
    require(gf.get('group_id')==t['group_id'] and gf.get('requested_roles')==['E3'] and gf.get('deferred_roles')==ROLES[1:],'group membership')
    require(gf.get('passed_execution') is True,'group execution false')
    rows=field(gf,'terminal'); require(type(rows) is list and len(rows)==1,'one whole terminal row')
    row=rows[0]
    require(row.get('role')=='E3' and row.get('GPU_UUID')==t['GPU_UUID'] and type(row.get('pid')) is int,'typed child identity')
    require(type(row.get('returncode')) is int and row['returncode']==0 and row.get('actual_waited') is True,'actual child wait, not RC0 alone')
    require(all(row.get(k) is True for k in ('ready','started','pre_close','passed_execution')) and row.get('error') is None,'worker error/start/close')
    require(typed_equal(row.get('data'),f),'terminal.data must be ORIGINAL whole worker FINAL')
    sem=field(row,'semantic')
    require(sem.get('kind')=='PHASE1_CAPTURE_WAITED_EXECUTION_SEMANTICS_V1' and sem.get('purpose')==PURPOSE and sem.get('passed_execution') is True and sem.get('errors')==[],'waited semantic')
    require(sem.get('actual_wait_call_attested_by_caller') is True,'child wait attestation')
    wait_epoch=number(field(sem,'waited_return_observed_epoch'))
    require(scope.get('all_own_children_waited') is True and scope.get('original_single_GPU_private_EX_released') is True and scope.get('original_global_finite_EX_released') is True,'all waits/two EX release')
    require(type(scope.get('canonical_writes')) is int and scope['canonical_writes']==0 and scope.get('errors')==[] and scope.get('no_foreign_scope_touched') is True,'exit scope errors')
    waits=field(scope,'child_waits'); require(type(waits) is list and len(waits)==1,'one finally wait')
    w=waits[0]; require(w.get('role')=='E3' and typed_equal(w.get('pid'),row['pid']) and type(w.get('returncode')) is int and w['returncode']==0 and w.get('actual_waited') is True,'finally actual wait linkage')
    require(grade.get('kind')=='PHASE1_CAPTURE_CLOSED_SOURCE_GRADE_V1' and grade.get('purpose')==PURPOSE and grade.get('passed_closed_capture_execution') is True and grade.get('errors')==[],'closed source grade')
    for doc in (gf,grade): require(doc.get('gate1')=='UNKNOWN' and doc.get('exact') is False and doc.get('stage2_GO') is False and doc.get('capture_interface_passed') is False,'lifecycle is not admission')
    require(number(field(gf,'terminal_epoch'))<=number(field(scope,'epoch')),'parent exit timestamp')
    go=field(l,'common_go'); ready=field(l,'worker_ready'); start=field(l,'worker_started')
    require(go.get('kind')=='PHASE1_PASSIVE_CAPTURE_COMMON_START_V1' and go.get('purpose')==PURPOSE and go.get('group_id')==t['group_id'] and go.get('members')==['E3'],'common GO identity')
    require(go.get('stage2_GO') is False,'passive GO is not stage2')
    for doc in (ready,start): require(doc.get('kind')==INTEGRATION and doc.get('role')=='E3','ready/start producer')
    setup=field(f,'original_setup')
    epochs=[number(field(setup,'started_epoch')),number(field(ready,'epoch')),number(field(go,'epoch')),number(field(start,'epoch')),number(field(setup,'first_control_epoch')),number(field(setup,'last_control_epoch')),wait_epoch,number(field(gf,'terminal_epoch')),number(field(scope,'epoch'))]
    require(epochs==sorted(epochs),'typed timestamp order')
    require(typed_equal(start.get('GO_epoch'),go['epoch']) and typed_equal(setup.get('GO_epoch'),go['epoch']) and typed_equal(gf.get('GO_epoch'),go['epoch']),'same GO timestamp')
    require(field(field(l,'env_close'),'closed') is True,'original env close')
    binding=field(l,'app_close_binding'); require(type(field(binding,'fast_shutdown')) is bool,'typed close mode')
    if binding['fast_shutdown']:
        intent=field(l,'app_fast_intent'); pin=field(field(p,'whole_documents'),'worker_final')
        require(intent.get('kind')=='PINNED_PHASE1_CAPTURE_FAST_CLOSE_INTENT_V1' and intent.get('binding')==binding and intent.get('original_env_close_returned') is True,'fast intent binding')
        require(intent.get('final_SHA')==pin['original_SHA256'] and typed_equal(intent.get('final_bytes'),pin['original_bytes']),'intent binds original bytes, not canonical reencoding')
    else:
        returned=field(l,'app_close_returned'); require(returned.get('returned') is True and returned.get('binding')==binding,'actual App close returned')
    require(not l.get('worker_error') and not l.get('parent_error'),'published primary error')
    return {'child_waits':1,'two_EX_released':True,'timestamps':epochs,'outer_parent_wait':'SEPARATE_PUBLISHED_CONTROLLER_WAIT_CHECK','App_binding_full_SDK_provenance':'UNKNOWN'}

def retained_sensor(f):
    b=field(field(f,'sensor'),'bounded'); require(b.get('kind')=='BOUNDED_PASSIVE_CAPTURE_V1','B1 recorder schema')
    first=field(b,'retained_first'); last=field(b,'retained_last')
    require(type(first) is list and type(last) is list and len(first)<=32 and len(last)<=32,'bounded sensor first/last')
    require(integer(field(b,'capture_errors'),0)==0 and field(b,'capture_exhausted') is False,'sensor loss/error')
    events={}
    for e in first+last:
        seq=integer(field(e,'sequence'),1); require(type(e.get('kind')) is str,'event kind')
        require(seq not in events or typed_equal(events[seq],e),'same sequence/different payload')
        events[seq]=e
    values=list(events.values())
    special=field(field(f,'bounded_trace'),'sensor_special')
    for kind in ('reset_boundary','terminal_pre_reset','actor35_original_buffer'):
        rows=field(special,kind); require(type(rows) is list and len(rows)<=4,'special cap')
        for e in rows:
            require(e.get('kind')==kind,'special kind')
            if not any(x.get('kind')==kind and typed_equal(x.get('payload'),e.get('payload')) for x in values): values.append(e)
    return values

def clock(c):
    tick=integer(field(c,'physics_tick'),0); fb=integer(field(c,'feedback_tick'),0); depth=integer(field(c,'reset_depth'),0)
    integer(field(c,'common_control_counter'),0)
    require(integer(field(c,'sim_time_us'))==tick*2500,'physics clock us')
    phase=field(c,'phase'); require(phase in ('scene_update','inside_reset','outside_scene_update'),'clock phase')
    slot='mid' if tick%8==4 else 'end' if tick>0 and tick%8==0 else 'UNKNOWN'
    require(c.get('control_slot')==slot,'MID/END slot')
    normal=phase=='scene_update' and depth==0 and tick%4==0
    require(type(c.get('is_original_100hz_slot')) is bool and c['is_original_100hz_slot']==normal,'reset-internal update counted as normal')
    if normal: require(fb==tick//4,'100Hz feedback clock')
    return tick,fb,normal

def f32(x): return struct.unpack('f',struct.pack('f',x))[0]

def feedback_record(p, memo):
    key=field(p,'key'); require(key in CHANNELS,'five channel identity')
    width=CHANNELS[key]; clean=matrix(field(p,'clean'),8,width); s=field(p,'sensor_stage'); d=field(p,'delay_stage')
    tick,fb,normal=clock(field(p,'clock')); require(p.get('exception') is None,'original feedback raised')
    require(p.get('full_clean35')=='UNKNOWN','clean16 is not full clean35')
    ep=vector(field(s,'episode'),8); before=field(s,'before')
    require(vector(field(before,'episode'),8)==ep,'sensor reset inside apply')
    noisy=matrix(field(s,'actual_noisy_return'),8,width); profile=field(s,'profile')
    if profile=='off': require(noisy==clean,'profile off value identity')
    else:
        require(profile=='noise_bias_mild_v1','pinned sensor profile')
        if field(s,'dtype')!='torch.float32': raise Missing('only declared noisy float32 conditional arithmetic supported; other/input tensor dtypes unmeasured')
        noise=matrix(field(s,'noise_used'),8,width)
        bias=matrix(field(s,'leg_bias_used'),8,width) if key=='leg_pos' else [[0.]*width for _ in range(8)]
        require(vector(field(s,'noise_cache_last'),8)==[fb]*8,'noise cache tick')
        for i in range(8):
            expected=[f32(f32(a+b)+c) for a,b,c in zip(clean[i],noise[i],bias[i])]
            require(noisy[i]==expected,'decoded float32 clean+used-noise+bias value mismatch')
            identity=(key,ep[i],fb,i)
            require(identity not in memo or memo[identity]==noise[i],'same episode/tick noise cache changed')
            memo[identity]=noise[i]
    require(matrix(field(p,'delay_actual_input'),8,width)==noisy,'actual delay input != noisy output')
    require(matrix(field(d,'actual_return'),8,width)==matrix(field(p,'return'),8,width),'feedback return/delay return')
    pre=field(d,'before'); post=field(d,'after')
    require(vector(field(post,'episode'),8)==ep and vector(field(pre,'episode'),8)==ep,'sensor/delay episode lineage')
    enabled=field(post,'enabled'); require(type(enabled) is bool and typed_equal(pre.get('enabled'),enabled),'delay mode changed')
    if not enabled:
        require(p['return']==noisy,'disabled delay output')
        return dict(key=key,tick=tick,feedback_tick=fb,normal=normal,episode=ep,slot=p['clock']['control_slot'])
    lag=vector(field(post,'delay_steps'),8); require(lag==vector(field(pre,'delay_steps'),8) and all(x in (0,1) for x in lag),'0/1 feedback lag')
    after=field(post,'cache'); old=pre.get('cache')
    for name in ('last','sample_tick'): vector(field(after,name),8)
    vector(field(after,'ready'),8,bool)
    for name in ('cur','out'): matrix(field(after,name),8,width)
    require(p['return']==after['out'],'original delayed selection return')
    if old=='UNKNOWN': old={'last':[-1]*8,'cur':noisy,'out':noisy,'sample_tick':[-1]*8,'ready':[False]*8}
    for name in ('last','sample_tick'): vector(field(old,name),8)
    vector(field(old,'ready'),8,bool)
    for name in ('cur','out'): matrix(field(old,name),8,width)
    for i in range(8):
        last=old['last'][i]
        if last==fb:
            require(all(after[k][i]==old[k][i] for k in ('last','sample_tick','cur','out','ready')),'sameTick delay cache changed')
        else:
            require(last<0 or last==fb-1,'skipped/reversed per-row feedback clock')
            delayed=lag[i]==1 and last>=0
            require(after['last'][i]==fb and after['cur'][i]==noisy[i],'fresh delay input/cache')
            require(after['out'][i]==(old['cur'][i] if delayed else noisy[i]),'delay cur/out selection')
            require(after['sample_tick'][i]==(last if delayed else fb) and after['ready'][i]==(last>=0),'warmup/sample_tick/ready')
    return dict(key=key,tick=tick,feedback_tick=fb,normal=normal,episode=ep,slot=p['clock']['control_slot'])

def sensor_component(events):
    memo={}; metrics=[]
    for e in sorted((e for e in events if e['kind']=='feedback'),key=lambda e:e['payload'].get('call_id',0)):
        integer(field(e['payload'],'call_id'),1); metrics.append(feedback_record(e['payload'],memo))
    if not metrics: raise Missing('no retained feedback events')
    pairs={}; slots=set()
    for m in metrics:
        if not m['normal']: continue
        slots.add((m['key'],m['tick'],m['feedback_tick']))
        for i,ep in enumerate(m['episode']):
            ident=(m['key'],i,ep,(m['tick']-1)//8)
            pairs.setdefault(ident,set()).add(m['slot'])
    return {'retained_feedback_records':len(metrics),'unique_normal_channel_slots':len(slots),
        'same_episode_mid_end_witness_pairs':sum(s=={'mid','end'} for s in pairs.values()),
        'retained_channels':sorted({m['key'] for m in metrics}),
        'row_mapping':'SOURCE_DECLARED row_ids0..7; no per-tensor row metadata survived materialize',
        'dtype':'actual_noisy_return dtype string only; input/cache tensor dtypes UNKNOWN',
        'formula_scope':'decoded value consistency under source-expected float32 additions, NOT bitwise/multi-dtype proof',
        'fresh_due_local':'UNKNOWN_NOT_CAPTURED; freshness constraints inferred from stored per-row cache/episode only'}

def reset_component(events):
    terms=[e['payload'] for e in events if e['kind']=='terminal_pre_reset']; resets=[e['payload'] for e in events if e['kind']=='reset_boundary']
    natural=0; linked=0
    for p in terms:
        clock(field(p,'clock')); b=field(p,'bridge_pre'); matrix(field(b,'s1'),8,73)
        flags=list(zip(vector(field(b,'term'),8,bool),vector(field(b,'trunc'),8,bool)))
        natural+=sum(a or b for a,b in flags); vector(field(p,'episode'),8)
    for p in resets:
        clock(field(p,'clock')); require(p.get('exception') is None,'original reset raised')
        ids=field(p,'ids'); require(type(ids) is list and len(ids)==len(set(ids)) and all(type(i) is int and 0<=i<80 for i in ids),'reset ids')
        before=field(p,'before'); after=field(p,'after')
        for name in ('sensor_episode','delay_episode'):
            old=vector(field(before,name),8); new=vector(field(after,name),8)
            require(all(new[i]==old[i]+int(i in ids) for i in range(8)),'per-row reset episode selection')
        for key,old in field(before,'queue').items():
            new=field(field(after,'queue'),key)
            for name in ('last','sample_tick','ready','cur','out'):
                a=field(old,name); b=field(new,name); require(type(a) is list and len(a)==8 and type(b) is list and len(b)==8,'reset queue witness rows')
                for i in range(8):
                    expected=(-1 if name in ('last','sample_tick') else False) if i in ids and name in ('last','sample_tick','ready') else a[i]
                    require(typed_equal(b[i],expected),'partial reset changed unselected/cache or retained stale flags')
        matches=[x for x in terms if x['clock']['physics_tick']==p['clock']['physics_tick'] and x['episode']==before['sensor_episode']]
        if len(matches)==1:
            b=matches[0]['bridge_pre']; require(all((i in ids)==(b['term'][i] or b['trunc'][i]) for i in range(8)),'pre-reset term/trunc/reset selection')
            linked+=1
    if not terms and not resets: raise Missing('no retained terminal/reset boundary')
    return {'pre_reset_endpoints':len(terms),'retained_resets':len(resets),'linked_reset_edges':linked,'natural_terminal_witness_rows':natural,
        'natural_terminal_edge':'OBSERVED_RETAINED_FLAGS' if natural and linked else 'UNKNOWN_NO_RETAINED_NATURAL_LINK',
        'complete80_reset_ids':'UNKNOWN row-selection adapter may also truncate an ids tensor of length80'}

def queue_state(q,width):
    for k in QUEUE:
        x=field(q,k)
        if k in ('pending','applied'): matrix(x,80,width)
        else: vector(x,80,bool if k.endswith('valid') else int)
    require(all(x in (0,1,2) for x in q['lag_steps']),'source0/1/2 physics lag')
    return q

def actuation_component(f):
    act=field(f,'actuation'); status=field(act,'status')
    require(integer(field(status,'dropped_events'),0)==0 and integer(field(status,'observer_errors'),0)==0 and field(status,'missing_hooks')==[] and field(status,'restore_conflicts')==[],'actuation capture loss')
    trace=field(field(f,'bounded_trace'),'actuation'); windows={}
    require(integer(field(trace,'control_windows_seen'),0)==f['controls'] and integer(field(trace,'retained_window_bound'))==4,'retention counters')
    first=field(trace,'first'); last=field(trace,'last'); require(type(first) is list and type(last) is list and len(first)<=2 and len(last)<=2,'two first/two last only')
    for w in first+last:
        idx=integer(field(w,'control_index'),0); require(idx<f['controls'],'retained control index')
        require(idx not in windows or typed_equal(windows[idx],w),'window duplicate differs'); windows[idx]=w
    if not windows: raise Missing('no retained actuation windows')
    endpoints={}; latency={g:set() for g in GROUPS}; age={g:[] for g in GROUPS}
    for idx,w in sorted(windows.items()):
        events=field(w,'events'); require(type(events) is list,'actuation events')
        seqs=[integer(field(e,'seq'),0) for e in events]; require(seqs==sorted(set(seqs)),'unique sorted tap seq')
        for e in events:
            require(e.get('outcome')=='RETURNED','original actuation callback raised')
            integer(field(e,'tick'),0); require(e.get('group') in GROUPS,'actuation group')
        for group,width in GROUPS.items():
            es=[e for e in events if e['group']==group]; submits=[e for e in es if e['kind']=='queue_submit']; issues=[e for e in es if e['kind']=='issue']
            if len(submits)!=1 or len(issues)!=1: raise Missing('one original issue/queue_submit per retained group/window')
            sub=submits[0]; issue=issues[0]; start=sub['tick']
            require(issue['tick']==start and issue['seq']<sub['seq'],'original process->submit linkage')
            matrix(field(issue,'args')[0],80,width)
            pre=queue_state(field(sub,'pre'),width); post=queue_state(field(sub,'post'),width)
            args=field(sub,'args'); require(type(args) is list and len(args)==3 and args[0]==group and typed_equal(args[2],start),'queue submit arguments')
            target=matrix(args[1],80,width)
            for i in range(80):
                require(pre['last_submit_tick'][i]<0 or start-pre['last_submit_tick'][i]==8,'20ms issue clock')
                expected={k:pre[k][i] for k in QUEUE}
                expected.update(pending=target[i],pending_valid=True,issued_tick=start,due_tick=start+pre['lag_steps'][i],last_submit_tick=start)
                require(all(post[k][i]==expected[k] for k in QUEUE),'queue submit state transition')
            require(typed_equal(field(issue,'post'),post),'issue includes original submit')
            applies=sorted((e for e in es if e['kind']=='queue_apply'),key=lambda e:e['tick'])
            if [e['tick'] for e in applies]!=list(range(start,start+8)): raise Missing('exactly8 retained natural apply ticks required')
            previous=post
            for a in applies:
                tick=a['tick']; pre=queue_state(field(a,'pre'),width); post=queue_state(field(a,'post'),width)
                require(typed_equal(pre,previous),'retained submit/apply chain discontinuity')
                previous=post
                require(matrix(field(a,'selected_target'),80,width)==post['applied'],'queue returned selected target')
                writes=[e for e in es if e['kind']=='target_write' and e['tick']==tick]
                terms=[e for e in es if e['kind']=='term_apply' and e['tick']==tick]
                if len(writes)!=1 or len(terms)!=1: raise Missing('one actual target_write/term_apply per tick')
                wr= writes[0]; term=terms[0]
                require(typed_equal(term.get('pre'),pre) and typed_equal(term.get('post'),post),'actual term encloses same queue transition')
                require(typed_equal(wr.get('pre'),post) and typed_equal(wr.get('post'),post),'original target writer does not mutate queue')
                require(wr.get('parent_term_apply_seq')==term['seq'] and term['seq']<a['seq']<wr['seq'],'actual term/apply/write nesting')
                arg=wr['args'][0] if wr.get('args') else field(field(wr,'kwargs'),'target')
                require(matrix(arg,80,width)==post['applied'],'original writer target differs')
                for i in range(80):
                    require(pre['last_apply_tick'][i]<0 or pre['last_apply_tick'][i]==tick-1,'400Hz natural apply clock')
                    select=pre['pending_valid'][i] and pre['due_tick'][i]<=tick
                    expected={k:pre[k][i] for k in QUEUE}; expected['last_apply_tick']=tick
                    if select:
                        require(pre['due_tick'][i]==tick,'late first application')
                        expected.update(applied=pre['pending'][i],applied_valid=True,applied_issue_tick=pre['issued_tick'][i],first_apply_tick=tick,pending_valid=False)
                    require(all(post[k][i]==expected[k] for k in QUEUE),'queue apply/held-state transition')
                    if post['applied_valid'][i]:
                        lat=post['first_apply_tick'][i]-post['applied_issue_tick'][i]; held=tick-post['applied_issue_tick'][i]
                        require(lat==post['lag_steps'][i] and held>=lat,'first latency distinct from held age')
                        latency[group].add(lat*2500); age[group].append(held*2500)
            endpoints[(idx,group)]=(sub['pre'],applies[-1]['post'])
    reset_edges=0
    for idx in sorted(windows):
        if idx+1 not in windows: continue
        for group in GROUPS:
            old=endpoints[(idx,group)][1]; new=endpoints[(idx+1,group)][0]
            for i in range(80):
                delta=new['episode'][i]-old['episode'][i]
                if delta==0: require(all(new[k][i]==old[k][i] for k in QUEUE),'unselected env changed across adjacent reset edge')
                elif delta==1:
                    reset_edges+=1
                    require(new['pending_valid'][i] is False and new['applied_valid'][i] is False,'reset stale validity')
                    require(all(new[k][i]==-1 for k in ('issued_tick','due_tick','applied_issue_tick','first_apply_tick','last_submit_tick')),'reset stale issue metadata')
                    require(new['last_apply_tick'][i]==old['last_apply_tick'][i],'partial reset rebased global clock')
                else: raise Missing('multiple/unobserved actuation episode transitions')
    return {'retained_control_indices':sorted(windows),'not_all_controls_retained':len(windows)<f['controls'],
        'first_transition_latency_us':{k:sorted(v) for k,v in latency.items()},'max_held_age_us':{k:max(v) if v else None for k,v in age.items()},
        'adjacent_reset_group_rows':reset_edges,'actual_reset_tick':'UNKNOWN_NO_C_RESET_HOOK',
        'group_coherence':'one four-leg vector / one two-wheel vector checked per env; RNG independence SOURCE_DECLARED_ONLY',
        'tensor_dtype':'UNKNOWN_AFTER_TOLIST; queue source specifies float32, not measured metadata', 'physical_readback':'UNKNOWN'}

def actor_component(events):
    rows=[e['payload'] for e in events if e['kind']=='actor35_original_buffer']
    if not rows: raise Missing('no retained actor sanity records')
    for p in rows:
        integer(field(p,'control_index'),0); matrix(field(p,'actor35'),8,35)
        require(field(p,'original_return_identity') is True and p.get('untapped_bitwise')=='UNKNOWN','same-buffer sanity is not a counterfactual baseline')
    return {'same_buffer_sanity_records':len(rows),'untapped_counterfactual_bitwise':'UNKNOWN','actor_source':'bridge.state.obs is original returned realobs dict, NOT mdp.obs or xi reconstruction'}

def stored_claims(f):
    counts=field(f,'rng_counts'); a=field(counts,'before'); b=field(counts,'after')
    for channel in CHANNELS:
        require(integer(field(field(b,'sensor_draw_counts'),channel),0)>=integer(field(field(a,'sensor_draw_counts'),channel),0),'stored draw counter reversed')
    for v in (a,b): require(v.get('observer_rng_draws')==0 and type(v['observer_rng_draws']) is int,'observer source-declared count')
    for name in ('static_before','static_after'):
        s=field(field(f,'actuation'),name)
        require(s.get('evidence')=='STORED_SOURCE_CONFIGURATION_OR_MODEL_MEMORY_NOT_PHYSICAL_READBACK','static source-memory label')
        require(type(s.get('physical_readback')) is dict and s['physical_readback'].get('status')=='UNKNOWN','stored configuration mislabeled measured physical readback')
        for group,width in GROUPS.items():
            m=field(field(s,'motors'),group)
            for k in ('episode_scale','step_scale'): matrix(field(m,k),80,width)
    return {'stored_counter_order':'checked','observer_rng_draws':'SOURCE_DECLARED zero, no private/global RNG states captured',
        'static_motor_decoded_shapes':'80x4 / 80x2','SDK_physical_DR_readback':'UNKNOWN','extra_obs_getter_reset_absence':'SOURCE_DECLARED_ONLY'}

def verify_capture(final, task, lifecycle, provenance):
    """Consume only decoded builtin values. Never mutate inputs or read artifacts.
    Missing final -> NOT_EVALUABLE and null execution; no automatic retry/approval.
    """
    out=dict(kind='PHASE1_DECODED_CAPTURE_EVIDENCE_REVIEW_V1',schema=[],lifecycle=[],components=[],unknowns=[],counts=None,
        execution={'status':'NOT_EVALUABLE','value':None},gate1='UNKNOWN',exact=False,stage2_GO=False,
        capture_interface_passed=False,verifier_is_approval=False,live_evidence_claim=False)
    docs=dict(lifecycle) if type(lifecycle) is dict else {}
    docs.update(worker_final=final,task=task)  # lifecycle cannot overwrite reserved original-document bindings
    prow=checked(out,'schema','original_provenance_and_whole_document_bindings',lambda:provenance_contract(provenance,docs))
    trow=checked(out,'schema','task_controls_and_identity',lambda:task_contract(task))
    if final is None:
        out['status']='NOT_EVALUABLE'; out['unknowns'].append('MISSING_ORIGINAL_FINAL; counts null, never zero/PASS')
        out['lifecycle'].append({'check':'published_failure_facts','status':'SOURCE_PROVIDED_ONLY','detail':copy.deepcopy(lifecycle)})
        return out
    frow=checked(out,'schema','original_whole_FINAL_schema',lambda:final_contract(final,task)) if trow['status']=='CONSISTENT' else {'status':'UNKNOWN'}
    if frow['status']!='CONSISTENT' or prow['status']=='CONTRADICTED':
        out['status']='CONTRADICTED' if 'CONTRADICTED' in (frow['status'],trow['status'],prow['status']) else 'INCONCLUSIVE'
        out['unknowns'].append('component verification skipped: invalid/missing original schema')
        return out
    erow=checked(out,'schema','bounded_execution_counter_consistency',lambda:execution(final,task))
    if erow['status']=='CONSISTENT': out['counts']={k:copy.deepcopy(final[k]) for k in ('controls','physics_callbacks','feedback_samples','delay_calls')}
    lrow=checked(out,'lifecycle','original_child_wait_EX_sourcegrade_and_timestamps',lambda:lifecycle_contract(lifecycle,task,final,provenance))
    orow=checked(out,'lifecycle','published_outer_actual_parent_wait',lambda:outer_wait_contract(lifecycle,task))
    statuses=[erow['status'],lrow['status'],orow['status'],prow['status']]
    closed=(orow.get('detail',{}).get('successful_closed_execution') if type(orow.get('detail')) is dict else None)
    value=False if 'CONTRADICTED' in statuses or closed is False else True if all(x=='CONSISTENT' for x in statuses) and closed is True else None
    out['execution']={'status':'CONSISTENT' if value is True else 'CONTRADICTED' if value is False else 'UNKNOWN',
        'value':value,'worker_counters_consistent':erow['status']=='CONSISTENT','scope':'decoded published bounded execution/wait closure, NOT window components or skill'}
    evrow=checked(out,'components','sensor_retention_schema',lambda:retained_sensor(final))
    if evrow['status']=='CONSISTENT':
        events=evrow.pop('detail'); evrow['detail']={'unique_retained_events':len(events)}
        checked(out,'components','clean16_used_noise_bias_delay_and_episode_clock',lambda:sensor_component(events))
        checked(out,'components','pre_reset_bridge_and_partial_reset',lambda:reset_component(events))
        checked(out,'components','original_actor_same_buffer_sanity',lambda:actor_component(events))
    checked(out,'components','retained_actuation_queue_issue_apply_write',lambda:actuation_component(final))
    checked(out,'components','stored_RNG_static_memory_and_source_claims',lambda:stored_claims(final))
    out['unknowns'] += ['Outer wait schema pinned separately; unavailable published docs remain UNKNOWN, not a new approval gate',
        '17 pins define reviewed schema/method only; actual future V3 index/seal/runtime provenance UNKNOWN here, not an old-B1 runtime approval requirement',
        'SOURCE/decoded provenance is caller-supplied, not independent artifact authentication',
        'No full64/128 trace inferred from aggregate counters; unretained windows UNKNOWN',
        'NO untapped actor baseline; full clean35/privileged RNG equality/localDue actual mask UNKNOWN',
        'No static physical DR readback or independent backend/getter; source-stored DR is not measured physical state',
        'Tensor shape is decoded list shape; row mapping SOURCE_DECLARED; original tensor dtype mostly lost by materialize',
        'observer no-extra-obs/getter/reset/RNG statements are SOURCE_DECLARED, not counterfactual measured facts']
    states=[r['status'] for g in ('schema','lifecycle','components') for r in out[g]]
    out['status']='CONTRADICTED' if 'CONTRADICTED' in states else 'INCONCLUSIVE'
    return out
