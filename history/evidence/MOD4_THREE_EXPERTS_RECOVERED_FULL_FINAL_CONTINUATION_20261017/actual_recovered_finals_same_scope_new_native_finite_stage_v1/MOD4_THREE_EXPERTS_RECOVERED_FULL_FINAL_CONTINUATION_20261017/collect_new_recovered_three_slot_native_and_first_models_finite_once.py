"""One bounded read of the newly dispatched finite chain, no second coordinator."""
from pathlib import Path
import sys,os,time,json,getpass,traceback
U=Path(__file__).resolve().parent;R=U/'reports';N=U.parent/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017';sys.path.insert(0,str(N))
import deploy_two72_new_native_after_actual_final_then_original_CURB_handoff_once as a
from deploy_recovered_three_finals_new_native_then_original_owner_once import SOURCE,ROOTS
READ=r'''
from pathlib import Path
import os,sys,time,json,hashlib,psutil
B=Path(sys.argv[1]);key=sys.argv[2];names=['OWNER_IDENTITY.json','OWNER_CURRENT.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json','NO_GO_PARTIAL_REGISTRATION_EXPIRED_ACTUAL.json'] if key=='owner' else ['NODE_IDENTITY.json','NODE_CURRENT.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','NODE_ORIGINAL_ERROR.json','H1_ACTUAL_SAME_SOURCE_BACKEND_NATIVE_REUSE_CPU_BINDING.json','OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json','NATIVE_CPU_ACTUAL_STATUS_BRIDGE_RECEIPT.json','job0/native/NATIVE144_COMPLETE.json','job0/native/NATIVE336_COMPLETE.json','job0/native/NATIVE_ALL_ROWS_CPU_ADMITTED.json','job0/native/FINAL.json','job0/GO_PRODUCTION.json','job0/production/STARTUP_H1_SOURCE_ACTUAL.json','job0/production/STARTUP_SOURCE_ACTUAL.json','job0/production/SOURCE_TYPED_ZERO_CLOCK_ACTUAL.json','job0/production/FINAL.json','job0/production/latest_complete.json','job0/production/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','job0/production/WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json'];files=[]
for rel in names:
 p=B/rel
 if p.is_file():
  raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw) if len(raw)<2000000 else None,large_index_only=len(raw)>=2000000))
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if p.pid!=os.getpid() and any(s.startswith(str(B)+'/') for s in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
models=[]
if key!='owner':
 for kind,name in [('immutable_startup0','own_H1_startup0.pt' if key=='h1' else 'own_startup0.pt'),('immutable_first','model_update1.pt')]:
  p=B/'job0/production'/name
  if p.is_file():models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),kind=kind))
 if key=='recovery':
  p=B/'job0/native/own_native336.pt';proof=B/'job0/native/NATIVE_ALL_ROWS_CPU_ADMITTED.json'
  if p.is_file() and proof.is_file() and json.loads(proof.read_bytes())['passed']:models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),kind='production_typed_source_native_reference'))
print(json.dumps(dict(epoch=time.time(),root=str(B),key=key,files=files,actual_own_processes=procs,models=models,readonly=True)))
'''
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def get_models(c,row,key):
 models=[];folder=U/'actual_three_slot_first_models'/key
 if row['models']:folder.mkdir(parents=True,exist_ok=True)
 sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:
  for r in row['models']:
   p=folder/Path(r['path']).name;tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf.get(r['path'],str(tmp));assert tmp.stat().st_size==r['bytes'] and a.H(tmp)==r['SHA'];tmp.replace(p);models.append(dict(r,local_path=str(p),twohost_complete_SHA=True))
 finally:sf.close()
 return models
def main():
 assert (R/'RECOVERED_THREE_SLOT_ALL_NEW_NATIVE_FINITE_CHAIN_DETACHED_ACTUAL.json').is_file();put('THREE_SLOT_FIRST_MODELS_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,max_one_source_connection1800seconds=True,readonly_existing_new_scopes_no_GPU_or_ledger_mutation=True));pw=getpass.getpass('Host72 new three-slot immutable first checkpoints only (hidden): ');c=None;v={};models={}
 try:
  c=a.t.connect();begin=time.time()
  while True:
   owner=a.code(c,a.t.PY,READ,SOURCE,'owner');cur=next((x['value'] for x in owner['files'] if x['path'].endswith('/OWNER_CURRENT.json')),{});rows=cur.get('rows',{});done={k:((r.get('latest_save') or {}).get('updates',0)>=1 and r.get('phase')=='production') or r.get('terminal_all_own_children_waited') for k,r in rows.items()}
   if set(done)=={'h1','e2','recovery'} and all(done.values()):break
   if any(x['path'].endswith(('/OWNER_ORIGINAL_ERROR.json','/NO_GO_PARTIAL_REGISTRATION_EXPIRED_ACTUAL.json','/OWNER_EXIT_ACTUAL.json')) for x in owner['files']) or time.time()-begin>=1800:break
   p=R/'THREE_SLOT_SOURCE_FIRST_FINITE_CURRENT.json';tmp=p.with_suffix('.json.partial');tmp.write_text(json.dumps(dict(epoch=time.time(),latest={k:dict(phase=r.get('phase'),latest=r.get('latest_save'),original_error=r.get('original_error')) for k,r in rows.items()},go=cur.get('go'),stop_by_slot=cur.get('stop_by_slot')),indent=2));tmp.replace(p);time.sleep(15)
  v['owner']=owner;v['h1']=a.code(c,a.t.PY,READ,ROOTS['h1'],'h1');models['h1']=get_models(c,v['h1'],'h1')
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None
  for key in ('e2','recovery'):v[key]=a.code(c,a.PY,READ,ROOTS[key],key);models[key]=get_models(c,v[key],key)
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();v['downloaded_models']=models;put('THREE_SLOT_ACTUAL_NATIVE_FIRST_IMMUTABLE_MODELS_COMPLETE_BOUND_COLLECTION.json',v);print(json.dumps(dict(epoch=v['epoch'],models=models,new_scope_errors={k:[x for x in v[k]['files'] if 'ORIGINAL_ERROR' in x['path']] for k in ROOTS})),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('THREE_SLOT_FIRST_MODEL_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_once_replay=True));raise
