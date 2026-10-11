"""Read own final, unique ledger, eight restore receipts, natural exits and OS locks."""
from pathlib import Path
import sys,json,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import NEW,save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io
def main():
 n,w=io.connect_both()
 try:
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib,fcntl,sys
D=Path(ROOT);R=D/'reports';B=Path(BUDGET);C=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002');j=lambda p:json.loads(p.read_bytes())
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'))
import supervise_curb20_entry_seed_reviewed_once as reviewed
actual_controller_state_path=reviewed.own.s.q.ctl.STATE_PATH
v=j(R/'e1_CURB20_entry_repair_observation_PASSED.json');s=j(R/'E1_STATE.json');g=j(R/'E1_GUARDIAN_STARTED.json');pub=j(R/'E1_CURB139_ASYNC_PUBLISHED.json');ready=j(R/'E1_REVIEW_READY.json')
assert s['child'] is None and s['phase']=='E1_CURB20_entry_repair_saved_review_ready' and not ready['all_courses_finished'] and ready['automatic_more_PPO_disallowed']
pid=v['own_PID_bound_receipt']['pid'];run=Path(v['run']);m=j(run/'run_manifest.json');assert m['init_checkpoint_sha256']==SOURCE_SHA and v['source_sha256']==SOURCE_SHA and v['source_count']==410
locs=[s['owner'],g,dict(pid=pid,start_ticks=86034491)];actual=[]
for loc in locs:
 p=Path('/proc')/str(loc['pid']);a=None
 if p.exists():
  f=(p/'stat').read_text().split(') ',1)[1].split();a=dict(state=f[0],start_ticks=int(f[19]));assert a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 actual.append(dict(locator=loc,actual=a))
b=j(B);assert b['active_segment'] is None and not j(actual_controller_state_path).get('active_training')
assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and 36000+sum(x['additional_training_seconds'] for x in b['budget_extensions'])==1188000
seg=[x for x in b['completed_segments'] if x['pid']==pid];assert len(seg)==1 and seg==v['unique_completed_segment'];duration=seg[0]['ended_epoch']-seg[0]['started_epoch']
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',C/'autonomy_controller.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(p))
restore={}
for p in run.glob('*STARTUP_VERIFIED.json'):
 raw=p.read_bytes();restore[p.name]=dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),receipt=j(p))
assert len(restore)==8
t=restore['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json']['receipt'];cmd=restore['E1_COMMAND_RETENTION_STARTUP_VERIFIED.json']['receipt']
assert not t['terrain_state_restored_exact'] and t['explicit_G3_to_CURB_geometry_transition'] and t['explicit_new_entry_reset_scope'] and not t['entry_reset_state_restored_exact']
assert t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['complete_D1_D7_optimizer_global_named_streams_verified'] and t['E1_episode_incremented_once'] and not t['PhysX_exact_resume_claimed']
assert cmd['saved_source_episode_plus_one_verified'] and cmd['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and cmd['old_full_D1_D7_optimizer_global_named_streams_verified']
h=v['health'];assert v['actual_updates']==7 and h['control_steps']==168 and v['actual_environment_steps']==3360000 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==672
assert h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and not h['nonfinite_observed'] and h['stop_reason'] is None and h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact']
assert len(pub['jobs'])==4 and pub['source']['sha256']==v['checkpoint']['sha256']
for job in pub['jobs']:assert job['artifacts']['checkpoint']['sha256']==v['checkpoint']['sha256'] and job['no_learning'] and not job['canonical_write_authority']
ck=Path(v['checkpoint']['path']);assert hashlib.sha256(ck.read_bytes()).hexdigest()==v['checkpoint']['sha256'];extra=[]
for p in [ck]+[x for x in run.iterdir() if x.is_file() and x.suffix in ('.pt','.npz','.npy')]:
 extra.append(dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),large_index_only=True))
print(json.dumps(dict(epoch=time.time(),formal_final_actual=True,own=v,checkpoint_bytes=ck.stat().st_size,actual_restore_receipts=restore,actual_natural_exits=actual,two_actual_OS_locks_free=locks,active_Sactive_empty=True,unique_formal_load_learn_save_exit_seconds=duration,formal_target_seconds=300,actual_published=pub,remaining_idle_seconds=b['remaining_training_seconds'],canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),canonical_total_seconds=1188000,budget_extensions=7,new_budget_seconds=0,large_actual_indices=extra,no_more_PPO_before_complete139_decision=True,no_CURB_RM_MoE_graduation=True,no_mutation=True)))
'''.replace('ROOT',repr(NEW)).replace('BUDGET',repr(io.B)).replace('SOURCE_SHA',repr(io.SHA)))
  p=save('ENTRY_SEED_FORMAL_FINAL_ACTUAL_REVIEW_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),checkpoint=v['own']['checkpoint']['sha256'],actual_duration_s=v['unique_formal_load_learn_save_exit_seconds'],natural_exits=True,two_OS_locks_free=True,published=[x['job_id'] for x in v['actual_published']['jobs']],remaining_idle_seconds=v['remaining_idle_seconds'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_FINAL_READER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),reader_only=True,no_physical_or_budget_write=True));raise
