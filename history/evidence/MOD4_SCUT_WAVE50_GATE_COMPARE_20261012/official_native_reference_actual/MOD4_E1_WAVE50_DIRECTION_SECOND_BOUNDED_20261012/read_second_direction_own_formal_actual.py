"""Read own426 final CPU/save/unique closeout; actual same-scope flags, no legacy transition."""
from wave_direction_second_io import *

def main():
    n,w=io.connect_both()
    try:
        v=run(n,r'''from pathlib import Path
import json,time,sys,hashlib,torch,fcntl
D=Path(ROOT_TOKEN);R=D/'reports';sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_direction_second_bounded_once as wrapper
own=wrapper.prior;j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'e1_WAVE50_direction_second_bounded_observation_PASSED.json'
if not p.exists():print(json.dumps(dict(epoch=time.time(),pending=True,no_ownfinal_generated=True,no_mutation=True)));raise SystemExit(0)
row=j(p);run=Path(row['run']);ck=Path(row['checkpoint']['path']);manifest=j(run/'run_manifest.json');receipt=j(run/'latest_complete.json');freeze=j(R/'SOURCE_FREEZE.json')['sha256'];info=own.fullsave(ck)
assert not row['discarded_preflight'] and ck.parent==run and ck.is_relative_to(D/'learning_logs') and receipt['checkpoint']==str(ck) and receipt['pid']==row['own_PID_bound_receipt']['pid']
assert info['sha256']==row['checkpoint']['sha256'] and info['finite_tensors']==row['checkpoint']['finite_tensors']==104 and len(freeze)==426 and manifest['source_map']==freeze and manifest['init_checkpoint_sha256']==wrapper.INIT_SHA
for name,sha in manifest['src_sha256'].items():assert h(run/'src_snapshot'/name)==sha
assert j(run/'rolling_source_freeze.json')['sha256']==freeze
for name,sha in freeze.items():assert h(run/'e1_source_snapshot'/name)==sha
markers={}
for name in ('SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json','E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json'):
 q=run/name;a=j(q);assert a['source_sha256']==wrapper.INIT_SHA;markers[name]=dict(path=str(q),bytes=q.stat().st_size,sha256=h(q))
t=j(run/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json');e=j(run/'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json');direction=j(run/'E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json');c=j(run/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json')
assert t['terrain_state_restored_exact'] and not t['explicit_G3_to_WAVE50_geometry_transition'] and not t['explicitly_new_E1_terrain'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['saved_source_episode_plus_one_verified']
assert e['passed'] and e['same_entry_identity_restored_exact'] and not e['explicit_new_entry_scope'] and e['actual_entry_terrain_command_CUDA_disk_roundtrip_exact']
assert direction['passed'] and direction['predecessor_direction_state_restored_exact'] and not direction['explicit_new_episode_direction_scope'] and direction['actual_CUDA_direction_disk_roundtrip_exact'] and direction['saved_source_episode_plus_one_verified']
assert c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact']
health=row['health'];assert health['control_steps']==row['actual_updates']*24 and health['actual_physics_callbacks']==health['expected_physics_callbacks']==health['control_steps']*4 and row['actual_environment_steps']==health['control_steps']*20000
assert health['termination_reason_coverage_exact'] and health['truncation_reason_coverage_exact'] and not health['nonfinite_observed'] and health['stop_reason'] is None and health['integrity_task_reset_events']==health['unknown_task_reset_events']==0
assert j(run/'RETENTION_COMMAND_ACTUAL.json')['actual_controls']==health['control_steps']
source=wrapper.source();assert h(source)==wrapper.INIT_SHA;before=torch.load(source,map_location='cpu',weights_only=False);saved=torch.load(ck,map_location='cpu',weights_only=False)
changed=sum(not torch.equal(v,before['actor_state_dict'][k]) for k,v in saved['actor_state_dict'].items());step=lambda s:float(s['step'].item()) if hasattr(s['step'],'item') else float(s['step']);delta=[step(v)-step(before['optimizer_state_dict']['state'][k]) for k,v in saved['optimizer_state_dict']['state'].items()];assert changed>0 and min(delta)>0
B=own.s.q.ctl.CANONICAL;b=j(B);pid=receipt['pid'];segments=[x for x in b['completed_segments'] if x['pid']==pid];assert len(segments)==1 and segments==row['unique_completed_segment'];st=j(R/'E1_STATE.json');guardian=j(R/'E1_GUARDIAN_STARTED.json')
locs=[st['owner'],guardian,dict(pid=pid,start_ticks=segments[0].get('start_ticks'))];processes=[own.identity(x['pid']) for x in locs];exited=all(not x or x['state']=='Z' or (loc.get('start_ticks') is not None and x['start_ticks']!=loc['start_ticks']) for loc,x in zip(locs,processes))
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',own.s.q.P/'autonomy_controller.lock'):
 with q.open('r') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:free=False
 locks.append(dict(path=str(q),actual_fcntl_free=free))
ready=exited and all(x['actual_fcntl_free'] for x in locks) and b['active_segment'] is None and not j(own.s.q.ctl.STATE_PATH).get('active_training') and st['phase']=='E1_WAVE50_direction_second_bounded_saved_review_ready'
assert ready and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,pending=False,own=row,own_checkpoint=info,checkpoint_bytes=ck.stat().st_size,actual_finite_tensor_count=104,actual_source_count=426,actual_snapshot_file_count=sum(q.is_file() for q in (run/'src_snapshot').rglob('*')),own_PID=pid,startup_markers=markers,actor_tensors_changed=changed,optimizer_step_delta_min=min(delta),optimizer_step_delta_max=max(delta),actual_PPO_updates_positive=True,actual_processes=processes,locks=locks,closeout_ready=ready,actual_state=st,unique_completed_segment=segments,unique_loadlearnsaveexit_seconds=segments[0]['ended_epoch']-segments[0]['started_epoch'],remaining_snapshot_seconds=b['remaining_training_seconds'],source_SHA=wrapper.INIT_SHA,same50_entry_direction_full_CPU_CUDA_restored_exact=True,not_PhysX_exact_resume=True,no_GPU_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
        p=save('SECOND_DIRECTION_OWN_FORMAL_CPU_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(report=str(p),passed=v.get('passed'),closeout=v.get('closeout_ready'),checkpoint=v.get('own_checkpoint'),updates=v.get('own',{}).get('actual_updates'),health=v.get('own',{}).get('health'),actorchanged=v.get('actor_tensors_changed'),optimizerdelta=v.get('optimizer_step_delta_min'),unique_seconds=v.get('unique_loadlearnsaveexit_seconds'))))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('SECOND_DIRECTION_OWN_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only_no_GPU_or_budget_replay=True));raise
