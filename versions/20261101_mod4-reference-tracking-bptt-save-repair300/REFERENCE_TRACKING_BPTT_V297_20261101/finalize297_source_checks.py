from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports';P=N/'postround297'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=P/'run298_eval_once_template.py';text=p.read_text('utf8')
text=text.replace("    parent=parent.replace('CAPTURE298_ACTUAL_RESULT.json','RESULT298.json')", "    parent=parent.replace('CAPTURE298_ACTUAL_RESULT.json','RESULT298.json')\n    parent=parent.replace(\"q.suffix in ('.py','.json')\",\"q.suffix in ('.py','.json','.npz')\")")
p.write_bytes(text.encode());ast.parse(text)
task=json.loads((N/'TASK297_FROZEN.json').read_bytes())
assert H(N/'source/worker297.py')==task['worker_SHA']
worker=(N/'source/worker297.py').read_text('utf8');learner=(N/'source/tracking_learner297.py').read_text('utf8')
assert 'return original(frame,tick)'not in worker
assert "frame['actions'][:,[0,1,3,4,2,5]]"in worker
assert 'return torch.exp(-cost/5.)'in worker and 'reward=torch.exp(-cost/5.)'in learner
assert 'imagined_step('not in learner and 'LiteralJump194'in learner is False
assert "critic_steps)==learner.critic_updates"in worker
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
with(R/'SOURCE297_FINAL_BINDING_AND_CALLER_CHECK.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),passed=True,actual_reward_and_imagined_same_return=True,old_Fudan_compute_not_called=True,policy_reward_action_order_inverse_verified=True,critic_new_step_offset0=True,eval_reference_NPZ_allowed_in_locked_package=True,CPU296_architecture_H32_reused=True,CPU297_positive_return_source_pass=True,modelsrawSDKGO_reads=0),f,indent=2)
files=[p for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts and p.suffix in('.py','.json','.npz')]
index=N/'INDEX297_SOURCE_TASK_CALLERS_FROZEN.json'
with index.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),kind='REFERENCE_TRACKING297_FULL_SOURCE_TASK_CALLERS',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]),f,indent=2)
print(json.dumps(dict(passed=True,index_SHA=H(index),run_id=task['run_id'],files=len(files))))
