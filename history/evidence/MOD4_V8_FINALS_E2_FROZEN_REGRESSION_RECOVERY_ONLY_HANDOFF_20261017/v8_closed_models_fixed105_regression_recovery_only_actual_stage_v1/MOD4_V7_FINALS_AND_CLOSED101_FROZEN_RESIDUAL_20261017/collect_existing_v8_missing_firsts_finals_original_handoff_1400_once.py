"""One sequential bounded source/target read, only missing existing artifacts; never GPU/relaunch/account writes."""
from pathlib import Path
import importlib.util,json,os,sys,time,getpass,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';G=W/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017'
sys.path.insert(0,str(G))
from deploy_v7_closed_finals_v8_healthy_native_after_frozen22of64_original_handoff_once import a,SOURCE,ROOTS
def module(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
first=module('actual_first_read_functions_only',D/'collect_new_v8_two72_native_immutable_first_existing_scope_finite_once.py')
final=module('actual_final_read_functions_only',G/'collect_existing_v5_actual_terminal_original_handoff_bounded_missing_final_only_once.py')
P=R/'V8_EXISTING_IMMUTABLE_FINALS_ORIGINAL_COST_EXIT_1400_BOUND_COLLECTION_ACTUAL.json';assert not P.exists()
def save(n,x):
 with (R/n).open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2)
def download(c,row,key,kind):
 out=[];folder=D/('actual_safe72_first_models' if kind=='first' else 'actual_safe72_closed_finals')/key;sf=c.open_sftp();sf.get_channel().settimeout(90)
 try:
  for r in row['models']:
   folder.mkdir(parents=True,exist_ok=True);p=folder/Path(r['path']).name
   if p.exists():assert p.stat().st_size==r['bytes'] and a.H(p)==r['SHA'];out.append(dict(r,local_path=str(p),twohost_complete_SHA=True,existing_complete_not_downloaded_again=True));continue
   tmp=p.with_suffix('.pt.partial');assert not tmp.exists();sf.get(r['path'],str(tmp));assert tmp.stat().st_size==r['bytes'] and a.H(tmp)==r['SHA'];tmp.replace(p);out.append(dict(r,local_path=str(p),twohost_complete_SHA=True))
 finally:sf.close()
 return out
save('V8_EXISTING_1400_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_transport=True,one_source_then_one_target_bounded_readonly_no_poll=True))
pw=getpass.getpass('Host72 existing missing immutable/finals only (hidden): ');c=None;v={};models={};finals={}
try:
 try:c=a.t.connect();v['owner']=a.code(c,a.t.PY,final.READ,SOURCE,'owner');v['account']=a.code(c,a.t.PY,final.ACCOUNT)
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None
  for key in ROOTS:
   v[key]=a.code(c,a.PY,first.READ,ROOTS[key],key);models[key]=download(c,v[key],key,'first');v[key+'_final']=a.code(c,a.PY,final.READ,ROOTS[key],key);finals[key]=download(c,v[key+'_final'],key,'final')
 finally:
  pw=None
  if c:c.close()
 done=next((r['value'] for r in v['owner']['files'] if r['path'].endswith('/COHORT_FINAL.json')),None)
 v.update(epoch=time.time(),downloaded_models=models,downloaded_final_models=finals,actual_owner_terminal_all_out=bool(done and all(not v[k]['actual_own_processes'] for k in ('owner','e2','recovery'))),original_canonical_None_two_fcntl_free=bool(v['account']['original_canonical']['active_segment'] is None and all(x['actual_fcntl_free'] for x in v['account']['actual_locks'])),readonly_no_GPU_budget_signal_or_replay=True)
 with P.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2)
 print(json.dumps(dict(report=str(P),models={k:[(x['kind'],x['SHA']) for x in z] for k,z in models.items()},finals=finals,owner_terminal_all_out=v['actual_owner_terminal_all_out'],canonical_None_two_locks_free=v['original_canonical_None_two_fcntl_free'],errors={k:[r for r in v[k]['files'] if 'ORIGINAL_ERROR' in r['path']] for k in ROOTS})),flush=True)
except BaseException:
 save('V8_EXISTING_1400_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_readonly_first_no_replay=True));raise
