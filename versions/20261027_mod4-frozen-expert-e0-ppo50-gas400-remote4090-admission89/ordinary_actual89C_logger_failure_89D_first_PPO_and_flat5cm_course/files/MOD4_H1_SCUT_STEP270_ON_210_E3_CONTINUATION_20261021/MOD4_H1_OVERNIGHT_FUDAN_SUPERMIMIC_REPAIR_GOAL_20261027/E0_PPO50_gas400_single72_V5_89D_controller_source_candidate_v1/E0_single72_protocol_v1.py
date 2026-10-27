"""One typed E0 slot, actual89C CPU proof; metadata only, no ledger/model I/O."""
from pathlib import Path
import hashlib,hmac,json,time,urllib.request
KEY='e0'
GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0'
BASE_JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89c/e0'
SOURCE='54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371'
WORKER='ec8eba0365f0129b2799ef4e1ae7f3673beb585f87d4e25d2c36cf7bdb33b08c'
BASE_V4_WORKER='87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19'
BASE_WORKER='1858c6395083bb7104385ec82d3dce6db4f79898a6346a250916ad7217524152'
CPU='5509f4a793be9d9e5e858bc75bfa326440267f1caeff040979935b2bed6f3c8e'
BASE_CPU='d06aa8550f915258b0b42a711d73b9859f5fbce68fbcea6289b8647cd0f4208c'
KIND='MOD4_E0_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
PRIVATE_LOCK='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+GPU+'.lock'
PYTHON='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,indent=2).encode()).hexdigest()
def require(v,message):
 if not v:raise ValueError(message)
def validate_spec(s):
 require(s.get('key')==KEY and s.get('E0_PPO50_gas400') is True,'one real E0 slot only')
 require(s.get('source_SHA')==SOURCE and s.get('worker_SHA')==WORKER and valid_source_extension_sha(s.get('source_CPU_SHA')),'actual89C source/worker/CPU binding')
 require(s.get('GPU_UUID')==GPU and s.get('execution_backend')=='target72' and s.get('private_lock')==PRIVATE_LOCK,'actual89C GPU and original private lock')
 require(s.get('job_root')==JOB and s.get('python')==PYTHON,'actual installed89C root and approved interpreter')
 require(s.get('max_parent_seconds')==3900 and s.get('exit_headroom_seconds')==300,'original finite bounds')
 require(s.get('owner_authority_generation')==GENERATION and s.get('num_envs')==20000 and s.get('policy_hz')==50,'original authority/new exact E0 scope')
 require(s.get('production_script')=='E0_PPO50_gas400_finite_worker_v5_writer_before_presave.py','installed fixed basename contains actual V3 bytes')
 require(isinstance(s.get('manifest_SHA'),str) and len(s['manifest_SHA'])==64,'installed controller manifest pin')
 return True
def validate_schedule(cfg):
 require(set(cfg['experts'])=={KEY} and cfg['deferred_experts']==[],'no second or invented registration')
 require(cfg['authority_generation']==GENERATION and cfg['scheduling_authority']=='human_requested_available_experts','sole original72 writer')
 validate_spec(cfg['experts'][KEY]);return True
def validate_base_cpu_value(v):
 require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE and v.get('worker_SHA')==BASE_WORKER,'actual89C CPU result')
 require(v.get('admission_reader_version')=='V2_CUDA_structural_only' and v.get('actor35_critic38_original_STD_17Adam_LR') is True and v.get('all_source_cpu_finite') is True,'actual full core/CPU scope')
 require(v.get('queue20ms_fields_CPU_structurally_valid') is True and v.get('actual_USD_gas400_composition_passed') is True,'actual clock structure/USD composition')
 q=v.get('queue_structure_proof') or {}
 require(q.get('original_CUDA_rng_bytes_untouched') is True and q.get('CPU_rng_substitution_used') is False and q.get('actual_CUDA_generator_restore_passed') is False,'CPU not a fabricated CUDA restore')
 require(v.get('actual_CUDA_fullrestore_pending') is True,'real worker CUDA restore remains required')
 return True
def load_E0_preinstalled_CPU(spec,B):
 validate_spec(spec);B=Path(B)
 p=Path(JOB)/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json';require(H(p)==CPU,'actual89C report bytes')
 value=json.loads(p.read_bytes());validate_cpu_value(value)
 proof=B/'E0_ACTUAL89C_CPU_RETURNED_PROOF.json';require(H(proof)==spec['CPU_returned_proof_SHA'],'actual returned witness pin')
 v=json.loads(proof.read_bytes())
 require(v.get('actual_finite_returned') is True and v.get('actual_source_SDK_CPU_passed') is True and v.get('source_CPU_SHA')==CPU and v.get('worker_V3_SHA')==WORKER and v.get('root')==JOB,'actual returned CPU witness, never a synthetic ready')
 return dict(value=value,path=str(p),SHA=CPU,actual_CPU_waited_EXIT0=True,original_returned_proof_SHA=H(proof))
def E0_valid_ready(row,spec):
 try:
  validate_spec(spec);e=row.get('closed_source_CPU') or {};v=e.get('value') or {};validate_cpu_value(v)
  require(row.get('key')==KEY and row.get('phase')=='ready' and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error'),'ready identity')
  require(row.get('actual_validation_fcntl_held') is True and e.get('actual_CPU_waited_EXIT0') is True and e.get('SHA')==CPU==digest(v),'actual locked/returned sourceCPU envelope')
  return True
 except (ValueError,KeyError,TypeError):return False
def E0_go_fields(spec):
 validate_spec(spec)
 return dict(GPU_UUID=GPU,authority_generation=GENERATION,num_envs=20000,policy_hz=50,worker_SHA=WORKER,
  source_qualification_kind=KIND,actual_H1_step270_scope_admitted=False,E0_PPO50_gas400=True)
def validate_payload(spec,B):
 validate_spec(spec);B=Path(B).resolve();p=B/'E0_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json';require(H(p)==spec['manifest_SHA'],'new installed controller manifest')
 manifest=json.loads(p.read_bytes());require(manifest['key']==KEY and manifest['source_SHA']==SOURCE and manifest['worker_SHA']==WORKER and manifest['source_CPU_SHA']==spec['source_CPU_SHA'],'manifest role/source')
 for r in manifest['files']:
  f=(B/r['relative']).resolve();require(f.is_relative_to(B) and not f.is_symlink() and f.stat().st_size==r['bytes'] and H(f)==r['SHA'],'controller source integrity '+r['relative'])
 require(H(Path(JOB)/spec['production_script'])==WORKER,'actual installed workerV3 bytes')
 task=json.loads((Path(JOB)/'TASK.json').read_bytes())
 require(task['source_SHA']==SOURCE and task['worker_SHA']==WORKER and task['source_CPU_SHA']==spec['source_CPU_SHA'] and task['GPU_UUID']==GPU and task['role']=='E0' and task['run_id']==spec['run_id'],'root-bound real worker Task')
 return True
def send(spec,row,port):
 validate_spec(spec);raw=json.dumps(dict(run_id=spec['run_id'],epoch=time.time(),row=row)).encode();token=spec['token'].encode()
 request=urllib.request.Request('http://127.0.0.1:'+str(port)+'/',data=raw,headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest()},method='POST')
 with urllib.request.urlopen(request,timeout=10) as response:
  result=response.read();require(hmac.compare_digest(response.headers.get('X-Own-Signature',''),hmac.new(token,result,hashlib.sha256).hexdigest()),'original owner response HMAC')
 return json.loads(result)

# Typed additive worker-only source migration. Base modelCPU witness stays V3.
EXTENSION_NAME='E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json'
def validate_V4_base_source_migration(v):
 require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE,'actual source-only migration result')
 require(v.get('base_actual_fullstate_CPU_SHA')==BASE_CPU and v.get('base_worker_SHA')==BASE_WORKER and v.get('target_worker_SHA')==BASE_V4_WORKER,'baseCPU and exactV4 worker source')
 require(v.get('target_worker_filename')=='E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py' and v.get('original_optimizer_LR_and_required_constructor_scalar')==.00038443359375000017,'only originalLR constructor literal migration')
 require(v.get('exact_single_CLI_literal_change') is True and v.get('no_model_reload') is True and v.get('no_new_fullstate_CPU_load_claim') is True and v.get('actual_CUDA_fullrestore_pending') is True,'honest extension scope')
 base=v.get('base_actual_fullstate_CPU_value') or {};validate_base_cpu_value(base)
 require(digest(base)==BASE_CPU and v.get('base_actual_fullstate_CPU_path')==BASE_JOB+'/E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json','original entire baseCPU unchanged')
 return True
def load_E0_preinstalled_CPU(spec,B):
 validate_spec(spec);B=Path(B)
 base_path=Path(JOB)/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json';require(H(base_path)==BASE_CPU,'actual89C fullstate witness unchanged')
 original=json.loads(base_path.read_bytes());validate_base_cpu_value(original)
 path=Path(JOB)/EXTENSION_NAME;require(H(path)==CPU==spec['source_CPU_SHA'],'actual233 worker-only migration byteSHA')
 value=json.loads(path.read_bytes());validate_cpu_value(value);require(value['base_actual_fullstate_CPU_value']==original,'embedded base is original89C')
 proof=B/'E0_ACTUAL89C_CPU_RETURNED_PROOF.json';require(H(proof)==spec['CPU_returned_proof_SHA'],'actual89C returned witness pin')
 v=json.loads(proof.read_bytes());require(v.get('actual_finite_returned') is True and v.get('actual_source_SDK_CPU_passed') is True and v.get('source_CPU_SHA')==BASE_CPU and v.get('worker_V3_SHA')==BASE_WORKER and v.get('root')==JOB,'actual89C return, distinct from worker-only migration')
 return dict(value=value,path=str(path),SHA=CPU,actual_CPU_waited_EXIT0=True,base_actual_CPU_waited_EXIT0=True,
  original_returned_proof_SHA=H(proof),scope='actual89C fullstate CPU plus actual233 worker-only source migration; no new modelCPU load',no_model_reload=True)

# New89D exact source-only V5 repair, original54f remains the model source.
FAILED89C_ENDING_SHA='e90bda2d34777c60661880f9aa390bd6974437e21a4a9adfade71b933d096ef1'
V5_EXTENSION_NAME='E0_V5_WRITER_PRESAVE_SOURCE_MIGRATION_ACTUAL.json'
def valid_source_extension_sha(v):return isinstance(v,str) and len(v)==64 and all(x in '0123456789abcdef' for x in v)
def validate_cpu_value(v):
 require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE,'actual V5 source-only extension, model still54f')
 require(v.get('base_actual_fullstate_CPU_SHA')==BASE_CPU and v.get('base_worker_SHA')==BASE_V4_WORKER and v.get('target_worker_SHA')==WORKER,'original fullstate/baseV4/targetV5 source binding')
 require(v.get('target_worker_filename')=='E0_PPO50_gas400_finite_worker_v5_writer_before_presave.py' and v.get('exact_existing_writer_assignment_move') is True,'only existing writer assignment moved before save')
 require(v.get('no_model_reload') is True and v.get('no_new_fullstate_CPU_load_claim') is True and v.get('actual_CUDA_fullrestore_pending') is True,'actual new runtime restore still required')
 require(v.get('new_job_root')==JOB and v.get('failed89C_resource_cost_only') is True and v.get('failed89C_original_ending_SHA')==FAILED89C_ENDING_SHA,'new unused89D, failed89C never a model source')
 base=v.get('base_actual_fullstate_CPU_value') or {};validate_base_cpu_value(base)
 require(digest(base)==BASE_CPU and v.get('base_actual_fullstate_CPU_path')==BASE_JOB+'/E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json','complete original89C modelCPU witness unchanged')
 previous=v.get('base_V4_worker_only_LR_source_migration_value') or {};validate_V4_base_source_migration(previous)
 require(v.get('base_V4_worker_only_LR_source_migration_SHA')==CPU and digest(previous)==CPU,'actual233 CLI LR migration unchanged')
 require(v.get('base_V4_worker_only_LR_source_migration_path')==BASE_JOB+'/E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json','exact original V4 migration path')
 return True
def E0_valid_ready(row,spec):
 try:
  validate_spec(spec);e=row.get('closed_source_CPU') or {};v=e.get('value') or {};validate_cpu_value(v)
  require(row.get('key')==KEY and row.get('phase')=='ready' and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error'),'ready identity')
  require(row.get('actual_validation_fcntl_held') is True and e.get('actual_CPU_waited_EXIT0') is True and e.get('SHA')==spec['source_CPU_SHA']==digest(v),'actual baseCPU+source-only extension and lock')
  return True
 except (ValueError,KeyError,TypeError):return False
def load_E0_preinstalled_CPU(spec,B):
 validate_spec(spec);B=Path(B)
 path=Path(JOB)/V5_EXTENSION_NAME;require(H(path)==spec['source_CPU_SHA'],'actual published89D V5 source-only extension SHA')
 value=json.loads(path.read_bytes());validate_cpu_value(value)
 base=Path(BASE_JOB)/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json';require(H(base)==BASE_CPU and json.loads(base.read_bytes())==value['base_actual_fullstate_CPU_value'],'original89C fullstateCPU never rewritten')
 lr=Path(BASE_JOB)/'E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json';require(H(lr)==CPU and json.loads(lr.read_bytes())==value['base_V4_worker_only_LR_source_migration_value'],'actualV4 LR extension untouched')
 returned=B/'E0_ACTUAL89C_CPU_RETURNED_PROOF.json';require(H(returned)==spec['CPU_returned_proof_SHA'],'original89C CPU return pin')
 witness=json.loads(returned.read_bytes());require(witness.get('actual_finite_returned') is True and witness.get('source_CPU_SHA')==BASE_CPU and witness.get('worker_V3_SHA')==BASE_WORKER and witness.get('root')==BASE_JOB,'base CPU actual return')
 close=B/'E0_89C_RESOURCE_COST_SETTLED_ACTUAL.json';require(H(close)==FAILED89C_ENDING_SHA,'actual failed89C resource/cost proof')
 ending=json.loads(close.read_bytes());require(ending.get('actual_early_error_ending_returned') is True and ending.get('original_error_not_skill_result') is True and ending.get('canonical_None') is True and ending.get('all_original_locks_free') is True,'actual89C settled/allout prerequisite')
 require(ending.get('original_fee_seconds')==397.61036682128906 and ending.get('closed_remaining_snapshot')==561777.961785078,'original full fee, no refund or new model')
 return dict(value=value,path=str(path),SHA=spec['source_CPU_SHA'],actual_CPU_waited_EXIT0=True,base_actual_CPU_waited_EXIT0=True,
  scope='original actual89C fullstateCPU + actualV4 LR + new V5 source-only move; no new modelCPU load',no_model_reload=True,failed_previous_scope='resource_cost_only')
