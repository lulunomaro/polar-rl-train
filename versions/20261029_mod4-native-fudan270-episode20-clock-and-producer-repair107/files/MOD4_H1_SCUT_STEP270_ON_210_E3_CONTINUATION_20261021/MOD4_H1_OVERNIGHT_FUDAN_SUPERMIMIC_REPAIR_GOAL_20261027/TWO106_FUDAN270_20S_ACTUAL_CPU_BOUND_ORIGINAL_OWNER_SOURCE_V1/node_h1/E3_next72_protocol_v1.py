"""Only E3 node/spec qualification for next UNSTARTED H1+E3 cohort. No writer."""
from pathlib import Path
import hashlib,hmac,json,time,urllib.request
KEY='e3'
GPU='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3'
SOURCE='59fa03e6e4d3ecf81153707082840df0347f6504508dd1a413dda7b714db6b75'
ORIGINAL='61c442d9b2ebdeef93ba874478e25db5099767783ff19975907796f53cb168de'
WORKER='4c1ec69814e0ac3a6a18c9d435faccc73d4ea9a84893f63ce9cf6ca2b2aefd80'
WORKER_NAME='E3_PPO50_gas400_finite_worker_v1.py'
KIND='MOD4_E3_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1'
ORIGINAL_MANIFEST='ad1d4681d85d18dde8a545dbf58fc2460173faf556b6102c96f5eef69c33e80f'
PAYLOAD_MANIFEST='04e88211fa685523c3a9a0bd074ac69a5618baf55ffea67c1eab93f7bc436023'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
PRIVATE_LOCK='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+GPU+'.lock'
PYTHON='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
CPU_PATH=JOB+'/E3_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json'
WAITED_PATH=JOB+'/E3_SOURCE_CPU_WAITED_ACTUAL_V1.json'

def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,indent=2).encode()).hexdigest()
def require(v,message):
 if not v:raise ValueError(message)
def sha(v):return isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v)

def validate_spec(s):
 require(s.get('key')==KEY and s.get('E3_PPO50_gas400') is True,'actual E3 slot only')
 require(s.get('source_SHA')==SOURCE and s.get('worker_SHA')==WORKER and s.get('source_qualification_kind')==KIND,'exact independent E3 source and worker')
 require(s.get('GPU_UUID')==GPU and s.get('execution_backend')=='target72' and s.get('private_lock')==PRIVATE_LOCK,'actual target72 second physical GPU and original private lock')
 require(s.get('job_root')==JOB and s.get('python')==PYTHON and s.get('production_script')==WORKER_NAME,'new E3 job and original worker CLI')
 require(s.get('max_parent_seconds')==3900 and s.get('exit_headroom_seconds')==300 and s.get('owner_authority_generation')==GENERATION,'original finite sole72 bounds')
 require(s.get('num_envs')==20000 and s.get('policy_hz')==50 and s.get('original_Adam_step')==864320 and s.get('original_LR')==6.666666666666667e-05,'original E3 population/Adam/LR exact fork')
 require(s.get('CPU_path')==CPU_PATH and s.get('CPU_proof_path')==WAITED_PATH,'actual installed report and waited proof path')
 require(s.get('payload_manifest_SHA')==PAYLOAD_MANIFEST,'frozen E3 payload manifest')
 for k in ['source_CPU_SHA','CPU_waited_proof_SHA','manifest_SHA']:require(sha(s.get(k)),'actual SHA required '+k)
 require(isinstance(s.get('run_id'),str) and bool(s['run_id']),'new mixed run identity')
 return True

def validate_cpu_value(v,s):
 require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE and v.get('original_source_SHA')==ORIGINAL,'actual E3 sourceCPU kind')
 require(v.get('worker_SHA')==WORKER and v.get('original_run_manifest_SHA')==ORIGINAL_MANIFEST,'exact worker/original manifest')
 for k in ['actor35_critic38_original_STD_17Adam_LR','original20k_D1_D7_and_CUDA_rng_codec_retained','all_source_cpu_finite','E3_13_recipe_phase_and_original_nearest250_bank_cache_valid','E3_original_task_semantics_retained','queue20ms_fields_CPU_structurally_valid','actual_USD_gas400_composition_passed','no_GPU_scene_native_or_PPO_or_account_write','actual_CUDA_fullrestore_pending','actual_E3_fall_recipe_GPU_reset_pending','actual_command_CUDA_rng_restore_pending']:
  require(v.get(k) is True,'actual CPU receipt field '+k)
 require(v.get('constructor_LR_literal_matches_original_optimizer')==6.666666666666667e-05 and v.get('E3_exact_flat_reset_bank',{}).get('original_height_filter_selected_poses')==74,'original E3 LR and exact133bank/74filter')
 q=v.get('queue_structure_proof') or {}
 require(q.get('original_CUDA_rng_bytes_untouched') is True and q.get('CPU_rng_substitution_used') is False and q.get('actual_CUDA_generator_restore_passed') is False,'CPU structure does not claim CUDA restore')
 versions=v.get('versions') or {}
 require(versions.get('torch')=='2.10.0+cu128' and versions.get('isaaclab')=='6.1.14' and versions.get('isaacsim')=='6.0.1.0' and versions.get('rsl-rl-lib')=='5.0.1','same exact installed SDK/RSL/Torch')
 require(v.get('actual_runtime_nominal_gas2000_source_bound') is True and v.get('actual_asset_parent_import_contract_bound') is True and v.get('new_initial_fullstate_source_CPU_for_new97_runtime_admission') is True,'new97 complete runtime nominal and actual asset import route')
 require(v.get('runtime_nominal_source_SHAs')=={'spring_pressure_index_runtime.py': '4ea0a70293f09dda4d7fe862068c1460ea6acbb8db2accb7ea0fa31d9ccedc58', 'spring_pressure_audit_runtime.py': '66011dcc84479ab660756364add2e45f006c3f9cef8bff86344d16ca0e1533d9', 'spring_nominal_sdk_readback.py': '52237fc36ee86ed2ff443bcd905ab17ad798258a79a7270c2e1c889f8335037c'},'exact selected gas400 nominal production sources')
 require(v.get('WM_transition_data_collection_executed') is False,'weights are not a WM dataset')
 return True

def load_E3_preinstalled_CPU(spec,B):
 validate_spec(spec)
 p=Path(CPU_PATH);require(H(p)==spec['source_CPU_SHA'],'actual CPU bytes pin')
 v=json.loads(p.read_bytes());validate_cpu_value(v,spec)
 proof=Path(WAITED_PATH);require(H(proof)==spec['CPU_waited_proof_SHA'],'actual waited proof pin')
 w=json.loads(proof.read_bytes())
 require(w.get('actual_waited') is True and w.get('returncode')==0 and w.get('report_SHA')==spec['source_CPU_SHA'] and w.get('job_root')==JOB,'external actual CPU process wait0')
 require(w.get('source_SHA')==SOURCE and w.get('worker_SHA')==WORKER and w.get('execution_backend')=='target72','exact source/worker target wait')
 identity=w.get('actual_identity') or {};require(isinstance(identity.get('pid'),int) and identity['pid']>0 and identity.get('exe') and identity.get('argv') and isinstance(identity.get('creation'),(int,float)),'actual owned CPU process identity')
 return dict(value=v,path=str(p),SHA=spec['source_CPU_SHA'],actual_CPU_waited_EXIT0=True,original_returned_proof_SHA=H(proof),scope='actual E3 source SDK CPU; CUDA restore native24 and new PPO remain mandatory')

def E3_valid_ready(row,spec):
 try:
  validate_spec(spec);e=row.get('closed_source_CPU') or {};v=e.get('value') or {};validate_cpu_value(v,spec)
  require(row.get('key')==KEY and row.get('phase')=='ready' and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error'),'ready identity')
  require(row.get('actual_validation_fcntl_held') is True and e.get('actual_CPU_waited_EXIT0') is True and e.get('SHA')==spec['source_CPU_SHA']==digest(v),'real node acquired lock and reuses actual waited CPU')
  return True
 except (ValueError,KeyError,TypeError):return False

def E3_go_fields(spec):
 validate_spec(spec)
 return dict(GPU_UUID=GPU,authority_generation=GENERATION,num_envs=20000,policy_hz=50,worker_SHA=WORKER,source_qualification_kind=KIND,E3_PPO50_gas400=True,actual_H1_step270_scope_admitted=False,payload_manifest_SHA=PAYLOAD_MANIFEST)

def validate_payload(spec,B):
 validate_spec(spec);B=Path(B).resolve();p=B/'E3_NODE_CONTROLLER_MANIFEST_V1.json';require(H(p)==spec['manifest_SHA'],'E3 node controller manifest')
 m=json.loads(p.read_bytes());require(m['key']==KEY and m['source_SHA']==SOURCE and m['worker_SHA']==WORKER,'node manifest source')
 for r in m['files']:
  f=(B/r['relative']).resolve();require(f.is_relative_to(B) and not f.is_symlink() and f.stat().st_size==r['bytes'] and H(f)==r['SHA'],'installed node source '+r['relative'])
 require(H(Path(JOB)/WORKER_NAME)==WORKER,'installed original E3 frozen worker')
 t=json.loads((Path(JOB)/'TASK.json').read_bytes())
 require(t['role']=='E3' and t['source_SHA']==SOURCE and t['worker_SHA']==WORKER and t['source_CPU_SHA']==spec['source_CPU_SHA'] and t['GPU_UUID']==GPU and t['run_id']==spec['run_id'],'dynamic actual Task binding after sourceCPU; not in sealed payload manifest')
 return True

def send(spec,row,port):
 validate_spec(spec);raw=json.dumps(dict(run_id=spec['run_id'],epoch=time.time(),row=row)).encode();token=spec['token'].encode()
 request=urllib.request.Request('http://127.0.0.1:'+str(port)+'/',data=raw,headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest()},method='POST')
 with urllib.request.urlopen(request,timeout=10) as response:
  result=response.read();require(hmac.compare_digest(response.headers.get('X-Own-Signature',''),hmac.new(token,result,hashlib.sha256).hexdigest()),'original owner response HMAC')
 return json.loads(result)

# Common original-writer interface; these names do not relabel PPO as native training.
nativeflat_valid_ready=E3_valid_ready
flat_go_fields=E3_go_fields
load_actual_flat_preinstalled_CPU=load_E3_preinstalled_CPU
