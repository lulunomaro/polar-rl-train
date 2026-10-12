from route_second_io import *
NEWROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_STARTUP_RESOURCE_REVIEWED_20261012'

def main():
    n,w=io.connect_both()
    try:
        v=run(n,r'''from pathlib import Path
import json,time,sys,hashlib,torch
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_startup_resource_reviewed_once as own
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
runs=list((D/'learning_logs').glob('*e1_WAVE50_route_startup_resource_reviewed_observation*'));assert len(runs)==1;run=runs[0]
names=('SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json','E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json','E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json')
markers={name:j(run/name) for name in names}
for name,v in markers.items():assert v['source_sha256']==SHA_TOKEN and v['pid']==3374665
s=markers[names[0]];assert s['actor_critic_std_exact'] and s['optimizer_loaded_original_path'] and s['sensor_streams_restored'] and s['global_CPU_CUDA_streams_restored'] and s['all_episode_counters_incremented_once'] and s['initial30q_error_rad']==0 and not s['PhysX_exact_resume_claimed']
a=markers[names[1]];assert a['action_queue_targets_timestamps_both_RNG_restored_exact'] and a['complete_D3_sensor_feedback_optimizer_global_named_streams_verified'] and a['action_episode_incremented_once']
for name,field,count in ((names[2],'actual_CUDA_spring_state_disk_roundtrip_exact','spring_episode_incremented_once'),(names[3],'actual_CUDA_gas_state_disk_roundtrip_exact','gas_episode_incremented_once'),(names[4],'actual_CUDA_chassis_PD_disk_roundtrip_exact','COM_PD_episode_incremented_once')):assert markers[name][field] and markers[name][count]
t=markers[names[5]];assert t['terrain_state_restored_exact'] and not t['explicitly_new_E1_terrain'] and not t['explicit_G3_to_WAVE50_geometry_transition'] and not t['explicit_G2_to_G3_geometry_transition'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['saved_source_episode_plus_one_verified']
c=markers[names[6]];assert c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and c['old_full_D1_D7_optimizer_global_named_streams_verified'] and c['saved_source_episode_plus_one_verified']
e=markers[names[7]];assert e['passed'] and e['same_entry_identity_restored_exact'] and not e['explicit_new_entry_scope'] and e['actual_entry_terrain_command_CUDA_disk_roundtrip_exact'] and e['saved_source_episode_plus_one_verified']
d=markers[names[8]];assert d['passed'] and d['predecessor_direction_state_restored_exact'] and not d['explicit_new_episode_direction_scope'] and d['actual_CUDA_direction_disk_roundtrip_exact'] and d['saved_source_episode_plus_one_verified']
r=markers[names[9]];assert r['passed'] and r['predecessor_route_state_restored_exact'] and not r['explicit_new_route_lifecycle_scope'] and r['actual_CUDA_route_disk_roundtrip_exact'] and r['saved_source_episode_plus_one_verified'] and r['old_full_actor_critic_optimizer_D0D7_global_named_private_restore_unmodified']
mf=j(run/'run_manifest.json');freeze=j(D/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==449 and mf['source_map']==freeze and mf['init_checkpoint_sha256']==SHA_TOKEN and mf['same50_entry_direction_route_fullstate_continuation']
indices=[dict(path=str(run/name),bytes=(run/name).stat().st_size,sha256=h(run/name)) for name in names]
if not (run/'latest_complete.json').exists():
 print(json.dumps(dict(epoch=time.time(),passed=True,startup_passed=True,PPO_saved_CPU_proof_pending=True,ten_markers=indices,manifest_SHA=h(run/'run_manifest.json'),no_own_saved_checkpoint_generated_yet=True)));raise SystemExit(0)
receipt=j(run/'latest_complete.json');ck=Path(receipt['checkpoint']);assert ck.parent==run and receipt['pid']==3374665 and ck.is_relative_to(D/'learning_logs')
info=own.fullsave(ck);assert info['finite_tensors']==107
source=own.source();assert h(source)==SHA_TOKEN;before=torch.load(source,map_location='cpu',weights_only=False);saved=torch.load(ck,map_location='cpu',weights_only=False)
changed=sum(not torch.equal(v,before['actor_state_dict'][k]) for k,v in saved['actor_state_dict'].items())
step=lambda v:float(v['step'].item()) if hasattr(v['step'],'item') else float(v['step']);delta=[step(v)-step(before['optimizer_state_dict']['state'][k]) for k,v in saved['optimizer_state_dict']['state'].items()];assert changed>0 and min(delta)>0
for name,sha in mf['src_sha256'].items():assert h(run/'src_snapshot'/name)==sha
assert j(run/'rolling_source_freeze.json')['sha256']==freeze
for name,sha in freeze.items():assert h(run/'e1_source_snapshot'/name)==sha
trace=j(run/'RETENTION_COMMAND_ACTUAL.json');assert trace['actual_controls']>0
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,startup_passed=True,actual_PPO_saved_CPU_verified=True,PPO_saved_CPU_proof_pending=False,own_checkpoint=info,CPU107=True,own_source449=True,own_PID=3374665,actual_actor_tensors_changed=changed,optimizer_step_delta_min=min(delta),optimizer_step_delta_max=max(delta),saved_trace_controls=trace['actual_controls'],ten_markers=indices,actual_module_snapshot_count=len(mf['src_sha256']),own_full_source_freeze449_verified=True,source_SHA_preserved=SHA_TOKEN,activity_only_not_formal_final_or_qualification=True,no_GPU_no_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(NEWROOT)).replace('SHA_TOKEN',repr(INIT_SHA)))
        p=save('RESOURCE449_OWN_SAVED_PPO_CPU_ACTUAL_'+str(time.time_ns())+'.json',v)
        print(json.dumps(dict(report=str(p),passed=v.get('passed'),startup=v.get('startup_passed'),PPO_CPU=v.get('actual_PPO_saved_CPU_verified'),checkpoint=v.get('own_checkpoint'),actorchanged=v.get('actual_actor_tensors_changed'),optimizerdelta=v.get('optimizer_step_delta_min'),controls=v.get('saved_trace_controls'))))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('RESOURCE449_OWN_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),observer_only_no_GPU_replay=True));raise
