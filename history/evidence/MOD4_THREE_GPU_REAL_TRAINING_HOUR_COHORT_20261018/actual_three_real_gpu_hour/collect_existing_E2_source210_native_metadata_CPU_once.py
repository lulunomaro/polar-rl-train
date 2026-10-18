"""One bounded existing native metadata collection, no raw replay/download or production writes."""
import deploy_E2_210_new_fullstate_native_before_three_training_handoff_once as d
import os,sys,time,json,traceback
META=r'''
from pathlib import Path
import sys,json,time,psutil,os,subprocess
B=Path(sys.argv[1]);rows={}
for p in [*B.glob('NATIVE_ONLY*.json'),B/'job0/native/FINAL.json',B/'job0/native/NATIVE144_COMPLETE.json',B/'job0/native/NATIVE_ALL_ROWS_CPU_ADMITTED.json',B/'job0/native/WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',*B.glob('NATIVE_CPU_ORIGINAL_ERROR_*.json')]:
 if p.is_file():rows[p.relative_to(B).as_posix()]=json.loads(p.read_bytes())
own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),rows=rows,own_processes=own,compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),readonly_no_rawhash=True)))
'''
if __name__=='__main__':
 c=None
 try:
  d.put('E2_SOURCE210_NATIVE_METADATA_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_transport=True,same_connection_metadata_max900=True));c=d.a.t.connect();begin=time.monotonic()
  while True:
   v=d.a.code(c,d.a.t.PY,META,d.TARGET,timeout=90)
   if 'NATIVE_ONLY_PARENT_EXIT_ACTUAL.json' in v['rows'] or time.monotonic()-begin>=900:break
   time.sleep(10)
  d.put('E2_SOURCE210_NATIVE_COMPLETE_OR_PENDING_CPU_METADATA_ACTUAL.json',v);print(json.dumps(v),flush=True)
 except BaseException:d.put('E2_SOURCE210_NATIVE_COLLECTOR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_replay=True));raise
 finally:
  if c:c.close()
