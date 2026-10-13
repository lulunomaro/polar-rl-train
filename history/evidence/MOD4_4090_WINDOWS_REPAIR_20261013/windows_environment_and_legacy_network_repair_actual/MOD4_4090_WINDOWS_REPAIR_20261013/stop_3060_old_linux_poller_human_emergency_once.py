from pathlib import Path
import sys,os,json,time,base64,traceback
D=Path(__file__).resolve().parent;W=D.parent
code=r'''
from pathlib import Path
import os,json,time,hashlib,psutil,subprocess,msvcrt
D=Path('D:/MOD4_async_eval/windows4090_transition_20261013');D.mkdir(exist_ok=True)
receipt=D/'OLD_LINUX_POLLER_HUMAN_EMERGENCY_STOP_ACTUAL.json';assert not receipt.exists(),'Emergency action already consumed; read receipt only'
worker=Path('D:/MOD4_async_eval/closure_episode_clock2500_v15/eval_worker_e1_wave50_query_review.py')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before_sha=H(worker);owned=[]
targets=[(2924,1791772440.1488748),(8664,1791772440.1525493)]
for pid,created in targets:
 p=psutil.Process(pid);assert abs(p.create_time()-created)<.001,'Old PID identity changed'
 assert any(str(worker).replace('\\','/').lower()==v.replace('\\','/').lower() for v in p.cmdline()),'Not the exact owned poller'
 children=p.children(recursive=True);assert all(c.pid==8664 for c in children),'GPU or other child exists; no stop authorized'
 owned.append(dict(pid=pid,creation=p.create_time(),argv=p.cmdline(),children=[dict(pid=c.pid,creation=c.create_time(),argv=c.cmdline()) for c in children]))
taskname='MOD4_AsyncFrozenEvaluation_v15_e1_wave50_query_review'
query=subprocess.run(['schtasks','/Query','/TN',taskname,'/XML'],capture_output=True);assert query.returncode==0,'Exact scheduler task missing'
(D/'ORIGINAL_OLD_POLLER_TASK.xml').write_bytes(query.stdout)
assert worker.name.encode('utf8') in query.stdout or worker.name.encode('utf16le') in query.stdout
started=time.time();disable=subprocess.run(['schtasks','/Change','/TN',taskname,'/DISABLE'],capture_output=True);assert disable.returncode==0,disable.stderr.decode(errors='replace')
end=subprocess.run(['schtasks','/End','/TN',taskname],capture_output=True);assert end.returncode==0,end.stderr.decode(errors='replace')
time.sleep(2);extra=[]
for pid,created in targets[::-1]:
 try:
  p=psutil.Process(pid)
  if abs(p.create_time()-created)<.001:
   assert not p.children(recursive=True) or all(c.pid==8664 for c in p.children(recursive=True))
   p.terminate();extra.append(dict(pid=pid,creation=created,action='terminate exact owned idle network poller after taskEnd'))
 except psutil.NoSuchProcess:pass
deadline=time.time()+12
while time.time()<deadline:
 alive=[]
 for pid,created in targets:
  try:
   p=psutil.Process(pid)
   if abs(p.create_time()-created)<.001:alive.append(pid)
  except psutil.NoSuchProcess:pass
 if not alive:break
 time.sleep(.5)
assert not alive,'Original poller still active; no further signal escalation'
assert H(worker)==before_sha,'Original worker source changed'
lock=Path('D:/MOD4_async_eval/worker.lock')
with lock.open('r+b') as f:
 f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
after=subprocess.run(['schtasks','/Query','/TN',taskname,'/XML'],capture_output=True);assert after.returncode==0
(D/'DISABLED_OLD_POLLER_TASK.xml').write_bytes(after.stdout)
result=dict(epoch=time.time(),passed=True,human_explicit_emergency_instruction='把这个修复一下，3060在撞主机',affected_only_exact_owned_idle_network_poller=True,before=owned,original_worker_sha256=before_sha,worker_source_after_sha256=H(worker),task_name=taskname,task_disabled=True,task_end_returncode=end.returncode,additional_exact_owned_termination_actions=extra,actual_original_parent_child_absent=True,shared_GPU_lock_actual_free=True,no_GPU_evaluation_or_PPO_child_before_stop=True,no_model_raw_result_source_deleted_or_changed=True,no_4090_service_restart_or_OS_change=True,no_budget_transaction=True,stop_started_epoch=started,old_Linux_account_auto_retry_no_longer_running=True,original_task_XML_path=str(D/'ORIGINAL_OLD_POLLER_TASK.xml'),disabled_task_XML_path=str(D/'DISABLED_OLD_POLLER_TASK.xml'))
receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False))
'''
def main():
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
 from reuse_authorized_session_transport import recover
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
 sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'))
 from eval_remote_io import connect_eval
 c=connect_eval()
 try:
  enc=base64.b64encode(code.encode()).decode();cmd='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
  _,o,e=c.exec_command(cmd,timeout=45);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:
   p=D/'reports'/('OLD_POLLER_EMERGENCY_STOP_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),returncode=rc,stdout=raw.decode('utf8','replace'),stderr=err.decode('utf8','replace'),unknown_partial_outcome_read_before_any_retry=True)),encoding='utf8');raise RuntimeError('Emergency stop failed; inspect retained partial outcome before repeating actions')
  a=json.loads(raw);p=D/'reports/OLD_LINUX_POLLER_HUMAN_EMERGENCY_STOP_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(a,ensure_ascii=False))
 finally:c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
if __name__=='__main__':main()
