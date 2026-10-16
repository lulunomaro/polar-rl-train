"""Single bounded own-source read; no new jobs, signals or global polling."""
from pathlib import Path
import json,hashlib,shlex,sys,os,time,traceback,subprocess
D=Path(__file__).resolve().parent;R=D/'reports';S='/mnt/mod4_linux_durable_20261013/'+D.name;CURB='/mnt/mod4_linux_durable_20261013/MOD4_E1_CURB35_FROM_878_NATIVE_TRAIN_20261016/production_fresh_process_v2'
sys.path.insert(0,str(D.parent/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
CODE=r'''
from pathlib import Path
import json,time,psutil
B=Path(ROOT);C=Path(CURB)
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
budget=read(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'))
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B) in z or str(C) in z for z in p.info['cmdline'] or []) and any(z.endswith('.py') for z in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),current=read(B/'OWNER_CURRENT.json'),final=read(B/'OWNER_FINAL.json'),original_error=read(B/'OWNER_ORIGINAL_ERROR.json'),own_exit=read(B/'OWNER_EXIT_ACTUAL.json'),CURB_final=read(C/'job0/production_only/FINAL.json'),CURB_owner_final=read(C/'OWNER_FINAL.json'),CURB_exit=read(C/'OWNER_EXIT_ACTUAL.json'),actual_own_processes=procs,canonical=dict(active=budget['active_segment'],charged=budget['charged_training_seconds'],remaining=budget['remaining_training_seconds'],own_completed=[x for x in budget['completed_segments'] if x.get('owner_parent_pid') in (480021,484739)]))))
'''
def main():
 put('E2_FIRST_REAL_PRODUCTION_BOUND_WAIT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),maximum_seconds=900,sole_sequential_transport_while_actual_alive=True,own_source_root=S,no_runtime_mutations=True));c=None;start=time.monotonic()
 try:
  c=t.connect()
  while True:
   si,so,se=c.exec_command(shlex.quote(t.PY)+' -B -',timeout=40);si.write('ROOT='+repr(S)+'\nCURB='+repr(CURB)+'\n'+CODE);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();v=json.loads(raw);cur=v.get('current') or {};row=(cur.get('rows') or {}).get('0') or {};latest=row.get('latest_save') or {};positive=row.get('phase')=='production' and latest.get('updates',0)>0
   if positive or v['original_error'] or v['final'] or time.monotonic()-start>=900:
    put('E2_FIRST_REAL_PRODUCTION_OR_ERROR_BOUND_ACTUAL.json',v);print(json.dumps(dict(first_production=latest if positive else None,owner_error=v['original_error'],owner_final=v['final'],last_phase=row.get('phase'),last_row=row,CURB_final=v['CURB_final'],canonical=v['canonical'])),flush=True);return
   time.sleep(15)
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_BOUND_WAIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_job_replay=True));raise
