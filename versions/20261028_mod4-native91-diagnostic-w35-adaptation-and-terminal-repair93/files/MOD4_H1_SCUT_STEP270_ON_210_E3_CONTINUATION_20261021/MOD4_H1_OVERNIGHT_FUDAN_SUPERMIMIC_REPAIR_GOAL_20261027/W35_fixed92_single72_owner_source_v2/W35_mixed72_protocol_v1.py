"""Only W35 node/spec qualification for next UNSTARTED H1+W35 cohort. No writer."""
from pathlib import Path
import hashlib,hmac,json,time,urllib.request
KEY='w35'
GPU='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_RETENTION_2610v92/w35'
SOURCE='36825921fb3e4a368791be7802c8ff16977e899240ac21ed2c067b2287bb9393'
ORIGINAL='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
WORKER='0ec27aae56bba060bac4ca1b68c5e977ad89da6c6abda0272bc46596460b6254'
WORKER_NAME='W35_PPO50_gas400_finite_worker_v1.py'
KIND='MOD4_W35_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1'
ORIGINAL_MANIFEST='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb'
PAYLOAD_MANIFEST='8ad322adbe7566aa7e8dfafeaf547533520ebc4c45075c4b696955806e8c758e'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
PRIVATE_LOCK='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+GPU+'.lock'
PYTHON='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
CPU_PATH=JOB+'/W35_RETENTION_BASELINE_ONLY_SOURCE_EXTENSION_ACTUAL_V2.json'
WAITED_PATH='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_2610v91/w35/W35_SOURCE_CPU_WAITED_ACTUAL_V1.json'

def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,indent=2).encode()).hexdigest()
def require(v,message):
 if not v:raise ValueError(message)
def sha(v):return isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v)

def validate_spec(s):
 require(s.get('key')==KEY and s.get('W35_PPO50_gas400') is True,'actual W35 slot only')
 require(s.get('source_SHA')==SOURCE and s.get('worker_SHA')==WORKER and s.get('source_qualification_kind')==KIND,'exact independent W35 source and worker')
 require(s.get('GPU_UUID')==GPU and s.get('execution_backend')=='target72' and s.get('private_lock')==PRIVATE_LOCK,'actual target72 second physical GPU and original private lock')
 require(s.get('job_root')==JOB and s.get('python')==PYTHON and s.get('production_script')==WORKER_NAME,'new W35 job and original worker CLI')
 require(s.get('max_parent_seconds')==3900 and s.get('exit_headroom_seconds')==300 and s.get('owner_authority_generation')==GENERATION,'original finite sole72 bounds')
 require(s.get('num_envs')==20000 and s.get('policy_hz')==50 and s.get('original_Adam_step')==646800 and s.get('original_LR')==.00001,'original W35 population/Adam/LR exact fork')
 require(s.get('CPU_path')==CPU_PATH and s.get('CPU_proof_path')==WAITED_PATH,'actual installed report and waited proof path')
 require(s.get('payload_manifest_SHA')==PAYLOAD_MANIFEST,'frozen W35 payload manifest')
 for k in ['source_CPU_SHA','CPU_waited_proof_SHA','manifest_SHA']:require(sha(s.get(k)),'actual SHA required '+k)
 require(isinstance(s.get('run_id'),str) and bool(s['run_id']),'new mixed run identity')
 return True

def validate_base_cpu_value(v,s):
 require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE and v.get('original_source_SHA')==ORIGINAL,'actual W35 sourceCPU kind')
 require(v.get('worker_SHA')==WORKER and v.get('original_run_manifest_SHA')==ORIGINAL_MANIFEST,'exact worker/original manifest')
 for k in ['actor35_critic38_original_STD_17Adam_LR','original20k_D1_D7_and_CUDA_rng_codec_retained','all_source_cpu_finite','W35_G3_saved_terrain_structure_valid','W35_retained_flat_command_structure_valid','queue20ms_fields_CPU_structurally_valid','actual_USD_gas400_composition_passed','no_GPU_scene_native_or_PPO_or_account_write','actual_CUDA_fullrestore_pending','actual_W35_mesh_GPU_identity_pending','actual_command_CUDA_rng_restore_pending']:
  require(v.get(k) is True,'actual CPU receipt field '+k)
 require(v.get('constructor_LR_literal_matches_original_optimizer')==.00001 and v.get('W35_nearest250_selected_bank',{}).get('selected_pose_index')==34,'original LR and W35 nearest250 pose34')
 q=v.get('queue_structure_proof') or {}
 require(q.get('original_CUDA_rng_bytes_untouched') is True and q.get('CPU_rng_substitution_used') is False and q.get('actual_CUDA_generator_restore_passed') is False,'CPU structure does not claim CUDA restore')
 versions=v.get('versions') or {}
 require(versions.get('torch')=='2.10.0+cu128' and versions.get('isaaclab')=='6.1.14' and versions.get('isaacsim')=='6.0.1.0' and versions.get('rsl-rl-lib')=='5.0.1','same exact installed SDK/RSL/Torch')
 require(v.get('WM_transition_data_collection_executed') is False,'weights are not a WM dataset')
 return True

BASE_JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_2610v91/w35'
BASE_CPU='d022ee93254dbf268c9b743ca0624951680b3f17e9ac791b317a95e2794f35cc'
BASE_PROOF='d932530973730ac7220274b61b62a006a2198a2693ac06680d372ef71a09941a'
MIGRATION='W35_RETENTION_SAVED_EPISODE_WITNESS_BASELINE_ONLY_V2'
EXTENSION_NAME='W35_RETENTION_BASELINE_ONLY_SOURCE_EXTENSION_ACTUAL_V2.json'
OLD_RETENTION_SHA='8f1c1f0f0f0af8cd30cefa94e4c9ea1b2139625ce55bf8af293dfa63657030f7'
NEW_RETENTION_SHA='8d3a49766a076f508118b5f84c4a1e9557d6e8a84369b9502516827336604894'

def validate_cpu_value(v,s):
 require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE and v.get('worker_SHA')==WORKER,'exact source-only extension, original model/worker')
 require(v.get('source_migration_kind')==MIGRATION and v.get('base_actual_fullstate_CPU_SHA')==BASE_CPU and v.get('base_actual_waited_proof_SHA')==BASE_PROOF,'original actual fullstateCPU and exactmigration')
 require(v.get('base_actual_fullstate_CPU_path')==BASE_JOB+'/W35_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json' and v.get('new_job_root')==JOB,'baseproof true origin/new unused target')
 require(v.get('old_retention_file_SHA')==OLD_RETENTION_SHA and v.get('new_retention_file_SHA')==NEW_RETENTION_SHA and v.get('inverse_single_expression_bytes_exact') is True,'only saved-episode witness expression changed')
 require(v.get('original_g3_reset_RNG_action_optimizer_reward_code_unchanged') is True and v.get('no_model_reload') is True and v.get('no_new_fullstate_CPU_load_claim') is True and v.get('actual_CUDA_fullrestore_pending') is True,'honest source-only migration')
 base=v.get('base_actual_fullstate_CPU_value') or {};validate_base_cpu_value(base,s);require(digest(base)==BASE_CPU,'entire original actualCPU value unchanged')
 require(v.get('payload_manifest_SHA')==PAYLOAD_MANIFEST and v.get('failed91_resource_cost_only') is True and v.get('failed91_original_fee_seconds')==488.166357755661,'exact new source manifest and failedcase not modelsource')
 return True

def load_W35_preinstalled_CPU(spec,B):
 validate_spec(spec)
 p=Path(JOB)/EXTENSION_NAME;require(H(p)==spec['source_CPU_SHA'],'actual source-only extension bytepin')
 value=json.loads(p.read_bytes());validate_cpu_value(value,spec)
 base=Path(BASE_JOB)/'W35_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json';require(H(base)==BASE_CPU and json.loads(base.read_bytes())==value['base_actual_fullstate_CPU_value'],'old actualCPU not rewritten')
 proof=Path(BASE_JOB)/'W35_SOURCE_CPU_WAITED_ACTUAL_V1.json';require(H(proof)==BASE_PROOF==spec['CPU_waited_proof_SHA'],'original CPUactualwait pin')
 w=json.loads(proof.read_bytes());require(w.get('actual_waited') is True and w.get('returncode')==0 and w.get('report_SHA')==BASE_CPU and w.get('job_root')==BASE_JOB,'original actual modelCPUwait0, not a new CPUrun')
 return dict(value=value,path=str(p),SHA=spec['source_CPU_SHA'],actual_CPU_waited_EXIT0=True,base_actual_CPU_waited_EXIT0=True,original_returned_proof_SHA=BASE_PROOF,scope='actual d022 fullstateCPU plus exact one-expression runtime source extension; no new modelCPU load',no_model_reload=True)

def W35_valid_ready(row,spec):
 try:
  validate_spec(spec);e=row.get('closed_source_CPU') or {};v=e.get('value') or {};validate_cpu_value(v,spec)
  require(row.get('key')==KEY and row.get('phase')=='ready' and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error'),'ready identity')
  require(row.get('actual_validation_fcntl_held') is True and e.get('actual_CPU_waited_EXIT0') is True and e.get('SHA')==spec['source_CPU_SHA']==digest(v),'real node acquired lock and reuses actual waited CPU')
  return True
 except (ValueError,KeyError,TypeError):return False

def W35_go_fields(spec):
 validate_spec(spec)
 return dict(GPU_UUID=GPU,authority_generation=GENERATION,num_envs=20000,policy_hz=50,worker_SHA=WORKER,source_qualification_kind=KIND,W35_PPO50_gas400=True,actual_H1_step270_scope_admitted=False,payload_manifest_SHA=PAYLOAD_MANIFEST)

def validate_payload(spec,B):
 validate_spec(spec);B=Path(B).resolve();p=B/'W35_NODE_CONTROLLER_MANIFEST_V1.json';require(H(p)==spec['manifest_SHA'],'W35 node controller manifest')
 m=json.loads(p.read_bytes());require(m['key']==KEY and m['source_SHA']==SOURCE and m['worker_SHA']==WORKER,'node manifest source')
 for r in m['files']:
  f=(B/r['relative']).resolve();require(f.is_relative_to(B) and not f.is_symlink() and f.stat().st_size==r['bytes'] and H(f)==r['SHA'],'installed node source '+r['relative'])
 require(H(Path(JOB)/WORKER_NAME)==WORKER,'installed original W35 frozen worker')
 require(H(Path(JOB)/'W35_RETENTION_BASELINE_V2_COMPLETE_INSTALL_MANIFEST.json')==PAYLOAD_MANIFEST,'actual new source install manifest')
 require(H(Path(JOB)/'runtime/isaac/mod4/retention_checkpoint.py')==NEW_RETENTION_SHA,'exact retention savedbaseline runtime')
 t=json.loads((Path(JOB)/'TASK.json').read_bytes())
 require(t['role']=='W35' and t['source_SHA']==SOURCE and t['worker_SHA']==WORKER and t['source_CPU_SHA']==spec['source_CPU_SHA'] and t['GPU_UUID']==GPU and t['run_id']==spec['run_id'],'dynamic actual Task binding after sourceCPU; not in sealed payload manifest')
 return True

def send(spec,row,port):
 validate_spec(spec);raw=json.dumps(dict(run_id=spec['run_id'],epoch=time.time(),row=row)).encode();token=spec['token'].encode()
 request=urllib.request.Request('http://127.0.0.1:'+str(port)+'/',data=raw,headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest()},method='POST')
 with urllib.request.urlopen(request,timeout=10) as response:
  result=response.read();require(hmac.compare_digest(response.headers.get('X-Own-Signature',''),hmac.new(token,result,hashlib.sha256).hexdigest()),'original owner response HMAC')
 return json.loads(result)
