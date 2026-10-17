"""One source-account read, then one target connection; no native replay or old PT collection."""
from pathlib import Path
import sys,os,time,json,getpass,hashlib,importlib.util,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;A=W/'MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017';sys.path[:0]=[str(B),str(A)]
import deploy_b326_mean_overflow_new_native180_only_once as d
sp=importlib.util.spec_from_file_location('prior_collection_pure_CODE_only',A/'collect_interrupted_native_only_two_missing_models_correct_import_V3_once.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
META=r'''
from pathlib import Path
import sys,time,json
B=Path(sys.argv[1]);read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
print(json.dumps(dict(epoch=time.time(),current=read(B/'NATIVE_ONLY_CURRENT.json'),terminal=read(B/'NATIVE_ONLY_PARENT_EXIT_ACTUAL.json'),final=read(B/'NATIVE_ONLY_FINAL_ACTUAL.json'),original_error=read(B/'NATIVE_ONLY_ORIGINAL_ERROR.json'),no_PT_or_raw_hash=True)))
'''
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert (R/'LATEST_H1_NEW_SOURCE_NATIVE180_ONLY_FINITE_PARENT_DETACHED_ACTUAL.json').is_file()
 save('NEW_B326_MEAN_NATIVE_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_creation_argv_alive_only_exclusive_all21072_249_transport=True,max_single_target_metadata_wait900seconds=True,no_new_watcher_Task_or_native=True))
 pw=getpass.getpass('Host72 new b326 mean repair native terminal and two new full models only (hidden): ');c=None
 try:
  import collect_existing_target72_H1_complete_final_original_cost_exit_once as closing
  c=d.a.t.connect();account=d.a.code(c,d.a.t.PY,closing.f.ACCOUNT,timeout=90);d.a.t.close(c);c=None
  c=d.a.connect72(pw);pw=None;begin=time.monotonic()
  while True:
   v=d.a.code(c,d.a.PY,META,d.TARGET,timeout=60);p=R/'NEW_B326_MEAN_NATIVE_FINITE_CURRENT_ACTUAL.json';tmp=p.with_suffix('.json.partial');tmp.write_text(json.dumps(v,indent=2));tmp.replace(p)
   if v['terminal'] or v['original_error'] or time.monotonic()-begin>=900:break
   time.sleep(min(15,max(0,900-(time.monotonic()-begin))))
  v=d.a.code(c,d.a.PY,old.CODE,d.TARGET,timeout=150);v['original_account_actual']=account;v['actual_return_hands_all_transport_back']=True
  out=B/'actual_new_b326_mean_native_models';out.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in v['models']:
    p=out/Path(row['path']).name;assert not p.exists();part=p.with_suffix('.pt.partial');assert not part.exists();sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and hashlib.sha256(part.read_bytes()).hexdigest()==row['SHA'];part.replace(p);row.update(local_path=str(p),twohost_complete_SHA=True)
  finally:sf.close()
  save('NEW_B326_MEAN_NATIVE_EXISTING_TERMINAL_COMPLETE_MODELS_BOUND_COLLECTION_ACTUAL.json',v)
  print(json.dumps(dict(actual_parent_terminal=v['parent_terminal_observed'],models=len(v['models']),actual_own_processes=len(v['actual_own_processes']),actual_target_locks=v['actual_target_locks'],zero_PPO=True)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:save('NEW_B326_MEAN_NATIVE_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True));raise
