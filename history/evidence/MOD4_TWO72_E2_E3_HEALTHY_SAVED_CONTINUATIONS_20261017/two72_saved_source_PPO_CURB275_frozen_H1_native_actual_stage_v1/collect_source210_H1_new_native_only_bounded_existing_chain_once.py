"""One bounded connection to collect only the new H1 native chain, no runtime command."""
from pathlib import Path
import sys,os,time,json,traceback
N=Path(__file__).resolve().parent;R=N/'reports';P=N.parent/'MOD4_E1_CURB275_BRIDGE_FROM_CURB35_40_20261016';sys.path.insert(0,str(P))
from collect_hourly0044_existing_V9_FINAL_and_CURB275_production_readonly_once import code,H,t,CANON,SNAP
ROOT='/mnt/mod4_linux_durable_20261013/H125_1710n1'
READ=r'''
from pathlib import Path
import sys,time,json,hashlib,psutil
B=Path(sys.argv[1]);files=[];procs=[];O=B/'job0/native'
for name in ('PARENT_IDENTITY.json','WORKER_STARTED_ACTUAL.json','WORKER_EXIT_ACTUAL.json','NATIVE_CPU_COMMAND_ACTUAL.json','PARENT_FINAL.json','PARENT_EXIT_ACTUAL.json','PARENT_ORIGINAL_ERROR.json','OWN_VALIDATION_FCNTL_HELD_ACTUAL.json','OWN_VALIDATION_FCNTL_RELEASED_ACTUAL.json','job0/native/CURRENT_ACTUAL.json','job0/native/FINAL.json','job0/native/NATIVE180_PRELAUNCH_V2_COMPLETE_ACTUAL.json','job0/native/H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json','job0/native/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','job0/native/ORIGINAL_ERROR.json','job0/native/NATIVE_CPU_ORIGINAL_ERROR.json'):
 p=B/name
 if p.is_file():
  raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if p.pid!=__import__('os').getpid() and any(s.startswith(str(B)+'/') for s in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
models=[];f=O/'NATIVE180_PRELAUNCH_V2_COMPLETE_ACTUAL.json'
if f.exists():
 v=json.loads(f.read_bytes())
 for key in ('initial','saved'):
  row=v[key];p=Path(row['path']);assert p.resolve().is_relative_to(O.resolve()) and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'];models.append(dict(row,kind=key))
print(json.dumps(dict(epoch=time.time(),files=files,actual_own_processes=procs,models=models,root=str(B))))
'''
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('H1_SOURCE210_NATIVE_ONLY_FINITE_COLLECTION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,one_source_connection_max600seconds=True,readonly_existing_artifacts=True));c=None;v={}
 try:
  c=t.connect();begin=time.time()
  while True:
   snap=code(c,t.PY,READ,ROOT)
   if any(x['path'].endswith(('/PARENT_EXIT_ACTUAL.json','/PARENT_ORIGINAL_ERROR.json')) for x in snap['files']) or time.time()-begin>=600:break
   time.sleep(15)
  v['H1']=snap;v['downloaded_models']=[]
  if snap['models']:
   folder=N/'actual_H1_source210_native_models';folder.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(120)
   try:
    for row in snap['models']:
     p=folder/Path(row['path']).name;tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and H(tmp)==row['SHA'];tmp.replace(p);v['downloaded_models'].append(dict(row,local_path=str(p),twohost_complete_SHA=True))
   finally:sf.close()
  v['original_canonical']=code(c,t.PY,CANON);v['N72_owner']=code(c,t.PY,SNAP,'/mnt/mod4_linux_durable_20261013/N72_1710v2','coordinator');v['epoch']=time.time();put('H1_SOURCE210_NATIVE_ONLY_EXISTING_CHAIN_BOUND_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(H1_epoch=snap['epoch'],processes=snap['actual_own_processes'],terminal=[x for x in snap['files'] if x['path'].endswith(('/PARENT_FINAL.json','/PARENT_ORIGINAL_ERROR.json','/PARENT_EXIT_ACTUAL.json'))],models=v['downloaded_models'])),flush=True)
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_SOURCE210_NATIVE_ONLY_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_native_or_GPU_replay=True));raise
