"""Read own PID/fullsave/source snapshot/PASSED/one settled segment, CPU-only."""
from stage_environment_view_log_receipt_once import D,R,E,B,PY,NEW,connect_both,cleanup,save
import json,time,shlex,traceback
def main():
 n,w=connect_both()
 try:
  code=r'''from pathlib import Path
import hashlib,json,sys,time,torch
D=Path(ROOT);R=D/'reports';B=Path(BUDGET);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
if not (R/'e1_CURB20_independent_observation_PASSED.json').exists():
 print(json.dumps(dict(epoch=time.time(),pending=True,phase='own_formal_PASSED_not_yet_generated',CPU_read_only=True)));raise SystemExit
import supervise_curb20_environment_view_once as own
j=lambda p:json.loads(p.read_bytes());row=j(R/'e1_CURB20_independent_observation_PASSED.json');run=Path(row['run']);rec=j(run/'latest_complete.json');cp=Path(rec['checkpoint']);h=hashlib.sha256(cp.read_bytes()).hexdigest()
assert cp.is_relative_to(D/'learning_logs') and rec['pid']==row['own_PID_bound_receipt']['pid'] and h==row['checkpoint']['sha256']
info=own.fullsave(cp);assert info['finite_tensors']==102 and info['iteration_stored']==rec['iteration']
m=j(run/'run_manifest.json');f=j(R/'SOURCE_FREEZE.json')['sha256'];rolling=j(run/'rolling_source_freeze.json')['sha256']
assert m['source_map']==f==rolling and len(f)==384 and m['init_checkpoint_sha256']==own.prior.SOURCE_SHA
for name,sha in f.items():assert hashlib.sha256((run/'e1_source_snapshot'/name).read_bytes()).hexdigest()==sha
for name,sha in m['src_sha256'].items():assert hashlib.sha256((run/'src_snapshot'/name).read_bytes()).hexdigest()==sha
health=row['health'];assert health['control_steps']==24*row['actual_updates'] and health['actual_physics_callbacks']==health['expected_physics_callbacks']==4*health['control_steps']
assert health['termination_reason_coverage_exact'] and health['truncation_reason_coverage_exact'] and not health['nonfinite_observed'] and health['stop_reason'] is None
assert health['integrity_task_reset_events']==health['unknown_task_reset_events']==0
startup=j(run/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json');terrain=j(run/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json')
assert startup['migration']['source_command_state_and_private_RNG_exact'] and startup['migration']['explicit_changed_assignment_binding'] and startup['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and startup['saved_source_episode_plus_one_verified']
assert terrain['explicit_G3_to_CURB_geometry_transition'] and not terrain['terrain_state_restored_exact'] and terrain['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact']
l=j(B);segs=[x for x in l['completed_segments'] if x['pid']==rec['pid']];assert len(segs)==1 and segs==row['unique_completed_segment']
assert l['authorized_training_seconds']==828000 and not torch.cuda.is_initialized()
weights=[]
for r in R.glob('*_PASSED.json'):
 v=j(r)
 if 'checkpoint' in v:
  q=Path(v['checkpoint']['path']);assert hashlib.sha256(q.read_bytes()).hexdigest()==v['checkpoint']['sha256']
  weights.append(dict(path=str(q),bytes=q.stat().st_size,sha256=v['checkpoint']['sha256'],role='discarded_preflight' if v.get('discarded_preflight') else 'own_formal',PID=v['own_PID_bound_receipt']['pid']))
print(json.dumps(dict(epoch=time.time(),pending=False,passed=True,CPU_only=True,no_CUDA_initialized=True,checkpoint=dict(info,bytes=cp.stat().st_size),own_PID=rec['pid'],actual_snapshot_count=len(m['src_sha256']),rolling_source_count=len(f),actual_updates=row['actual_updates'],actual_environment_steps=row['actual_environment_steps'],health=health,source_assignment_migration=startup,terrain_startup=terrain,unique_completed_segment=segs,actual_total_segment_seconds=segs[0]['ended_epoch']-segs[0]['started_epoch'],own_weight_indices=weights,canonical_active=l['active_segment'],own_fullsave_not_behavior_pass=True)))
'''.replace('ROOT',repr(NEW)).replace('BUDGET',repr(B))
  compile(code,'<own-formal-cpu-review>','exec');_,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
  v=json.loads(raw);p=save(('ENVIRONMENT_VIEW_OWN_FORMAL_CPU_PENDING_' if v['pending'] else 'ENVIRONMENT_VIEW_OWN_FORMAL_CPU_VERIFIED_')+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),pending=v['pending'],checkpoint=v.get('checkpoint'),actual_updates=v.get('actual_updates'),actual_snapshot_count=v.get('actual_snapshot_count'),actual_segment_seconds=v.get('actual_total_segment_seconds'))))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ENVIRONMENT_VIEW_OWN_FORMAL_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only=True,no_signals_or_production_change=True));raise
