"""One logical nativeflat h1 slot; sealed actual CPU metadata only, no ledger/PT I/O."""
from pathlib import Path
import hashlib,hmac,json,time,urllib.request
KEY='h1';GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FUDAN270_EPISODE20_2610v106/seed27'
SOURCE='764129c1b4c9ec4560d83423856e9f4f5867f8f18c841215f43ed5552415b89c'
BOOTSTRAP='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'
REFERENCE='1a03883127eae81ef815fbb6f7450bdee68f489561cd16a9d4b193a48243153e'
PROGRESS={'updates': 16063, 'world_updates': 160630, 'policy_updates': 15487}
KIND='MOD4_NATIVE104_FUDAN270_TARGET106_20S_TYPED_SOURCE_CPU_V1'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
PRIVATE_LOCK='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+GPU+'.lock'
PYTHON='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
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
 require(s.get('resource_admission')=={'schema': 'mod4.user_allowed_light_compute.20261029.v1', 'free_MiB_strictly_above': 15669, 'utilization_percent_max': 30, 'compute_UUID_rows_allowed': True, 'other_processes_untouched': True},'explicit user light-compute policy')
 require(s.get('goal_conditioning')=={'encoding': 'mod4.flat91.mask_aware_after_normalization.v1', 'source_networks_SHA': '60eebefc997b2c441969e237d2f2b2a1cab5fe2fedc715a5a7944f40c6503e2d', 'source_helper_SHA': '051aa553a3f26a18c9e04b9a1c31d750fbcab3f26e6067232ec227014ae40fa8', 'normalization_buffers_and_parameters_restored_literal': True},'literal preserved mask-aware goal encoding')
 require(s.get('key')==KEY and s.get('nativeflat90') is True,'one actual logical native99 slot')
 require(s.get('input_start_mode')=='continue_qualified104_fudan270_clock_aligned20s' and s.get('fudan_step_task')=={'schema': 'mod4.fudan106.own270.jump_and_recovery20s.v1', 'upstream_commit': '8204e853dfd2ed06d85a322e1a998c3d20a3be2c', 'request_age_ticks': 200, 'request_end_exclusive': 2000, 'approach_speed_m_s': 0.5, 'terminal_root_x_m': 0.75, 'step_edge_x_m': 0.35, 'step_top_z_m': 0.27, 'landing_callbacks': 12, 'stable_callbacks': 200, 'stable_seconds': 0.5, 'contact_modes_refreshed_each_predicted_state': True, 'no_scripted_action_or_force_or_airborne_reset': True, 'original_exact270_physical_criterion_retained': True, 'flat20_course_superseded': True, 'episode_seconds': 20.0, 'episode_ticks': 2000, 'clock_contract': {'schema': 'mod4.fudan106.coherent_episode20_clock.v1', 'policy_hz': 100, 'episode_seconds': 20.0, 'episode_ticks': 2000, 'settle_ticks': 200, 'request_start_inclusive': 200, 'request_end_exclusive': 2000, 'private_frame_stride': 4096, 'delay_period_ticks': 250, 'maximum_world_lookahead_ticks': 32, 'relative_age_feature_units': 'seconds; no rescaling', 'request_feature_matches_actual_command': True, 'physical_timeout_changed_from_seconds': 5.0, 'original_solver_PD_actions_DR_reset_and_real270_acceptance_retained': True}},'exact Fudan103 own270 task')
 require(s.get('logical_slot')==KEY and s.get('canonical_worker_key')=='h1','explicit signed logical slot and native worker ABI')
 require(s.get('source_SHA')==SOURCE and s.get('source_progress')==PROGRESS and s.get('source_Adamstep')==832460,'qualified88C/native and separate frozen832460')
 require(s.get('bootstrap_source_SHA')==BOOTSTRAP and s.get('native_seed')==27 and s.get('native_reference_SHA')==REFERENCE,'exact own bootstrap/seed/new flat reference')
 require(s.get('GPU_UUID')==GPU and s.get('execution_backend')=='target72' and s.get('private_lock')==PRIVATE_LOCK,'actual c27 target lock; not source210/R5 lock')
 require(s.get('job_root')==JOB and s.get('python')==PYTHON and s.get('production_script')==WORKER_NAME,'actual new90 worker root/CLI')
 require(s.get('num_envs')==4096 and s.get('policy_hz')==100 and s.get('max_parent_seconds')==3900 and s.get('exit_headroom_seconds')==300,'native4096/100Hz original finite bounds')
 require(s.get('owner_authority_generation')==GENERATION and s.get('source_qualification_kind')==KIND,'sole72 and typed88C->flat kind')
 require(s.get('changed_plant700_to_nominal400') is False and s.get('flat05_objective_changed_from_native88C') is True,'new objective, same400 plant')
 require(s.get('gas400_parameter_source_contract_SHA')==PARAMETER,'same400 parameter contract')
 require(s.get('goal_encoding_changed_from90B') is True,'new mask-aware input encoding')
 require(s.get('native_learning_seed')==27 and s.get('task_focused_real_replay')=={'schema': 'mod4.fudan106.actual_replay_prestep_to_recovery20s.v1', 'numerator': 1, 'denominator': 2, 'maximum_original_sampler_calls': 8, 'actual_age_start': 180, 'actual_age_end_exclusive': 2000, 'policy_hz': 100, 'physical_timeout_ticks': 2000, 'insufficient_focus': 'fill_with_original_valid_starts', 'generated_or_modified_transitions': False, 'original_sampler_RNG_draw_count_unchanged': False, 'source_SHA': 'e3ba2f76e11ffe825a0bdc5c8c49a9cfc5fc8156b90324927c4b1491e2680a32'},'exact Fudan103 replay/source learning seed')
 require(s.get('imagination_terminal_exposure')=={'schema': 'mod4.fudan106.terminal_exposure20s.v1', 'selected_mdp_SHA': 'd068a6d012c7d7d0eeb8cb9337dbc98e71b2e3199a5c7e41341e8c8256fcb976', 'actual_start_age_min': 0, 'actual_start_age_max': 1999, 'physical_timeout_age': 2000, 'learner_BPTT_and_TD_lambda_unchanged': True, 'clock_contract': {'schema': 'mod4.fudan106.coherent_episode20_clock.v1', 'policy_hz': 100, 'episode_seconds': 20.0, 'episode_ticks': 2000, 'settle_ticks': 200, 'request_start_inclusive': 200, 'request_end_exclusive': 2000, 'private_frame_stride': 4096, 'delay_period_ticks': 250, 'maximum_world_lookahead_ticks': 32, 'relative_age_feature_units': 'seconds; no rescaling', 'request_feature_matches_actual_command': True, 'physical_timeout_changed_from_seconds': 5.0, 'original_solver_PD_actions_DR_reset_and_real270_acceptance_retained': True}},'new terminal exposure exact contract')
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
 require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE,'actual typed Fudan103 CPU')
 require(v.get('episode_clock')==s['fudan_step_task']['clock_contract'] and v.get('request_observation_clock_aligned') is True,'actual coherent20s CPU proof')
 require(v.get('fudan_step_task')==s['fudan_step_task'] and v.get('physical_initial_seed')==s['native_seed'],'actual270 task and physical seed')
 require(v.get('logical_slot')==KEY and v.get('canonical_worker_key')=='h1','native worker alias')
 require(v.get('native_learning_seed')==27 and v.get('task_focused_real_replay')==s['task_focused_real_replay'],'actual prestep-recovery replay')
 require(v.get('worker_SHA')==s['worker_SHA'] and v.get('payload_manifest_SHA')==s['payload_manifest_SHA'] and v.get('source_contract_SHA')==s['source_contract_SHA'],'actual worker/source fullSHA binding')
 require(v.get('GPU_UUID')==GPU and v.get('execution_backend')=='target72' and v.get('num_envs')==4096 and v.get('source_progress')==PROGRESS,'actual CPU target/source counters')
 require(v.get('runtime_clock')==dict(physics_dt_s=.0025,control_dt_s=.01,decimation=4,policy_hz=100) and v.get('nominal_gas_N')==400,'native100Hz and400N')
 for k in ('own_FK_reward_and_goal_source_CPU_passed','task_focused_replay_source_CPU_passed','source_native_fullstate_finite','all_native_modules_norms_threeoptimizers_strict_restore_CPU_passed','frozen_RSL832460_exact','actual_source_SDK_CPU_passed','no_GPU_yet','fudan270_objective','source_native_args_exact'):
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
 fields=('resource_admission','fudan_step_task','goal_conditioning','input_start_mode','logical_slot','canonical_worker_key','task_focused_real_replay','native_learning_seed','source_progress','native_seed','native_reference_SHA','source_Adamstep','gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA')
 return dict(**{k:spec[k] for k in fields},GPU_UUID=GPU,authority_generation=GENERATION,num_envs=4096,policy_hz=100,worker_SHA=spec['worker_SHA'],
  source_qualification_kind=KIND,payload_manifest_SHA=spec['payload_manifest_SHA'],bootstrap_SHA=BOOTSTRAP,bootstrap_Adam=832460,nativeflat90=True,changed_plant700_to_nominal400=False,
  flat05_objective_changed_from_native88C=True,goal_encoding_changed_from90B=True,imagination_terminal_exposure=spec['imagination_terminal_exposure'],actual_H1_flat05_scope_admitted=False,actual_H1_step270_scope_admitted=True,actual_H1_prelaunch_v2_scope_admitted=False)

def validate_payload(spec,B):
 validate_spec(spec);B=Path(B).resolve();p=B/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json';require(H(p)==spec['manifest_SHA'],'actual installed controller manifest')
 manifest=json.loads(p.read_bytes());require(manifest['key']==KEY and manifest['source_SHA']==SOURCE and manifest['worker_SHA']==spec['worker_SHA'] and manifest['source_CPU_SHA']==spec['source_CPU_SHA'],'controller manifest binding')
 for r in manifest['files']:
  f=(B/r['relative']).resolve();require(f.is_relative_to(B) and not f.is_symlink() and f.stat().st_size==r['bytes'] and H(f)==r['SHA'],'controller source integrity '+r['relative'])
 require(H(Path(JOB)/WORKER_NAME)==spec['worker_SHA'],'actual installed nativeflat worker source')
 task=json.loads((Path(JOB)/'job0/FLAT90_RUNTIME_GRANT_BINDING.json').read_bytes())
 for k in ('resource_admission','fudan_step_task','goal_conditioning','input_start_mode','task_focused_real_replay','native_learning_seed','source_SHA','worker_SHA','source_CPU_SHA','GPU_UUID','run_id','source_progress','native_seed','native_reference_SHA','source_Adamstep','changed_plant700_to_nominal400','flat05_objective_changed_from_native88C','gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA'):
  require(task[k]==spec[k],'actual native job0 Task '+k)
 require(task['key']==KEY,'native logical h1 task');return True

# Original authenticated loopback send function appended unchanged by derivation.


def send(spec,row,port):
 validate_spec(spec);raw=json.dumps(dict(run_id=spec['run_id'],epoch=time.time(),row=row)).encode();token=spec['token'].encode()
 request=urllib.request.Request('http://127.0.0.1:'+str(port)+'/',data=raw,headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest()},method='POST')
 with urllib.request.urlopen(request,timeout=10) as response:
  result=response.read();require(hmac.compare_digest(response.headers.get('X-Own-Signature',''),hmac.new(token,result,hashlib.sha256).hexdigest()),'original owner response HMAC')
 return json.loads(result)
