"""New explicitly reviewed evaluator namespace; never replays retired queue items."""
from pathlib import Path
import sys,json,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
assert not (R/'SENSOR_COMPLETE_WORKER_DEPLOYED.json').exists()
old=(W/'MOD4_S1A_MATCHED_EVALUATION_20261007/eval_worker_clock1000.py').read_bytes()
assert hashlib.sha256(old).hexdigest()=='8a6e23977a942d3599d33ce6ed0dca430321a0516e466965be274274ee2a63db'
source=old.decode();assert source.count("j.startswith('clk1000-')")==1
source=source.replace("j.startswith('clk1000-')","j.startswith('clk1000-s2complete-')")
compile(source,'sensor_worker','exec');(D/'eval_worker_sensor.py').write_text(source)
proof=dict(original_worker_sha256=hashlib.sha256(old).hexdigest(),new_worker_sha256=hashlib.sha256((D/'eval_worker_sensor.py').read_bytes()).hexdigest(),only_change='Explicit complete-sensor job namespace filter',shared_single_GPU_lock=True,no_GPU_or_canonical_training_authority=True)
(R/'SENSOR_WORKER_SOURCE_REVIEW.json').write_text(json.dumps(proof,indent=2))
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval();root='D:/MOD4_async_eval/sensor_clock1000_v15'
try:
 with c.open_sftp() as s:
  try:s.stat(root);raise AssertionError('New scope worker root already exists; inspect')
  except FileNotFoundError:pass
  s.mkdir(root)
  for n in ('eval_worker_sensor.py','handover_sensor_dependency_worker_once.py'):s.put(str(D/n),root+'/'+n)
  s.put(str(R/'SENSOR_WORKER_SOURCE_REVIEW.json'),root+'/WORKER_SOURCE_REVIEW.json')
 _,o,e=c.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" "'+root+'/handover_sensor_dependency_worker_once.py"',timeout=40)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);(R/'SENSOR_COMPLETE_WORKER_DEPLOYED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
finally:c.close()
