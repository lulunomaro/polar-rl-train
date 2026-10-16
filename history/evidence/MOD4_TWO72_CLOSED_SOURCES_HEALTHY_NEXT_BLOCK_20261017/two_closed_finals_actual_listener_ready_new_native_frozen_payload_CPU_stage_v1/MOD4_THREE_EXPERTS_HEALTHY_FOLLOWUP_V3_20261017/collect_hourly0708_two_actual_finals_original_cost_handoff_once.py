"""Only new final models and original cost/exit handoff; no runtime commands."""
from pathlib import Path
import os,sys,time,json,getpass,traceback,importlib.util
F=Path(__file__).resolve().parent;R=F/'reports';W=F.parent;U=W/'MOD4_UNIFIED_THREE_SLOT_H1_E2_E3_HANDOFF_20261017';V=W/'MOD4_THREE_EXPERTS_RECOVERED_FULL_FINAL_CONTINUATION_20261017';sys.path.insert(0,str(U))
from deploy_two72_followup_storage_rejected_H1_original_writer_once import a,SOURCE,ROOTS
sp=importlib.util.spec_from_file_location('existing_final_reader_sources_only',V/'collect_window_v2_actual_closed_finals_original_handoff_finite_v2_once.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old);READ=old.READ;ACCOUNT=old.old.ACCOUNT
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def download(c,row,key):
 out=[];folder=F/'actual_safe72_closed_finals'/key
 if row['models']:folder.mkdir(parents=True,exist_ok=True)
 sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:
  for r in row['models']:
   p=folder/Path(r['path']).name;tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf.get(r['path'],str(tmp));assert tmp.stat().st_size==r['bytes'] and a.H(tmp)==r['SHA'];tmp.replace(p);out.append(dict(r,local_path=str(p),twohost_complete_SHA=True))
 finally:sf.close()
 return out
def main():
 put('HOURLY0708_TWO_FINALS_HANDOFF_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,one_source_then_one_target_connection_no_poll=True,no_runtime_GPU_budget_mutation=True));pw=getpass.getpass('Host72 only new final models and original handoff (hidden): ');c=None;v={};models={}
 try:c=a.t.connect();v['owner']=a.code(c,a.t.PY,READ,SOURCE,'owner');v['account']=a.code(c,a.t.PY,ACCOUNT)
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None
  for key in ROOTS:v[key]=a.code(c,a.PY,READ,ROOTS[key],key);models[key]=download(c,v[key],key)
 finally:
  pw=None
  if c:c.close()
 done=next((r['value'] for r in v['owner']['files'] if r['path'].endswith('/COHORT_FINAL.json')),None);v.update(epoch=time.time(),downloaded_final_models=models,H1_preGO_resource_rejected_no_worker_no_GO_no_charge=True,no_old_immutable_first_startup_native_redownload=True,actual_closed=bool(done and all(models.values()) and all(not v[k]['actual_own_processes'] for k in ('owner','e2','recovery')) and v['account']['original_canonical']['active_segment'] is None and all(x['actual_fcntl_free'] for x in v['account']['actual_locks'])));put('SAFE72_HOURLY0708_TWO_COMPLETE_FINALS_COST_EXIT_ORIGINAL_HANDOFF_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(actual_closed=v['actual_closed'],models=models,original_locks=v['account']['actual_locks'],remaining=v['account']['original_canonical']['remaining_training_seconds'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('HOURLY0708_TWO_FINALS_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_readonly_no_GPU_or_once_replay=True));raise
