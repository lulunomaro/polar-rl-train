"""Bounded existing-scope evidence collection; no new runtime or budget action."""
from pathlib import Path
import os,sys,time,json,getpass,traceback,importlib.util
F=Path(__file__).resolve().parent;R=F/'reports';V=F.parent/'MOD4_THREE_EXPERTS_RECOVERED_FULL_FINAL_CONTINUATION_20261017'
from deploy_healthy_recovery_only_E2_frozen_regression_review_hold_original_handoff_once import a,SOURCE,ROOTS
sp=importlib.util.spec_from_file_location('previous_collector_read_source_only',V/'collect_new_recovered_three_slot_native_and_first_models_finite_once.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old);READ=old.READ
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def get(c,row,key):
 folder=F/'actual_safe72_first_models'/key;models=[]
 if row['models']:folder.mkdir(parents=True,exist_ok=True)
 sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:
  for r in row['models']:
   p=folder/Path(r['path']).name;tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf.get(r['path'],str(tmp));assert tmp.stat().st_size==r['bytes'] and a.H(tmp)==r['SHA'];tmp.replace(p);models.append(dict(r,local_path=str(p),twohost_complete_SHA=True))
 finally:sf.close()
 return models
def main():
 assert (R/'V2_TWO72_HEALTHY_NEW_NATIVE_FINITE_CHAINS_H1_STORAGE_REJECTED_DETACHED_ACTUAL.json').is_file();put('RECOVERY_ONLY_FIRST_MODELS_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,max_one_source_connection900seconds=True,readonly_existing_scopes_no_GPU_or_ledger_mutation=True));pw=getpass.getpass('Host72 existing recovery-only native/immutable first only (hidden): ');c=None;v={};models={}
 try:
  c=a.t.connect();begin=time.time()
  while True:
   owner=a.code(c,a.t.PY,READ,SOURCE,'owner');cur=next((r['value'] for r in owner['files'] if r['path'].endswith('/OWNER_CURRENT.json')),{});rows=cur.get('rows',{});done={k:((rows.get(k,{}).get('latest_save') or {}).get('updates',0)>=1 and rows.get(k,{}).get('phase')=='production') or rows.get(k,{}).get('terminal_all_own_children_waited') for k in ROOTS}
   latest=dict(epoch=time.time(),latest={k:dict(phase=r.get('phase'),latest=r.get('latest_save'),original_error=r.get('original_error'),actual_worker=r.get('worker')) for k,r in rows.items()},go=cur.get('go'),stop_by_slot=cur.get('stop_by_slot'),actual_owner_processes=owner['actual_own_processes'],H1_preGO_storage_rejected_no_GPU_or_GO=True)
   p=R/'RECOVERY_ONLY_SOURCE_FIRST_FINITE_CURRENT.json';tmp=p.with_suffix('.json.partial');tmp.write_text(json.dumps(latest,indent=2));tmp.replace(p)
   if all(done.values()) or any(x['path'].endswith(('/OWNER_ORIGINAL_ERROR.json','/NO_GO_PARTIAL_REGISTRATION_EXPIRED_ACTUAL.json','/OWNER_EXIT_ACTUAL.json')) for x in owner['files']) or time.time()-begin>=900:break
   time.sleep(15)
  v['owner']=owner
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None
  for key in ROOTS:v[key]=a.code(c,a.PY,READ,ROOTS[key],key);models[key]=get(c,v[key],key)
 finally:
  pw=None
  if c:c.close()
 v.update(epoch=time.time(),downloaded_models=models,H1_preGO_resource_rejected_no_training=True);put('RECOVERY_ONLY_NATIVE_FIRST_IMMUTABLE_MODELS_COMPLETE_BOUND_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(epoch=v['epoch'],models=models,new_errors={k:[x for x in v[k]['files'] if 'ORIGINAL_ERROR' in x['path']] for k in ROOTS})),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('RECOVERY_ONLY_FIRST_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_old_once_replay=True));raise
