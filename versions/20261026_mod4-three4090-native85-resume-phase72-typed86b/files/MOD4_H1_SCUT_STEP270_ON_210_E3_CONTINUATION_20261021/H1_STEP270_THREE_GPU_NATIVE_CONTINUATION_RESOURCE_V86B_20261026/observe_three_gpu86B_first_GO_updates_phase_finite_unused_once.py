"""One finite first-update observer; metadata only, no mid-window PT/raw."""
from pathlib import Path
import importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as out:json.dump(value,out,indent=2)
OWNER_READ=r'''
from pathlib import Path
import json,psutil,time
B=Path(v['owner_root']);identity=v['owner_identity'];owner=psutil.Process(identity['pid'])
assert owner.create_time()==identity['creation'] and owner.cmdline()==identity['argv']
until=time.monotonic()+1200;status='pending';phase=None;native=None;owner_error=None
while True:
 current=json.loads((B/'OWNER_CURRENT.json').read_bytes());rows=current['rows'];go=current['go']
 native_file=Path(v['roots']['e2'])/'job0/production/FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json'
 phase_file=Path(v['roots']['e2'])/'job0/production/NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json'
 try:native=json.loads(native_file.read_bytes()) if native_file.is_file() else None
 except (OSError,ValueError):native=None
 try:phase=json.loads(phase_file.read_bytes()) if phase_file.is_file() else None
 except (OSError,ValueError):phase=None
 positive=bool(native and native.get('policy_updates',0)>58 and native.get('world_updates',0)>680 and all((rows.get(k,{}).get('latest_save') or {}).get('updates',0)>0 for k in ('h1','recovery'))
 phase_exposure=bool(phase and phase.get('diagnostic_valid') and sum(phase.get('bands',{}).get(k,0) for k in ('100to135','136to179'))>0)
 if any(row.get('original_error') for row in rows.values()) or (B/'OWNER_ORIGINAL_ERROR.json').exists():
  status='actual_original_error';owner_error=json.loads((B/'OWNER_ORIGINAL_ERROR.json').read_bytes()) if (B/'OWNER_ORIGINAL_ERROR.json').exists() else None;break
 if set(go)=={'h1','e2','recovery'} and positive and phase_exposure:status='positive_updates_and_phase_exposure';break
 if time.monotonic()>=until:
  status='positive_updates_phase_optional_pending' if positive and set(go)=={'h1','e2','recovery'} else 'first_positive_not_proven_within_finite';break
 time.sleep(3)
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes())
active=c['active_segment'];held=[f.path for f in owner.open_files()] if owner.is_running() else []
if active is not None:
 assert active['owner_parent_pid']==owner.pid and set(active['experts'])==set(go)
 assert str(C.parent/'native_floor_supervisor.lock') in held and str(C.parent/'autonomy_controller.lock') in held
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
assert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[]
assert current['deferred_experts_without_GO']==[]
print(json.dumps(dict(epoch=time.time(),status=status,owner=v['owner_identity'],owner_root=str(B),current=current,go=go,canonical_active=active,remaining_actual_snapshot=c['remaining_training_seconds'],actual_original_two_locks_open=bool(active is not None),native_first_policy=native,phase_sampling=phase,phase_exposure_observed=phase_exposure,owner_original_error=owner_error,not_FINAL_skill_or_continuous_alive=True)))
'''
TARGET_READ=r'''
from pathlib import Path
import hashlib,json,psutil,subprocess,time
B=Path(v['root']);key=v['key'];spec=v['spec'];node=json.loads((B/'NODE_IDENTITY.json').read_bytes());np=psutil.Process(node['pid']);assert np.create_time()==node['creation'] and np.cmdline()==node['argv']
row=v['row'];w=row.get('worker');errors=[dict(path=str(p),value=json.loads(p.read_bytes())) for p in B.glob('NODE_CONTROL_ORIGINAL_ERROR_*.json')]
if row.get('original_error') or w is None:
 small={}
 for p in [B/'NODE_ORIGINAL_ERROR.json',B/'NODE_TERMINAL_ACTUAL.json']+list((B/'job0/production').glob('*ORIGINAL_ERROR*.json')):
  if p.is_file():small[str(p)]=p.read_text('utf8')
 print(json.dumps(dict(key=key,original_node_row=row,small_original_errors=small,control_errors=errors,no_model_GPU_read_after_failure=True)))
else:
 p=psutil.Process(w['pid']);assert p.create_time()==w['creation'] and p.cmdline()==w['argv'] and p.exe()==np.exe()
 expected=[p.cmdline()[0],'-u','-B',str(B/spec['production_script'])]+(['--phase','production'] if key=='h1' else ['--job','0','--phase','production']);assert p.cmdline()==expected
 go=json.loads((B/'job0/GO_PRODUCTION.json').read_bytes());assert go['run_id']==v['run_id'] and go['source_SHA']==spec['source_SHA'] and go['manifest_SHA']==spec['manifest_SHA'] and go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300
 compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);own=[line for line in compute.splitlines() if line.split(',')[1].strip()==str(p.pid)];assert own and all(spec['GPU_UUID'] in line for line in own)
 extra={}
 if key=='e2':
  first=json.loads((B/'job0/production/FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json').read_bytes());assert first['policy_updates']>58 and first['world_updates']>680
  restore=json.loads((B/'job0/production/NATIVE_CONTINUATION_STARTUP_ACTUAL.json').read_bytes());assert restore['passed'] and restore['source_checkpoint_SHA']==spec['source_SHA'] and restore['restored_iteration']==68 and restore['restored_world_updates']==680 and restore['restored_policy_updates']==58 and restore['all_three_native_optimizers_restored'] and restore['fresh_replay_refill_steps']==48 and not restore['replay_restored']
  runtime=json.loads((B/'job0/production/NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json').read_bytes());old=json.loads((B/'native_source_metadata/NATIVE85M2_RUNTIME_ORDER_ACTUAL.json').read_bytes());assert runtime['actual_runtime_order_readback'] and runtime['before_first_physical_step_and_Pi'] and runtime['actual_robot_joint_names']==old['actual_robot_joint_names'] and runtime['runtime_objective_contract_SHA']==old['runtime_objective_contract_SHA']
  objective=(B/'job0/production/NATIVE_FUDAN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json').read_bytes();assert hashlib.sha256(objective).hexdigest()==runtime['runtime_objective_contract_SHA']
  phase=B/'job0/production/NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json';extra=dict(native_first=first,restore=restore,runtime_order=runtime,phase=json.loads(phase.read_bytes()) if phase.exists() else None)
 else:assert row['latest_save']['updates']>0
 print(json.dumps(dict(epoch=time.time(),key=key,node=node,node_exe=np.exe(),worker=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),cwd=p.cwd()),actual_GO=go,own_GPU_compute=own,latest_save=row.get('latest_save'),source_CPU=row.get('closed_source_CPU'),control_original_errors=errors,control_error_count=len(errors),**extra,not_FINAL_or_skill_or_continuous_alive=True)))
'''
def main():
 q=json.loads((R/'THREE_GPU86B_ACTUAL_OWNER_NODES_DETACHED.json').read_bytes());put('THREE_GPU86B_FIRST_GO_POLICY_OBSERVER_STARTED_ACTUAL.json',dict(epoch=time.time(),max_owner_wait=1200,one_first_metadata_observer=True,native_requires_newPi_above58=True,phase_diagnostic_optional_not_model_gate=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('known72_auth_in_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
 secret=memory.recover();client=None
 try:
  client=d.connect72(secret);owner=d.code(client,d.PY72,OWNER_READ,q,timeout=1240);put('THREE_GPU86B_FIRST_OWNER_SIGNED_GO_POLICY_SNAPSHOT_RETURNED_ACTUAL.json',owner)
  target={}
  for key in ('e2','recovery'):target[key]=d.code(client,d.PY72,TARGET_READ,dict(root=q['roots'][key],key=key,spec=q['specs'][key],row=owner['current']['rows'].get(key,{}),run_id=q['run_id']),timeout=60)
  client.close();client=None
  client=route.connect();target['h1']=d.code(client,route.PY,TARGET_READ,dict(root=q['roots']['h1'],key='h1',spec=q['specs']['h1'],row=owner['current']['rows'].get('h1',{}),run_id=q['run_id']),timeout=60)
  passed=owner['status'] in ('positive_updates_and_phase_exposure','positive_updates_phase_optional_pending')
  result=dict(epoch=time.time(),passed=passed,actual_finite_returned=True,run_id=q['run_id'],go=owner['go'],authority72=owner,targets=target,all3_unique_expected_UUIDs_verified=passed,native_restored_and_new_policy_updates_verified=passed,phase_exposure_observed=owner['phase_exposure_observed'],no_skill_or_FINAL_or_continuous_alive_claim=True)
  put('THREE_GPU86B_FIRST_GO_PPO_NATIVE_POLICY_PHASE_ACTUAL.json',result)
  print(json.dumps(dict(passed=passed,run_id=q['run_id'],native_Pi=(target['e2'].get('native_first') or {}).get('policy_updates'),phase_exposure_observed=result['phase_exposure_observed'],no_skill_claim=True)))
 finally:
  secret=None
  if client:client.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('THREE_GPU86B_FIRST_OBSERVER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_retry_or_hotpatch_or_stop=True));raise
