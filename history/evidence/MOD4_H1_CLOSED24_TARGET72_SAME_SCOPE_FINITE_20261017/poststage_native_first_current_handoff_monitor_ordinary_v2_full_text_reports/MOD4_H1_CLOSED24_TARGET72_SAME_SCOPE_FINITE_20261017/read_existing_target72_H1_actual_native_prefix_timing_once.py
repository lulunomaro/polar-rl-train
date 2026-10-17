"""One own-scope actual progress/log/OS read after bounded collector handback; no restart."""
from pathlib import Path
import sys,os,json,time,getpass,traceback
B=Path(__file__).resolve().parent;R=B/'reports';from deploy_H1_closed24_target72_new_native_original_handoff_once import a,TARGET
CODE=r'''
from pathlib import Path
import sys,os,time,json,psutil,subprocess
B=Path(sys.argv[1]);J=B/'job0';out={}
for name in ('CURRENT_ACTUAL.json','FINAL.json','NATIVE180_PRELAUNCH_V2_COMPLETE_ACTUAL.json','H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json','ORIGINAL_ERROR.json','ORIGINAL_ERROR_BEFORE_APP_CLOSE.json'):
 p=J/'native'/name
 if p.is_file():out[name]=json.loads(p.read_bytes())
p=J/'native/ALL_VALID_NATIVE_PREFIX_INDEX.json'
if p.is_file():
 v=json.loads(p.read_bytes());out[p.name]=dict(epoch=v['epoch'],controls_chunks=len(v['controls']),physics_chunks=len(v['physics']),controls=sum(x['rows'] for x in v['controls']),physics=sum(x['rows'] for x in v['physics']))
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','status','cpu_times','memory_info','num_threads']):
 try:
  if p.pid!=os.getpid() and any(s.startswith(str(B)+'/') for s in p.info['cmdline'] or []):
   x=p.info;x['cpu_times']=list(x['cpu_times']);x['memory_info']=list(x['memory_info']);procs.append(x)
 except psutil.Error:pass
p=J/'native_WORKER.log';tail=None
if p.is_file():
 with p.open('rb') as f:f.seek(max(0,p.stat().st_size-16000));tail=f.read().decode('utf8','replace')
print(json.dumps(dict(epoch=time.time(),root=str(B),files=out,actual_own_processes=procs,own_native_log_last16000=tail,gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,utilization.gpu,memory.used,memory.total','--format=csv,noheader,nounits']).decode(),compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory','--format=csv,noheader,nounits']).decode(),no_GPU_task_or_source_mutation=True)))
'''
def main():
 old=json.loads((R/'H1_TARGET72_NEW_NATIVE_IMMUTABLE_FIRST_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert old['actual_return_hands_all_transport_back'];pw=getpass.getpass('Host72 current H1 native timing read-only (hidden): ');c=None
 try:c=a.connect72(pw);pw=None;v=a.code(c,a.PY,CODE,TARGET,timeout=60)
 finally:
  pw=None
  if c:c.close()
 v['actual_return_hands_all_transport_back']=True
 with (R/'H1_TARGET72_ACTUAL_NATIVE_PREFIX_TIMING_EXISTING_ONLY_SINGLE_READ_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 print(json.dumps(dict(epoch=v['epoch'],progress=v['files'].get('CURRENT_ACTUAL.json'),prefix=v['files'].get('ALL_VALID_NATIVE_PREFIX_INDEX.json'),GPU=v['gpu'],compute=v['compute'],own_processes=v['actual_own_processes'],logtail=(v['own_native_log_last16000'] or '')[-3500:])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_TARGET72_PREFIX_TIMING_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_restart_or_GPU_replay=True),f,indent=2)
  raise
