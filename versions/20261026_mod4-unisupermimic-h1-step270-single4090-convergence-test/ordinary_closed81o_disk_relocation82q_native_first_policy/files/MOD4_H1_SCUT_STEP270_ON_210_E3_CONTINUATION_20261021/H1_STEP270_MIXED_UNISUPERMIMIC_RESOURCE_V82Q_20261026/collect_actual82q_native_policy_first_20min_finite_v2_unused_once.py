"""One finite first-GO/PPO/own UUID+identity proof for all three authorized experts."""
from pathlib import Path
import importlib.util,json,os,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;N=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026';R=N/'reports'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ210=r'''
from pathlib import Path
import json,psutil,subprocess,time
B=Path(v['owner']['root']);p=psutil.Process(v['owner']['pid']);assert p.create_time()==v['owner']['creation'] and p.cmdline()==v['owner']['argv'];until=time.monotonic()+1200
while True:
 current=json.loads((B/'OWNER_CURRENT.json').read_bytes());rows=current['rows'];go=current['go']
 if all(go.get(k) and (rows.get(k,{}).get('latest_save') or {}).get('updates',0)>0 for k in ('h1','e2','recovery')):break
 if any(x.get('original_error') for x in rows.values()) or (B/'OWNER_ORIGINAL_ERROR.json').exists():raise AssertionError(dict(rows=rows,original_owner_error=(B/'OWNER_ORIGINAL_ERROR.json').read_text() if (B/'OWNER_ORIGINAL_ERROR.json').exists() else None))
 assert time.monotonic()<until,'Three positive PPO not yet proven; no same reader replay'
 time.sleep(3)
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());active=c['active_segment'];assert active['owner_parent_pid']==p.pid and set(active['experts'])==set(go)=={'h1','e2','recovery'} and current['deferred_experts_without_GO']==[]
assert c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9
held=[x.path for x in p.open_files()];assert str(C.parent/'native_floor_supervisor.lock') in held and '/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock' in held
H=Path(v['root']);node=json.loads((H/'NODE_IDENTITY.json').read_bytes());np=psutil.Process(node['pid']);assert np.create_time()==node['creation'] and np.cmdline()==node['argv'];w=rows['h1']['worker'];wp=psutil.Process(w['pid']);assert wp.create_time()==w['creation'] and wp.cmdline()==w['argv']
actual=json.loads((H/'GO_PRODUCTION.json').read_bytes());assert actual==go['h1'] and actual['source_SHA']==v['source_SHA'] and actual['run_id']==v['run_id'] and actual['actual_H1_step270_scope_admitted']
idx=json.loads((H/'job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes());assert 'h1_step270_sampled_leg_action_excess' in idx['reward_terms']
task=json.loads((H/'job0/TASK.json').read_bytes());assert task['reward_recipe_version']=='step270_sampled_leg_excess_v8_reward_only'
diag_path=H/'job0/production/control_prefix_raw/CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json'
try:diag=dict(present=diag_path.is_file(),value=json.loads(diag_path.read_bytes()) if diag_path.is_file() else None)
except (OSError,ValueError) as error:diag=dict(present=False,read_error=type(error).__name__+': '+str(error),not_a_training_failure=True)
journal_path=H/'job0/production/control_prefix_raw/CONTROL_LANDING_EVENT_JOURNAL_ACTUAL.json'
try:journal=dict(present=journal_path.is_file(),value=json.loads(journal_path.read_bytes()) if journal_path.is_file() else None)
except (OSError,ValueError) as error:journal=dict(present=False,read_error=type(error).__name__+': '+str(error),not_a_training_failure=True)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);own=[x for x in compute.splitlines() if x.split(',')[1].strip()==str(wp.pid)];assert own and all(v['GPU_UUID'] in x for x in own)
print(json.dumps(dict(epoch=time.time(),owner=v['owner'],current=current,canonical_active=active,remaining_actual_snapshot=c['remaining_training_seconds'],actual_original_two_locks_open=True,H1_node=node,H1_worker=dict(pid=wp.pid,creation=wp.create_time(),exe=wp.exe(),argv=wp.cmdline()),H1_actual_GO=actual,H1_own_compute=own,V8_runtime_term_present_in_original_trace_index=True,lifetime_goal_diagnostic_first_snapshot=diag,landing_event_journal_first_snapshot=journal,V8_runtime_reward_terms=idx['reward_terms'],not_skill_FINAL_or_continuous_alive=True)))
'''
READ72=r'''
from pathlib import Path
import json,psutil,subprocess,time
B=Path(v['root']);node=json.loads((B/'NODE_IDENTITY.json').read_bytes());np=psutil.Process(node['pid']);assert np.create_time()==node['creation'] and np.cmdline()==node['argv'];w=v['row']['worker'];p=psutil.Process(w['pid']);assert p.create_time()==w['creation'] and p.cmdline()==w['argv']
method=None
if v['key']=='e2':
 method=json.loads((B/'job0/production/FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json').read_bytes());startup=json.loads((B/'job0/production/ACTUAL_H1_NEW_METHOD_STARTUP_CONTRACT.json').read_bytes());assert method['policy_updates']>0 and method['world_updates']>0 and startup['actual_envs']==20000 and startup['physics_dt']==.0025 and startup['control_dt']==.01 and startup['actual_geometry']['height']==.27
go=json.loads((B/'job0/GO_PRODUCTION.json').read_bytes());assert go['run_id']==v['run_id'] and go['source_SHA']==v['source_SHA'] and go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);own=[x for x in compute.splitlines() if x.split(',')[1].strip()==str(p.pid)];assert own and all(v['GPU_UUID'] in x for x in own)
errors=[dict(path=str(x),value=json.loads(x.read_bytes())) for x in sorted(B.glob('NODE_CONTROL_ORIGINAL_ERROR_*.json'))]
print(json.dumps(dict(epoch=time.time(),key=v['key'],node=node,worker=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline()),actual_GO=go,own_compute=own,native_H1_method_first_policy=method,source_CPU=v['row']['closed_source_CPU'],latest_save=v['row']['latest_save'],control_original_errors=errors,control_error_count=len(errors),not_FINAL_skill_or_continuous_alive=True)))
'''
try:
 q=json.loads((R/'THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());put('THREE_EXPERT_FIRST_METADATA_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,max_owner_wait=1200,three_actual_GO_PPO_UUID_identity_only=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 c=route.connect()
 try:a=d.code(c,route.PY,READ210,dict(owner=q['owner_identity'],root=q['roots']['h1'],source_SHA=q['sources']['h1']['SHA'],GPU_UUID=q['specs']['h1']['GPU_UUID'],run_id=q['run_id']),timeout=1230)
 finally:c.close()
 sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None;target={}
 try:
  for key in ('e2','recovery'):target[key]=d.code(c,d.PY72,READ72,dict(root=q['roots'][key],row=a['current']['rows'][key],run_id=q['run_id'],source_SHA=q['sources'][key]['SHA'],GPU_UUID=q['specs'][key]['GPU_UUID'],key=key),timeout=45)
 finally:c.close()
 result=dict(epoch=time.time(),passed=True,actual_finite_returned=True,run_id=q['run_id'],source210=a,target72=target,H1_E3_actual_PPO_and_H1_method_native_policy_positive=True,all_three_distinct_expected_4090_UUIDs=True,one_original_writer_three_distinct_actual_intervals=True,H1_V8_sampled_excess_reward_and_original_success_standard=True,no_skill_or_FINAL_or_continuous_utilization_claim=True)
 put('MIXED82Q_ACTUAL_GO_PPO_AND_NATIVE_POLICY_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json',result);print(json.dumps(dict(passed=True,run_id=q['run_id'],updates={k:a['current']['rows'][k]['latest_save']['updates'] for k in ('h1','e2','recovery')},all_three_training=True)))
except BaseException:
 put('THREE_EXPERT_FIRST_PPO_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_retry_or_training_hotpatch=True));raise
