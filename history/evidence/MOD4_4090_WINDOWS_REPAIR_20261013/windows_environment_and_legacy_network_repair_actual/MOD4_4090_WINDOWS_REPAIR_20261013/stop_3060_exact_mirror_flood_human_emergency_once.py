from pathlib import Path
import sys,os,json,time,base64,traceback
D=Path(__file__).resolve().parent;W=D.parent
CODE=r'''
from pathlib import Path
import psutil,json,time,hashlib,os
D=Path('D:/MOD4_async_eval/windows4090_transition_20261013');receipt=D/'OLD_MIRROR_SSH_FLOOD_HUMAN_EMERGENCY_STOP_ACTUAL.json'
assert not receipt.exists(),'Exact mirror emergency action consumed; inspect receipt only'
script=Path('D:/claude2/fangzhen/runs3060/flat_scratch_v1/monitor/mirror_target_tui.py')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sha='4289e326dfaf1ec45cada4244f75aa546e8cd578d2829f7cdbb9c3b66a46c274'
assert H(script)==sha,'Monitor source changed'
targets=[(24856,1791299198.2378356),(5192,1791299198.2293997)]; before=[]
for pid,created in targets:
 p=psutil.Process(pid);assert abs(p.create_time()-created)<.001,'PID identity changed'
 assert any(str(script).replace('\\','/').lower()==v.replace('\\','/').lower() for v in p.cmdline()),'Not exact source monitor'
 children=p.children(recursive=True);assert all(c.pid==24856 and abs(c.create_time()-targets[0][1])<.001 for c in children),'Other/GPU child exists'
 conns=[c for c in p.connections(kind='tcp') if c.raddr and c.raddr.ip=='10.24.4.210']
 before.append(dict(pid=pid,creation=p.create_time(),argv=p.cmdline(),children=[c.pid for c in children],connection_count_210=len(conns)))
intent=dict(epoch=time.time(),human_instruction='把这个修复一下，3060在撞主机',actual_connection_owner=before,source_sha256=sha,targets_exact=targets,no_GPU_or_training_children=True,no_scheduled_task_matched_previous_readonly=True)
intentpath=D/'OLD_MIRROR_SSH_FLOOD_STOP_INTENT_ACTUAL.json'
with intentpath.open('x',encoding='utf8') as f:json.dump(intent,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
actions=[]
psutil.Process(targets[0][0]).terminate();actions.append(dict(pid=targets[0][0],creation=targets[0][1],action='terminate exact no-GPU network monitor under human emergency repair authorization'))
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
if alive==[5192]:
 p=psutil.Process(5192);assert abs(p.create_time()-targets[1][1])<.001 and not p.children(recursive=True)
 p.terminate();actions.append(dict(pid=5192,creation=targets[1][1],action='terminate exact orphaned mirror Python shim without children'))
 time.sleep(1)
alive=[]
for pid,created in targets:
 try:
  p=psutil.Process(pid)
  if abs(p.create_time()-created)<.001:alive.append(pid)
 except psutil.NoSuchProcess:pass
assert not alive,'Exact monitor still present; no blind escalation or parent terminal termination'
allconns=[c for c in psutil.net_connections(kind='tcp') if c.raddr and c.raddr.ip=='10.24.4.210']
assert H(script)==sha
out=dict(epoch=time.time(),passed=True,before=before,actions=actions,original_exact_PIDs_absent=True,remaining_210_connections_by_status={v:sum(c.status==v for c in allconns) for v in sorted({c.status for c in allconns})},remaining_connection_owner_PIDs=sorted({c.pid for c in allconns if c.pid}),source_before_after_sha256=sha,source_unchanged=True,no_training_or_GPU_process_stopped=True,no_terminal_GUI_key_or_close=True,no_sshd_restart_or_setting_changed=True,no_budget_or_model_or_raw_changed=True,authorization_consumed_only_exact_monitor_pair=True)
with receipt.open('x',encoding='utf8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
print(json.dumps(out,ensure_ascii=False))
'''
def main():
 local=D/'reports/OLD_MIRROR_SSH_FLOOD_HUMAN_EMERGENCY_STOP_ACTUAL.json';assert not local.exists(),'Read saved action receipt; do not rerun'
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
 from reuse_authorized_session_transport import recover
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
 sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'))
 from eval_remote_io import connect_eval
 c=connect_eval()
 try:
  enc=base64.b64encode(CODE.encode()).decode();cmd='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
  _,o,e=c.exec_command(cmd,timeout=45);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:raise RuntimeError('Exact emergency stop returned '+str(rc)+': '+err.decode('utf8','replace')+' UNKNOWN OUTCOME: read receipt before any further action')
  a=json.loads(raw);local.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(a,ensure_ascii=False))
 except Exception:
  (D/'reports'/('OLD_MIRROR_EMERGENCY_STOP_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_read_remote_intent_and_receipt_before_any_retry=True)),encoding='utf8');raise
 finally:c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
if __name__=='__main__':main()
