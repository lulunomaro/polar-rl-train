from entry_second_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,hashlib,fcntl
D=Path(ROOT_TOKEN);R=D/'reports';sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_entry_second_bounded_once as wrapper
own=wrapper.prior
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
passed=R/'e1_WAVE50_entry_second_bounded_observation_PASSED.json'
if not passed.exists():print(json.dumps(dict(epoch=time.time(),pending=True,actual_state=j(R/'E1_STATE.json'),own_final_not_generated=True,no_mutation=True)));raise SystemExit(0)
row=j(passed);run=Path(row['run']);ck=Path(row['checkpoint']['path']);receipt=j(run/'latest_complete.json');manifest=j(run/'run_manifest.json');freeze=j(R/'SOURCE_FREEZE.json')['sha256'];info=own.fullsave(ck)
assert not row['discarded_preflight'] and ck.is_relative_to(D/'learning_logs') and ck.parent==run and receipt['checkpoint']==str(ck) and receipt['pid']==row['own_PID_bound_receipt']['pid']
assert info['sha256']==row['checkpoint']['sha256'] and info['finite_tensors']==row['checkpoint']['finite_tensors'] and len(freeze)==412 and manifest['source_map']==freeze and manifest['init_checkpoint_sha256']==wrapper.INIT_SHA
for name,sha in manifest['src_sha256'].items():assert h(run/'src_snapshot'/name)==sha
rolling=j(run/'rolling_source_freeze.json');assert rolling['sha256']==freeze
for name,sha in freeze.items():assert h(run/'e1_source_snapshot'/name)==sha
markers={}
for name in ('SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json'):
 p=run/name;a=j(p);assert a['source_sha256']==wrapper.INIT_SHA;markers[name]=dict(path=str(p),bytes=p.stat().st_size,sha256=h(p))
t=j(run/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json');c=j(run/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_WAVE50_ENTRY_STARTUP_VERIFIED.json')
assert t['terrain_state_restored_exact'] and not t['explicit_G3_to_WAVE50_geometry_transition'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['E1_episode_incremented_once'] and not t['PhysX_exact_resume_claimed']
ep=j(run/'E1_WAVE50_ENTRY_STARTUP_VERIFIED.json');assert ep['passed'] and ep['same_entry_identity_restored_exact'] and not ep['explicit_new_entry_scope'] and ep['actual_entry_terrain_command_CUDA_disk_roundtrip_exact']
assert c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and c['saved_source_episode_plus_one_verified']
health=row['health'];assert health['control_steps']==row['actual_updates']*24 and health['actual_physics_callbacks']==health['expected_physics_callbacks']==health['control_steps']*4 and row['actual_environment_steps']==health['control_steps']*20000
assert health['termination_reason_coverage_exact'] and health['truncation_reason_coverage_exact'] and not health['nonfinite_observed'] and health['stop_reason'] is None and health['integrity_task_reset_events']==health['unknown_task_reset_events']==0
assert j(run/'RETENTION_COMMAND_ACTUAL.json')['actual_controls']==health['control_steps']
B=own.s.q.ctl.CANONICAL;b=j(B);pid=receipt['pid'];segments=[x for x in b['completed_segments'] if x['pid']==pid];assert len(segments)==1 and segments==row['unique_completed_segment']
st=j(R/'E1_STATE.json');owner=st['owner'];guardian=j(R/'E1_GUARDIAN_STARTED.json');locs=[owner,guardian,dict(pid=pid,start_ticks=segments[0].get('start_ticks'))]
processes=[own.identity(x['pid']) for x in locs];exited=all(not x or x['state']=='Z' or (loc.get('start_ticks') is not None and x['start_ticks']!=loc['start_ticks']) for loc,x in zip(locs,processes))
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',own.s.q.P/'autonomy_controller.lock'):
 with p.open('r') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:free=False
 locks.append(dict(path=str(p),actual_fcntl_free=free))
superstate=j(own.s.q.ctl.STATE_PATH);ready=exited and all(x['actual_fcntl_free'] for x in locks) and b['active_segment'] is None and not superstate.get('active_training') and st['phase']=='E1_WAVE50_entry_second_bounded_saved_review_ready'
assert h(own.source())==wrapper.INIT_SHA and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,pending=False,own=row,own_checkpoint=info,actual_finite_tensor_count=info['finite_tensors'],actual_source_count=len(freeze),actual_snapshot_file_count=sum(p.is_file() for p in (run/'src_snapshot').rglob('*')),own_PID=pid,startup_markers=markers,actual_processes=processes,locks=locks,closeout_ready=ready,actual_state=st,unique_completed_segment=segments,remaining_snapshot_seconds=b['remaining_training_seconds'],source_SHA=wrapper.INIT_SHA,not_PhysX_exact_resume=True,no_GPU_or_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  p=save('ENTRY_SECOND_OWN_FORMAL_CPU_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(report=str(p),passed=v.get('passed'),pending=v.get('pending'),closeout_ready=v.get('closeout_ready'),checkpoint=v.get('own_checkpoint'))))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('OWN_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only_no_GPU_or_budget_replay=True));raise
