"""Human-authorized three experts, original one-writer math, qualified E2 cross-host source."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,shutil,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports'
P=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_NET_V5_RESOURCE_V71_20261025'
N=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V72_20261025'
E=W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
E2_RESOURCE=r'''
 if spec.get('cross_host_qualified_source'):
  import hashlib
  assert spec['key']=='e2' and spec['execution_backend']=='target72' and spec['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
  owned=Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve())
  proof=json.loads((B/'SOURCE_ORIGIN_210_C52/CLOSED_MODELS_COST_CPU_ACTUAL.json').read_bytes());model=proof['models']['e2'];terminal=json.loads((B/'SOURCE_ORIGIN_210_C52/NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];exit=json.loads((B/'SOURCE_ORIGIN_210_C52/NODE_EXIT_ACTUAL.json').read_bytes());auth=json.loads((B/'CROSS_HOST_QUALIFIED_SOURCE_AUTH_ACTUAL.json').read_bytes())
  assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free']
  assert model['final']['twohost_complete_SHA'] and model['final']['SHA']==spec['source_SHA'] and model['Adam']==spec['source_Adamstep'] and model['actual_cost']['duration_bound_passed']
  assert terminal['terminal_all_own_children_waited'] and terminal['returncode']==0 and terminal['final']['passed'] and not terminal['errors'] and terminal['final']['final']['SHA']==spec['source_SHA']
  assert exit['actual_all_own_children_waited'] and exit['validation_fcntl_released_if_acquired']
  assert auth['approved'] and auth['kind']=='human_three_GPU_existing_E2_cross_host_continuation' and auth['origin_runtime_root']==spec['previous_runtime_root'] and auth['source_SHA']==spec['source_SHA']
  lock=Path(spec['private_lock']).open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:
   with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
   compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);assert not any(spec['GPU_UUID'] in x for x in compute.splitlines())
   line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if spec['GPU_UUID'] in x)
   assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(B).free>25*1024**3
   (B/'OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json').write_text(json.dumps(dict(epoch=time.time(),path=spec['private_lock'],actual_private_GPU_fcntl_acquired=True,source_origin_runtime_root=spec['previous_runtime_root'],actual_previous_source_all_children_out=True,source_origin_host='original210',target_host='72',explicit_cross_host_source_proof=True,shared_validation_brief_only=True,GPU_line=line,no_unknown_peer_identity_query=True),indent=2));return lock
  except BaseException:fcntl.flock(lock,fcntl.LOCK_UN);lock.close();raise
'''
E2_GUARD='''
from pathlib import Path
import hashlib,json
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(spec,B):
 B=Path(B);read=lambda p:json.loads(Path(p).read_bytes());assert spec['key']=='e2' and spec['execution_backend']=='target72' and spec['cross_host_qualified_source']
 auth=read(B/'CROSS_HOST_QUALIFIED_SOURCE_AUTH_ACTUAL.json');proof=read(B/'SOURCE_ORIGIN_210_C52/CLOSED_MODELS_COST_CPU_ACTUAL.json');model=proof['models']['e2'];cpu=read(B/'TARGET_TWO50_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json');m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');prior=read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json')
 assert auth['approved'] and auth['kind']=='human_three_GPU_existing_E2_cross_host_continuation' and auth['source_SHA']==spec['source_SHA']==model['final']['SHA'] and model['Adam']==spec['source_Adamstep']==839920
 assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free'] and model['actual_cost']['duration_bound_passed']
 assert model['counts']==[175,98] and len(model['all17_changed']['actor_state_dict'])==9 and 'distribution.std_param' in model['all17_changed']['actor_state_dict'] and len(model['all17_changed']['critic_state_dict'])==8
 terminal=read(B/'SOURCE_ORIGIN_210_C52/NODE_TERMINAL_ACTUAL.json')['row'];exit=read(B/'SOURCE_ORIGIN_210_C52/NODE_EXIT_ACTUAL.json');assert terminal['returncode']==0 and not terminal['original_error'] and not terminal['errors'] and terminal['terminal_all_own_children_waited'] and terminal['final']['passed'] and terminal['final']['final']['SHA']==spec['source_SHA'] and exit['actual_all_own_children_waited'] and exit['validation_fcntl_released_if_acquired']
 clock=read(B/'SOURCE_ORIGIN_210_C52/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json');assert clock['policy_hz']==spec['policy_hz']==spec['source_policy_hz']==50 and clock['physics_dt_s']==.0025 and clock['decimation']==8
 before={r['relative']:r for r in prior['files']};after={r['relative']:r for r in m['files']}
 protected=lambda rows:{k:v for k,v in rows.items() if k.startswith(('job0/runtime/','job0/assets/','lib/'))}
 a=protected(before);b=protected(after);assert set(a)==set(b)
 for rel,row in a.items():assert b[rel]['bytes']==row['bytes'] and b[rel]['SHA']==row['SHA'],rel
 assert H(B/'native_admission_worker.py')==before['native_admission_worker.py']['SHA'] and H(B/'target_two50_source_sdk_cpu_review.py')==before['target_two50_source_sdk_cpu_review.py']['SHA']
 approved=read(B/'THREE_GPU_CONTROLLER_SOURCE_AUTH_ACTUAL.json')
 for name,row in approved['new_sources'].items():assert H(B/name)==row['SHA']
 assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA'] and cpu['source_schema_counts']==[175,98] and cpu['all17Adam']==839920 and cpu['manifest_SHA']==H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 assert cpu['actual_SDK_math']['SHA']==m['expected_actual_SDK_math_SHA'] and len(cpu['actual_RSL_sources'])==2
 v=dict(kind='closed_cross_host_policy50_production',key='e2',passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend='target72',all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,explicit_policy_clock_50Hz_admitted=True,explicit_cross_host_source_CPU_admitted=True,same_clock_closed_production=True,source_cost_original_account_ready=True,source_account_reconciliation_receipt_SHA=H(B/'SOURCE_ORIGIN_210_C52/CLOSED_MODELS_COST_CPU_ACTUAL.json'),original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True,existing_same_source_native_physics_evidence_reused=True,new_target_GPU_PPO_not_claimed=True,not_skill_graduation=True)
 return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
'''
try:
 resource=read(R/'THIRD_GPU_ORIGINAL_PRIVATE_SHARED_LOCKS_RESOURCE_RETURNED_ACTUAL.json');assert resource['actual_finite_returned'] and resource['expected_GPU_empty'] and all(x['exclusive_probe_free'] for x in resource['locks'])
 N.mkdir();(N/'reports').mkdir();(N/'controllers').mkdir()
 common=(P/'controllers/three_slot_common_v1.py').read_text('utf8');needle="'e2':'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'";assert common.count(needle)==1;common=common.replace(needle,"'e2':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'",1)
 needle="kind='policy_clock_100_to_50_migration' if spec['source_policy_hz']==100 else 'closed_same_backend_policy50_production'";assert common.count(needle)==1
 common=common.replace(needle,"kind=('closed_cross_host_policy50_production' if spec.get('cross_host_qualified_source') else ('policy_clock_100_to_50_migration' if spec['source_policy_hz']==100 else 'closed_same_backend_policy50_production'))",1)
 needle="and v.get('explicit_policy_clock_50Hz_admitted') and v.get('source_cost_original_account_ready')";assert common.count(needle)==1
 common=common.replace(needle,"and v.get('explicit_policy_clock_50Hz_admitted') and ((spec['key']=='e2' and spec['execution_backend']=='target72' and v.get('explicit_cross_host_source_CPU_admitted')) if spec.get('cross_host_qualified_source') else True) and v.get('source_cost_original_account_ready')",1)
 owner=(P/'controllers/three_slot_finite_owner_v1.py').read_text('utf8');assert owner.count("set(specs)=={'h1','recovery'}")==1 and owner.count("cfg['deferred_experts']==['e2']")==1
 owner=owner.replace("set(specs)=={'h1','recovery'}","set(specs)=={'h1','e2','recovery'}",1).replace("cfg['deferred_experts']==['e2']","cfg['deferred_experts']==[]",1)
 rs=(P/'controllers/three_real_gpu_resource_v1.py').read_text('utf8');needle='def acquire(spec,B):';assert rs.count(needle)==1;rs=rs.replace(needle,needle+E2_RESOURCE,1)
 network=(P/'forwarded_original_owner_control_v2.py').read_text('utf8')
 assert network.count("spec['key']=='recovery'")==2;network=network.replace("spec['key']=='recovery'","spec['key'] in ('e2','recovery')")
 for p in (P/'controllers').glob('*.py'):shutil.copy2(p,N/'controllers'/p.name)
 for name,text in [('three_slot_common_v1.py',common),('three_slot_finite_owner_v1.py',owner),('three_real_gpu_resource_v1.py',rs),('forwarded_original_owner_control_v1.py',network)]:
  ast.parse(text);(N/'controllers'/name).write_text(text,encoding='utf8')
 # Execute actual reviewed pure ready/account functions, without importing Windows-incompatible fcntl.
 tree=ast.parse(common);functions=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('terminal','valid_ready','charge_values')];ns=dict(hashlib=hashlib,json=json);exec(compile(ast.Module(body=functions,type_ignores=[]),'<actual_three_slot_pure_functions>','exec'),ns)
 c=dict(charged_training_seconds=100.,remaining_training_seconds=2267900.);active=dict(experts={},charged_expert_seconds=0.);go={k:dict(learning_started_epoch=v,max_parent_seconds=3900) for k,v in [('h1',100.),('e2',110.),('recovery',120.)]};rows={k:dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=v) for k,v in [('h1',130.),('e2',140.)]}
 ns['charge_values'](c,active,go,rows,150.);assert active['charged_expert_seconds']==90. and c['charged_training_seconds']==190.
 ns['charge_values'](c,active,go,rows,160.);assert active['charged_expert_seconds']==100. and c['charged_training_seconds']==200. and c['remaining_training_seconds']==2267800.
 spec=dict(key='e2',policy_hz=50,source_policy_hz=50,cross_host_qualified_source=True,execution_backend='target72',GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',source_SHA='a'*64,manifest_SHA='b'*64)
 value=dict(kind='closed_cross_host_policy50_production',passed=True,explicit_policy_clock_50Hz_admitted=True,explicit_cross_host_source_CPU_admitted=True,source_cost_original_account_ready=True,source_account_reconciliation_receipt_SHA='c'*64,same_clock_closed_production=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True)
 row=dict(key='e2',phase='ready',closed_source_CPU=dict(value=value,SHA=hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True),manifest_SHA=spec['manifest_SHA'],original_error=False)
 assert ns['valid_ready'](row,spec)
 bad=copy.deepcopy(row);bad['closed_source_CPU']['value']['explicit_cross_host_source_CPU_admitted']=False;bad['closed_source_CPU']['SHA']=hashlib.sha256(json.dumps(bad['closed_source_CPU']['value'],indent=2).encode()).hexdigest();assert not ns['valid_ready'](bad,spec)
 tests=dict(actual_three_expert_independent_sumonce=True,overlapping_wall_intervals_not_undercharged=True,terminal_slots_not_charged_twice=True,explicit_cross_host_ready_accepted=True,missing_explicit_cross_host_admission_rejected=True,three_parent_caps_seconds=11700,three_slot_remaining_guard=86412.86069250107)
 basecontrollers={name:dict(SHA=H(P/'controllers'/name)) for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_real_gpu_resource_v1.py','three_slot_finite_node_v1.py')}
 newcontrollers={p.name:dict(SHA=H(p),bytes=p.stat().st_size) for p in (N/'controllers').glob('*.py')}
 auth=dict(epoch=time.time(),approved=True,human_instruction='三张都用上，继续修复h1上台阶还有继续推进其他专家训练',kind='explicit_existing_H1_E2_E3_three_GPU_single_original_writer',base_sources=basecontrollers,new_sources=newcontrollers,tests=tests,no_active71_hotpatch_or_second_writer=True,no_budget_extension_or_refund=True)
 put(R/'THREE_GPU_CONTROLLER_SOURCE_AUTH_ACTUAL.json',auth);put(N/'reports/THREE_GPU_CONTROLLER_SOURCE_AUTH_ACTUAL.json',auth)
 q=read(E/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');proof=read(E/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');model=proof['models']['e2'];assert proof['passed'] and proof['original_canonical_cost_settled'] and model['Adam']==839920 and model['final']['twohost_complete_SHA']
 base=Path(q['payloads']['e2']);out=N/'payloads/e2';out.parent.mkdir();shutil.copytree(base,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'));oldm=read(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 history=out/'prebind52_exact_history';history.mkdir()
 for name in ('job0/TASK.json','THREE_SLOT_COMPLETE_MANIFEST_V1.json'):shutil.copy2(out/name,history/Path(name).name)
 origin=out/'SOURCE_ORIGIN_210_C52';origin.mkdir()
 for src,name in [(E/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json','CLOSED_MODELS_COST_CPU_ACTUAL.json'),(E/'current_two50_closed_text/e2/NODE_EXIT_ACTUAL.json','NODE_EXIT_ACTUAL.json'),(E/'current_two50_closed_text/e2/NODE_TERMINAL_ACTUAL.json','NODE_TERMINAL_ACTUAL.json'),(E/'current_two50_closed_text/e2/job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json','POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json')]:shutil.copy2(src,origin/name)
 for p in (N/'controllers').glob('*.py'):
  if p.name!='three_slot_finite_owner_v1.py':shutil.copy2(p,out/p.name)
 (out/'original_account_policy50_source_CPU.py').write_text(E2_GUARD,encoding='utf8')
 shutil.copy2(model['final']['local_path'],out/'job0/source'/q['specs']['e2']['source_filename'])
 task=read(out/'job0/TASK.json');task.update(id=N.name+'_e2',source_SHA=model['final']['SHA'],source_Adamstep=model['Adam'],source_owned_updates=model['updates'],source_owned_completed_updates=model['updates'],exact_closed_source_updates=model['updates'],source_parent_production_root=q['roots']['e2'],GPU_UUID=spec['GPU_UUID'],execution_backend='target72',source_execution_backend='source210',cross_host_qualified_source=True,source_policy_hz=50,policy_hz=50)
 (out/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
 (out/'QUALIFIED_RUNTIME_BASE_MANIFEST.json').write_text(json.dumps(oldm,indent=2),encoding='utf8');put(out/'THREE_GPU_CONTROLLER_SOURCE_AUTH_ACTUAL.json',auth)
 cross=dict(epoch=time.time(),approved=True,kind='human_three_GPU_existing_E2_cross_host_continuation',human_instruction=auth['human_instruction'],source_SHA=model['final']['SHA'],source_Adam=839920,origin_host='original210',origin_runtime_root=q['roots']['e2'],target_host='72',target_GPU_UUID=spec['GPU_UUID'],original_full_cost_already_settled_no_recharge=True,same_physics_assets_reward_action_observation_PPO_source=True,new_target_installed_source_SDK_RSL_CPU_required=True,existing_same_source_native_evidence_reused_no_new_FP64_query_gate=True)
 put(out/'CROSS_HOST_QUALIFIED_SOURCE_AUTH_ACTUAL.json',cross)
 prior={r['relative']:r for r in oldm['files']};rows=[]
 for p in sorted(out.rglob('*')):
  if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
  rel=p.relative_to(out).as_posix()
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  digest=(model['final']['SHA'] if rel=='job0/source/'+q['specs']['e2']['source_filename'] else prior[rel]['SHA']) if p.suffix in ('.pt','.npz','.usd','.stl') else H(p)
  rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=digest))
 m=dict(oldm,source_SHA=model['final']['SHA'],source_Adamstep=839920,actual_GPU_UUID=spec['GPU_UUID'],execution_backend='target72',files=rows)
 (out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 es=dict(q['specs']['e2']);es.update(GPU_UUID=spec['GPU_UUID'],source_SHA=model['final']['SHA'],source_Adamstep=839920,manifest_SHA=H(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),execution_backend='target72',python='/home/lc01/Zonglin Li/zonglin2/run-python.sh',previous_runtime_root=q['roots']['e2'],previous_exit_kind='qualified_cross_host',private_lock='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+spec['GPU_UUID']+'.lock',cross_host_qualified_source=True,clock_migration_native_required=False)
 put(N/'reports/E2_CROSS_HOST_TARGET_PAYLOAD_SOURCE_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed=True,payload=str(out),root='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_experts_2510v72/e2',spec=es,source=model['final'],origin_complete_proof=str(E/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'),no_GPU_load_remote_Task_GO_or_fee=True))
 print(json.dumps(dict(prepared=True,three_slot_controller_tests=tests,E2_source_SHA=model['final']['SHA'],E2_Adam=839920,no_remote_install_or_GO=True)))
except BaseException:
 put(R/('THREE_GPU_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_retry_same_once_or_active71_hotpatch=True));raise
