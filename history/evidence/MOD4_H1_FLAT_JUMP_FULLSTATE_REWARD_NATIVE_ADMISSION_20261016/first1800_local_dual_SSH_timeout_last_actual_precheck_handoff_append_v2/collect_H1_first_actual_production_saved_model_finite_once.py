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
 put('H1_FIRST_PRODUCTION_MODEL_READONLY_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),max_source_wait_seconds=600,actual_alive_only_sole_210_72_249_transport_owner=True,only_original_H1_scope_no_GPU_launch=True));c=None;sf=None
 try:
  c=t.connect();begun=time.monotonic()
  while True:
   v=code(c,t.PY,r'''
from pathlib import Path
import sys,json,time,psutil,hashlib
B=Path(sys.argv[1]);names=('OWNER_IDENTITY.json','OWNER_CURRENT.json','OWNER_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json');rows=[]
for n in names:
 p=B/n
 if p.exists():
  raw=p.read_bytes();rows.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');budget=json.loads(C.read_bytes());scripts={str(B/'h1_first1800_original_canonical_owner_v1.py')};procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(x in scripts for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),files=rows,actual_owner_processes=procs,actual_original_canonical_snapshot={k:budget[k] for k in ('active_segment','authorized_training_seconds','charged_training_seconds','remaining_training_seconds')},readonly=True)))
''',S);p=R/'H1_FIRST_PRODUCTION_FINITE_SOURCE_CURRENT_ACTUAL.json';tmp=p.with_suffix('.json.partial');tmp.write_text(json.dumps(v,indent=2),encoding='utf8');tmp.replace(p);current=next((x['value'] for x in v['files'] if x['path'].endswith('/OWNER_CURRENT.json')),{});row=current.get('row',{});latest=row.get('latest_save') or {}
   if (row.get('phase')=='production' and latest.get('updates',0)>=1) or any(x['path'].endswith('/OWNER_EXIT_ACTUAL.json') or 'ORIGINAL_ERROR' in x['path'] for x in v['files']) or time.monotonic()-begun>=600:break
   time.sleep(15)
  put('H1_FIRST_PRODUCTION_BOUND_SOURCE_READONLY_COMPLETE_ACTUAL.json',v)
 finally:t.close(c);c=None
 if row.get('phase')!='production' or latest.get('updates',0)<1:
  print(json.dumps(dict(no_complete_production_PPO_observed_yet=True,current=row)),flush=True);return
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
 p=B/'job0/production'/name;assert p.is_file();models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
prefix=B/'job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json'
if prefix.exists():
 raw=prefix.read_bytes();files.append(dict(path=str(prefix),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
scripts={str(B/n) for n in ('h1_first1800_node72_finite_v1.py','h1_learning_phase_worker_v1.py')};procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(x in scripts for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),files=files,models=models,actual_own_processes=procs,readonly_no_mutation=True,model_update1_immutable_not_rolling_latest=True)))
''',T);sf=c.open_sftp();sf.get_channel().settimeout(120);out=D/'actual_complete_first_production_models';out.mkdir();rows=[]
  for x in v['models']:
   p=out/Path(x['path']).name;part=p.with_suffix('.pt.partial');sf.get(x['path'],str(part));assert part.stat().st_size==x['bytes'] and H(part)==x['SHA'];part.replace(p);rows.append(dict(path=str(p.resolve()),remote=x['path'],bytes=x['bytes'],SHA=x['SHA'],twohost_bytes_SHA_exact=True))
  sf.close();sf=None;v['local_models']=rows;put('H1_FIRST_PRODUCTION_IMMUTABLE_UPDATE1_COMPLETE_MODELS_BOUND_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(complete_production_models=rows,actual_own_processes=v['actual_own_processes'],not_full1800_FINAL_or_jump_skill=True)),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_FIRST_PRODUCTION_FINITE_COLLECT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_new_scope=True));raise
