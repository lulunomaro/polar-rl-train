from pathlib import Path
import sys,json,time,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
CODE=r'''from pathlib import Path
import json,time,psutil,subprocess
owner=Path(v['owner']);node=Path(v['node']);job=Path(v['job']);out=job/'job0/production'
def read(p):return json.loads(p.read_bytes()) if p.is_file() else None
def ident(expected):
 try:
  p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation'],'own PID recycled'
  q=dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),exe=p.exe(),root=p.cwd())
  assert all(q[k]==expected[k] for k in ('argv','exe','root')),(q,expected)
  return q
 except psutil.NoSuchProcess:return None
expected_owner=v['actual']['owner'];expected_node=v['actual']['node'];started=time.time();worker=None;go=None
while True:
 oi=ident(expected_owner);ni=ident(expected_node)
 go=read(job/'job0/GO_PRODUCTION.json')
 stamp=read(job/'production_STARTED_ACTUAL.json')
 if stamp and worker is None:
  loader=expected_node['exe'];base=expected_node['argv'][:6]
  argv=base+['-u','-B',str(job/'h1_native_flat90_worker_v1.py'),'--slot','h1','--phase','production','--num-envs','4096','--seed','27','--source-scope','native_models_only_fresh400N_environment']
  worker=dict(pid=stamp['pid'],creation=stamp['creation'],exe=loader,argv=argv,root='/home/lc01/Zonglin Li/zonglin2')
 wi=ident(worker) if worker else None
 errors=[dict(path=str(p),text=p.read_text(errors='replace')) for root in (owner,node,out) if root.is_dir() for p in root.glob('*ORIGINAL_ERROR*.json')]
 positive=read(out/'FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json')
 if positive:
  assert oi and ni and wi and go and go['run_id']==v['run_id'] and go['original_owner_pid']==expected_owner['pid']
  assert positive['native_actual_method']=='own_MOD4_native_flat5cm_same_nominal400' and positive['world_updates']>64690 and positive['policy_updates']>6341
  win=positive['native88_migration_window'];assert win['schema']=='mod4.native88C_to_flat05.objective_window.v1' and win['counters']['new_world_updates']>=640 and win['counters']['new_policy_updates']>0
  pre=read(out/'NATIVE88_ACTUAL_GPU_PRECONTROL_ADMISSION.json');assert pre['original_first_reset_completed'] and pre['actual_flat_command']['flat_task_command_zero'] and pre['flat_counter_installed_before_first_control']
  assert pre['actual_selected_flat_objective_class']=='OwnFlatJumpMdp' and pre['actual_new_gas_parameters']['actual_new_gas_parameters_passed']
  assert not errors,errors
  gpu=subprocess.check_output(['nvidia-smi','-i','GPU-c27eecbd-6838-7290-1cd2-37e34522213d','--query-gpu=uuid,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
  C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=read(C)
  print(json.dumps(dict(passed_first_native_flat_policy=True,go=go,positive=positive,actual_precontrol=pre,owner=oi,node=ni,worker=wi,GPU_snapshot=gpu,remaining_snapshot=c['remaining_training_seconds'],original_current_active_owner=c['active_segment']['owner_parent_pid'],no_model_read_or_account_write=True,not_skill_success_or_continuous_alive=True)));break
 if errors or not oi or not ni or (worker and not wi):
  print(json.dumps(dict(passed_first_native_flat_policy=False,go=go,owner=oi,node=ni,worker=wi,errors=errors,owner_current=read(owner/'OWNER_CURRENT.json'),node_current=read(node/'NODE_CURRENT.json'),no_kill_or_refund=True)));break
 assert time.time()-started<900,'bounded first native observer timeout'
 time.sleep(3)
'''
def main():
 put('FLAT90_FIRST_NATIVE_OBSERVER_CONSUMED_ACTUAL.json',dict(epoch=time.time(),first_once_only=True))
 actual=json.loads((R/'FLAT90_ACTUAL_OWNER_NODE_DETACHED_RETURNED.json').read_bytes());request=json.loads((R/'FLAT90_PUBLIC_ACTUAL_LAUNCH_REQUEST.json').read_bytes())
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('flat90_observer_memory_secret',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  value=d.code(c,d.PY72,CODE,dict(actual=actual,owner=request['owner_root'],node=request['node_root'],job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_NATIVE_2610v90/h1',run_id=request['run_id']),timeout=960)
  put('FLAT90_FIRST_ACTUAL_NATIVE_POLICY_RETURNED_ACTUAL.json',value)
  assert value['passed_first_native_flat_policy'],value
  print(json.dumps(dict(passed=True,actual_flat_SuperMimic_training=True,new_window=value['positive']['native88_migration_window']['counters'],flat_real_events=value['positive']['flat_real_physics_events']['lifetime'],no_skill_success_claim=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('FLAT90_FIRST_OBSERVER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_retry_hotpatch_or_refund=True));raise
