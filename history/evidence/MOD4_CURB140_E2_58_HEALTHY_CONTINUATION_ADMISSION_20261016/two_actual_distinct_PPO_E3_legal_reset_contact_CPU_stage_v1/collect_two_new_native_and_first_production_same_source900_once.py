"""One finite source connection observes both owned jobs; no redispatch/signals."""
from pathlib import Path
import sys,os,json,time,getpass,subprocess,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_two_exact_source_continuation_native_cohort_once import code,H,connect72,t,S,T,PY
def put(n,v,rolling=False):
 p=R/n
 if rolling:q=p.with_suffix('.json.partial');q.write_text(json.dumps(v,indent=2),encoding='utf8');q.replace(p)
 else:
  with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
READ=r'''
from pathlib import Path
import sys,json,time,psutil,hashlib
B=Path(sys.argv[1]);key=sys.argv[2];files=[];models=[];names=['OWNER_IDENTITY.json','OWNER_CURRENT.json','OWNER_ORIGINAL_ERROR.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','NO_GRANT_REMOTE_UNOBSERVED_FINITE_EXIT.json','NODE_IDENTITY.json','NODE_CURRENT.json','NODE_ORIGINAL_ERROR.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','HUMAN_TWO_HEALTHY_SAME_SCOPE_CONTINUATION_ACCOUNTING_CONTRACT.json'];selected=[B/n for n in names]
for phase in (('native20k_then_production','production_only') if key=='curb' else ('native','production')):
 out=B/'job0'/phase;selected+=list(out.glob('*.json'))
 for log in (out/'logs').glob('*'):selected+=list(log.glob('*STARTUP_VERIFIED.json'))
 for name in (('own_restored0.pt','own_native144.pt') if 'native' in phase else ('own_fresh_startup0.pt' if key=='curb' else 'own_startup0.pt','model_update1.pt')):
  p=out/name
  if p.is_file():models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),role=phase+'/'+name))
for p in sorted(set(selected)):
 if p.is_file():
  raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B)+'/' in x for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),key=key,files=files,models=models,actual_own_processes=procs,readonly=True)))
'''
def download(c,v,key):
 folder=D/'actual_complete_first_models'/key;folder.mkdir(parents=True,exist_ok=True);sf=c.open_sftp();sf.get_channel().settimeout(120);local=[]
 try:
  for r in v['models']:
   p=folder/r['role'].replace('/','_')
   if p.exists():assert p.stat().st_size==r['bytes'] and H(p)==r['SHA']
   else:
    tmp=p.with_suffix('.pt.partial');assert not tmp.exists();sf.get(r['path'],str(tmp));assert tmp.stat().st_size==r['bytes'] and H(tmp)==r['SHA'];tmp.replace(p)
   local.append(dict(path=str(p),remote=r['path'],bytes=r['bytes'],SHA=r['SHA'],role=r['role'],twohost_bytes_SHA_exact=True))
 finally:sf.close()
 v['local_models']=local
def main():
 put('TWO_CONTINUATION_FIRST_PRODUCTION_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),actual_alive_only_exclusive_transport_owner210_72_249=True,same_source_connection_max900_then_one_target_read=True,no_runtime_launch_or_signal=True));pw=getpass.getpass('Host72 new scopes read-only first-model password (hidden): ');c=None;result={}
 try:
  c=t.connect();begun=time.monotonic()
  while True:
   v=code(c,t.PY,READ,S,'curb');put('TWO_CONTINUATION_SOURCE_CURRENT_FINITE_LOCAL_ACTUAL.json',v,True);cur=next((x['value'] for x in v['files'] if x['path'].endswith('/OWNER_CURRENT.json')),{});rows=cur.get('rows') or {};positive=all((rows.get(k,{}).get('latest_save') or {}).get('updates',0)>=1 and rows.get(k,{}).get('phase')=='production' for k in ('curb','e2'))
   if positive or any(x['path'].endswith(('/OWNER_ORIGINAL_ERROR.json','/OWNER_EXIT_ACTUAL.json')) for x in v['files']) or time.monotonic()-begun>=900:break
   time.sleep(15)
  download(c,v,'curb');result['curb']=v
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;v=code(c,PY,READ,T,'e2');download(c,v,'e2');result['e2']=v;result['epoch']=time.time();put('TWO_CONTINUATION_NATIVE_FIRST_PRODUCTION_COMPLETE_BOUND_COLLECTION_ACTUAL.json',result);print(json.dumps(dict(epoch=result['epoch'],curb_models=result['curb'].get('local_models'),e2_models=result['e2'].get('local_models'),actual_two_PPO_not_inferred_from_native=True)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO_CONTINUATION_FIRST_MODEL_COLLECTOR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_runtime_mutation=True));raise
