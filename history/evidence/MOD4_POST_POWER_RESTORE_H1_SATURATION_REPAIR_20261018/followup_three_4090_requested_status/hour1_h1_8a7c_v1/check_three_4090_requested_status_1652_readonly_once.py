"""One requested physical-GPU status snapshot on both hosts; no job mutation."""
from pathlib import Path
import os,sys,json,time,getpass,traceback
import deploy_H1_one_hour_8a7c_native_then_timed_training_once as d
CODE=r'''
from pathlib import Path
import json,sys,time,subprocess,shutil
B=Path(sys.argv[1]);rows={}
for n in ('NODE_CURRENT.json','GO_PRODUCTION.json','NODE_TERMINAL_ACTUAL.json','NODE_ORIGINAL_ERROR.json','OWNER_CURRENT.json','job0/production/OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json','job0/production/FINAL.json'):
 p=B/n
 if p.is_file():rows[n]=json.loads(p.read_bytes())
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,name,utilization.gpu,memory.used,memory.free,power.draw','--format=csv,noheader,nounits'],timeout=15).decode()
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_memory','--format=csv,noheader,nounits'],timeout=15).decode()
D=Path('/mnt/mod4_linux_durable_20261013');disk=dict(path=str(D),is_mount=D.is_mount(),free=shutil.disk_usage(D).free) if D.is_dir() else None
print(json.dumps(dict(epoch=time.time(),gpu_columns='index,uuid,name,utilization_percent,memory_used_MiB,memory_free_MiB,power_W',GPUs=gpu,compute=compute,rows=rows,source_durable_disk=disk,no_runtime_or_budget_write=True)))
'''
def main():
 d.put('THREE_4090_HUMAN_STATUS_1652_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,one_snapshot_no_poll=True,only_actual_CIM_alive_exclusive_transport=True))
 pw=getpass.getpass('72 all-GPU current status (hidden): ');c=None
 try:
  c=d.a.connect72(pw);pw=None;target=d.a.code(c,d.a.PY,CODE,d.TARGET,timeout=90)
 finally:
  pw=None
  if c:c.close();c=None
 try:
  c=d.a.t.connect();source=d.a.code(c,d.a.t.PY,CODE,d.SOURCE,timeout=90)
 finally:
  if c:c.close()
 v=dict(epoch=time.time(),host72=target,host210=source,actual_transport_returned=True,no_job_launch_stop_models_raw_hash_or_account_mutation=True)
 d.put('THREE_4090_HUMAN_STATUS_1652_READONLY_ACTUAL.json',v)
 print(json.dumps(dict(epoch=v['epoch'],host72_GPU=target['GPUs'],host72_compute=target['compute'],host72_progress=target['rows'].get('job0/production/OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json'),host210_GPU=source['GPUs'],host210_compute=source['compute'],source_disk=source['source_durable_disk'],actual_transport_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:d.put('THREE_4090_HUMAN_STATUS_1652_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_job_or_budget_mutation=True));raise
