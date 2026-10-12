from route_second_io import *
NEWROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_STARTUP_RESOURCE_REVIEWED_20261012'

def main():
    n,w=io.connect_both()
    try:
        v=run(n,r'''from pathlib import Path
import sys,json,time,hashlib,torch,fcntl,ast
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_route_startup_resource_reviewed_once as own
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=list((D/'learning_logs').glob('*e1_WAVE50_route_startup_resource_reviewed_observation*'))[0];receipt=j(run/'latest_complete.json');ck=Path(receipt['checkpoint']);pid=receipt['pid'];assert pid==3374665 and ck.parent==run and ck.is_relative_to(D/'learning_logs')
att=j(D/'reports/E1_ATTENTION.json');assert not att['own_child_still_alive'] and att['active_segment'] is None and '#same-scope-train' in att['error'] and 'line 53' in att['error'] and 'AssertionError' in att['error']
controller=(D/'controller.log').read_text();assert 'line 53, in train' in controller
tree=ast.parse((D/'supervise_wave50_route_lifecycle_once.py').read_text());node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='train');text=ast.unparse(node)
for a,b in own.prior446.replacements.items():text=text.replace(a,own.ENTRY if a=='train_wave50_route_resume_ppo.py' else b)
lines=text.splitlines();assert "assert p.returncode == 0 and 'Traceback (most recent call last)' not in log.read_text" in lines[38]
assert "assert not terrain['terrain_state_restored_exact']" in lines[52]
assert all("not terrain['terrain_state_restored_exact']" not in a for a in ("assert terrain['terrain_state_restored_exact']",))
log=D/(j(run/'run_manifest.json')['run_name']+'.log');lograw=log.read_text(errors='replace');assert '[rescue] Full checkpoint saved; authorized budget or stop-file reached' in lograw and '[INFO]: SimulationContext cleared' in lograw and 'Traceback (most recent call last)' not in lograw and 'PxgPinnedMemoryAllocate failed' not in lograw
mf=j(run/'run_manifest.json');freeze=j(D/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==449 and mf['source_map']==freeze and mf['init_checkpoint_sha256']==SHA_TOKEN
assert mf['same50_entry_direction_route_fullstate_continuation'] and not mf['new_route_lifecycle_axis'] and not mf['new_episode_direction_axis'] and not mf['explicit_G3_to_WAVE50_geometry_transition']
info=own.fullsave(ck);assert info['finite_tensors']==107
for name,sha in mf['src_sha256'].items():assert h(run/'src_snapshot'/name)==sha
assert j(run/'rolling_source_freeze.json')['sha256']==freeze
for name,sha in freeze.items():assert h(run/'e1_source_snapshot'/name)==sha
names=('SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json','E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json','E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json')
markers={k:j(run/k) for k in names}
for k,a in markers.items():assert a['source_sha256']==SHA_TOKEN and a['pid']==pid
t=markers[names[5]];assert t['terrain_state_restored_exact'] and not t['explicit_G3_to_WAVE50_geometry_transition'] and not t['explicitly_new_E1_terrain'] and not t['explicit_G2_to_G3_geometry_transition'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['complete_D1_D7_optimizer_global_named_streams_verified'] and t['saved_source_episode_plus_one_verified'] and not t['PhysX_exact_resume_claimed']
e=markers[names[7]];assert e['passed'] and e['same_entry_identity_restored_exact'] and not e['explicit_new_entry_scope'] and e['actual_entry_terrain_command_CUDA_disk_roundtrip_exact'] and e['saved_source_episode_plus_one_verified']
d=markers[names[8]];assert d['passed'] and d['predecessor_direction_state_restored_exact'] and not d['explicit_new_episode_direction_scope'] and d['actual_CUDA_direction_disk_roundtrip_exact'] and d['saved_source_episode_plus_one_verified']
r=markers[names[9]];assert r['passed'] and r['predecessor_route_state_restored_exact'] and not r['explicit_new_route_lifecycle_scope'] and r['actual_CUDA_route_disk_roundtrip_exact'] and r['saved_source_episode_plus_one_verified'] and r['old_full_actor_critic_optimizer_D0D7_global_named_private_restore_unmodified']
c=markers[names[6]];assert c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and c['old_full_D1_D7_optimizer_global_named_streams_verified'] and c['saved_source_episode_plus_one_verified']
s=markers[names[0]];assert s['actor_critic_std_exact'] and s['optimizer_loaded_original_path'] and s['sensor_streams_restored'] and s['global_CPU_CUDA_streams_restored'] and s['all_episode_counters_incremented_once'] and s['initial30q_error_rad']==0
assert markers[names[1]]['action_queue_targets_timestamps_both_RNG_restored_exact'] and markers[names[1]]['action_episode_incremented_once'] and markers[names[1]]['complete_D3_sensor_feedback_optimizer_global_named_streams_verified']
for name,field,count in ((names[2],'actual_CUDA_spring_state_disk_roundtrip_exact','spring_episode_incremented_once'),(names[3],'actual_CUDA_gas_state_disk_roundtrip_exact','gas_episode_incremented_once'),(names[4],'actual_CUDA_chassis_PD_disk_roundtrip_exact','COM_PD_episode_incremented_once')):assert markers[name][field] and markers[name][count]
health=j(run/'CLOCK_TRAINING_HEALTH.json');assert own.prior.learning_health_pass(health)
assert health['control_steps']%24==0 and health['actual_physics_callbacks']==health['expected_physics_callbacks']==health['control_steps']*4
assert health['termination_reason_coverage_exact'] and health['truncation_reason_coverage_exact'] and not health['nonfinite_observed'] and health['stop_reason'] is None and health['integrity_task_reset_events']==health['unknown_task_reset_events']==0
assert j(run/'RETENTION_COMMAND_ACTUAL.json')['actual_controls']==health['control_steps']
source=own.source();assert h(source)==SHA_TOKEN;before=torch.load(source,map_location='cpu',weights_only=False);saved=torch.load(ck,map_location='cpu',weights_only=False)
changed=sum(not torch.equal(v,before['actor_state_dict'][k]) for k,v in saved['actor_state_dict'].items());step=lambda s:float(s['step'].item()) if hasattr(s['step'],'item') else float(s['step']);delta=[step(v)-step(before['optimizer_state_dict']['state'][k]) for k,v in saved['optimizer_state_dict']['state'].items()];assert changed>0 and min(delta)>0
B=own.s.q.ctl.CANONICAL;b=j(B);segments=[x for x in b['completed_segments'] if x['pid']==pid];assert len(segments)==1
assert b['active_segment'] is None and not j(own.s.q.ctl.STATE_PATH).get('active_training')
locs=[dict(pid=3374566,start_ticks=94934607),dict(pid=pid,start_ticks=94934812),j(D/'reports/E1_GUARDIAN_STARTED.json')];processes=[own.identity(x['pid']) for x in locs]
assert all(not p or p['state']=='Z' or p['start_ticks']!=loc['start_ticks'] for loc,p in zip(locs,processes))
locks=[]
for path in (B.parent/'native_floor_supervisor.lock',own.s.q.P/'autonomy_controller.lock'):
 with path.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(path),actual_fcntl_free=True))
assert not own.trainers() and not torch.cuda.is_initialized()
row=dict(epoch=time.time(),expert='E1_WAVE50',source_sha256=SHA_TOKEN,source_count=449,checkpoint=info,run=str(run),own_PID_bound_receipt=receipt,health=health,actual_updates=health['control_steps']//24,actual_environment_steps=health['control_steps']*20000,unique_completed_segment=segments,discarded_preflight=False,original_parent_assertion_failed_preserved=True,independent_same_identity_closeout_review=True,own_worker_returncode0_verified_by_original_parent_guard_before_failed_line53=True)
print(json.dumps(dict(epoch=time.time(),passed=True,closeout_ready=True,own=row,own_checkpoint=info,checkpoint_bytes=ck.stat().st_size,actual_finite_tensor_count=107,actual_source_count=449,actual_snapshot_file_count=len(mf['src_sha256']),own_PID=pid,startup_markers=[dict(path=str(run/k),bytes=(run/k).stat().st_size,sha256=h(run/k)) for k in names],actor_tensors_changed=changed,optimizer_step_delta_min=min(delta),optimizer_step_delta_max=max(delta),actual_PPO_updates_positive=True,actual_processes=processes,locks=locks,unique_completed_segment=segments,unique_loadlearnsaveexit_seconds=segments[0]['ended_epoch']-segments[0]['started_epoch'],remaining_snapshot_seconds=b['remaining_training_seconds'],source_SHA=SHA_TOKEN,same50_entry_direction_route_full_CPU_CUDA_restored_exact=True,not_PhysX_exact_resume=True,original_parent_error=dict(path=str(D/'reports/E1_ATTENTION.json'),sha256=h(D/'reports/E1_ATTENTION.json'),failed_generated_line=53,legacy_transition_assertion_not_same_scope=True),original_parent_state_attention_source_bytes_not_written=True,no_GPU_no_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(NEWROOT)).replace('SHA_TOKEN',repr(INIT_SHA)))
        p=save('RESOURCE449_INDEPENDENT_OWN_FORMAL_CPU_ACTUAL_'+str(time.time_ns())+'.json',v)
        print(json.dumps(dict(report=str(p),passed=v['passed'],checkpoint=v['own_checkpoint'],updates=v['own']['actual_updates'],health=v['own']['health'],actorchanged=v['actor_tensors_changed'],optimizerdelta=v['optimizer_step_delta_min'],unique_seconds=v['unique_loadlearnsaveexit_seconds'])))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('RESOURCE449_POSTEXIT_REVIEW_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),CPU_only_no_GPU_oldmain_budget_replay=True));raise
