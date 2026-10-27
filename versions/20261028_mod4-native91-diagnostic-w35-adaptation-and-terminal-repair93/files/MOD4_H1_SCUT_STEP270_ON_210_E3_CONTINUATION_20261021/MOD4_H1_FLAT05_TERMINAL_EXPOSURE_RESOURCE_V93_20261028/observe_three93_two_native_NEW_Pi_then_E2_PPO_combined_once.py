"""One new finite observer; serial known72owner, source210, target72, E2."""
from pathlib import Path
import json,sys,importlib.util,time,threading,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
OWNER=r'''from pathlib import Path
import json,time,psutil
def ident(x):
 p=psutil.Process(x['pid']);assert p.create_time()==x['creation'];q=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd());assert q==x;return q
owner=Path(v['owner']);oi=ident(v['identity']);start=time.time()
while True:
 path=owner/'OWNER_CURRENT.json';row=json.loads(path.read_bytes()) if path.is_file() else {};go=row.get('go') or {}
 if set(go)=={'h1','h1_210','e2'} or any(x.get('original_error') for x in row.get('rows',{}).values()) or time.time()-start>=130:
  assert all(g['run_id']==v['run_id'] and g['original_owner_pid']==oi['pid'] and g['original_owner_creation']==oi['creation'] and g['max_parent_seconds']==3900 and g['save_deadline']==g['learning_started_epoch']+3600 for g in go.values())
  print(json.dumps(dict(passed_all_three_GO=set(go)=={'h1','h1_210','e2'},owner=oi,go=go,owner_current=row,no_account_or_GPU_write=True)));break
 if (owner/'OWNER_ORIGINAL_ERROR.json').is_file():raise RuntimeError((owner/'OWNER_ORIGINAL_ERROR.json').read_text())
 assert time.time()-start<130,'original three-node registration/GO not complete';time.sleep(2)
'''
NATIVE=r'''from pathlib import Path
import json,time,psutil,subprocess
spec=v['spec'];node=Path(v['node']);job=Path(spec['job_root']);out=job/'job0/production';expected_node=v['node_identity'];started=time.time();worker=None
def read(p):return json.loads(p.read_bytes()) if p.is_file() else None
def ident(expected):
 try:
  p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation'],'own PID recycled';q=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd());assert q==expected,(q,expected);return q
 except psutil.NoSuchProcess:return None
while True:
 ni=ident(expected_node);go=read(job/'job0/GO_PRODUCTION.json');stamp=read(job/'production_STARTED_ACTUAL.json')
 if stamp and worker is None:
  if spec['execution_backend']=='source210':argv=[spec['python'],'-u','-B',str(job/spec['production_script'])];exe=str(Path(spec['python']).resolve());cwd=str(node)
  else:argv=expected_node['argv'][:5]+['-u','-B',str(job/spec['production_script'])];exe=expected_node['exe'];cwd='/home/lc01/Zonglin Li/zonglin2'
  argv+=['--slot','h1','--phase','production','--num-envs','4096','--seed',str(spec['native_seed']),'--source-scope','native_models_only_fresh400N_environment']
  worker=dict(pid=stamp['pid'],creation=stamp['creation'],exe=exe,argv=argv,root=cwd)
 wi=ident(worker) if worker else None
 errors=[dict(path=str(p),text=p.read_text()) for root in (node,out,job) if root.is_dir() for p in root.glob('*ORIGINAL_ERROR*.json')]
 positive=read(out/'FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json')
 if positive:
  assert ni and wi and go==v['go'] and go['run_id']==spec['run_id'] and go['logical_slot']==spec['key'] and go['canonical_worker_key']=='h1'
  assert positive['native_actual_method']=='own_MOD4_native_flat5cm_same_nominal400' and positive['world_updates']>92560 and positive['policy_updates']>9000
  win=positive['native88_migration_window'];assert win['schema']=='mod4.native91_to_flat05_terminal93.objective_window.v1' and win['counters']['new_world_updates']>=640 and win['counters']['new_policy_updates']>0
  pre=read(out/'NATIVE88_ACTUAL_GPU_PRECONTROL_ADMISSION.json');assert pre['original_first_reset_completed'] and pre['actual_flat_command']['flat_task_command_zero'] and pre['flat_counter_installed_before_first_control'] and pre['actual_selected_flat_objective_class']=='OwnFlatJumpMdp' and pre['actual_new_gas_parameters']['actual_new_gas_parameters_passed']
  assert positive['producer']['imagination_terminal_exposure']==spec['imagination_terminal_exposure'] and positive['producer']['goal_conditioning']['encoding']=='mod4.flat91.mask_aware_after_normalization.v1'
  assert not errors,errors
  gpu=subprocess.check_output(['nvidia-smi','-i',spec['GPU_UUID'],'--query-gpu=uuid,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
  print(json.dumps(dict(passed_first_NEW_native_policy=True,spec_key=spec['key'],go=go,positive=positive,actual_precontrol=pre,node=ni,worker=wi,GPU_snapshot=gpu,no_model_read_or_account_write=True,not_skill_or_continuous_alive=True)));break
 if errors or not ni or (worker and not wi):
  print(json.dumps(dict(passed_first_NEW_native_policy=False,spec_key=spec['key'],go=go,node=ni,worker=wi,errors=errors,node_current=read(node/'NODE_CURRENT.json'),no_kill_refund_or_other_slot_interference=True)));break
 assert time.time()-started<v['maxwait'],'first native policy observer bounded timeout';time.sleep(3)
'''
def main():
 p=json.loads((R/'THREE93_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes());a=json.loads((R/'THREE93_ACTUAL_OWNER_AND_THREE_NODES_DETACHED.json').read_bytes());put('THREE93_COMBINED_FIRST_OBSERVER_CONSUMED_ACTUAL.json',dict(epoch=time.time(),only_this_combined_first_reader=True,no_second_watcher=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('three93_authorized_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec);secret=sec.recover();c=None;stop=threading.Event();phase=['owner_GO'];started=time.time()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_FINITE_FIRST_OBSERVER_WAIT',phase=phase[0],epoch=time.time())),flush=True)
 th=threading.Thread(target=progress,daemon=True);th.start();results={}
 try:
  c=d.connect72(secret);go=d.code(c,d.PY72,OWNER,dict(owner=p['owner_root'],identity=a['identities']['owner']['exact_identity'],run_id=p['run_id']),timeout=150);put('THREE93_ACTUAL_THREE_GO_OWNER_METADATA_ACTUAL.json',go);c.close();c=None
  for key in ('h1_210','h1'):
   phase[0]=key+'_first_NEW_native_policy';c=route.connect() if key=='h1_210' else d.connect72(secret);python=route.PY if key=='h1_210' else d.PY72
   remaining=max(1,min(480,int(1200-(time.time()-started)-60)))
   try:results[key]=d.code(c,python,NATIVE,dict(spec=p['experts'][key],node=p['node_roots'][key],node_identity=a['identities'][key]['exact_identity'],go=go['go'].get(key),maxwait=remaining),timeout=remaining+20)
   except BaseException:results[key]=dict(passed_first_NEW_native_policy=False,original_observer_error=traceback.format_exc(),healthy_others_continue=True)
   put(key+'_THREE93_FIRST_NEW_NATIVE_POLICY_RETURNED_ACTUAL.json',results[key]);print(json.dumps(dict(stage='NATIVE_FIRST_RETURNED',key=key,passed=results[key].get('passed_first_NEW_native_policy'))),flush=True);c.close();c=None
  phase[0]='E2_first_actual_PPO'
  src=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/E2_PPO50_gas400_first_actual_PPO_observer_source_v1/E2_first_PPO_readonly_CODE_v1.py';sp=importlib.util.spec_from_file_location('new93_E2_first_CODE_definitions_only',src);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
  code=m.CODE;assert code.count('time.time()-start>=780')==1;code=code.replace('time.time()-start>=780',"time.time()-start>=v['maxwait']",1)
  remaining=max(1,min(780,int(1200-(time.time()-started)-30)));c=d.connect72(secret)
  try:results['e2']=d.code(c,d.PY72,code,dict(request=dict(owner_root=p['owner_root'],node_root=p['node_roots']['e2'],run_id=p['run_id']),actual=dict(owner=a['identities']['owner']['exact_identity'],node=a['identities']['e2']['exact_identity']),maxwait=remaining),timeout=remaining+20)
  except BaseException:results['e2']=dict(passed=False,original_observer_error=traceback.format_exc(),healthy_others_continue=True)
  put('E2_THREE93_FIRST_ACTUAL_PPO_RETURNED_ACTUAL.json',results['e2']);c.close();c=None
  put('THREE93_ALL_FIRST_POLICY_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',dict(actual_finite_returned=True,go=go['go'],results=results,earliest_normal900=max(g['nominal_end_epoch'] for g in go['go'].values())-900,source_models_not_promoted_and_original_fees_pending=True,no_model_PT_read_or_account_write=True))
  print(json.dumps(dict(actual_first_observer_returned=True,native={k:results[k].get('passed_first_NEW_native_policy') for k in ('h1','h1_210')},E2_status_keys=list(results['e2'])[:10])))
 finally:
  secret=None;stop.set();th.join(1)
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('THREE93_COMBINED_FIRST_OBSERVER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_repeat_first_metadata=True));raise
