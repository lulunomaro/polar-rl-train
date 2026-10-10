"""Read actual own run and complete saved state on CPU; never launch, charge or signal."""
from pathlib import Path
import os,sys,json,shlex,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_NAMED_OWNED_20261010'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
def main():
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  code=r'''from pathlib import Path
import os,sys,json,time,hashlib
D=Path(ROOT);R=D/'reports';j=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(D));import torch;torch.set_num_threads(1);import supervise_e1_command_retention_named_owned_once as m
expected=j(R/'SOURCE_FREEZE.json')['sha256'];assert len(expected)==360 and all(H(D/n)==h for n,h in expected.items())
saved=[];pending=[]
for run in (D/'learning_logs').glob('*'):
 if not run.is_dir():continue
 if not (R/'e1_G3_command_retention_observation_PASSED.json').exists():pending.append(dict(run=str(run),phase='formal_final_not_yet_saved_or_closed'));continue
 if not (run/'latest_complete.json').exists():pending.append(dict(run=str(run),phase='own_save_not_yet_generated'));continue
 rec=j(run/'latest_complete.json');manifest=j(run/'run_manifest.json');assert rec['pid']>0 and manifest['source_map']==expected
 freeze=j(run/'rolling_source_freeze.json');assert freeze['sha256']==expected
 assert all(H(run/'e1_source_snapshot'/n)==h for n,h in expected.items())
 assert all(H(run/'src_snapshot'/n)==h for n,h in manifest['src_sha256'].items())
 info=m.fullsave(Path(rec['checkpoint']),count=manifest['num_envs']);info['bytes']=Path(rec['checkpoint']).stat().st_size;assert info['finite_tensors']>=102 and info['sha256']==H(Path(rec['checkpoint']))
 closed=j(R/'e1_G3_command_retention_observation_PASSED.json');assert closed['checkpoint']['sha256']==info['sha256'] and closed['own_PID_bound_receipt']==rec and len(closed['unique_completed_segment'])==1
 startup={n:j(run/n) for n in ('E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json')}
 for value in startup.values():assert value['source_sha256']==manifest['init_checkpoint_sha256'] and not value['PhysX_exact_resume_claimed']
 e=startup['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'];assert e['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and e['complete_D1_D7_optimizer_global_named_streams_verified'] and e['E1_episode_incremented_once']
 assert not e['terrain_state_restored_exact'] and e['explicit_G2_to_G3_geometry_transition'] and e['explicitly_new_E1_terrain']
 command=startup['E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'];assert command['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and command['old_full_D1_D7_optimizer_global_named_streams_verified'] and command['explicitly_new_command_scope'] and command['E1_episode_incremented_once']
 assert not torch.cuda.is_initialized()
 saved.append(dict(run=str(run),own_PID_bound_receipt=rec,checkpoint=info,source360_and_own_freeze_byteexact=True,snapshot_count=len(manifest['src_sha256']),full_old_D1_D7_optimizer_global_named_startup=startup,explicit_G2_to_G3_new_geometry=True,no_PhysX_exactresume_claim=True))
if not saved and not pending:pending.append(dict(phase='formal_run_not_started_or_saved_yet'))
print(json.dumps(dict(epoch=time.time(),read_only_CPU=True,no_CUDA_initialized=True,formal_saved=saved,pending=pending,actual_phase=j(R/'E1_STATE.json')['phase'],no_PPO_canonical_or_signal=True)))
'''.replace('Path(ROOT)','Path('+repr(ROOT)+')')
  _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
  out=R/('COMMAND_OWN_SAVE_ACTUAL_'+str(int(v['epoch']))+'.json');assert not out.exists();out.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),actual_phase=v['actual_phase'],formal_saved=[dict(checkpoint=x['checkpoint'],snapshot_count=x['snapshot_count']) for x in v['formal_saved']],pending=v['pending'])))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  out=R/('COMMAND_OWN_SAVE_READ_ERROR_'+str(int(time.time()))+'.json');assert not out.exists();out.write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G3-COMMAND-OWN-PID-CPU-READER-01',error=traceback.format_exc(),read_only_before_any_mutation=True),indent=2),encoding='utf8');raise
