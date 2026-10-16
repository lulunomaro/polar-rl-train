from pathlib import Path
import os,sys,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ,S,T,code,H,connect72,t,PY
def put(n,v,rolling=False):
 p=R/n
 if rolling:q=p.with_suffix('.json.partial');q.write_text(json.dumps(v,indent=2),encoding='utf8');q.replace(p)
 else:
  with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
MODELS=r'''
from pathlib import Path
import sys,json,time,hashlib
B=Path(sys.argv[1]);key=sys.argv[2];rows=[];phases=('native20k_then_production','production_only') if key=='curb' else ('native','production')
for phase in phases:
 for name in ('own_restored0.pt','own_startup0.pt','own_fresh_startup0.pt','own_native144.pt','own_native336.pt','model_update1.pt'):
  p=B/'job0'/phase/name
  if p.is_file():rows.append(dict(path=str(p),role=phase+'/'+name,bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
print(json.dumps(dict(epoch=time.time(),models=rows)))
'''
def download(c,py,root,key):
 v=code(c,py,MODELS,root,key);folder=D/'actual_full_native_and_first_models'/key;folder.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(120);local=[]
 try:
  for row in v['models']:
   p=folder/row['role'].replace('/','_');tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and H(tmp)==row['SHA'];tmp.replace(p);local.append(dict(**row,local_path=str(p),twohost_complete_SHA_exact=True))
 finally:sf.close()
 return local
def main():
 put('TWO_NATIVE_PPO_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,max_same_connection600s=True,no_runtime_mutation=True));pw=getpass.getpass('Host72 finite new native and first saves (hidden): ');c=None;v={}
 try:
  c=t.connect();begun=time.monotonic()
  while True:
   x=code(c,t.PY,READ,S,'curb');put('TWO_NATIVE_PPO_SOURCE_CURRENT_FINITE_LOCAL_ACTUAL.json',x,True);current=next((r['value'] for r in x['files'] if r['path'].endswith('/OWNER_CURRENT.json')),{});rows=current.get('rows') or {};positive=all((rows.get(k,{}).get('latest_save') or {}).get('updates',0)>=1 and rows.get(k,{}).get('phase')=='production' for k in ('curb','recovery'));error=any('ORIGINAL_ERROR' in r['path'] for r in x['files'])
   if positive or error or any(r['path'].endswith('/OWNER_EXIT_ACTUAL.json') for r in x['files']) or time.monotonic()-begun>=600:break
   time.sleep(20)
  v['curb']=x;v['curb']['local_models']=download(c,t.PY,S,'curb')
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;v['recovery']=code(c,PY,READ,T,'recovery');v['recovery']['local_models']=download(c,PY,T,'recovery')
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();put('TWO_NEW_NATIVE_CPU_AND_AVAILABLE_FIRST_PPO_BOUND_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(epoch=v['epoch'],curb_models=v['curb']['local_models'],recovery_models=v['recovery']['local_models'],curb_errors=[r for r in v['curb']['files'] if 'ORIGINAL_ERROR' in r['path']],recovery_errors=[r for r in v['recovery']['files'] if 'ORIGINAL_ERROR' in r['path']])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO_NATIVE_PPO_COLLECTOR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_signals=True));raise
