"""Freeze this unused teacher/student source and the original finite controls."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
CPU=R/'CPU284_ACTUAL_CARRIER_MIGRATION_AND_H32_NO_STEP.json'
assert json.loads(CPU.read_bytes())['passed']
old=T/'OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276V3_20261101'
whole=old/'reports/ROOT281_NEW_WM_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json'
closed=json.loads((old/'reports/ROOT276_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
assert closed['passed_collection'] and closed['owner_closed']['canonical_None'] and closed['owner_closed']['shared_locks_free']
carrier=json.loads(whole.read_bytes());assert carrier['SHA']=='cbd25c80a55c87296b4b2a50eb21869e4b12127f9aa3a5d5f9a607823d44242b'
base=json.loads((old/'TASK276_FROZEN.json').read_bytes())
task=dict(base)
from teacher_task283 import KIND,validate_task
stamp=str(time.time_ns());run='LQR_MPC_DEPTH_STUDENT283_'+stamp
root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_'+run
remote_carrier=closed['roles']['jump_72']['formal']['path']
assert remote_carrier.endswith('/production/model_final_complete.pt')
task.update(kind=KIND,run_id=run,job_root=root+'/student72',owner_root=root+'/owner72',
 GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',
 model_path=remote_carrier,model_SHA=carrier['SHA'],model_bytes=carrier['bytes'],source_SHA=carrier['SHA'],
 teacher_SHA='0f5de75a488b79bfe9513b2cd01664d8bf98450800b785b8e787301276552a07',
 source_WM_updates=4719,actor_obs=44,critic_obs=47,num_envs=80,ground_envs=8,jump_envs=72,
 reference=dict(path='reference283.npz',bytes=128231,SHA='d5bb68fdbe098c3fd3fa2bcba9e0f5121fae44dc43c9e9c30a2080b73a811650'),
 carrier_CPU_receipt_SHA=H(whole),teacher_whole_CPU_receipt_SHA=H(whole),source_CPU_report_SHA=H(CPU),
 worker_SHA=H(N/'source/worker283.py'),closure_m=.01,mimic_rad=.01,policy_hz=50,feedback_hz=100,
 physics_dt=.0025,TGS=[32,4],gas_nominal_N=400,reference_only=True,literal_reward_unchanged=True,
 generation='FROZEN_BEFORE_GO_TEACHER283',learning_scope='teacher_assisted_depth_SuperMimic',
 actual_learning_GO_pending=True,teacher_supervision_coefficient='max(.05,1-Pi_updates/4000)',
 student_optimizer_LR=1e-4,student_batch=256,student_H=32,restore_source_CUDA_RNG_for_WM_sampling=True,
 reference_rollout_engine='MuJoCo reference labels only; own PhysX replay',
 human_authorization='Referenced chat user: 开始教师训练教导深度supermimic rl训练; current chat: 读取对话，继续任务 / 继续',
 budget='original canonical one writer3900/save3600/exit300; no extra grant or automatic extension')
validate_task(task);put(N/'TASK283_FROZEN.json',task)
for p in N.rglob('*.py'):
    if '__pycache__'not in p.parts:ast.parse(p.read_text('utf8'),filename=str(p))
files=[p for p in N.rglob('*') if p.is_file() and '__pycache__'not in p.parts and p.suffix in ('.py','.json','.md','.txt')]
put(N/'INDEX283_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),kind='FROZEN_TEACHER283_BEFORE_GO',
 files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in sorted(files)],
 reference_binary_metadata_only=task['reference'],predecessor282_unchanged=True))
print(json.dumps(dict(passed=True,run_id=run,task=str(N/'TASK283_FROZEN.json'),
 index_SHA=H(N/'INDEX283_SOURCE_TASK_CALLERS_FROZEN.json'),remote_model=remote_carrier)))
