"""One bounded sequential read of the existing recovery final; no native/PPO or old first/raw replay."""
from pathlib import Path
import sys,os,time,json,getpass,traceback,importlib.util
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';R.mkdir(exist_ok=True)
K=W/'MOD4_V8_FINALS_E2_FROZEN_REGRESSION_RECOVERY_ONLY_HANDOFF_20261017';G=W/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017'
sys.path.insert(0,str(K));sys.path.insert(0,str(G))
from deploy_healthy_recovery_only_E2_frozen_regression_review_hold_original_handoff_once import a,SOURCE,ROOTS
sp=importlib.util.spec_from_file_location('existing_closed_final_read_functions_only',G/'collect_existing_v5_actual_terminal_original_handoff_bounded_missing_final_only_once.py');f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f)
def save(n,v):
 with (R/n).open('x',encoding='utf8') as h:json.dump(v,h,indent=2)
def main():
 save('RECOVERY_EXISTING_FINAL_1603_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_all_transport=True,one_source_then_one_target_read_only_no_poll=True,max_source_seconds=180))
 pw=getpass.getpass('Host72 existing recovery final only (hidden): ');c=None;v={};models=[]
 try:
  c=a.t.connect();v['owner']=a.code(c,a.t.PY,f.READ,SOURCE,'owner',timeout=120);v['account']=a.code(c,a.t.PY,f.ACCOUNT,timeout=90)
  v['source_current_storage']=a.code(c,a.t.PY,"import json,time,shutil;from pathlib import Path;D=Path('/mnt/mod4_linux_durable_20261013');print(json.dumps(dict(epoch=time.time(),D=dict(zip(('total','used','free'),shutil.disk_usage(D))),home=dict(zip(('total','used','free'),shutil.disk_usage('/home/egde/rl_candidates'))),storage_readonly=True)))",timeout=30)
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None;key='recovery';v[key]=a.code(c,a.PY,f.READ,ROOTS[key],key,timeout=120)
  sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in v[key]['models']:
    p=B/'actual_closed_final_models'/key/Path(row['path']).name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();tmp=p.with_suffix('.pt.partial');assert not tmp.exists();sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and a.H(tmp)==row['SHA'];tmp.replace(p);models.append(dict(row,local_path=str(p),twohost_complete_SHA=True))
  finally:sf.close()
 finally:
  pw=None
  if c:c.close()
 done=next((r['value'] for r in v['owner']['files'] if r['path'].endswith('/COHORT_FINAL.json')),None)
 v.update(epoch=time.time(),downloaded_final_models=dict(recovery=models),no_first_native_or_old_complete_PT_raw_rehashed_or_redownloaded=True,actual_closed=bool(done and models and not v['owner']['actual_own_processes'] and not v['recovery']['actual_own_processes'] and v['account']['original_canonical']['active_segment'] is None and all(x['actual_fcntl_free'] for x in v['account']['actual_locks'])),no_runtime_GPU_budget_signal_or_replay=True)
 save('RECOVERY_EXISTING_FINAL_COMPLETE_COST_EXIT_ORIGINAL_HANDOFF_1603_BOUND_COLLECTION_ACTUAL.json',v)
 print(json.dumps(dict(actual_closed=v['actual_closed'],models=models,canonical_active=v['account']['original_canonical']['active_segment'],locks=v['account']['actual_locks'],remaining=v['account']['original_canonical']['remaining_training_seconds'],storage=v['source_current_storage'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('RECOVERY_FINAL_1603_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),read_only_unknown_outcome_no_replay=True));raise
