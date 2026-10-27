"""One typed E0 slot, actual89C CPU proof; metadata only, no ledger/model I/O."""
from pathlib import Path
import hashlib,hmac,json,time,urllib.request
KEY='e0'
GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89c/e0'
SOURCE='54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371'
WORKER='1858c6395083bb7104385ec82d3dce6db4f79898a6346a250916ad7217524152'
CPU='d06aa8550f915258b0b42a711d73b9859f5fbce68fbcea6289b8647cd0f4208c'
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
 require(s.get('source_SHA')==SOURCE and s.get('worker_SHA')==WORKER and s.get('source_CPU_SHA')==CPU,'actual89C source/worker/CPU binding')
 require(s.get('GPU_UUID')==GPU and s.get('execution_backend')=='target72' and s.get('private_lock')==PRIVATE_LOCK,'actual89C GPU and original private lock')
 require(s.get('job_root')==JOB and s.get('python')==PYTHON,'actual installed89C root and approved interpreter')
 require(s.get('max_parent_seconds')==3900 and s.get('exit_headroom_seconds')==300,'original finite bounds')
 require(s.get('owner_authority_generation')==GENERATION and s.get('num_envs')==20000 and s.get('policy_hz')==50,'original authority/new exact E0 scope')
 require(s.get('production_script')=='E0_PPO50_gas400_finite_worker_v1.py','installed fixed basename contains actual V3 bytes')
 require(isinstance(s.get('manifest_SHA'),str) and len(s['manifest_SHA'])==64,'installed controller manifest pin')
 return True
def validate_schedule(cfg):
 require(set(cfg['experts'])=={KEY} and cfg['deferred_experts']==[],'no second or invented registration')
 require(cfg['authority_generation']==GENERATION and cfg['scheduling_authority']=='human_requested_available_experts','sole original72 writer')
 validate_spec(cfg['experts'][KEY]);return True
def validate_cpu_value(v):
 require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE and v.get('worker_SHA')==WORKER,'actual89C CPU result')
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
 manifest=json.loads(p.read_bytes());require(manifest['key']==KEY and manifest['source_SHA']==SOURCE and manifest['worker_SHA']==WORKER and manifest['source_CPU_SHA']==CPU,'manifest role/source')
 for r in manifest['files']:
  f=(B/r['relative']).resolve();require(f.is_relative_to(B) and not f.is_symlink() and f.stat().st_size==r['bytes'] and H(f)==r['SHA'],'controller source integrity '+r['relative'])
 require(H(Path(JOB)/spec['production_script'])==WORKER,'actual installed workerV3 bytes')
 task=json.loads((Path(JOB)/'TASK.json').read_bytes())
 require(task['source_SHA']==SOURCE and task['worker_SHA']==WORKER and task['source_CPU_SHA']==CPU and task['GPU_UUID']==GPU and task['role']=='E0' and task['run_id']==spec['run_id'],'root-bound real worker Task')
 return True
def send(spec,row,port):
 validate_spec(spec);raw=json.dumps(dict(run_id=spec['run_id'],epoch=time.time(),row=row)).encode();token=spec['token'].encode()
 request=urllib.request.Request('http://127.0.0.1:'+str(port)+'/',data=raw,headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest()},method='POST')
 with urllib.request.urlopen(request,timeout=10) as response:
  result=response.read();require(hmac.compare_digest(response.headers.get('X-Own-Signature',''),hmac.new(token,result,hashlib.sha256).hexdigest()),'original owner response HMAC')
 return json.loads(result)
