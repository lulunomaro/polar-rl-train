"""Only new final models/accounting from the running v2, not old first/native replay."""
from pathlib import Path
import os,sys,time,json,getpass,traceback
V=Path(__file__).resolve().parent;R=V/'reports'
from deploy_recovered_three_finals_new_native_then_original_owner_once import a,SOURCE,ROOTS
from importlib.util import spec_from_file_location,module_from_spec
U=V.parent/'MOD4_UNIFIED_THREE_SLOT_H1_E2_E3_HANDOFF_20261017';sp=spec_from_file_location('existing_account_readonly',U/'collect_existing_three_slot_after_local_collector_unreported_exit_v2_once.py');old=module_from_spec(sp);sp.loader.exec_module(old)
READ=r'''
from pathlib import Path
import os,sys,json,time,hashlib,psutil
B=Path(sys.argv[1]);key=sys.argv[2];names=['OWNER_IDENTITY.json','OWNER_CURRENT.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json'] if key=='owner' else ['NODE_IDENTITY.json','NODE_CURRENT.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','NODE_ORIGINAL_ERROR.json','OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json','job0/GO_PRODUCTION.json','job0/production/FINAL.json','job0/production/latest_complete.json','job0/production/STARTUP_H1_SOURCE_ACTUAL.json','job0/production/STARTUP_SOURCE_ACTUAL.json','job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json'];files=[]
if key!='owner':names += [p.relative_to(B).as_posix() for p in (B/'job0/production').glob('*ORIGINAL_ERROR*.json')]
for rel in dict.fromkeys(names):
 p=B/rel
 if p.is_file():
  raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if p.pid!=os.getpid() and any(s.startswith(str(B)+'/') for s in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
models=[];f=B/'job0/production/FINAL.json'
if key!='owner' and f.is_file():
 v=json.loads(f.read_bytes())
 if v.get('passed'):
  r=v['final'];p=Path(r['path']);assert p.resolve().is_relative_to((B/'job0/production').resolve()) and p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'];models.append(dict(r,kind='actual_complete_final'))
print(json.dumps(dict(epoch=time.time(),root=str(B),key=key,files=files,actual_own_processes=procs,models=models,readonly=True)))
'''
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def download(conn,row,key):
 folder=V/'actual_window_v2_closed_finals'/key;folder.mkdir(parents=True);sf=conn.open_sftp();sf.get_channel().settimeout(120);out=[]
 try:
  for r in row['models']:
   p=folder/Path(r['path']).name;tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf.get(r['path'],str(tmp));assert tmp.stat().st_size==r['bytes'] and a.H(tmp)==r['SHA'];tmp.replace(p);out.append(dict(r,local_path=str(p),twohost_complete_SHA=True))
 finally:sf.close()
 return out
def main():
 put('WINDOW_V2_FINALS_ORIGINAL_HANDOFF_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,one_source_connection_max600seconds=True,no_GPU_runtime_or_ledger_write=True));pw=getpass.getpass('Host72 only new v2 final models (hidden): ');conn=None;v={};models={}
 try:
  conn=a.t.connect();begin=time.time()
  while True:
   owner=a.code(conn,a.t.PY,READ,SOURCE,'owner');done=next((x['value'] for x in owner['files'] if x['path'].endswith('/COHORT_FINAL.json')),None);error=any('OWNER_ORIGINAL_ERROR' in x['path'] for x in owner['files'])
   if done or error or time.time()-begin>=600:break
   current=next((x['value'] for x in owner['files'] if x['path'].endswith('/OWNER_CURRENT.json')),{});tmp=R/'WINDOW_V2_FINALS_SOURCE_WAIT_CURRENT.json.partial';tmp.write_text(json.dumps(dict(epoch=time.time(),go=current.get('go'),rows={k:dict(phase=r.get('phase'),latest=r.get('latest_save'),terminal=r.get('terminal_all_own_children_waited'),original_error=r.get('original_error')) for k,r in current.get('rows',{}).items()}),indent=2));tmp.replace(R/'WINDOW_V2_FINALS_SOURCE_WAIT_CURRENT.json');time.sleep(15)
  v['owner']=owner;v['h1']=a.code(conn,a.t.PY,READ,ROOTS['h1'],'h1');models['h1']=download(conn,v['h1'],'h1');v['account']=a.code(conn,a.t.PY,old.ACCOUNT)
 finally:a.t.close(conn);conn=None
 try:
  conn=a.connect72(pw);pw=None
  for key in ('e2','recovery'):v[key]=a.code(conn,a.PY,READ,ROOTS[key],key);models[key]=download(conn,v[key],key)
 finally:
  pw=None
  if conn:conn.close()
 v.update(epoch=time.time(),downloaded_final_models=models,no_old_first_startup_native_PT_redownloaded=True,actual_closed=bool(done and all(models.values()) and all(not v[k]['actual_own_processes'] for k in ('owner','h1','e2','recovery')) and v['account']['original_canonical']['active_segment'] is None and all(x['actual_fcntl_free'] for x in v['account']['actual_locks'])));put('WINDOW_V2_THREE_FINALS_EXISTING_FULLSAVE_COST_EXIT_ORIGINAL_HANDOFF_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(actual_closed=v['actual_closed'],models={k:[dict(SHA=r['SHA'],updates=r['updates'],bytes=r['bytes']) for r in rs] for k,rs in models.items()},original_locks=v['account']['actual_locks'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('WINDOW_V2_FINALS_HANDOFF_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_once_or_ledger_replay=True));raise
