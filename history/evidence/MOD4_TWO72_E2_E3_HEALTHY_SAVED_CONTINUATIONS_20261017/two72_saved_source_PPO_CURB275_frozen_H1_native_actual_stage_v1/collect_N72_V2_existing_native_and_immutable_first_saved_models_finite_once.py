"""Read only the already dispatched N72_v2 scope; never restart any worker."""
from pathlib import Path
import sys,os,json,time,getpass,traceback
N=Path(__file__).resolve().parent;P=N.parent/'MOD4_E1_CURB275_BRIDGE_FROM_CURB35_40_20261016';R=N/'reports'
sys.path.insert(0,str(P))
from collect_hourly0044_existing_V9_FINAL_and_CURB275_production_readonly_once import SNAP,CANON,code,H,connect72,t,PY
S='/mnt/mod4_linux_durable_20261013/N72_1710v2'
T={k:'/home/lc01/Zonglin Li/zonglin2/tasks/N72_1710v2/'+k for k in ('e2','recovery')}
SNAP2=SNAP.replace("'NODE_IDENTITY.json',", "'NODE_TERMINAL_ACTUAL.json','job0/native_CPU_WAITED_EXIT_ACTUAL.json','job0/native/NATIVE_ALL_ROWS_CPU_ADMITTED.json','job0/native/FINAL.json','NODE_IDENTITY.json',").replace("(('model_update1.pt','own_fresh_startup0.pt') if key=='curb' else ())", "('model_update1.pt','own_fresh_startup0.pt')")
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('N72_V2_FINITE_IMMUTABLE_FIRST_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,max_same_connection_wait_seconds=600,no_runtime_GPU_accounting_mutation=True))
 pw=getpass.getpass('Host72 existing N72_v2 artifacts only (hidden): ');c=None;v={};captured={}
 try:
  c=t.connect();v['owner_before']=code(c,t.PY,SNAP,S,'coordinator');v['canonical_before']=code(c,t.PY,CANON)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;begun=time.time();sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   while True:
    all_done=True
    for key,root in T.items():
     row=code(c,PY,SNAP2,root,key);v[key]=row
     for model in row['models']:
      label=(key,model['kind'])
      if label in captured:continue
      folder=N/'actual_N72_v2_immutable_first'/key;folder.mkdir(parents=True,exist_ok=True)
      dest=folder/Path(model['path']).name;part=dest.with_suffix('.pt.partial');assert not dest.exists() and not part.exists();sf.get(model['path'],str(part));assert part.stat().st_size==model['bytes'] and H(part)==model['SHA'];part.replace(dest);captured[label]=dict(model,local_path=str(dest),twohost_complete_SHA=True)
     final_or_error=any('ORIGINAL_ERROR' in q['path'] or q['path'].endswith('/NODE_EXIT_ACTUAL.json') for q in row['files'])
     all_done=all_done and (any(q[0]==key and q[1]=='immutable_model_update1.pt' for q in captured) or final_or_error)
    if all_done or time.time()-begun>=600:break
    time.sleep(15)
   v['target_resources']=code(c,PY,"import time,json,subprocess,psutil;print(json.dumps(dict(epoch=time.time(),GPU_snapshot=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,utilization.gpu,memory.free','--format=csv,noheader,nounits']).decode(),compute_snapshot=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),RAM_available=psutil.virtual_memory().available)))")
  finally:sf.close()
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();v['downloaded_models']=list(captured.values());put('N72_V2_EXISTING_NATIVE_IMMUTABLE_FIRST_COMPLETE_READONLY_ACTUAL.json',v)
 for key in T:
  files=v[key]['files'];node=next((q['value'] for q in files if q['path'].endswith('/NODE_CURRENT.json')),{});row=node.get('row',{});print(json.dumps(dict(key=key,epoch=v[key]['epoch'],phase=row.get('phase'),worker=row.get('worker'),native_CPU=(row.get('native_CPU') or {}).get('value'),latest_save=row.get('latest_save'),errors=[q for q in files if 'ORIGINAL_ERROR' in q['path']],models=[q for q in v['downloaded_models'] if q['path'].startswith(T[key]+'/')]),default=str),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('N72_V2_FIRST_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_replay=True));raise
