"""Actual sealed request -> one owner/node config; token memory/stdin only."""
from pathlib import Path
from flat90_protocol_v1 import KEY,GPU,JOB,SOURCE,BOOTSTRAP,REFERENCE,PROGRESS,KIND,PARAMETER,GENERATION,PRIVATE_LOCK,PYTHON,WORKER_NAME,CPU_PATH,WAITED_PATH,validate_spec
LOADER='/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2'
LIBRARY='/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib'
REALPY='/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python'
OWNER_NAME='flat90_finite_owner_authority72_v1.py';NODE_NAME='flat90_finite_node_v1.py'
def bound_cfgs(request,token):
 parent=Path(JOB).parent
 assert Path(request['owner_root'])==parent/'owner' and Path(request['node_root'])==parent/'node_h1'
 assert 'token' not in request and isinstance(token,str) and len(token)>=32
 s=dict(key=KEY,nativeflat90=True,native_continuation=True,source_SHA=SOURCE,source_progress=dict(PROGRESS),source_Adamstep=832460,
  bootstrap_source_SHA=BOOTSTRAP,native_seed=27,native_reference_SHA=REFERENCE,source_native_iteration=6469,
  GPU_UUID=GPU,execution_backend='target72',private_lock=PRIVATE_LOCK,job_root=JOB,python=PYTHON,production_script=WORKER_NAME,
  max_parent_seconds=3900,exit_headroom_seconds=300,owner_authority_generation=GENERATION,num_envs=4096,policy_hz=100,
  source_qualification_kind=KIND,changed_plant700_to_nominal400=False,flat05_objective_changed_from_native88C=True,
  gas400_parameter_source_contract_SHA=PARAMETER,CPU_path=request.get('CPU_path',CPU_PATH),CPU_proof_path=request.get('CPU_proof_path',WAITED_PATH),run_id=request['run_id'])
 for k in ('worker_SHA','source_CPU_SHA','CPU_waited_proof_SHA','manifest_SHA','payload_manifest_SHA','source_contract_SHA','payload_manifest_path','source_contract_path','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA'):s[k]=request[k]
 validate_spec(s)
 return dict(role='owner',token=token,run_id=s['run_id'],experts={KEY:dict(s)},deferred_experts=[],scheduling_authority='human_requested_available_experts',authority_generation=GENERATION),dict(s,role='node',token=token)
def logical_argv(root,name):return [PYTHON,'-u','-B',str(Path(root)/name)]
def expected_exec(logical):return dict(exe=LOADER,argv=[LOADER,'--library-path',LIBRARY,REALPY,'-B',*logical[1:]],root='/home/lc01/Zonglin Li/zonglin2')
RUNTIME_FILES=['flat90_protocol_v1.py','flat90_finite_owner_authority72_v1.py','flat90_finite_node_v1.py','three_slot_common_v1.py',
 'single_writer72_authority_V85M_source.py','flat90_resource_guard_v1.py','flat90_bound_cfg_v1.py','flat90_detached_launcher_v1.py']
def controller_manifest(request,source_dir):
 # Root runs only after exact actual CPU+wait SHA and worker/payload are sealed.
 from flat90_protocol_v1 import H
 base=Path(source_dir)
 return dict(key=KEY,source_SHA=SOURCE,worker_SHA=request['worker_SHA'],source_CPU_SHA=request['source_CPU_SHA'],
  files=[dict(relative=n,bytes=(base/n).stat().st_size,SHA=H(base/n)) for n in RUNTIME_FILES])
