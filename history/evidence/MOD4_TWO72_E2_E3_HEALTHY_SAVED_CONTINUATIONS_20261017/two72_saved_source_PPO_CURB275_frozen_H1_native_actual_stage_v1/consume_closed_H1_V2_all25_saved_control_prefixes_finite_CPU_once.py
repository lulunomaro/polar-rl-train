"""CPU-only preparation for the already authorized flat-jump expert; no replay."""
from pathlib import Path
import sys,os,time,json,getpass,traceback,hashlib
N=Path(__file__).resolve().parent;R=N/'reports';P=N.parent/'MOD4_E1_CURB275_BRIDGE_FROM_CURB35_40_20261016'
sys.path.insert(0,str(P));from collect_hourly0044_existing_V9_FINAL_and_CURB275_production_readonly_once import code,connect72,PY
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_GROUNDED_PRELAUNCH_PROGRESS_V2_20261016';AUDIT=ROOT+'/all25_control_CPU_20261017_v1'
SOURCE=N.parent/'MOD4_H1_GROUNDED_PRELAUNCH_PROGRESS_V2_20261016/review_V2_closed_production_all_control_rows_CPU_v1.py'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def main():
 put('H1_CLOSED25_ALL_CONTROL_CPU_FINITE_TRANSPORT_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,no_new_GPU_native_lease_PPO_or_budget=True,existing_saved_raw_only=True));pw=getpass.getpass('Host72 closed H1 saved-prefix CPU audit only (hidden): ');c=None
 try:
  c=connect72(pw);pw=None
  admitted=code(c,PY,r'''
from pathlib import Path
import sys,os,json,psutil,time
R=Path(sys.argv[1]);A=Path(sys.argv[2]);O=Path('/home/lc01/Zonglin Li/zonglin2').resolve();assert R.resolve().is_relative_to(O) and A.parent==R and not A.exists();assert json.loads((R/'NODE_EXIT_ACTUAL.json').read_bytes())['all_own_children_actual_waited'];assert json.loads((R/'NODE_TERMINAL_ALL_OWN_CHILDREN_EXIT_ACTUAL.json').read_bytes())['row']['production_complete']
alive=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if p.pid!=os.getpid() and any(s.startswith(str(R)+'/') for s in p.info['cmdline'] or []):alive.append(p.info)
 except psutil.Error:pass
assert not alive,alive;A.mkdir();print(json.dumps(dict(epoch=time.time(),all_old_H1_children_actual_out=True,new_owned_CPU_folder=str(A),new_GPU_or_optimizer=False)))
''',ROOT,AUDIT);put('H1_CLOSED25_ACTUAL_OUT_NEW_CPU_FOLDER_ADMITTED.json',admitted)
  sf=c.open_sftp()
  try:sf.put(str(SOURCE),AUDIT+'/review.py')
  finally:sf.close()
  v=code(c,PY,r'''
from pathlib import Path
import sys,os,time,json,hashlib,subprocess
A=Path(sys.argv[1]);env=dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1');log=(A/'CPU_CONSOLE.log').open('xb');p=subprocess.Popen([sys.argv[2],'-u','-B',str(A/'review.py')],cwd=A,env=env,stdout=log,stderr=subprocess.STDOUT);import psutil;q=psutil.Process(p.pid);identity=dict(pid=q.pid,creation=q.create_time(),argv=q.cmdline(),root=q.cwd());(A/'CPU_IDENTITY_ACTUAL.json').write_text(json.dumps(identity,indent=2));rc=p.wait(timeout=1200);log.close();v=dict(epoch=time.time(),actual_waited_CPU_returncode=rc,identity=identity,new_GPU_or_budget=False,files=[])
for name in ('ALL_V2_PRODUCTION_CONTROL_ROWS_CPU_ACTUAL.json','CURRENT_ACTUAL.json','ORIGINAL_ERROR_ACTUAL.json','CPU_IDENTITY_ACTUAL.json'):
 f=A/name
 if f.is_file():
  raw=f.read_bytes();v['files'].append(dict(path=str(f),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
(A/'CPU_WAITED_EXIT_ACTUAL.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
''',AUDIT,PY,timeout=1260);put('H1_CLOSED25_ALL_CONTROL_CPU_ACTUAL_COMPLETE_OR_ERROR.json',v)
  report=next((r['value'] for r in v['files'] if r['path'].endswith('/ALL_V2_PRODUCTION_CONTROL_ROWS_CPU_ACTUAL.json')),None)
  print(json.dumps(dict(returncode=v['actual_waited_CPU_returncode'],report=None if report is None else {k:report[k] for k in ('passed_integrity_CPU','formal_updates','all_policy_rows','candidate_takeoff_landing_recovery_events','candidate_event_env_counts','elapsed_CPU_seconds')})),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_ALL25_SAVED_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_automatic_CPU_retry=True));raise
