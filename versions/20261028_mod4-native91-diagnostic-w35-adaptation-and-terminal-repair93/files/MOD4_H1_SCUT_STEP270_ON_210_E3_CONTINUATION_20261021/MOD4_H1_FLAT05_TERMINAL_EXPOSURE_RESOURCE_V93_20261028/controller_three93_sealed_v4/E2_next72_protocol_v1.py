"""Only E2 node/spec qualification for next UNSTARTED H1+E2 cohort. No writer."""
from pathlib import Path
import hashlib,hmac,json,time,urllib.request
KEY='e2'
GPU='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_PPO50_GAS400_2610v93/e2'
SOURCE='5b5d1ee88bf9f56f865378d82d9f8864fa5ec2859f636c9b33b07558323d7f6e'
ORIGINAL='72f4cbefeb5bf02af6f39a9d2922faa8032e36e81cb9a142df45154158998c9f'
WORKER='6945d96b88da874a7c83311620b3a329366d33c9a5c97c887510223241f0754e'
WORKER_NAME='E2_PPO50_gas400_finite_worker_v1.py'
KIND='MOD4_E2_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1'
ORIGINAL_MANIFEST='ad1d4681d85d18dde8a545dbf58fc2460173faf556b6102c96f5eef69c33e80f'
PAYLOAD_MANIFEST='0e27157ce13a88748504c02a5702b7d6027ca14ca3224e4c6d4d5bcbe52175fd'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
PRIVATE_LOCK='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+GPU+'.lock'
PYTHON='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
CPU_PATH=JOB+'/E2_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json'
WAITED_PATH=JOB+'/E2_SOURCE_CPU_WAITED_ACTUAL_V1.json'

def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,indent=2).encode()).hexdigest()
def require(v,message):
 if not v:raise ValueError(message)
def sha(v):return isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v)

def validate_spec(s):
 require(s.get('key')==KEY and s.get('E2_PPO50_gas400') is True,'actual E2 slot only')
 require(s.get('source_SHA')==SOURCE and s.get('worker_SHA')==WORKER and s.get('source_qualification_kind')==KIND,'exact independent E2 source and worker')
 require(s.get('GPU_UUID')==GPU and s.get('execution_backend')=='target72' and s.get('private_lock')==PRIVATE_LOCK,'actual target72 second physical GPU and original private lock')
 require(s.get('job_root')==JOB and s.get('python')==PYTHON and s.get('production_script')==WORKER_NAME,'new E2 job and original worker CLI')
 require(s.get('max_parent_seconds')==3900 and s.get('exit_headroom_seconds')==300 and s.get('owner_authority_generation')==GENERATION,'original finite sole72 bounds')
 require(s.get('num_envs')==20000 and s.get('policy_hz')==50 and s.get('original_Adam_step')==857460 and s.get('original_LR')==6.666666666666667e-05,'original E2 population/Adam/LR exact fork')
 require(s.get('CPU_path')==CPU_PATH and s.get('CPU_proof_path')==WAITED_PATH,'actual installed report and waited proof path')
 require(s.get('payload_manifest_SHA')==PAYLOAD_MANIFEST,'frozen E2 payload manifest')
 for k in ['source_CPU_SHA','CPU_waited_proof_SHA','manifest_SHA']:require(sha(s.get(k)),'actual SHA required '+k)
 require(isinstance(s.get('run_id'),str) and bool(s['run_id']),'new mixed run identity')
 return True

def validate_cpu_value(v,s):
 require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE and v.get('original_source_SHA')==ORIGINAL,'actual E2 sourceCPU kind')
 require(v.get('worker_SHA')==WORKER and v.get('original_run_manifest_SHA')==ORIGINAL_MANIFEST,'exact worker/original manifest')
 for k in ['actor35_critic38_original_STD_17Adam_LR','original20k_D1_D7_and_CUDA_rng_codec_retained','all_source_cpu_finite','E2_moving4_command_structure_valid','E2_original_task_semantics_retained','queue20ms_fields_CPU_structurally_valid','actual_USD_gas400_composition_passed','no_GPU_scene_native_or_PPO_or_account_write','actual_CUDA_fullrestore_pending','actual_E2_mesh_GPU_identity_pending','actual_command_CUDA_rng_restore_pending']:
  require(v.get(k) is True,'actual CPU receipt field '+k)
 require(v.get('constructor_LR_literal_matches_original_optimizer')==6.666666666666667e-05 and v.get('E2_exact_flat_reset_bank',{}).get('original_height_filter_selected_poses')==74,'original E2 LR and exact133bank/74filter')
 q=v.get('queue_structure_proof') or {}
 require(q.get('original_CUDA_rng_bytes_untouched') is True and q.get('CPU_rng_substitution_used') is False and q.get('actual_CUDA_generator_restore_passed') is False,'CPU structure does not claim CUDA restore')
 versions=v.get('versions') or {}
 require(versions.get('torch')=='2.10.0+cu128' and versions.get('isaaclab')=='6.1.14' and versions.get('isaacsim')=='6.0.1.0' and versions.get('rsl-rl-lib')=='5.0.1','same exact installed SDK/RSL/Torch')
 require(v.get('WM_transition_data_collection_executed') is False,'weights are not a WM dataset')
 return True

def load_E2_preinstalled_CPU(spec,B):
 validate_spec(spec)
 p=Path(CPU_PATH);require(H(p)==spec['source_CPU_SHA'],'actual CPU bytes pin')
 v=json.loads(p.read_bytes());validate_cpu_value(v,spec)
 proof=Path(WAITED_PATH);require(H(proof)==spec['CPU_waited_proof_SHA'],'actual waited proof pin')
 w=json.loads(proof.read_bytes())
 require(w.get('actual_waited') is True and w.get('returncode')==0 and w.get('report_SHA')==spec['source_CPU_SHA'] and w.get('job_root')==JOB,'external actual CPU process wait0')
 require(w.get('source_SHA')==SOURCE and w.get('worker_SHA')==WORKER and w.get('execution_backend')=='target72','exact source/worker target wait')
 identity=w.get('actual_identity') or {};require(isinstance(identity.get('pid'),int) and identity['pid']>0 and identity.get('exe') and identity.get('argv') and isinstance(identity.get('creation'),(int,float)),'actual owned CPU process identity')
 return dict(value=v,path=str(p),SHA=spec['source_CPU_SHA'],actual_CPU_waited_EXIT0=True,original_returned_proof_SHA=H(proof),scope='actual E2 source SDK CPU; CUDA restore native24 and new PPO remain mandatory')

def E2_valid_ready(row,spec):
 try:
  validate_spec(spec);e=row.get('closed_source_CPU') or {};v=e.get('value') or {};validate_cpu_value(v,spec)
  require(row.get('key')==KEY and row.get('phase')=='ready' and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error'),'ready identity')
  require(row.get('actual_validation_fcntl_held') is True and e.get('actual_CPU_waited_EXIT0') is True and e.get('SHA')==spec['source_CPU_SHA']==digest(v),'real node acquired lock and reuses actual waited CPU')
  return True
 except (ValueError,KeyError,TypeError):return False

def E2_go_fields(spec):
 validate_spec(spec)
 return dict(GPU_UUID=GPU,authority_generation=GENERATION,num_envs=20000,policy_hz=50,worker_SHA=WORKER,source_qualification_kind=KIND,E2_PPO50_gas400=True,actual_H1_step270_scope_admitted=False,payload_manifest_SHA=PAYLOAD_MANIFEST)

def validate_payload(spec,B):
 validate_spec(spec);B=Path(B).resolve();p=B/'E2_NODE_CONTROLLER_MANIFEST_V1.json';require(H(p)==spec['manifest_SHA'],'E2 node controller manifest')
 m=json.loads(p.read_bytes());require(m['key']==KEY and m['source_SHA']==SOURCE and m['worker_SHA']==WORKER,'node manifest source')
 for r in m['files']:
  f=(B/r['relative']).resolve();require(f.is_relative_to(B) and not f.is_symlink() and f.stat().st_size==r['bytes'] and H(f)==r['SHA'],'installed node source '+r['relative'])
 require(H(Path(JOB)/WORKER_NAME)==WORKER,'installed original E2 frozen worker')
 t=json.loads((Path(JOB)/'TASK.json').read_bytes())
 require(t['role']=='E2' and t['source_SHA']==SOURCE and t['worker_SHA']==WORKER and t['source_CPU_SHA']==spec['source_CPU_SHA'] and t['GPU_UUID']==GPU and t['run_id']==spec['run_id'],'dynamic actual Task binding after sourceCPU; not in sealed payload manifest')
 return True

def send(spec,row,port):
 validate_spec(spec);raw=json.dumps(dict(run_id=spec['run_id'],epoch=time.time(),row=row)).encode();token=spec['token'].encode()
 request=urllib.request.Request('http://127.0.0.1:'+str(port)+'/',data=raw,headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest()},method='POST')
 with urllib.request.urlopen(request,timeout=10) as response:
  result=response.read();require(hmac.compare_digest(response.headers.get('X-Own-Signature',''),hmac.new(token,result,hashlib.sha256).hexdigest()),'original owner response HMAC')
 return json.loads(result)

# Common original-writer interface; these names do not relabel PPO as native training.
nativeflat_valid_ready=E2_valid_ready
flat_go_fields=E2_go_fields
load_actual_flat_preinstalled_CPU=load_E2_preinstalled_CPU
