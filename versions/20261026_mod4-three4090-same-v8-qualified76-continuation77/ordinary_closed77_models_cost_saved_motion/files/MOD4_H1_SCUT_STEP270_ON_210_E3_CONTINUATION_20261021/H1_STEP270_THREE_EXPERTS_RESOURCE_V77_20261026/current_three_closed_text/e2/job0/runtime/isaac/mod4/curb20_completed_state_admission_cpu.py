"""Read-only admission of actual384 fullsave/PPO and actual386 fresh fullresume."""
from pathlib import Path
import ast,json,hashlib,torch
from retention_command_state import same
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FRESH_PROCESS_REVIEWED_20261011')
def admit(D,fullsave):
 j=lambda p:json.loads(p.read_bytes());big=j(D/'reports/FRESH_PROCESS_BIG_CORE_VERIFIED.json');cp=Path(big['checkpoint']['path'])
 assert hashlib.sha256(cp.read_bytes()).hexdigest()==big['checkpoint']['sha256']=='7f1b74b1c1d4b0227d42da191c13ff9cc65b639c43b973c352b2131451d65caa'
 info=fullsave(cp);assert info['finite_tensors']==102
 h=big['health'];assert h['control_steps']==96 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==384
 assert h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and not h['nonfinite_observed'] and h['stop_reason'] is None
 assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and len(big['unique_completed_segment'])==1
 sourcefreeze=j(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(sourcefreeze)==386
 for name,digest in sourcefreeze.items():assert hashlib.sha256((OLD/name).read_bytes()).hexdigest()==digest
 st=j(OLD/'reports/E1_STATE.json');pid=st['child']['pid'];assert pid==2440342
 error=OLD/'reports/FRESH_PROCESS_PROBE_ERROR.txt';text=error.read_text();assert "'Logger' object has no attribute 'writer'" in text and 'runner.save(str(saved))' in text
 records={};indices=[]
 requirements={
  'SENSOR_RESUME_STARTUP_VERIFIED.json':['actor_critic_std_exact','optimizer_loaded_original_path','sensor_streams_restored','global_CPU_CUDA_streams_restored','all_episode_counters_incremented_once'],
  'DELAY_RESUME_STARTUP_VERIFIED.json':['delay_state_and_RNG_exactly_restored_before_reset','full_sensor_optimizer_global_named_streams_verified','delay_episode_incremented_once'],
  'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json':['action_queue_targets_timestamps_both_RNG_restored_exact','restored_before_new_scene_clock_rebase','complete_D3_sensor_feedback_optimizer_global_named_streams_verified'],
  'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json':['actual_CUDA_spring_state_disk_roundtrip_exact','complete_D1_D4_optimizer_global_named_streams_verified'],
  'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json':['actual_CUDA_gas_state_disk_roundtrip_exact','complete_D1_D5_optimizer_global_named_streams_verified'],
  'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json':['actual_CUDA_chassis_PD_disk_roundtrip_exact','complete_D1_D6_optimizer_global_named_streams_verified'],
  'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json':['predecessor_command_state_restored_exact','actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact','old_full_D1_D7_optimizer_global_named_streams_verified','saved_source_episode_plus_one_verified'],
  'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json':['terrain_state_restored_exact','actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact','complete_D1_D7_optimizer_global_named_streams_verified','saved_source_episode_plus_one_verified']}
 for name,keys in requirements.items():
  p=OLD/'fresh_process_resume'/name;raw=p.read_bytes();v=json.loads(raw)
  assert v['pid']==pid and v['source_sha256']==info['sha256'] and all(v[k] for k in keys) and v['PhysX_exact_resume_claimed'] is False
  records[name]=v;indices.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
 assert not records['E1_COMMAND_RETENTION_STARTUP_VERIFIED.json']['explicitly_new_command_scope']
 assert not records['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json']['explicit_G3_to_CURB_geometry_transition']
 script=OLD/'isaac/mod4/probe_curb20_fresh_process_full_resume.py';tree=ast.parse(script.read_text());main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
 calls=[x.func.attr for x in ast.walk(main) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute)];assert not any(x in calls for x in ('learn','step','update'))
 statements=main.body;savepos=next(i for i,x in enumerate(statements) if 'runner.save(str(saved))' in ast.unparse(x))
 zero_positions=[i for i,x in enumerate(statements[:savepos]) if isinstance(x,ast.Assert) and 'int(env._sim_step_counter) == 0' in ast.unparse(x)]
 assert len(zero_positions)>=2 and max(zero_positions)<savepos
 # Logger failed after base runner wrote weights, before full DR decorators appended state.
 p=OLD/'fresh_process_resume/fullsave_after_fresh_resume_no_learning.pt';a=torch.load(p,map_location='cpu',weights_only=False);b=torch.load(cp,map_location='cpu',weights_only=False)
 for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict','iter'):assert same(a[key],b[key]),key
 assert 'E1_terrain_state' not in a and 'sensor_DR_state' not in a
 partial=dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),base_network_optimizer_only_not_fullstate=True,not_a_formal_or_learning_source=True,actor_critic_std_optimizer_equal_completed_big_source=True)
 assert not torch.cuda.is_initialized()
 return dict(passed=True,CPU_only_read_only=True,no_CUDA_initialized=True,complete_big_PPO_and_fullsave=big,complete_big_checkpoint_CPU102=info,
  actual_fresh_process_sameCURB_fullrestore=records,actual_fresh_process_PID=pid,actual_receipt_indices=indices,
  original_zero_step_guard_unchanged_and_reached_before_logger_failure=True,actual_additional_PPO_updates=0,actual_additional_control_steps=0,
  whole_original_probe_exit_failure_preserved=True,original_partial_save=partial,original_error=dict(path=str(error),bytes=error.stat().st_size,sha256=hashlib.sha256(error.read_bytes()).hexdigest()),
  fullsave_from384_and_fullresume_from386_are_separately_complete_actual_evidence=True,
  original_failed_records_not_relabeled_pass=True,SDK_native_small_big_fullresume_GPU_not_repeated=True,
  formal_source_must_remain_original129_3c97=True,own_formal_fullsave_still_required=True)
