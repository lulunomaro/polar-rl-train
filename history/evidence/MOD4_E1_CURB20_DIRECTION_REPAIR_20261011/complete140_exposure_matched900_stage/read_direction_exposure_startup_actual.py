from direction_io import *
from prepare_direction140_decision_and_exposure_continuation_once import ROOT

def main():
 n,w=io.connect_both()
 try:
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib
D=Path(NEW_ROOT_TOKEN);R=D/'reports';j=lambda p:json.loads(p.read_bytes());st=j(R/'E1_STATE.json');runs=list((D/'learning_logs').glob('*_'+Path(st['active_log']).stem));assert len(runs)<=1
names=['ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','E1_CURB_DIRECTION_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json']
markers={};indices=[]
if runs:
 run=runs[0]
 for name in names:
  p=run/name
  if p.exists():
   raw=p.read_bytes();markers[name]=json.loads(raw);indices.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
ready=set(markers)==set(names)
if ready:
 assert all(x['source_sha256']=='e6df067ada011e06cb6fcb4989c3d32007680bf6926340e313f94ed305871e16' for x in markers.values())
 s=markers['SENSOR_RESUME_STARTUP_VERIFIED.json'];assert s['sensor_streams_restored'] and s['global_CPU_CUDA_streams_restored'] and s['all_episode_counters_incremented_once']
 t=markers['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'];assert t['terrain_state_restored_exact'] and t['entry_reset_state_restored_exact'] and not t['explicitly_new_E1_terrain'] and not t['explicit_G3_to_CURB_geometry_transition'] and not t['explicit_new_entry_reset_scope'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['saved_source_episode_plus_one_verified']
 d=markers['E1_CURB_DIRECTION_RESUME_STARTUP_VERIFIED.json'];assert d['passed'] and d['predecessor_direction_state_restored_exact'] and not d['explicit_new_episode_direction_scope'] and d['actual_CUDA_direction_disk_roundtrip_exact'] and d['saved_source_episode_plus_one_verified']
 c=markers['E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'];assert c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and c['old_full_D1_D7_optimizer_global_named_streams_verified']
 for name,key in [('CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','actual_CUDA_chassis_PD_disk_roundtrip_exact'),('SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','actual_CUDA_spring_state_disk_roundtrip_exact'),('GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','actual_CUDA_gas_state_disk_roundtrip_exact')]:assert markers[name][key]
 assert markers['ACTION_DELAY_RESUME_STARTUP_VERIFIED.json']['action_queue_targets_timestamps_both_RNG_restored_exact'] and markers['DELAY_RESUME_STARTUP_VERIFIED.json']['delay_state_and_RNG_exactly_restored_before_reset']
 m=j(run/'run_manifest.json');assert m['source_map']==j(R/'SOURCE_FREEZE.json')['sha256'] and m['init_checkpoint_sha256']=='e6df067ada011e06cb6fcb4989c3d32007680bf6926340e313f94ed305871e16'
health=j(R/'E1_ACTIVE_HEALTH.json') if (R/'E1_ACTIVE_HEALTH.json').exists() else None
if health:assert health['actual_physics_callbacks']==health['expected_physics_callbacks']==4*health['control_steps'] and not health['nonfinite_observed'] and health['stop_reason'] is None and health['integrity_task_reset_events']==health['unknown_task_reset_events']==0
print(json.dumps(dict(epoch=time.time(),root=str(D),actual_run=str(runs[0]) if runs else None,startup_complete=ready,pending=not ready,expected_actual_startup_files=names,markers=markers,actual_file_SHA_indices=indices,health=health,source424_actual_identity=True,same_scope_not_initial_transition=ready,no_GPU_PPO_budget_write=True)))
'''.replace('NEW_ROOT_TOKEN',repr(ROOT)))
  p=save('EXPOSURE_MATCHED_STARTUP_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),root=ROOT,startup_complete=v['startup_complete'],markers=len(v['markers']),health=v['health'])))
 finally:io.cleanup(n,w)

if __name__=='__main__':main()
