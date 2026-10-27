"""One finite first-update receipt, own JSON/identities only, no model/GPU query."""
from pathlib import Path
import json,time,sys,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE='''from pathlib import Path
import importlib.util,json,time,sys
job=Path(v['job']);owner=job.parent/'owner';sys.path.insert(0,str(owner))
sp=importlib.util.spec_from_file_location('owned_first_E0_snapshot_only',owner/'E0_first_metadata_observer_readonly_v1.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
from E0_single72_bound_cfg_v1 import expected_exec,logical_argv
started=time.time();result=None
while time.time()-started<600:
 s=m.snapshot();files=s['known_own_JSON'];out=job/'adaptation'
 def value(p):return (files.get(str(p)) or {}).get('value')
 positive=value(out/'PPO_POSITIVE_CURRENT.json');restore=value(out/'SOURCE_FULLRESTORE_ZERO_VERIFIED.json');clock=value(out/'CLOCK_GAS400_NATIVE24_ACTUAL.json');go=value(job/'GO_PRODUCTION.json')
 errors={}
 for p in (job.parent/'node_e0/NODE_ORIGINAL_ERROR.json',owner/'OWNER_ORIGINAL_ERROR.json',out/'WORKER_ORIGINAL_ERROR.json',out/'WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json'):
  if p.is_file():errors[str(p)]=json.loads(p.read_bytes())
 terminal=value(job.parent/'node_e0/NODE_TERMINAL_ACTUAL.json')
 if errors or (terminal and terminal.get('row',{}).get('original_error')):
  result=dict(passed_first_PPO=False,original_errors=errors,snapshot=s,stopped_on_original_terminal_or_error=True);break
 if positive and restore and clock and go:
  assert positive['new_updates']>0 and positive['Adam_step']==639560+20*positive['new_updates']
  assert restore['original_actor9_critic8_STD_17Adam_LR_D1_D7_exact'] and restore['own0']['Adam_step']==639560
  assert clock['passed'] and clock['controls']==24 and clock['physics_callbacks']==192 and clock['feedback_samples']==48 and clock['actual_RewardManager_dt_s']==.02 and clock['actual_reward_compute_calls']==24
  assert go['GPU_UUID']=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d' and go['source_CPU_SHA']=='a51a28b52c6c3a5ab01bbb346db48de78730c77274dc59655ec4b2275986f80a' and go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300
  worker=value(job/'production_STARTED_ACTUAL.json');assert worker
  own=next(r for r in s['known_own_processes'] if r['pid']==worker['pid'])
  if own.get('exact_recorded_own_creation_matched'):
   expected=expected_exec(logical_argv(job,'E0_PPO50_gas400_finite_worker_v5_writer_before_presave.py')+['--job-root',str(job)])
   assert all(own[k]==expected[k] for k in ('exe','argv','root'))
  else:assert own.get('actual_own_process_out')
  result=dict(passed_first_PPO=True,actual_GPU=go['GPU_UUID'],actual_restore_and_24control_clock_gas_readback=True,positive=positive,go=go,snapshot=s,policy_skill_or_FULL_FINAL_not_claimed=True);break
 time.sleep(3)
if result is None:result=dict(passed_first_PPO=False,bounded_observation_timeout=True,snapshot=m.snapshot(),no_failure_cause_invented=True)
result.update(actual_remote_observer_returned=True,observer_wall_seconds=time.time()-started,no_PT_GPU_or_account_IO=True)
print(json.dumps(result))
'''
def main():
 put('E0_FIRST_ACTUAL_PPO_OBSERVER_CONSUMED_ACTUAL.json',dict(epoch=time.time(),finite600s_max=True,no_second_daemon_or_model_read=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('E0_first_PPO_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None;result=d.code(c,d.PY72,CODE,dict(job=JOB),timeout=650)
  put('E0_FIRST_ACTUAL_4090_PPO_V5_FULLRESTORE_CLOCK_GAS400_RETURNED_ACTUAL.json',result)
  print(json.dumps({k:v for k,v in result.items() if k!='snapshot'}))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('E0_FIRST_PPO_OBSERVER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_retry_or_training_action=True));raise
