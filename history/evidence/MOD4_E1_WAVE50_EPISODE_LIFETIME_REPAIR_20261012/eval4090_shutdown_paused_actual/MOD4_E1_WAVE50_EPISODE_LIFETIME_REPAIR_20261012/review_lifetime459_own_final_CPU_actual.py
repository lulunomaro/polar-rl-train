from pathlib import Path
import os,json,time,traceback
import stage_lifetime_target_CPU_once as io
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_LIFETIME_ASYNC_REVIEWED_20261012'
def main():
 n,w=io.connect_linux_only()
 try:
  v=io.run(n,r'''from pathlib import Path
import sys,json,time,torch,hashlib,fcntl
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_lifetime_async_reviewed_once as own
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();R=D/'reports';row=j(R/'e1_WAVE50_episode_lifetime_observation_PASSED.json');run=Path(row['run']);receipt=j(run/'latest_complete.json');p=Path(receipt['checkpoint']);info=own.parent.fullsave(p);assert info['finite_tensors']==107 and info['lifetime_state_verified'] and receipt['pid']==row['own_PID_bound_receipt']['pid'];pid=receipt['pid']
m=j(run/'run_manifest.json');f=j(R/'SOURCE_FREEZE.json')['sha256'];assert len(f)==459 and m['source_map']==f and m['init_checkpoint_sha256']==own.parent.SOURCE_SHA
assert j(run/'rolling_source_freeze.json')['sha256']==f
for name,sha in f.items():assert h(run/'e1_source_snapshot'/name)==sha
for name,sha in m['src_sha256'].items():assert h(run/'src_snapshot'/name)==sha
names=('SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json','E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json','E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json','E1_WAVE50_LIFETIME_RESUME_STARTUP_VERIFIED.json')
markers={k:j(run/k) for k in names}
for k,s in markers.items():assert s['pid']==pid and s['source_sha256']==own.parent.SOURCE_SHA
l=markers[names[-1]];assert l['passed'] and l['explicit_new_episode_lifetime_scope'] and not l['predecessor_lifetime_state_restored_exact'] and l['actual_CUDA_lifetime_disk_roundtrip_exact'] and l['saved_source_episode_plus_one_verified']
t=markers[names[5]];assert not t['terrain_state_restored_exact'] and t['explicit_G3_to_WAVE50_geometry_transition'] and t['complete_D1_D7_optimizer_global_named_streams_verified'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['saved_source_episode_plus_one_verified']
s=markers[names[0]];assert s['actor_critic_std_exact'] and s['optimizer_loaded_original_path'] and s['sensor_streams_restored'] and s['global_CPU_CUDA_streams_restored'] and s['all_episode_counters_incremented_once'] and s['initial30q_error_rad']==0
assert markers[names[1]]['action_queue_targets_timestamps_both_RNG_restored_exact'] and markers[names[1]]['action_episode_incremented_once']
for name,field,count in ((names[2],'actual_CUDA_spring_state_disk_roundtrip_exact','spring_episode_incremented_once'),(names[3],'actual_CUDA_gas_state_disk_roundtrip_exact','gas_episode_incremented_once'),(names[4],'actual_CUDA_chassis_PD_disk_roundtrip_exact','COM_PD_episode_incremented_once')):assert markers[name][field] and markers[name][count]
for name in names[7:10]:assert markers[name]['passed'] and markers[name]['saved_source_episode_plus_one_verified']
c=markers[names[6]];assert c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and c['old_full_D1_D7_optimizer_global_named_streams_verified']
ck=torch.load(p,map_location='cpu',weights_only=False);source=Path(m['init_checkpoint']);before=torch.load(source,map_location='cpu',weights_only=False);changed=sum(not torch.equal(v,before['actor_state_dict'][k]) for k,v in ck['actor_state_dict'].items());step=lambda v:float(v['step'].item()) if hasattr(v['step'],'item') else float(v['step']);delta=[step(v)-step(before['optimizer_state_dict']['state'][k]) for k,v in ck['optimizer_state_dict']['state'].items()];assert changed>0 and min(delta)>0 and h(source)==own.parent.SOURCE_SHA
health=j(run/'CLOCK_TRAINING_HEALTH.json');assert own.prior.learning_health_pass(health) and health['control_steps']>0 and health['control_steps']%24==0 and health['actual_physics_callbacks']==health['control_steps']*4 and health['termination_reason_coverage_exact'] and health['truncation_reason_coverage_exact']
B=own.s.q.ctl.CANONICAL;b=j(B);seg=[s for s in b['completed_segments'] if s['pid']==pid];assert len(seg)==1 and b['active_segment'] is None and not j(own.s.q.ctl.STATE_PATH).get('active_training');st=j(R/'E1_STATE.json');assert st['phase']=='E1_WAVE50_episode_lifetime_saved_review_ready' and st['child'] is None
locs=[st['owner'],j(R/'E1_GUARDIAN_STARTED.json'),dict(pid=pid,start_ticks=own.identity(pid)['start_ticks'] if own.identity(pid) else -1)];actual=[own.identity(x['pid']) for x in locs];assert all(not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks'] for loc,a in zip(locs,actual))
locks=[]
for pth in (B.parent/'native_floor_supervisor.lock',own.s.q.P/'autonomy_controller.lock'):
 with pth.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(pth),actual_fcntl_free=True))
assert not own.parent.trainers() and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,closeout_ready=True,source_count=459,actual_finite_tensor_count=107,actual_snapshot_count=len(m['src_sha256']),own_checkpoint=info,own=row,actual_PID=pid,actual_positive_PPO=True,actor_tensors_changed=changed,optimizer_step_delta_min=min(delta),startup_markers={k:dict(path=str(run/k),sha256=h(run/k),proof=s) for k,s in markers.items()},unique_completed_segment=seg,unique_loadlearnsaveexit_seconds=seg[0]['ended_epoch']-seg[0]['started_epoch'],actual_processes=actual,two_fcntl_free=locks,remaining_snapshot_seconds=b['remaining_training_seconds'],actual_lifetime_state_dtypes={k:str(ck['E1_WAVE50_episode_lifetime_state'][k].dtype) for k in ('wave_mask','bound_episode','limit_steps')},first_newscope_initial_transition_not_samefresh=True,source_b026_ancestor129_and_otherexperts_preserved=True,qualified50=False,no_GPU_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  p=io.save('LIFETIME459_OWN_FINAL_CPU_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(passed=True,report=str(p),own_checkpoint=v['own_checkpoint'],controls=v['own']['health']['control_steps'],updates=v['own']['actual_updates'],actorchanged=v['actor_tensors_changed'],optimizerdelta=v['optimizer_step_delta_min'],unique_seconds=v['unique_loadlearnsaveexit_seconds'],snapshots=v['actual_snapshot_count'])))
 finally:n.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except BaseException:io.save('LIFETIME459_FINAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_oldmain=True));raise
