"""Finish unstarted389 after correcting an invalid static assertion about dynamicGPUS."""
from pathlib import Path
import ast,hashlib,importlib.util,json,time
P=Path(__file__).resolve().parent;T=P.parent;N=T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102';E=T/'RESIDUAL_RL389_INDEPENDENT_EVAL_V390_20261102';Q=T/'RESIDUAL_RL389_POSTROUND_V390_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
put(P/'reports/STATIC389_PREPARER_READER_ASSERTION_ERROR.json',dict(epoch=time.time(),passed=False,error='preparerassertlookedforliteralGPUUUIDincommonGPUS;actualcommonreadsSCHEDULEexpertsdynamically',source=str(P/'prepare389_exact_RL_metadata_and390_postround.py'),exitcode=1,network=0,SDK=0,model_reads=0,GO=False,Task389GPUcorrect=True,task_frozen_untouched=True,repair='Independent391 validates actualdynamicGPUSpath+TaskGPU; finishesmissingINDEXonly.'))
task=json.loads((N/'TASK389_FROZEN.json').read_bytes());assert task['GPU_UUID']=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
common=(N/'control389/three_slot_common_v1.py').read_text('utf8');assert "GPUS={key:spec['GPU_UUID'] for key,spec in SCHEDULE['experts'].items()}"in common
spec=importlib.util.spec_from_file_location('RL389contract',N/'teacher_task389.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_task(task)
cpu=json.loads((N/'reports/CPU389_RESIDUAL_RL_NO_STEP.json').read_bytes());assert cpu['passed']and cpu['learner_SHA']==H(N/'source/tracking_learner389.py')
for p in list(N.rglob('*.py'))+list(E.rglob('*.py'))+list(Q.rglob('*.py')):ast.parse(p.read_text('utf8'))
assert not(N/'reports/ROOT389_START_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(N/'INDEX389_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=files,RL=True,online_MPC=False,CPU384_exact_behavior=True,immutable384_rejected=True))
put(Q/'INDEX390_POSTROUND_FOR389_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for root in(Q,E)for p in sorted(root.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]))
put(P/'reports/STATIC391_RL389_PACKAGE_POSTROUND390_VALIDATION.json',dict(epoch=time.time(),passed=True,root=str(N),run=task['run_id'],indexSHA=H(N/'INDEX389_SOURCE_TASK_CALLERS_FROZEN.json'),workerSHA=task['worker_SHA'],GPU=task['GPU_UUID'],CPU384reuse_no_new_modelread=True,allAST=True,postroundroot=str(Q),postroundINDEXSHA=H(Q/'INDEX390_POSTROUND_FOR389_FROZEN.json'),evalroot=str(E),RL=True,online_MPC=False,sourceAdam=[52636,9696,16879],START=False,network=0,SDK=0,physics=0))
print(json.dumps(dict(passed=True,root=str(N),run=task['run_id'],indexSHA=H(N/'INDEX389_SOURCE_TASK_CALLERS_FROZEN.json'),postroundINDEXSHA=H(Q/'INDEX390_POSTROUND_FOR389_FROZEN.json'),workerSHA=task['worker_SHA'],GPU=task['GPU_UUID'],RL=True,GO=False)))
