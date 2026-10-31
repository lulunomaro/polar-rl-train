"""Use original owner/charge/HMAC mechanisms for one actually-ready role."""
from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';C=N/'control'
S=T/'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031'

def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
def read(p):return json.loads(p.read_bytes())
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)

assert read(R/'ROOT209_MIXED_SOURCE_AND_TaskGO_CPU_ACTUAL.json')['passed']
a=read(R/'ACTUAL209_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json');assert a['passed_execution'] and a['all_own_children_waited'] and a['private_EX_released']
assert a['admission']['source_iteration']==32066 and a['admission']['source_Adam_step']==642840
assert a['CPU_returncode']==a['GPU_returncode']==0
result=a['result'];assert result['passed'] and result['num_envs']==80
assert result['measured_mapping']['flat_envs']==8 and result['measured_mapping']['jump_envs']==72
assert read(R/'ACTUAL209_ADMIT_ALL_SSH_CLOSED_SESSION_RESTORED.json')['global_serial_control_client_lease']=='FREE'
C.mkdir()
for name in ('forwarded_original_owner_control_v1.py','single_writer72_authority_V85M_source.py'):
 shutil.copyfile(S/'control'/name,C/name)
common=(S/'control/three_slot_common_v1.py').read_text('utf8').replace('from parallel197_protocol import valid_ready','from owner209_protocol import valid_ready')
write(C/'three_slot_common_v1.py',common)
shutil.copyfile(N/'owner209_protocol.py',C/'owner209_protocol.py')
owner=(S/'control/parallel197_finite_owner_authority72.py').read_text('utf8')
owner=owner.replace('from parallel197_protocol import validate_schedule,flat_go_fields','from owner209_protocol import validate_schedule,flat_go_fields')
owner=owner.replace("set(specs)=={'h1_210','e0_72'}","set(specs)=={'e0_72'}")
owner=owner.replace('human_requested_E0_one_hour_parallel_with194_remaining','human_requested_E0_latest_branch_mixed_one_hour')
owner=owner.replace('Linux_PARALLEL197_LITERAL_JUMP_194REMAIN_E0_','Linux_MIX209_E0_GROUND10_JUMP90_')
write(C/'mixed209_finite_owner_authority72.py',owner)
node=(S/'control/parallel197_fullstate_slot_node.py').read_text('utf8').replace('ADMISSION197_READY.json','ADMISSION209_READY.json')
write(C/'mixed209_fullstate_slot_node.py',node)
for p in C.glob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
def funcs(p):return {n.name:ast.dump(n) for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.FunctionDef)}
for fn in ('charge_values','authenticated_row','terminal'):
 assert funcs(C/'three_slot_common_v1.py')[fn]==funcs(S/'control/three_slot_common_v1.py')[fn],fn
assert H(C/'forwarded_original_owner_control_v1.py')==H(S/'control/forwarded_original_owner_control_v1.py')
assert H(C/'single_writer72_authority_V85M_source.py')==H(S/'control/single_writer72_authority_V85M_source.py')
task=read(N/'package/TASK209.json');manifest=H(N/'PACKAGE209_MANIFEST.json')
spec=dict(key='e0_72',execution_backend='target72',GPU_UUID=a['admission']['selected_GPU'],
 source_SHA=task['source_SHA'],source_iteration=32066,source_Adamstep=642840,
 source_bytes=17519967,max_parent_seconds=3900,exit_headroom_seconds=300,num_envs=20000,
 ground_envs=2000,jump_envs=18000,literal_original_fudan_JUMP=True,original_E0_ground_reward=True,no_physics_change=True,
 manifest_file='PACKAGE209_MANIFEST.json',manifest_SHA=manifest,
 job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_JUMP32066_GROUND10_400N50_20261031v209/e0_72',
 private_lock=a['admission']['resource']['private_lock'],python='/home/lc01/Zonglin Li/zonglin2/run-python.sh',
 worker_script='run209_mixed_E0_JUMP_worker.py')
schedule=dict(kind='ONE209_STATIC_GENUINE_MIXED_PPO',owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_ONE209_E0_GROUND10_JUMP90_2610v209/owner',
 scheduling_authority='human_requested_available_experts',experts={'e0_72':spec},deferred_experts=[],
 W35_208='source preparation separate; no fake role, no hotadd to healthy owner')
write(N/'SCHEDULE_PUBLIC.json',json.dumps(schedule,indent=2))
ready=dict(epoch=time.time(),passed=True,kind='MIX209_READY',source_SHA=task['source_SHA'],source_iteration=32066,Adam_step=642840,
 manifest_SHA=manifest,all_actor_critic_optimizer_tensors_finite=True,actual_35_38_6_shapes=True,actual_original_JUMP19_text_identity=True,
 source_fullstate_CPU_passed=True,actual_target0PT_waited_RC=0,actual_target0PT_controls=8,actual_target0PT_physics=64,actual_target0PT_feedback=16,
 target0PT_private_EX_released=True,ground_envs=2000,jump_envs=18000,actual_target0PT_ground_envs=8,actual_target0PT_jump_envs=72,
 source_fullstate_CPU_report=task['source_fullstate_CPU_report'],source_fullstate_CPU_report_SHA=task['source_fullstate_CPU_report_SHA'],
 target_actual_report=str(R/'ACTUAL209_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json'),target_actual_report_SHA=H(R/'ACTUAL209_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json'))
write(N/'ADMISSION209_READY.json',json.dumps(ready,indent=2))
rows=[dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(C.glob('*.py'))]
write(N/'CONTROL209_MANIFEST.json',json.dumps(dict(files=rows),indent=2))
put('FROZEN209_SINGLE_WRITER_SOURCE_AND_ACTUAL_TARGET_READY.json',dict(epoch=time.time(),passed=True,
 original_twofcntl_HMAC_and_raw_charge_values_AST_unchanged=True,one_actual_role=True,max_parent=3900,save_seconds=3600,
 no_new_budget_grant_or_old_model_decode=True,schedule_SHA=H(N/'SCHEDULE_PUBLIC.json'),control_manifest_SHA=H(N/'CONTROL209_MANIFEST.json')))
print(json.dumps(dict(passed=True,one_real_role=True,selected_GPU=spec['GPU_UUID'])))
