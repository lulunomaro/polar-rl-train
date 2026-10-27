"""One logical nativeflat h1 slot; sealed actual CPU metadata only, no ledger/PT I/O."""
from pathlib import Path
import hashlib,hmac,json,time,urllib.request
KEY='h1_210';GPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
JOB='/mnt/mod4_linux_durable_20261013/MOD4_H1_FLAT05_TERMINAL_2610v93/h1_210'
SOURCE='bd36a58c6bb31471212f4329407e85113064337650e51fc3c1587995dc2e3d50'
BOOTSTRAP='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'
REFERENCE='b4d801a47b92a0d63378df0cea15e8c736fe489c2fd37a63399a1a2ed3d00502'
PROGRESS=dict(updates=9256,world_updates=92560,policy_updates=9000)
KIND='MOD4_NATIVE91_H1_TERMINAL_EXPOSURE93_TYPED_SOURCE_CPU_V1'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
PRIVATE_LOCK='/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock'
PYTHON='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
WORKER_NAME='h1_native_flat90_worker_v1.py'
CPU_PATH=JOB+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json'
WAITED_PATH=JOB+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json'
PARAMETER='52142c8458aacc3ca251474cd5c61a3664b4c76b9eb60a63e43f30a75b8ae08e'
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,indent=2).encode()).hexdigest()
def require(v,message):
 if not v:raise ValueError(message)
def sha(v):return isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v)
def validate_spec(s):
 require(s.get('logical_slot')==KEY and s.get('canonical_worker_key')=='h1','explicit owner alias versus native ABI')
 require(s.get('key')==KEY and s.get('nativeflat90') is True,'one actual logical h1 flat slot')
 require(s.get('source_SHA')==SOURCE and s.get('source_progress')==PROGRESS and s.get('source_Adamstep')==832460,'qualified88C/native and separate frozen832460')
 require(s.get('bootstrap_source_SHA')==BOOTSTRAP and s.get('native_seed')==28 and s.get('native_reference_SHA')==REFERENCE,'exact own bootstrap/seed/new flat reference')
 require(s.get('GPU_UUID')==GPU and s.get('execution_backend')=='source210' and s.get('private_lock')==PRIVATE_LOCK,'actual c27 target lock; not source210/R5 lock')
 require(s.get('job_root')==JOB and s.get('python')==PYTHON and s.get('production_script')==WORKER_NAME,'actual new90 worker root/CLI')
 require(s.get('num_envs')==4096 and s.get('policy_hz')==100 and s.get('max_parent_seconds')==3900 and s.get('exit_headroom_seconds')==300,'native4096/100Hz original finite bounds')
 require(s.get('owner_authority_generation')==GENERATION and s.get('source_qualification_kind')==KIND,'sole72 and typed88C->flat kind')
 require(s.get('changed_plant700_to_nominal400') is False and s.get('flat05_objective_changed_from_native88C') is True,'new objective, same400 plant')
 require(s.get('gas400_parameter_source_contract_SHA')==PARAMETER,'same400 parameter contract')
 require(s.get('goal_encoding_changed_from90B') is True,'new mask-aware input encoding')
 require(s.get('imagination_terminal_exposure')=={'schema': 'mod4.flat93.terminal_exposure.v1', 'source_old_mdp_SHA': 'c075181fa92d8ce098a45102127070abeba6b04195c9037a038fe6172b56806a', 'selected_mdp_SHA': 'b7c9124550521025ad81826872663d918bc94199c18ac70385b35a235d79c623', 'source_CPU_proof_SHA': '0b2f4e5a19f7db3550bb66348ae6e0f949a6aa61f95044e8e15e20ad9b8620a7', 'actual_start_age_min': 0, 'actual_start_age_max': 499, 'physical_timeout_age': 500, 'learner_BPTT_and_TD_lambda_unchanged': True},'new terminal exposure exact contract')
 for k in ('worker_SHA','source_CPU_SHA','CPU_waited_proof_SHA','manifest_SHA','payload_manifest_SHA','source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA'):
  require(sha(s.get(k)),'actual sealed SHA required '+k)
 require(s.get('CPU_path')==CPU_PATH and s.get('CPU_proof_path')==WAITED_PATH,'exact preinstalled CPU report and actualwait proof')
 for k in ('payload_manifest_path','source_contract_path'):
  require(isinstance(s.get(k),str) and '..' not in Path(s[k]).parts and Path(s[k]).is_relative_to(Path(JOB)),'root-bound small source path '+k)
 return True
def validate_schedule(cfg):
 require(set(cfg['experts'])=={KEY} and cfg['deferred_experts']==[],'one real h1, no fake second slot')
 require(cfg['authority_generation']==GENERATION and cfg['scheduling_authority']=='human_requested_available_experts','sole original72 writer')
 validate_spec(cfg['experts'][KEY]);return True
def validate_cpu_value(v,s):
 require(v.get('logical_slot')==KEY and v.get('canonical_worker_key')=='h1','actual target CPU alias, no projected foreign proof')
 require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE,'actual typed sourceCPU')
 require(v.get('worker_SHA')==s['worker_SHA'] and v.get('payload_manifest_SHA')==s['payload_manifest_SHA'] and v.get('source_contract_SHA')==s['source_contract_SHA'],'sealed source/worker/payload contract')
 require(v.get('GPU_UUID')==GPU and v.get('execution_backend')=='source210' and v.get('num_envs')==4096 and v.get('source_progress')==PROGRESS,'actual CPU target/source counters')
 require(v.get('runtime_clock')==dict(physics_dt_s=.0025,control_dt_s=.01,decimation=4,policy_hz=100) and v.get('nominal_gas_N')==400,'native clock/same400')
 for k in ('terminal_exposure_source_CPU_passed','source_native_fullstate_finite','all_native_modules_norms_threeoptimizers_strict_restore_CPU_passed','frozen_RSL832460_exact','actual_source_SDK_CPU_passed','no_GPU_yet','flat_objective'):
  require(v.get(k) is True,'actual CPU evidence '+k)
 return True
def validate_waited_value(v,s):
 require(v.get('actual_waited') is True and v.get('returncode')==0 and isinstance(v.get('actual_identity'),dict) and bool(v['actual_identity']),'actual child identity+wait0, not report self-assertion')
 require(v.get('payload_manifest_SHA')==s['payload_manifest_SHA'] and v.get('report_SHA')==s['source_CPU_SHA'],'actual wait proof report/payload binding')
 return True
def load_actual_flat_preinstalled_CPU(spec,B):
 validate_spec(spec);raw=Path(spec['CPU_path']).read_bytes();require(hashlib.sha256(raw).hexdigest()==spec['source_CPU_SHA'],'sealed actual CPU report fullSHA')
 value=json.loads(raw);validate_cpu_value(value,spec)
 proof=Path(spec['CPU_proof_path']);proof_raw=proof.read_bytes();require(hashlib.sha256(proof_raw).hexdigest()==spec['CPU_waited_proof_SHA'],'actualwait proof fullSHA')
 waited=json.loads(proof_raw);validate_waited_value(waited,spec)
 require(H(spec['payload_manifest_path'])==spec['payload_manifest_SHA'] and H(spec['source_contract_path'])==spec['source_contract_SHA'],'same sealed installed source; no CPU/model rerun')
 return dict(value=value,path=spec['CPU_path'],SHA=spec['source_CPU_SHA'],raw_report_UTF8=raw.decode('utf8'),value_digest=digest(value),
  actual_CPU_waited_EXIT0=True,actual_waited_proof=waited,actual_waited_proof_SHA=spec['CPU_waited_proof_SHA'],raw_waited_proof_UTF8=proof_raw.decode('utf8'),source_CPU_reused_without_rerun=True)
def nativeflat_valid_ready(row,spec):
 try:
  validate_spec(spec);e=row.get('closed_source_CPU') or {};v=e.get('value') or {};validate_cpu_value(v,spec)
  require(row.get('key')==KEY and row.get('phase')=='ready' and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error'),'ready identity')
  require(row.get('actual_validation_fcntl_held') is True and e.get('actual_CPU_waited_EXIT0') is True and e.get('SHA')==spec['source_CPU_SHA'],'actual locked/returned CPU envelope')
  raw=e.get('raw_report_UTF8');require(isinstance(raw,str) and hashlib.sha256(raw.encode()).hexdigest()==spec['source_CPU_SHA'] and json.loads(raw)==v and e.get('value_digest')==digest(v),'exact sealed report raw/value binding independent of JSON whitespace')
  require(e.get('actual_waited_proof_SHA')==spec['CPU_waited_proof_SHA'],'actualwait proof SHA envelope')
  proof_raw=e.get('raw_waited_proof_UTF8');require(isinstance(proof_raw,str) and hashlib.sha256(proof_raw.encode()).hexdigest()==spec['CPU_waited_proof_SHA'] and json.loads(proof_raw)==e['actual_waited_proof'],'sealed actualwait raw/value binding')
  validate_waited_value(e['actual_waited_proof'],spec)
  return True
 except (ValueError,KeyError,TypeError):return False
def flat_go_fields(spec):
 validate_spec(spec)
 fields=('source_progress','native_seed','native_reference_SHA','source_Adamstep','gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA')
 return dict(**{k:spec[k] for k in fields},GPU_UUID=GPU,authority_generation=GENERATION,num_envs=4096,policy_hz=100,worker_SHA=spec['worker_SHA'],
  source_qualification_kind=KIND,payload_manifest_SHA=spec['payload_manifest_SHA'],bootstrap_SHA=BOOTSTRAP,bootstrap_Adam=832460,nativeflat90=True,changed_plant700_to_nominal400=False,
  logical_slot=KEY,canonical_worker_key='h1',flat05_objective_changed_from_native88C=True,goal_encoding_changed_from90B=True,imagination_terminal_exposure=spec['imagination_terminal_exposure'],actual_H1_flat05_scope_admitted=True,actual_H1_step270_scope_admitted=False,actual_H1_prelaunch_v2_scope_admitted=False)
def validate_payload(spec,B):
 validate_spec(spec);B=Path(B).resolve();p=B/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json';require(H(p)==spec['manifest_SHA'],'actual installed controller manifest')
 manifest=json.loads(p.read_bytes());require(manifest['key']==KEY and manifest['source_SHA']==SOURCE and manifest['worker_SHA']==spec['worker_SHA'] and manifest['source_CPU_SHA']==spec['source_CPU_SHA'],'controller manifest binding')
 for r in manifest['files']:
  f=(B/r['relative']).resolve();require(f.is_relative_to(B) and not f.is_symlink() and f.stat().st_size==r['bytes'] and H(f)==r['SHA'],'controller source integrity '+r['relative'])
 require(H(Path(JOB)/WORKER_NAME)==spec['worker_SHA'],'actual installed nativeflat worker source')
 task=json.loads((Path(JOB)/'job0/FLAT90_RUNTIME_GRANT_BINDING.json').read_bytes())
 for k in ('source_SHA','worker_SHA','source_CPU_SHA','GPU_UUID','run_id','source_progress','native_seed','native_reference_SHA','source_Adamstep','changed_plant700_to_nominal400','flat05_objective_changed_from_native88C','gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA'):
  require(task[k]==spec[k],'actual native job0 Task '+k)
 require(task['key']==KEY,'native logical h1 task');return True
# Original authenticated loopback send function appended unchanged by derivation.


def send(spec,row,port):
 validate_spec(spec);raw=json.dumps(dict(run_id=spec['run_id'],epoch=time.time(),row=row)).encode();token=spec['token'].encode()
 request=urllib.request.Request('http://127.0.0.1:'+str(port)+'/',data=raw,headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest()},method='POST')
 with urllib.request.urlopen(request,timeout=10) as response:
  result=response.read();require(hmac.compare_digest(response.headers.get('X-Own-Signature',''),hmac.new(token,result,hashlib.sha256).hexdigest()),'original owner response HMAC')
 return json.loads(result)
