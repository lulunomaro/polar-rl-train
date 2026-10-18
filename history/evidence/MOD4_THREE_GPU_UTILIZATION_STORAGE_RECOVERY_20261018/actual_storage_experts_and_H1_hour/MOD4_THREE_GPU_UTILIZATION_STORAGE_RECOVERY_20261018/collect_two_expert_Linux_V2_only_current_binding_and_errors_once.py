"""One current-state capture of both new finite observations and H1 compute snapshot."""
from inventory_current_owned210_storage_readonly_once import *
import getpass
CODE=r'''
from pathlib import Path
import sys,json,time,subprocess,psutil,os
B=Path(sys.argv[1]);rows={}
for n in ('OBSERVATION_PARENT_CHILD_ACTUAL.json','OBSERVATION_PARENT_EXIT_ACTUAL.json','native120_observation/STARTED.json','native120_observation/ACTUAL_LINUX_INSTALLED_BACKEND_AND_LOADED_PHYSX_READBACK.json','native120_observation/ACTUAL_LOADED_REWARD_TERMS_WEIGHTS_PARAMS_SOURCE.json','native120_observation/ACTUAL_REWARD_FRAME_LEGACY_READOUT_COMPLETE.json','native120_observation/COMPLETE_ACTUAL.json','native120_observation/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','native120_observation/FAILED_PREFIX_SAVER_ORIGINAL_ERROR.json','native120_observation/APP_CLOSE_ORIGINAL_ERROR.json','native120_observation/EXIT_NATURAL.json'):
 p=B/n
 if p.is_file():rows[n]=json.loads(p.read_bytes())
own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
logs={n:(B/n).read_text(errors='replace')[-9000:] for n in ('observation_parent.log','observation_worker.log') if (B/n).is_file()}
print(json.dumps(dict(epoch=time.time(),root=str(B),rows=rows,own_processes=own,log_tail=logs,compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),read_only=True)))
'''
if __name__=='__main__':
 c=None;pw=None
 try:
  save('TWO_EXPERT_LINUX_V2_CURRENT_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_all_transports=True));pw=getpass.getpass('72 GPU1 new finite observation status (hidden): ');c=a.t.connect();e2=a.code(c,a.t.PY,CODE,'/mnt/mod4_linux_durable_20261013/E2rf_1810d2',timeout=90);c.close();c=a.connect72(pw);pw=None;e3=a.code(c,a.PY,CODE,'/home/lc01/Zonglin Li/zonglin2/tasks/E3rf_1810d2',timeout=90);c.close();c=None;save('TWO_EXPERT_V2_LINUX_CURRENT_ACTUAL.json',dict(epoch=time.time(),E2=e2,E3=e3,actual_transport_returned=True,no_H1_or_budget_mutation=True));print(json.dumps({k:dict(own_processes=x['own_processes'],parent_exit=x['rows'].get('OBSERVATION_PARENT_EXIT_ACTUAL.json'),error=x['rows'].get('native120_observation/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json'),compute=x['compute'],native_binding=[r for r in x['rows'].get('native120_observation/ACTUAL_LINUX_INSTALLED_BACKEND_AND_LOADED_PHYSX_READBACK.json',{}).get('actual_loaded_PhysX',[]) if '/bindings/_physx.cpython' in r['path']]) for k,x in [('E2',e2),('E3',e3)]}),flush=True)
 except BaseException:save('TWO_EXPERT_V2_CURRENT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_mutation=True));raise
 finally:
  pw=None
  if c:c.close()
