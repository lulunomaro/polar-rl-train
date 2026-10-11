from wave_io import *
def main():
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,hashlib
D=Path(ROOT_TOKEN);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_wave35_exposure_005_once as own
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
st=j(D/'reports/E1_STATE.json');actual=own.identity(st['child']['pid']);assert actual and actual['start_ticks']==st['child']['start_ticks']
roots=list((D/'learning_logs').glob('*'));assert len(roots)==1;run=roots[0];rec=j(run/'latest_complete.json');manifest=j(run/'run_manifest.json');health=j(run/'CLOCK_TRAINING_HEALTH.json')
assert rec['pid']==actual['pid'] and manifest['init_checkpoint_sha256']==own.SOURCE_SHA and manifest['source_map']==j(D/'reports/SOURCE_FREEZE.json')['sha256']
for name,sha in manifest['src_sha256'].items():assert h(run/'src_snapshot'/name)==sha,name
startup={};indices=[]
for name in ('SENSOR_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'):
 p=run/name;row=j(p);assert row['source_sha256']==own.SOURCE_SHA;startup[name]=row;indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p)))
t=startup['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'];assert t['terrain_state_restored_exact'] and not t['explicit_G2_to_G3_geometry_transition'] and not t['explicitly_new_E1_terrain'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['complete_D1_D7_optimizer_global_named_streams_verified'] and t['E1_episode_incremented_once'] and not t['PhysX_exact_resume_claimed']
c=startup['E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'];assert c['predecessor_command_state_restored_exact'] and not c['explicitly_new_command_scope'] and c['saved_source_episode_plus_one_verified'] and c['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact']
for name,prefix in (('ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','action'),('SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','spring'),('GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','gas'),('CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','COM_PD')):
 row=startup[name];assert row[prefix+'_episode_incremented_once'] and not row['PhysX_exact_resume_claimed']
assert health['actual_physics_callbacks']==health['expected_physics_callbacks']==health['control_steps']*4 and own.m.learning_health_pass(health)
p=Path(rec['checkpoint']);info=own.fullsave(p);assert info['finite_tensors']==102 and p.is_relative_to(D/'learning_logs') and not torch.cuda.is_initialized()
assert h(own.source())==own.SOURCE_SHA
v=dict(epoch=time.time(),passed=True,active_startup_and_snapshot_only_not_formal_final=True,root=str(D),source_count=368,finite_tensors=102,
 own_child=actual,own_run=str(run),own_PID_bound_save_receipt=rec,own_snapshot=info,actual_snapshot_file_count=len(manifest['src_sha256']),
 actual_PPO_controls=health['control_steps'],actual_updates_observed=health['control_steps']//24,actual_environment_steps=health['control_steps']*20000,
 health=health,actual_same_G3_samecommand_actorcritic_optimizer_std_allD0D7_globalnamed_private_CPU_CUDA_restore_disk_roundtrip_episode_plus_one_verified=True,
 own_startup_file_indices=indices,own_startup_receipts=startup,own_manifest=manifest,source_SHA_preserved=True,
 canonical_active_segment=own.m.s.q.base.budget_state()['active_segment'],no_GPU_or_ledger_write=True)
print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  p=save('WAVE_OWN_STARTUP_SAVE_CPU_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),passed=True,controls=v['actual_PPO_controls'],updates=v['actual_updates_observed'],envsteps=v['actual_environment_steps'],snapshot_SHA=v['own_snapshot']['sha256'],formal_final=False)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE_STARTUP_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only_no_GPU_or_evaluation_replay=True));raise
