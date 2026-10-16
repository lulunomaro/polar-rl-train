"""Human status question: one source and one target snapshot; no task changes."""
from pathlib import Path
import sys,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_grounded_H1_V2_new_native_CPU_then_finite1800_once import code,connect72,t,PY
READ=r'''
from pathlib import Path
import sys,json,time,psutil,subprocess
host=sys.argv[1];roots=json.loads(sys.argv[2]);procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  cmd=p.info['cmdline'] or [];owned=any('/mnt/mod4_linux_durable_20261013/' in x or '/home/lc01/Zonglin Li/zonglin2/tasks/' in x for x in cmd)
  if owned:procs.append(p.info)
 except psutil.Error:pass
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,name,utilization.gpu,memory.used,memory.total','--format=csv,noheader,nounits']).decode();compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();files=[]
for root in roots:
 B=Path(root)
 for rel in ('OWNER_CURRENT.json','OWNER_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json','NODE_CURRENT.json','NODE_EXIT_ACTUAL.json','job0/production/FINAL.json','job0/production/latest_complete.json','job0/production/STARTUP_H1_SOURCE_ACTUAL.json','job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json'):
  p=B/rel
  if p.is_file():
   raw=p.read_bytes()
   if len(raw)<1000000:files.append(dict(path=str(p),value=json.loads(raw)))
print(json.dumps(dict(epoch=time.time(),host=host,gpus_csv=gpu,compute_gpu_pid_memory_csv=compute,actual_owned_processes=procs,files=files,readonly_no_launch_stop_signal_or_budget_change=True)))
'''
def main():
 dest=R/'HUMAN_THREE4090_TASKS_CURRENT_READONLY1718_ACTUAL.json';assert not dest.exists();c=None;pw=getpass.getpass('Host72 current tasks read-only password (hidden): ');v={}
 try:
  c=t.connect();v['source210']=code(c,t.PY,READ,'210',json.dumps(['/mnt/mod4_linux_durable_20261013/MOD4_E1_CURB35_FROM_878_NATIVE_TRAIN_20261016/production_fresh_process_v2','/mnt/mod4_linux_durable_20261013/'+D.name]))
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;v['target72']=code(c,PY,READ,'72',json.dumps(['/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_HOST72_E2_MOVING4_AND_H1_JUMP_ADMISSION_20261016','/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name]));v.update(epoch=time.time(),current_status_snapshot_not_permanent_idle_or_active=True);dest.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:(R/('HUMAN_THREE_GPU_TASKS_READONLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_mutation=True),indent=2),encoding='utf8');raise
