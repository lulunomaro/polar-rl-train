"""One exact E0 cfg producer. The HMAC token exists only in returned memory/stdin."""
from pathlib import Path
from E0_single72_protocol_v1 import KEY,GPU,JOB,SOURCE,WORKER,CPU,GENERATION,PRIVATE_LOCK,PYTHON,validate_spec
LOADER='/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2'
LIBRARY='/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib'
REALPY='/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python'
OWNER_NAME='E0_single72_finite_owner_authority72_v1.py'
NODE_NAME='E0_single72_finite_node_v1.py'
def bound_cfgs(request,token):
 owner=Path(request['owner_root']);node=Path(request['node_root']);parent=Path(JOB).parent
 assert owner==parent/'owner' and node==parent/'node_e0' and isinstance(token,str) and len(token)>=32
 spec=dict(key=KEY,E0_PPO50_gas400=True,source_SHA=SOURCE,worker_SHA=WORKER,source_CPU_SHA=request['source_CPU_SHA'],
  GPU_UUID=GPU,execution_backend='target72',private_lock=PRIVATE_LOCK,job_root=JOB,python=PYTHON,
  production_script='E0_PPO50_gas400_finite_worker_v5_writer_before_presave.py',max_parent_seconds=3900,exit_headroom_seconds=300,
  owner_authority_generation=GENERATION,num_envs=20000,policy_hz=50,
  manifest_SHA=request['manifest_SHA'],CPU_returned_proof_SHA=request['CPU_returned_proof_SHA'],run_id=request['run_id'])
 validate_spec(spec)
 ownercfg=dict(role='owner',token=token,run_id=request['run_id'],experts={KEY:dict(spec)},deferred_experts=[],
  scheduling_authority='human_requested_available_experts',authority_generation=GENERATION)
 nodespec=dict(spec,role='node',token=token)
 return ownercfg,nodespec
def logical_argv(root,name):return [PYTHON,'-u','-B',str(Path(root)/name)]
def expected_exec(logical):return dict(exe=LOADER,argv=[LOADER,'--library-path',LIBRARY,REALPY,'-B',*logical[1:]],root='/home/lc01/Zonglin Li/zonglin2')
