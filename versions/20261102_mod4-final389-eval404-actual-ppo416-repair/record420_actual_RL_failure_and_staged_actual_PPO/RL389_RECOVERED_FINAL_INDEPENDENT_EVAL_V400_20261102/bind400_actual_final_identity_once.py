"""Bind first actual fullfinalCPU389 metadata to independent eval400, no PT read."""
from pathlib import Path
import ast,hashlib,json,time
E=Path(__file__).resolve().parent;N=E.parent/'MPC_COMMAND_RESIDUAL_RL_V389_20261102';R=N/'reports'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
full=json.loads((R/'ROOT389_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes())
complete=json.loads((R/'ROOT389_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
assert full['passed']and complete['recovery399']and complete['owner_closed']['canonical_None']
assert not(E/'TASK400_FROZEN.json').exists()and not(E/'reports/ROOT400_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
task=json.loads((E/'TASK400_PENDING_FINAL_IDENTITY.json').read_bytes())
task.update(model_path=complete['roles']['jump_72']['formal']['path'],model_SHA=full['SHA'],model_bytes=full['bytes'],expected_Pi_updates=full['Pi'],source_run=complete['run_id'],source_full_CPU_receipt_SHA=H(R/'ROOT389_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'))
with(E/'TASK400_FROZEN.json').open('x',encoding='utf8')as stream:json.dump(task,stream,indent=2)
for path in E.rglob('*.py'):ast.parse(path.read_text('utf8'))
files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in sorted(E.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]
index=E/'INDEX400_SOURCE_TASK_CALLERS_FROZEN.json'
with index.open('x',encoding='utf8')as stream:json.dump(dict(epoch=time.time(),files=files),stream,indent=2)
print(json.dumps(dict(passed=True,indexSHA=H(index),modelSHA=full['SHA'],RL=True,onlineMPC=False)))
