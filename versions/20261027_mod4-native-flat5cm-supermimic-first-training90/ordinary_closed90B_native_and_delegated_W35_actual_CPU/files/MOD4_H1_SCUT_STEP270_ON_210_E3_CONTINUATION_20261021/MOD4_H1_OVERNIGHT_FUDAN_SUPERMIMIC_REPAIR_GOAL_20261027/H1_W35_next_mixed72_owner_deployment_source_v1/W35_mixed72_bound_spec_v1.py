"""Produce only W35 node spec and Task, AFTER actual CPU and fresh resource."""
from pathlib import Path
from W35_mixed72_protocol_v1 import *

def bound_W35_spec(request,token):
 assert isinstance(token,str) and len(token)>=32
 assert Path(request['node_root'])==Path(JOB).parent/'node_w35'
 spec=dict(key=KEY,W35_PPO50_gas400=True,source_SHA=SOURCE,worker_SHA=WORKER,source_qualification_kind=KIND,
  source_CPU_SHA=request['source_CPU_SHA'],CPU_waited_proof_SHA=request['CPU_waited_proof_SHA'],manifest_SHA=request['manifest_SHA'],payload_manifest_SHA=PAYLOAD_MANIFEST,
  CPU_path=CPU_PATH,CPU_proof_path=WAITED_PATH,GPU_UUID=GPU,execution_backend='target72',private_lock=PRIVATE_LOCK,job_root=JOB,python=PYTHON,production_script=WORKER_NAME,
  max_parent_seconds=3900,exit_headroom_seconds=300,owner_authority_generation=GENERATION,num_envs=20000,policy_hz=50,original_Adam_step=646800,original_LR=.00001,run_id=request['run_id'])
 validate_spec(spec)
 return dict(spec,role='node',token=token)

def bound_Task(spec,actual_resource):
 validate_spec(spec)
 assert actual_resource['GPU_UUID']==GPU and actual_resource['GPU_name']=='NVIDIA GeForce RTX 4090' and actual_resource['compute_UUID_only_rows']==0
 return dict(role='W35',source_SHA=SOURCE,original_source_SHA=ORIGINAL,worker_SHA=WORKER,original_run_manifest_SHA=ORIGINAL_MANIFEST,num_envs=20000,
  source_qualification_kind=KIND,canonical_authority_path='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json',
  authority_generation=GENERATION,source_CPU_SHA=spec['source_CPU_SHA'],GPU_UUID=GPU,actual_resource_admission=actual_resource,actual_USD_gas400_composition_passed=True,run_id=spec['run_id'])
