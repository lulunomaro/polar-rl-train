"""One finite target-only read of the existing new-source native parent; never dispatches."""
from pathlib import Path
import sys,os,time,json,getpass,hashlib,traceback
B=Path(__file__).resolve().parent;R=B/'reports';sys.path.insert(0,str(B));import deploy_latest_H1_native_only_after_actual_final_handoff_once as d
a=d.a
PROGRAM=r'''
import sys,json,time,psutil,fcntl,hashlib,os
from pathlib import Path
B=Path(sys.argv[1]);deadline=time.monotonic()+900
def read(p):return json.loads(p.read_bytes()) if p.is_file() else None
while True:
 end=read(B/'NATIVE_ONLY_PARENT_EXIT_ACTUAL.json')
 if end or time.monotonic()>=deadline:break
 time.sleep(10)
rows={str(p.relative_to(B)):read(p) for p in sorted(B.rglob('*.json')) if ('job0/native' in str(p) or p.parent==B or p.name.endswith('WAITED_EXIT_ACTUAL.json')) and p.stat().st_size<20000000 and not p.name.startswith('THREE_SLOT_COMPLETE_MANIFEST')}
processes=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  v=p.info
  if any(str(B) in x for x in (v['cmdline'] or [])) and v['pid']!=os.getpid():processes.append(v)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
models=[]
for p in sorted((B/'job0/native').glob('*.pt')):
 models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
locks=[]
for name in ('GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock','validation.lock'):
 # Real resource receipt includes the exact lock paths; unknown names are not asserted free.
 pass
print(json.dumps(dict(epoch=time.time(),root=str(B),rows=rows,actual_own_processes=processes,models=models,zero_PPO_zero_charge=True,parent_terminal_observed=end is not None)))
'''
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 launch=json.loads((R/'LATEST_H1_NEW_SOURCE_NATIVE180_ONLY_FINITE_PARENT_DETACHED_ACTUAL.json').read_bytes());assert launch['native_only_no_production_GO_or_PPO_or_canonical_charge'];save('LATEST_H1_NATIVE_ONLY_FINITE_COLLECTION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_creation_argv_alive_only_exclusive_all_transport=True,source_connection_none=True,target_single_connection_max900_seconds_metadata_wait=True));pw=getpass.getpass('Host72 existing native-only collection (hidden): ');c=None
 try:
  c=a.connect72(pw);pw=None;v=a.code(c,a.PY,PROGRAM,d.TARGET,timeout=960);O=B/'actual_latest_H1_native_models';O.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in v['models']:
    p=O/Path(row['path']).name;assert not p.exists();partial=p.with_suffix('.pt.partial');sf.get(row['path'],str(partial));assert partial.stat().st_size==row['bytes'] and hashlib.sha256(partial.read_bytes()).hexdigest()==row['SHA'];partial.rename(p);row.update(local_path=str(p),twohost_complete_SHA=True)
  finally:sf.close()
  save('LATEST_H1_NATIVE_ONLY_BOUNDED_ACTUAL_PARENT_EXIT_MODELS_COLLECTION.json',v);print(json.dumps(dict(terminal=v['parent_terminal_observed'],models=len(v['models']),actual_own_processes=len(v['actual_own_processes']),native_only_not_PPO=True)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:save('LATEST_H1_NATIVE_ONLY_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
