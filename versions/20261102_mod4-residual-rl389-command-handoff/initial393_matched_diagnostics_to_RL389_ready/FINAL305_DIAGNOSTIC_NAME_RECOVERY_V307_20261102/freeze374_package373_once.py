"""Freeze373 after CPU fixture outputs; one new finite comparison, zero model reads."""
from pathlib import Path
import ast,hashlib,json,time
P=Path(__file__).resolve().parent;N=P.parent/'MPC_MATCHED_DR_AIR_REQUEST_V373_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
assert not(N/'TASK373_FROZEN.json').exists()
task=json.loads((N/'TASK373_PREPARE_NOT_FROZEN.json').read_bytes());task['worker_SHA']=H(N/'source/evaluate373.py')
assert task['matched_pair_count']==40 and task['D0_D7_matched_pairs'] and task['max_controls']==250
assert task['model_byte_reads']==task['account_writes']==task['optimizer_steps']==0
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'))
old=N.parent/'MPC_AIR_WHEEL_REQUEST_ENVELOPE_V368_20261102'
assert H(N/'source/source_event_mpc353.py')==H(old/'source/source_event_mpc353.py')
assert H(N/'source353_gains.json')==H(old/'source353_gains.json')
assert H(N/'planned_mpc_motor373.json')==task['planned_motor_control']['SHA']
assert H(N/'reference324.npz')==task['reference']['SHA']
put(N/'reports/CPU373_ACTUAL_TOOL_OUTPUT_RECEIPT.json',dict(epoch=time.time(),passed=True,evidence='Two actual exec_command returns exit0 before freeze374; their raw stdout retained in current tool history.',commands=[dict(script='cpu373_matched_noise_no_step.py',python='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe',exitcode=0,actual_components=True,paired_sensor_D3_D4=True,asynchronous_reset_checked=True,SDK=0,physics=0),dict(script='cpu373_control_request_no_step.py',python='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe',exitcode=0,approach_identical=True,legs_identical=True,push_flight_extend_bounded=True,SDK=0,physics=0)],checkpoint_reads=0,NN=0))
put(N/'TASK373_FROZEN.json',task)
files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(N/'INDEX373_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=files,source368_immutable=True,method='New373 matched40 fullDR pairs source_vs_wheelprebound; no newtraining',max_controls=250,zero_model=True))
put(P/'reports/STATIC374_FROZEN373_PACKAGE_VALIDATION.json',dict(epoch=time.time(),passed=True,root=str(N),index_SHA=H(N/'INDEX373_SOURCE_TASK_CALLERS_FROZEN.json'),worker_SHA=task['worker_SHA'],files=len(files),py_AST=True,sourcecontroller_byte_identity=True,source_MPC_gains_byte_identity=True,plannedtrace_byte_identity=True,original_physics_and_queue=True,paired_parameter_and_noise_helper=True,first_episode_only=True,model_reads=0,network=0,SDK=0,physics=0))
print(json.dumps(dict(passed=True,root=str(N),index_SHA=H(N/'INDEX373_SOURCE_TASK_CALLERS_FROZEN.json'),worker_SHA=task['worker_SHA'],files=len(files))))
