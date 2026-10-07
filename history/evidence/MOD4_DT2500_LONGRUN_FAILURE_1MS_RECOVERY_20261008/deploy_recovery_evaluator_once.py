from pathlib import Path
import sys,json,hashlib,ast
D=Path(__file__).resolve().parent;R=D/'reports';root='D:/MOD4_async_eval/sensor_recovery_clock1000_v15'
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
for n in ('eval_worker_recovery1000.py','handover_idle_recovery_evaluator_once.py'):ast.parse((D/n).read_text())
old=(D.parent/'MOD4_E0_SENSOR_DR_STAGE1_20261007/eval_worker_sensor.py').read_text();new=(D/'eval_worker_recovery1000.py').read_text();assert new==old.replace("j.startswith('clk1000-s2complete-')","j.startswith('clk1000-recovery-')")
c=connect_eval()
try:
 with c.open_sftp() as sf:
  try:sf.stat(root);raise AssertionError('Recovery worker root exists: do not repeat')
  except FileNotFoundError:pass
  sf.mkdir(root)
  for n in ('eval_worker_recovery1000.py','handover_idle_recovery_evaluator_once.py'):sf.put(str(D/n),root+'/'+n)
 _,o,e=c.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" "'+root+'/handover_idle_recovery_evaluator_once.py"',timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);(R/'RECOVERY_EVALUATOR_DEPLOYED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(raw.decode())
finally:c.close()
