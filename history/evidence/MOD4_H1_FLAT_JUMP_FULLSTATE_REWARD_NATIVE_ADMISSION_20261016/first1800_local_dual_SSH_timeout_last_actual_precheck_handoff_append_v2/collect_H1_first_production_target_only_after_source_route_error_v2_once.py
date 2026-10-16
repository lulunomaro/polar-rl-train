"""After earlier transport handoff, collect this one admitted H1 first production save.

Bounded source connection, then target connection; no runtime launch or mutation.
"""
from pathlib import Path
import sys,os,json,time,hashlib,subprocess,traceback,getpass
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D))
from deploy_H1_admitted_first1800_original_owner_fresh_chain_once import code,H,connect72,t,S,T,PY
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('H1_FIRST_PRODUCTION_TARGET_ONLY_READONLY_V2_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),max_source_wait_seconds=600,actual_alive_only_sole_210_72_249_transport_owner=True,only_original_H1_scope_no_GPU_launch=True));c=None;sf=None
 # Original source observer connection reset then fresh read-only route timed out.
 # This independent V2 reads actual owned target state, never assumes a runtime fault.
 pw=getpass.getpass('Host72 complete H1 first production model collection password (hidden): ')
 try:
  c=connect72(pw);pw=None;v=code(c,PY,r'''
from pathlib import Path
import sys,json,time,hashlib,psutil
B=Path(sys.argv[1]);files=[]
selected=list(B.glob('*.json'))
for name in ('precheck128','precheck20k','production'):
 out=B/'job0'/name;selected+=list(out.glob('*.json'))
 for log in (out/'logs').glob('*'):
  selected+=list(log.glob('*STARTUP_VERIFIED.json'))+list(log.glob('run_manifest.json'))
for p in sorted(set(selected)):
 raw=p.read_bytes();row=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
 try:row['value']=json.loads(raw)
 except ValueError:row['parse_failed']=True
 files.append(row)
models=[]
for name in ('own_H1_startup0.pt','model_update1.pt'):
 p=B/'job0/production'/name
 if not p.is_file():continue
 models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
prefix=B/'job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json'
if prefix.exists():
 raw=prefix.read_bytes();files.append(dict(path=str(prefix),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
scripts={str(B/n) for n in ('h1_first1800_node72_finite_v1.py','h1_learning_phase_worker_v1.py')};procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(x in scripts for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),files=files,models=models,actual_own_processes=procs,readonly_no_mutation=True,model_update1_immutable_not_rolling_latest=True)))
''',T)
  if len(v['models'])<2:
   put('H1_FIRST_PRODUCTION_TARGET_ONLY_V2_NO_COMPLETE_MODEL_SNAPSHOT_ACTUAL.json',v);print(json.dumps(dict(complete_production_models_notyetobserved=True,selected=[dict(name=Path(x['path']).name,value=x.get('value')) for x in v['files'] if Path(x['path']).name in ('NODE_CURRENT.json','NODE_ORIGINAL_ERROR.json','NODE_EXIT_ACTUAL.json')],actual_processes=v['actual_own_processes'])));return
  sf=c.open_sftp();sf.get_channel().settimeout(120);out=D/'actual_complete_first_production_models';out.mkdir();rows=[]
  for x in v['models']:
   p=out/Path(x['path']).name;part=p.with_suffix('.pt.partial');sf.get(x['path'],str(part));assert part.stat().st_size==x['bytes'] and H(part)==x['SHA'];part.replace(p);rows.append(dict(path=str(p.resolve()),remote=x['path'],bytes=x['bytes'],SHA=x['SHA'],twohost_bytes_SHA_exact=True))
  sf.close();sf=None;v['local_models']=rows;put('H1_FIRST_PRODUCTION_IMMUTABLE_UPDATE1_COMPLETE_MODELS_BOUND_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(complete_production_models=rows,actual_own_processes=v['actual_own_processes'],not_full1800_FINAL_or_jump_skill=True)),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_FIRST_PRODUCTION_TARGET_ONLY_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_new_scope=True));raise
